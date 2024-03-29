import httpx
import pytest
import respx

from fusion_stat import App

from .utils import (
    fbref_mock,
    fotmob_mock,
    premier_league_mock,
    transfermarkt_mock,
)


@pytest.mark.anyio
async def test_fusion_close_include_client() -> None:
    app = App(client=httpx.AsyncClient(params={"a": "b"}))
    assert app._engine.downloader.client.params["a"] == "b"
    assert not app._engine.downloader.client.is_closed
    await app.close()
    assert app._engine.downloader.client.is_closed


@pytest.mark.anyio
async def test_fusion_close_context() -> None:
    async with App() as app:
        assert not app._engine.downloader.client.is_closed
    assert app._engine.downloader.client.is_closed


class TestFusion:
    @pytest.fixture(scope="class")
    def app(self, client: httpx.AsyncClient) -> App:
        return App(client=client)

    @pytest.mark.anyio
    async def test_get_competitions(self, app: App) -> None:
        fotmob_route = fotmob_mock("allLeagues.json")
        fbref_route = fbref_mock("comps_.html")
        transfermarkt_route = transfermarkt_mock("wettbewerbe_europa.html")

        with respx.mock:
            coms = await app.get_competitions()
            assert fotmob_route.called
            assert fbref_route.called
            assert transfermarkt_route.called
        assert len(coms._fotmob) > 0
        assert len(coms._fbref) > 0
        assert len(coms._transfermarkt) > 0

    @pytest.mark.anyio
    async def test_get_competition(self, app: App) -> None:
        fotmob_route = fotmob_mock("leagues?id=47.json")
        fbref_route = fbref_mock("comps_9_Premier-League-Stats.html")
        pl_route = premier_league_mock(
            "teams?pageSize=100&compSeasons=578&comps=1&altIds=true&page=0.json"
        )
        transfermarkt_route = transfermarkt_mock(
            "premier-league_startseite_wettbewerb_GB1.html"
        )

        with respx.mock:
            com = await app.get_competition(
                fotmob_id="47",
                fbref_id="9",
                fbref_path_name="Premier-League",
                official_name="Premier League",
                transfermarkt_id="GB1",
                transfermarkt_path_name="premier-league",
            )
            assert fotmob_route.called
            assert fbref_route.called
            assert pl_route.called
            assert transfermarkt_route.called
        assert com._fotmob.name
        assert com._fbref.name
        assert com._official.name
        assert com._transfermarkt.name

    @pytest.mark.anyio
    async def test_get_team(self, app: App) -> None:
        fotmob_route = fotmob_mock("teams?id=9825.json")
        fbref_route = fbref_mock("squads_18bb7c10_Arsenal-Stats.html")
        transfermarkt_route = transfermarkt_mock(
            "arsenal-fc_startseite_verein_11.html"
        )
        transfermarkt_staffs_route = transfermarkt_mock(
            "ceapi_staff_team_11_.json"
        )

        params = {
            "fotmob_id": "9825",
            "fbref_id": "18bb7c10",
            "fbref_path_name": "Arsenal",
            "transfermarkt_id": "11",
            "transfermarkt_path_name": "arsenal-fc",
        }
        with respx.mock:
            team = await app.get_team(**params)
            assert fotmob_route.called
            assert fbref_route.called
            assert transfermarkt_route.called
            assert transfermarkt_staffs_route.called
        assert team._fotmob.name
        assert team._fbref.name
        assert team._transfermarkt.name
        assert team._transfermarkt_staffs

    @pytest.mark.anyio
    async def test_get_player(self, app: App) -> None:
        fotmob_route = fotmob_mock("playerData?id=961995.json")
        fbref_route = fbref_mock("players_bc7dc64d_Bukayo-Saka.html")
        transfermarkt_route = transfermarkt_mock(
            "bukayo-saka_profil_spieler_433177.html"
        )

        with respx.mock:
            player = await app.get_player(
                fotmob_id="961995",
                fbref_id="bc7dc64d",
                fbref_path_name="Bukayo-Saka",
                transfermarkt_id="433177",
                transfermarkt_path_name="bukayo-saka",
            )
            assert fotmob_route.called
            assert fbref_route.called
            assert transfermarkt_route.called
        assert player._fotmob.name
        assert player._fbref.name
        assert player._transfermarkt.name

    @pytest.mark.anyio
    async def test_get_staff(self, app: App) -> None:
        transfermarkt_route = transfermarkt_mock(
            "mikel-arteta_profil_trainer_47620.html"
        )

        with respx.mock:
            staff = await app.get_staff(
                transfermarkt_id="47620",
                transfermarkt_path_name="mikel-arteta",
            )
            assert transfermarkt_route.called
        assert staff._transfermarkt.name

    @pytest.mark.anyio
    async def test_get_matches(self, app: App) -> None:
        fotmob_route = fotmob_mock("matches?date=20230903.json")

        with respx.mock:
            matches = await app.get_matches(date="2023-09-03")
            assert fotmob_route.called
        assert len(matches._fotmob) > 0

    @pytest.mark.anyio
    async def test_get_match(self, app: App) -> None:
        fotmob_route = fotmob_mock("matchDetails?matchId=4193490.json")

        with respx.mock:
            match = await app.get_match(fotmob_id="4193490")
            assert fotmob_route.called
        assert match._fotmob.name
