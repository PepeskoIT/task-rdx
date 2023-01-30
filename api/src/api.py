import logging

from aiocache import Cache
from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from envs import APP_LOGGER_NAME, CACHE_PORT, CACHE_URL


class AdressesToMonitor(BaseModel):
    addresses: list[str]


logger = logging.getLogger(APP_LOGGER_NAME)

SERVICE_STATUS_PATH = "/"
TRANSFERS_DATA_PATH = "/transfers"
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
async def get_status():
    return {"message": "Backend service is available"}


@router.get(TRANSFERS_DATA_PATH)
async def get_transfers():
    return JSONResponse(
        content=jsonable_encoder(
            await cache_transfers.get(TRANSFERS_KEY) or []
            )
        )


@router.get(f"{TRANSFERS_DATA_PATH}/{{item_id}}")
async def get_transfer(item_id):
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
async def post_monitor(adresses_to_add: AdressesToMonitor):
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
async def delete_monitor():
    await cache_main.delete(ADDRESSES_TO_MONITOR_KEY)

    addresses = await cache_main.get(ADDRESSES_TO_MONITOR_KEY)
    logger.info(f"addresses currenlty monitored: {addresses}")
    if addresses is None:
        return status.HTTP_200_OK
    else:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
