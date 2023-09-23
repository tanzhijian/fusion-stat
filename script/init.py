import asyncio

from fusion_stat import Competitions


async def main() -> None:
    Competitions()


if __name__ == "__main__":
    asyncio.run(main())
