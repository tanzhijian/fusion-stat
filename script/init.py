import asyncio
import json
from pathlib import Path

from fusion_stat import Competitions


async def main() -> None:
    competitions = Competitions()
    await competitions.get()
    index = competitions.index()

    with open(
        Path(
            Path(__file__).resolve().parent,
            "static/competitions_index.json",
        ),
        "w",
    ) as f:
        f.write(json.dumps(index, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
