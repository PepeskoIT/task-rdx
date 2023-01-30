import logging

from aiocache import Cache
from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from envs import APP_LOGGER_NAME, CACHE_PORT, CACHE_URL


class AdressesToMonitor(BaseModel):
    addresses: list[str]


logger = logging.getLogger(APP_LOGGER_NAME)

SERVICE_STATUS_PATH = "/"
TRANSFERS_DATA_PATH = "/transfers"
FILTER_TRANSFERS_DATA_PATH = f"{TRANSFERS_DATA_PATH}/{{item_id}}"
MONITOR_DATA_PATH = "/monitor"

ADDRESSES_TO_MONITOR_KEY = "addresses_to_monitor"
LAST_STATE_VERSION_KEY = "last_state_version"
TRANSFERS_KEY = "transfers"


cache_main = Cache(
    Cache.REDIS, endpoint=CACHE_URL, port=CACHE_PORT, namespace="main"
    )

cache_transfers = Cache(
    Cache.REDIS, endpoint=CACHE_URL, port=CACHE_PORT, namespace="transfers"
    )

router = APIRouter()


@router.get(SERVICE_STATUS_PATH)
async def get_status() -> JSONResponse:
    """Return backend status message.

    Returns:
        JSONResponse: backend status message
    """
    return {"message": "Backend service is available"}


@router.get(TRANSFERS_DATA_PATH)
async def get_transfers() -> JSONResponse:
    """Return all stored token transfers.

    Returns:
        JSONResponse: all found token transfers encoded into json
    """
    return JSONResponse(
        content=jsonable_encoder(
            await cache_transfers.get(TRANSFERS_KEY) or []
            )
        )


@router.get(FILTER_TRANSFERS_DATA_PATH)
async def get_filtered_transfers(item_id: str) -> JSONResponse:
    """Returns transfers 'to' the monitored address or transfers 'with'
    given token rri_id.

    Args:
        item_id (str): address or token rri_id

    Returns:
        JSONResponse: filtered found token transfers encoded into json
    """
    logger.debug(f"start with id {item_id}")
    response = []

    stored_transfers = await cache_transfers.get(TRANSFERS_KEY) or []
    # TODO: performance key lookup issue. Consider regular db with proper key
    # indexing for efficient lookups, take a look at REDIS OM or apply some
    # key hashing.
    for transfer in stored_transfers:
        # TODO: create common data class for transfer metadata
        if item_id in (transfer["rri"], transfer["to_address"]):
            response.append(transfer)

    return JSONResponse(content=jsonable_encoder(response))


@router.post(MONITOR_DATA_PATH)
async def post_monitor(adresses_to_add: AdressesToMonitor) -> Response:
    """Add addresses to monitor with including already stored.

    Args:
        adresses_to_add (AdressesToMonitor): post request body of
        {"addresses": <list_of_str_addresses>}

    Returns:
        Response: addresses pocessing status
    """
    addresses = await cache_main.get(ADDRESSES_TO_MONITOR_KEY)
    logger.debug(f"addresses currenlty monitored: {addresses}")

    new_addresses = adresses_to_add.addresses
    logger.debug(f"adding new addresses: {new_addresses}")
    addresses = addresses or []
    addresses.extend(new_addresses)
    await cache_main.set(ADDRESSES_TO_MONITOR_KEY, list(set(addresses)))

    addresses = await cache_main.get(ADDRESSES_TO_MONITOR_KEY)
    logger.info(f"addresses currenlty monitored: {addresses}")
    return status.HTTP_200_OK


@router.delete(MONITOR_DATA_PATH)
async def delete_monitor() -> Response:
    """Deletes all stored monitoring addressess.

    Returns:
        Response: addresses deletion status
    """
    await cache_main.delete(ADDRESSES_TO_MONITOR_KEY)

    addresses = await cache_main.get(ADDRESSES_TO_MONITOR_KEY)
    logger.info(f"addresses currenlty monitored: {addresses}")
    if addresses is None:
        return status.HTTP_200_OK
    else:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
