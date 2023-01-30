import asyncio
import logging
from enum import Enum

from aiocache import Cache

from core_api import core_api, network_api
from envs import APP_LOGGER_NAME, CACHE_PORT, CACHE_URL
from logging_setup import load_logger_config

load_logger_config()

logger = logging.getLogger(APP_LOGGER_NAME)

SUBSTATE_OPERATION_SHUTDOWN = "SHUTDOWN"
SUBSTATE_OPERATION_BOOTUP = "BOOTUP"
OPERATION_RESOURCE = "Resource"

ADDRESSES_TO_MONITOR_KEY = "addresses_to_monitor"
LAST_STATE_VERSION_KEY = "last_state_version"
TRANSACTIONS_KEY = "transactions"
CORE_API_TRANSACTIONS_ENDPOINT = "/transactions"
NETWORK_API_STATUS_ENDPOINT = "/network/status"
TRANSATIONS_QUERY_LIMIT = 100000

cache_main = Cache(
    Cache.REDIS, endpoint=CACHE_URL, port=CACHE_PORT, namespace="main"
    )

cache_transfers = Cache(
    Cache.REDIS, endpoint=CACHE_URL, port=CACHE_PORT, namespace="transfers"
    )


class TransactionParsingError(Exception):
    pass


class Operation(Enum):
    RESOURCE = "Resource"
    RESOURCE_AND_DATA = "ResourceAndData"


class SubstateOperation(Enum):
    SHUTDOWN = "SHUTDOWN"
    BOOTUP = "BOOTUP"


def is_resource_operation(operation):
    return operation["type"] == Operation.RESOURCE.value


def is_resource_and_data_operation(operation):
    return operation["type"] == Operation.RESOURCE_AND_DATA.value


def is_shutdown_substate_operation(operation):
    return (
        operation["substate"]["substate_operation"]
        == SubstateOperation.SHUTDOWN.value
    )


def is_bootup_substate_operation(operation):
    return (
        operation["substate"]["substate_operation"]
        == SubstateOperation.BOOTUP.value
    )


def detect_transfer(operation_group):
    # TODO: Refactor and adapt to fact that "metadata" is not present in
    # operation groups
    shutdown_found = False
    from_address = None  # shutdown
    to_address = None  # bootup
    shutdown_amount = None  # negative
    shutdown_rri = None
    bootup_amount = None  # positive
    bootup_rri = None
    operation_amount = None
    transfer_amount = None

    operations = operation_group["operations"]
    num_of_operations = len(operations)

    for operation in operations:
        if not is_resource_operation(operation):
            # skip this group
            return
            # raise TransactionParsingError(
            #         f"Not processed due to {operation['type']} in operations"
            #     )
        operation_amount_data = operation["amount"]
        address = operation["entity_identifier"]["address"]
        amount = int(operation_amount_data["value"])
        resource_type = operation_amount_data["resource_identifier"]["type"]
        if resource_type == "Token":
            rri = operation_amount_data["resource_identifier"]["rri"]
        else:
            raise TransactionParsingError(
                    "Not processed due to "
                    f"resource {resource_type} in operations"
                )
        if is_shutdown_substate_operation(operation):
            if shutdown_found:
                logger.error("Found more then one shutdown in operations")
                raise TransactionParsingError(
                    "more then one shutdown"
                    )
            else:
                shutdown_found = True
            # DRY this part
            from_address = address
            shutdown_amount = amount
            shutdown_rri = rri
        if is_bootup_substate_operation(operation):
            bootup_rri = rri
            if bootup_rri != shutdown_rri:
                logger.error("Found more then one token rri in operations")
                raise TransactionParsingError(
                    "more then one rii"
                    )
            to_address = address
            bootup_amount = amount

            if to_address == from_address:
                operation_amount = shutdown_amount + bootup_amount
            else:
                transfer_amount = bootup_amount

    if not transfer_amount and operation_amount:
        logger.debug(f"burn or fee detected: {operations}")

    if to_address != from_address and num_of_operations > 3:
        logger.error(f"number of operations >3: {num_of_operations}")
        logger.error(operations)

    logger.debug(f"{transfer_amount} - {operation_amount}")
    if transfer_amount:  # abs(transfer_amount) == abs(operation_amount):
        logger.info(f"transfer detected: {operations}")

        return {
            "from_address": from_address, "to_address": to_address,
            "rri": rri, "transfer_amount": transfer_amount
        }


