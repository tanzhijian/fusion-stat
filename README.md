# fusion-stat

A football data scraper that can scrape data from multiple sources simultaneously.

## Installation

```
pip install fusion-stat
```

## Usage

```python
from fusion_stat import App
```

You can use it like this

```python
async with App() as app:
    competitions = await app.get_competitions()
```

or

```python
app = App()
competitions = await app.get_competitions()
await app.close()
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
async with App(client=client) as app:
    competition = await app.get_competition(**pl_params)
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
     'market_values': '€11.09bn',
     'player_average_market_value': '€20.85m'}

```python
competition.teams[1]
```

    {'id': '8650',
     'name': 'Liverpool',
     'names': {'Liverpool'},
     'played': 28,
     'wins': 19,
     'draws': 7,
     'losses': 2,
     'goals_for': 65,
     'goals_against': 26,
     'points': 64,
     'country_code': 'ENG',
     'market_values': '€921.40m',
     'logo': 'https://resources.premierleague.com/premierleague/badges/rb/t14.svg',
     'shooting': {'shots': 534, 'xg': 62.6}}
