import logging
from envs import CACHE_PORT, CACHE_URL, APP_LOGGER_NAME
from enum import Enum
logger = logging.getLogger(APP_LOGGER_NAME)

SUBSTATE_OPERATION_SHUTDOWN = "SHUTDOWN"
SUBSTATE_OPERATION_BOOTUP = "BOOTUP"
OPERATION_RESOURCE = "Resource"


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
    logger.debug(f"operations: {operations}")
    num_of_operations = len(operations)

    for operation in operations:
        if not is_resource_operation(operation):
            # skip this group
            raise TransactionParsingError(
                    f"Not processed due to {operation['type']} in operations"
                )
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
            # else?
        if is_bootup_substate_operation(operation):
            # operation_amout = operation["amount"]
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
    if transfer_amount and abs(transfer_amount) == abs(operation_amount):
        logger.info(f"transfer detected: {operations}")

        return {
            "from_address": from_address, "to_address": to_address,
            "rri": rri, "transfer_amount": transfer_amount
        }


def parse_transaction(transaction):
    results = []

    # logger.debug(f"transaction: {transaction}")
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
