# fusion-stat

A football data scraper that can scrape data from multiple sources simultaneously.

## Installation

```
pip install fusion-stat
```

## Usage

```python
from fusion_stat import Competitions, Competition
```

You can use it like this

```python
competitions = Competitions()
fusion = await competitions.gather()
index = fusion.index()
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
    competition = Competition(
        **index[0],
        client=client,
    )
    fusion = await competition.gather()
```

```python
fusion.info
```

    {'name': 'Premier League',
     'logo': 'https://www.premierleague.com/resources/rebrand/v7.129.2/i/elements/pl-main-logo.png',
     'type': 'league',
     'season': '2023/2024',
     'names': {'Premier League'}}

```python
fusion.teams[3]
```

    {'name': 'Arsenal',
     'names': {'Arsenal'},
     'played': 11,
     'wins': 7,
     'draws': 3,
     'losses': 1,
     'goals_for': 23,
     'goals_against': 9,
     'points': 24,
     'logo': 'https://resources.premierleague.com/premierleague/badges/rb/t3.svg',
     'shooting': {'shots': 152.0, 'xg': 19.2}}
