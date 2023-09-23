import asyncio
import json
from pathlib import Path

from fusion_stat import Competitions
from fusion_stat._index import get_competitions_index


async def main() -> None:
    competitions = Competitions()
    data = await competitions.get()
    index = get_competitions_index(data)

    with open(Path("fusion_stat/static/competitions_index.json"), "w") as f:
        f.write(json.dumps(index, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
