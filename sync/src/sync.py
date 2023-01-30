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
LAST_STATE_VERSION_KEY = "last_state_version"
TRANSFERS_KEY = "transfers"

# CORE API
CORE_API_TRANSACTIONS_ENDPOINT = "/transactions"
NETWORK_API_STATUS_ENDPOINT = "/network/status"
TRANSATIONS_QUERY_LIMIT = 100000
SUBSTATE_OPERATION_SHUTDOWN = "SHUTDOWN"
SUBSTATE_OPERATION_BOOTUP = "BOOTUP"
OPERATION_RESOURCE = "Resource"

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
    """Extracts metadata of simple transfersers.
    WARNING: Not all cases may be supported yet.
    # TODO: do more test cases to find missing transfers

    Args:
        operation_group (Mapping): object representing part of transaction

    Raises:
        NotSupported: when ther are multiple shutdowns in operation group
        NotSupported: when there are multiple rri's in operation group

    Returns:
        Mapping: detected token transfer
    """

    shutdown_found = False
    from_address = None  # shutdown
    to_address = None  # bootup
    shutdown_rri = None
    bootup_amount = None  # positive
    bootup_rri = None
    transfer_amount = None

    operations = operation_group["operations"]

    for operation in operations:
        if not is_resource_operation(operation["type"]):
            continue  # TODO: or abort whole group?
        operation_amount_data = operation["amount"]
        resource_type = operation_amount_data["resource_identifier"]["type"]
        if is_token_resource(resource_type):
            rri = operation_amount_data["resource_identifier"]["rri"]
        else:
            continue  # TODO: or abort whole group?
        address = operation["entity_identifier"]["address"]
        amount = operation_amount_data["value"]
        substate_operation = operation["substate"]["substate_operation"]
        if is_shutdown_substate_operation(substate_operation):
            if shutdown_found:
                raise NotSupported(
                    "more then one shutdown"
                    )
            else:
                shutdown_found = True
            from_address = address
            shutdown_rri = rri
        if is_bootup_substate_operation(substate_operation):
            bootup_rri = rri
            if bootup_rri != shutdown_rri:
                raise NotSupported(
                    "more then one rri"
                    )
            to_address = address
            bootup_amount = amount
            if to_address != from_address:
                transfer_amount = bootup_amount

    if transfer_amount:
        logger.info(f"transfer detected: {operations}")

        # TODO: create common data class for transfer metadata
        return {
            "from_address": from_address, "to_address": to_address,
            "rri": rri, "transfer_amount": transfer_amount
        }


def get_token_transfers(transaction: Mapping) -> Sequence[Mapping]:
    """Process single transaction item from 'transactions' key provided by
    Core Api /transactions endpoint response.

    Args:
        transaction (Mapping): single transation

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
    """Synchronize stored token transfers from local 'last_state_version' to
    latest reported 'state_version' reported by Core Api.
    """
    core_api.prepare_session()
    network_api.prepare_session()

    last_state_version = await cache_main.get(LAST_STATE_VERSION_KEY)
    logger.debug(f"last processed state_version {last_state_version}")
    latest_state_version = (await (await network_api.post(
        NETWORK_API_STATUS_ENDPOINT, ssl=False,
        json={"network_identifier": {"network": "mainnet"}}
        )).json())["current_state_identifier"]["state_version"]

    logger.debug(f"latest reported state_version {latest_state_version}")
    if last_state_version is None:
        # this is the point from wich we start processing data
        # for now just store the state version and wait for next call
        await cache_main.set(LAST_STATE_VERSION_KEY, latest_state_version-1)
        return

    if last_state_version >= latest_state_version:
        logger.info(
            f"last_state_version {last_state_version} >= latest_state_version"
            f" {latest_state_version}. nothing to do"
            )
        return

    state_diff = latest_state_version - last_state_version
    logger.debug(
        f"difference between last and latest state versions: {state_diff}"
    )
    iters, left = divmod(state_diff, TRANSATIONS_QUERY_LIMIT)
    cur_state_version = last_state_version
    logger.debug(f"curent state version: {cur_state_version}")

    addresses_to_monitor = await cache_main.get(ADDRESSES_TO_MONITOR_KEY)
    logger.debug(f"addresses_to_monitor: {addresses_to_monitor}")

    # TODO: this is not memory efficient. Consider using direct Redis client
    # RPUSH usage to avoid loading and merging everything into python memory.
    # However atomicity is also to be taken into consideration.
    all_transfers = await cache_transfers.get(TRANSFERS_KEY) or []
    logger.debug(f"transfers in db: {all_transfers}")

    # TODO: instead of batch processing consider stream for lower memory usage
    for _ in range(iters):
        transactions = await get_transactions(
            cur_state_version, TRANSATIONS_QUERY_LIMIT
        )
        for transaction in transactions:
            transfers_to_add = get_token_transfers(transaction)
        cur_state_version += TRANSATIONS_QUERY_LIMIT
        logger.debug(f"curent state version: {cur_state_version}")

    if left:
        transactions = await get_transactions(
            cur_state_version, left
        )
        for transaction in transactions:
            transfers_to_add.extend(get_token_transfers(transaction))
        cur_state_version += left

    logger.debug(f"curent state version: {cur_state_version}")

    if cur_state_version == latest_state_version:
        logger.info(
            f"current state_version: {cur_state_version} "
            f"== latest state version: {latest_state_version}"
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
    await cache_main.set(LAST_STATE_VERSION_KEY, cur_state_version)
