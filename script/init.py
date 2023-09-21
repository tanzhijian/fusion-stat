import asyncio

from fusion_stat import Competitions


async def main() -> None:
    competitions = Competitions()
    data = await competitions.get()
    competitions._export_index(data)


if __name__ == "__main__":
    asyncio.run(main())