def parse_transaction(transaction):
    results = []

    state_version = transaction["committed_state_identifier"]["state_version"]
    for operation_group in transaction["operation_groups"]:
        try:
            detected_transfer = detect_transfer(operation_group)
        except TransactionParsingError as e:
            logger.debug(
                f"{type(e).__name__} - {str(e)}. "
                f'{state_version}'
                )
        except Exception:
            logger.exception(
                "Unhandled exception :"
                f'{state_version}'
            )
            raise
        else:
            if detected_transfer:
                detected_transfer["state_version"] = state_version
                results.append(detected_transfer)
    return results


async def sync():
    core_api.prepare_session()
    network_api.prepare_session()


    last_state_version = await cache_main.get(LAST_STATE_VERSION_KEY)
    logger.debug(f"last processed state_version {last_state_version}")

    network_state_version = (await (await network_api.post(
        NETWORK_API_STATUS_ENDPOINT, ssl=False,
        json={"network_identifier": {"network": "mainnet"}}
        )).json())["current_state_identifier"]["state_version"]

    logger.debug(f"network state_version {network_state_version}")
    if last_state_version is None:
        # this is the point from wich we start processing data
        # for now just store the state version
        await cache_main.set(LAST_STATE_VERSION_KEY, network_state_version-1)
        return

    # think about last state cleanup if network node get reset
    # what about addresses to monitor change? I guess ignore atm
    if last_state_version >= network_state_version:
        logger.info(
            f"last_state_version {last_state_version} >= network_state_version"
            f" {network_state_version}. nothing to do"
            )
        return

    # if last_state_version is empty start from current network_state_version
    last_state_version = last_state_version or network_state_version

    state_diff = network_state_version - last_state_version
    logger.debug(
        f"{state_diff}(diff)={network_state_version}(network_state_version)"
        f"-{last_state_version}(last_state_version)"
    )
    iters, left = divmod(state_diff, TRANSATIONS_QUERY_LIMIT)
    cur_state_version = last_state_version
    logger.debug(f"curent state version: {cur_state_version}")

    addresses_to_monitor = await cache_main.get(ADDRESSES_TO_MONITOR_KEY)
    logger.debug(f"addresses_to_monitor: {addresses_to_monitor}")

    transactions_to_store = await cache_main.get(TRANSACTIONS_KEY) or []
    logger.debug(f"transactions in db: {transactions_to_store}")

    # TODO:  ===refactor block begin===
    for _ in range(iters):
        transactions = (await (await core_api.post(
            CORE_API_TRANSACTIONS_ENDPOINT, ssl=False,
            json={
                "network_identifier": {
                    "network": "mainnet"
                },
                "state_identifier": {
                    "state_version": cur_state_version
                },
                "limit": TRANSATIONS_QUERY_LIMIT
            }
            )).json())["transactions"]
        #   ----------------
        for transaction in transactions:
            transactions_to_store.extend(parse_transaction(transaction))
    # ------------
        cur_state_version += TRANSATIONS_QUERY_LIMIT
        logger.debug(f"curent state version: {cur_state_version}")

    transactions = (await (await core_api.post(
        CORE_API_TRANSACTIONS_ENDPOINT, ssl=False,
        json={
            "network_identifier": {
                "network": "mainnet"
            },
            "state_identifier": {
                "state_version": cur_state_version
            },
            "limit": left
        }
        )).json())["transactions"]
    # --------------------
    for transaction in transactions:
        transactions_to_store.extend(parse_transaction(transaction))

    # TODO:  ===refactor block end===
    # --------------------
    cur_state_version += left
    logger.debug(f"curent state version: {cur_state_version}")

    if cur_state_version == network_state_version:
        logger.info("end of sync")
    logger.info(transactions_to_store)
    await cache_main.set(TRANSACTIONS_KEY, cur_state_version)
    await cache_main.set(LAST_STATE_VERSION_KEY, transactions_to_store)


async def main():
    while True:
        await sync()
        await asyncio.sleep(300)

asyncio.run(main())
