import pytest
from httpx import Response

from fusion_stat import Staff
from fusion_stat.spiders import transfermarkt
from tests.utils import read_data


class TestStaff:
    @pytest.fixture(scope="class")
    def staff(self) -> Staff:
        transfermarkt_data = read_data(
            "transfermarkt", "mikel-arteta_profil_trainer_47620.html"
        )
        transfermarkt_spider = transfermarkt.Staff(
            id="47620", path_name="mikel-arteta"
        )
        return Staff(
            transfermarkt=transfermarkt_spider.parse(
                Response(200, text=transfermarkt_data)
            )
        )
