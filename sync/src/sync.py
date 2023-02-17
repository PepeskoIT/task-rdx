import logging
from enum import Enum
from typing import Mapping, Sequence, Union

from aiocache import Cache

from core_api import core_api, network_api
from envs import (APP_LOGGER_NAME, CACHE_PORT, CACHE_URL,
                  ONLY_MONITORED_ADDRESSES)
from logging_setup import load_logger_config

load_logger_config()

logger = logging.getLogger(APP_LOGGER_NAME)

# REDIS
ADDRESSES_TO_MONITOR_KEY = "addresses_to_monitor"
LOCAL_STATE_VERSION_KEY = "local_state_version"
TRANSFERS_KEY = "transfers"

# CORE API
CORE_API_TRANSACTIONS_ENDPOINT = "/transactions"
NETWORK_API_STATUS_ENDPOINT = "/network/status"
TRANSACTIONS_QUERY_LIMIT = 100000
SUBSTATE_OPERATION_SHUTDOWN = "SHUTDOWN"
SUBSTATE_OPERATION_BOOTUP = "BOOTUP"
OPERATION_RESOURCE = "Resource"

ACCOUNT_ADDRESS_PREFIX = "rdx1"

cache_main = Cache(
    Cache.REDIS, endpoint=CACHE_URL, port=CACHE_PORT, namespace="main"
)
cache_transfers = Cache(
    Cache.REDIS, endpoint=CACHE_URL, port=CACHE_PORT, namespace="transfers"
)


class NotSupported(Exception):
    pass


class Operation(Enum):
    RESOURCE = "Resource"


class Resource(Enum):
    TOKEN = "Token"


class SubstateOperation(Enum):
    SHUTDOWN = "SHUTDOWN"
    BOOTUP = "BOOTUP"


def is_resource_operation(operation_type: str) -> bool:
    return operation_type == Operation.RESOURCE.value


def is_token_resource(resource_type: str) -> bool:
    return resource_type == Resource.TOKEN.value


def is_shutdown_substate_operation(substate_operation: str) -> bool:
    return substate_operation == SubstateOperation.SHUTDOWN.value


def is_bootup_substate_operation(substate_operation: str) -> bool:
    return substate_operation == SubstateOperation.BOOTUP.value


