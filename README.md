# fusion-stat

A football data scraper that can scrape data from multiple sources simultaneously.

## Installation

```
pip install fusion-stat
```

## Usage

```python
from fusion_stat import Fusion
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
await fusion.close()
```

```python
params = competitions.get_params()
pl_params = next(params)
pl_params
```

    {'fotmob_id': '47',
     'fbref_id': '9',
     'fbref_path_name': 'Premier-League',
     'official_name': 'Premier League',
     'transfermarkt_id': 'GB1',
     'transfermarkt_path_name': 'premier-league'}

The client uses httpx.AsyncClient, you can also customize parameters.

```python
import httpx

client = httpx.AsyncClient()
async with Fusion(client=client) as fusion:
    competition = await fusion.get_competition(**pl_params)
```

```python
competition.info
```

    {'id': '47',
     'name': 'Premier League',
     'logo': 'https://www.premierleague.com/resources/rebrand/v7.129.2/i/elements/pl-main-logo.png',
     'type': 'league',
     'season': '2023/2024',
     'country_code': 'ENG',
     'names': {'Premier League'},
     'market_values': '€10.96bn',
     'player_average_market_value': '€19.54m'}

```python
competition.teams[1]
```

    {'id': '8456',
     'name': 'Manchester City',
     'names': {'Man City', 'Manchester City'},
     'played': 20,
     'wins': 13,
     'draws': 4,
     'losses': 3,
     'goals_for': 48,
     'goals_against': 23,
     'points': 43,
     'country_code': 'ENG',
     'market_values': '€1.29bn',
     'logo': 'https://resources.premierleague.com/premierleague/badges/rb/t43.svg',
     'shooting': {'shots': 333, 'xg': 39.7}}
