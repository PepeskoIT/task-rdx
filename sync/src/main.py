import asyncio

from sync import sync


async def main():
    while True:
        await asyncio.sleep(60)
        await sync()

asyncio.run(main())