def get_token_transfer_operation(operation_group: Mapping) -> Mapping:
    """Extracts metadata of simple token transferrers from address A to
    address B. Does not track stacking, burning or network emissions.
    # TODO: do more test cases to find missing transfers, break into smaller
    # pieces

    Args:
        operation_group (Mapping): object representing part of transaction

    Returns:
        Mapping: detected token transfer
    """

    shutdown_found = False
    from_address = None  # shutdown
    to_address = None  # bootup
    transfer_amount = None
    transfers = {}
    transfers_meta = {}
    valid_transactions = []  # I think there should be only one but lets try it

    operations = operation_group["operations"]

    for operation in operations:
        # -- CHECKS START
        # 1. check if Resource Operation
        if not is_resource_operation(operation["type"]):
            continue  # TODO: or abort whole group?

        # 2. check if has amount key
        try:
            operation_amount_data = operation["amount"]
        except KeyError:
            # does this ever happen in Resource Operation?
            logger.warning(
                f"No 'amount' key in resource operations: {operation}"
            )
            continue

        # 3. check if stacking
        operation_entity_identifier = operation["entity_identifier"]
        try:
            operation_entity_identifier["sub_entity"]
        except KeyError:
            pass
        else:
            # don't process staking
            continue

        # 4. check if token
        resource_type = operation_amount_data["resource_identifier"]["type"]
        if is_token_resource(resource_type):
            rri = operation_amount_data["resource_identifier"]["rri"]
        else:
            continue  # TODO: or abort whole group?
        # 5. check if address starts with rdx1 prefix?
        # -- CHECKS END

        address = operation["entity_identifier"]["address"]
        amount = operation_amount_data["value"]
        substate_operation = operation["substate"]["substate_operation"]
        if is_shutdown_substate_operation(substate_operation):
            shutdown_found = True  # at least one valid shutdown
        # group by addresses and record balance changes for each
        try:
            address_transfers = transfers[address]
        except KeyError:
            transfers[address] = {rri: int(amount)}
        else:
            # try:
            address_transfers[rri] += int(amount)

    if not shutdown_found:
        # when there is no shutdown there is no transfer from A to B
        return

    # find address pairs for each token - maybe only one token is possible?
    for address in transfers:
        address_transfers = transfers[address]
        for rri in address_transfers:
            rri_transfer_amount = address_transfers[rri]
            try:
                rri_meta = transfers_meta[rri]
            except KeyError:
                transfers_meta[rri] = {}  # consider defaultdict
                rri_meta = transfers_meta[rri]
            if rri_transfer_amount > 0:
                if "to" in rri_meta:
                    logger.error(f"transfers: {transfers}")
                    raise Exception(
                        "duplicated 'to' entries for (address,key) pair in "
                        "operation group"
                    )
                rri_meta["to"] = {
                    "address": address, "amount": rri_transfer_amount
                }
            else:
                if "from" in rri_meta:
                    logger.error(f"transfers: {transfers}")
                    raise Exception(
                        "duplicated 'from' entries for (address,key) pair in "
                        "operation group"
                    )
                rri_meta["from"] = {
                    "address": address, "amount": rri_transfer_amount
                }

    for rri in transfers_meta:
        if "from" in transfers_meta[rri] and "to" in transfers_meta[rri]:
            if (
                abs(transfers_meta[rri]["to"]["amount"])
                == abs(transfers_meta[rri]["from"]["amount"])
            ):
                from_address = transfers_meta[rri]["from"]["address"]
                to_address = transfers_meta[rri]["to"]["address"]
                transfer_amount = str(transfers_meta[rri]["to"]["amount"])
                valid_transactions.append({
                    "from_address": from_address, "to_address": to_address,
                    "rri": rri, "transfer_amount": transfer_amount
                })
            else:
                logger.error(
                    "Detected transaction but amount's didn't match: "
                    "f{operation_group}"
                )

    if len(valid_transactions) > 1:
        logger.error(
            f"Operation group with many valid transactions {operation_group}"
        )
        raise Exception(
            "Seems like group operation can have many token transactions!"
        )

        # TODO: create common data class for transfer metadata
    if valid_transactions:
        logger.debug(f"transfer detected: {operations}")
        return valid_transactions[0]


def get_token_transfers(transaction: Mapping) -> Sequence[Mapping]:
    """Process single transaction item from 'transactions' key provided by
    Core Api /transactions endpoint response.

    Args:
        transaction (Mapping): single transaction

    Returns:
        Sequence[Mapping]: sequence of found transactions
    """
    results = []

    if not transaction:
        logger.warning("not able to process empty transaction")
        return results

    # TODO:consider more exceptions proof parsing
    state_version = transaction["committed_state_identifier"]["state_version"]
    for operation_group in transaction["operation_groups"]:
        try:
            token_transfer_metadata = get_token_transfer_operation(
                operation_group
            )
        except NotSupported as e:
            logger.debug(
                f"{type(e).__name__} - {str(e)}. "
                f'{state_version}'
            )
        except Exception:
            logger.exception(
                "Unhandled exception :"
                f'{state_version}'
            )
        else:
            if token_transfer_metadata:
                token_transfer_metadata["state_version"] = state_version
                results.append(token_transfer_metadata)
    return results


async def get_transactions(
    state_version: Union[str, int], limit: Union[str, int]
) -> Sequence:
    """Request transactions from Core Api.

    Args:
        state_version (Union[str, int]): value passed to api's state_version
            request parameter

        limit (Union[str, int]): value passed to api's "limit"
            request parameter

    Returns:
        Sequence: transactions
    """
    transactions = (await (await core_api.post(
        CORE_API_TRANSACTIONS_ENDPOINT, ssl=False,
        json={
            "network_identifier": {
                "network": "mainnet"
            },
            "state_identifier": {
                "state_version": state_version
            },
            "limit": limit
        }
    )).json())["transactions"]
    return transactions


