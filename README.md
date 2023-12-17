# fusion-stat

A football data scraper that can scrape data from multiple sources simultaneously.

## Installation

```
pip install fusion-stat
```

## Usage

```python
from fusion_stat import Fusion, Competitions, Competition
```

You can use it like this

```python
async with Fusion() as fusion:
    competitions = await fusion.get_competitions()
```

or

```python
fusion = Fusion()
competitions = await fusion.get_competitions()
await fusion.aclose()
```

```python
index = competitions.index()
index
```

    [{'fotmob_id': '47',
      'fbref_id': '9',
      'fbref_path_name': 'Premier-League',
      'official_name': 'Premier League'},
     {'fotmob_id': '87',
      'fbref_id': '12',
      'fbref_path_name': 'La-Liga',
      'official_name': 'La Liga'},
     {'fotmob_id': '54',
      'fbref_id': '20',
      'fbref_path_name': 'Bundesliga',
      'official_name': 'Bundesliga'},
     {'fotmob_id': '55',
      'fbref_id': '11',
      'fbref_path_name': 'Serie-A',
      'official_name': 'Serie A'},
     {'fotmob_id': '53',
      'fbref_id': '13',
      'fbref_path_name': 'Ligue-1',
      'official_name': 'Ligue 1'}]

You can also use it like this

```python
import httpx

async with httpx.AsyncClient() as client:
    fusion = Fusion(client=client)
    competition = await fusion.get_competition(**index[0])
```

```python
competition.info
```

    {'id': '47',
     'name': 'Premier League',
     'logo': 'https://www.premierleague.com/resources/rebrand/v7.129.2/i/elements/pl-main-logo.png',
     'type': 'league',
     'season': '2023/2024',
     'names': {'Premier League'}}

```python
competition.teams[1]
```

    {'id': '9825',
     'name': 'Arsenal',
     'names': {'Arsenal'},
     'played': 16,
     'wins': 11,
     'draws': 3,
     'losses': 2,
     'goals_for': 33,
     'goals_against': 15,
     'points': 36,
     'logo': 'https://resources.premierleague.com/premierleague/badges/rb/t3.svg',
     'shooting': {'shots': 237.0, 'xg': 29.0}}