async def sync() -> None:
    """Synchronize stored token transfers from local 'local_state_version' to
    latest reported 'state_version' reported by Core Api.
    """
    # TODO: break into smaller pieces
    transfers_to_add = []

    core_api.prepare_session()
    network_api.prepare_session()

    local_state_version = await cache_main.get(LOCAL_STATE_VERSION_KEY)
    logger.debug(f"last processed state_version {local_state_version}")
    latest_state_version = (await (await network_api.post(
        NETWORK_API_STATUS_ENDPOINT, ssl=False,
        json={"network_identifier": {"network": "mainnet"}}
    )).json())["current_state_identifier"]["state_version"]

    logger.debug(f"latest reported state_version {latest_state_version}")
    if local_state_version is None:
        # this is the point from which we start processing data
        # for now just store the state version and wait for next call
        await cache_main.set(LOCAL_STATE_VERSION_KEY, latest_state_version-1)
        return

    if local_state_version >= latest_state_version:
        logger.info(
            f"last_state_version {local_state_version} >= latest_state_version"
            f" {latest_state_version}. nothing to do"
        )
        return

    state_diff = latest_state_version - local_state_version
    logger.debug(
        f"difference between last and latest state versions: {state_diff}"
    )
    iters, left = divmod(state_diff, TRANSACTIONS_QUERY_LIMIT)
    cur_state_version = local_state_version
    logger.debug(f"current state version: {cur_state_version}")

    addresses_to_monitor = await cache_main.get(ADDRESSES_TO_MONITOR_KEY)
    logger.debug(f"addresses_to_monitor: {addresses_to_monitor}")

    # TODO: this is not memory efficient. Consider using direct Redis client
    # RPUSH usage to avoid loading and merging everything into python memory.
    # However atomicity is also to be taken into consideration.
    all_transfers = await cache_transfers.get(TRANSFERS_KEY) or []
    logger.debug(f"transfers in db: {all_transfers}")

    # TODO: instead of batch processing consider stream for lower memory usage
    # TODO: consider node malfunction mitigation - node reports version
    for _ in range(iters):
        # TODO: consider utilizing async requests response aggregation instead
        # of sync processing
        transactions = await get_transactions(
            cur_state_version, TRANSACTIONS_QUERY_LIMIT
        )
        for transaction in transactions:
            transfers_to_add = get_token_transfers(transaction)
        cur_state_version += len(transactions)
        logger.debug(f"current state version: {cur_state_version}")

    if left:
        transactions = await get_transactions(
            cur_state_version, left
        )
        for transaction in transactions:
            transfers_to_add.extend(get_token_transfers(transaction))
        cur_state_version += len(transactions)

    logger.debug(f"current state version: {cur_state_version}")

    if cur_state_version == latest_state_version:
        logger.info(
            f"current state_version: {cur_state_version} "
            f"== latest state version: {latest_state_version}"
        )
    else:
        logger.critical(
            "Synchronization process did not cover whole state difference. "
            f"current state_version: {cur_state_version} "
            f"!= latest state version: {latest_state_version}. "
            "One of possible causes could be that node did not provide all "
            "available transactions"
        )
        raise NotSupported(
            "Case when api is returning less data then promised is "
            "not supported at the moment."
        )

    logger.info("number of all new transfers: "f"{len(transfers_to_add)}")
    if int(ONLY_MONITORED_ADDRESSES):
        # TODO: should we allow deleting old detected transfers if
        # monitored addresses change? At the moment change in
        # address_to_monitor affect only 'new' batch of detected transfers.
        transfers_to_add = [
            transfer
            for transfer in transfers_to_add
            if (
                transfer["from_address"] in addresses_to_monitor
                or transfer["to_address"] in addresses_to_monitor
            )
        ]
        logger.info(
            "number of new transfers matching monitored addresses "
            f"{len(transfers_to_add)}"
        )
    await cache_transfers.set(
        TRANSFERS_KEY, all_transfers + transfers_to_add
    )
    await cache_main.set(LOCAL_STATE_VERSION_KEY, cur_state_version)
