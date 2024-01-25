import pytest

from fusion_stat import Staff


class TestStaff:
    @pytest.fixture(scope="class")
    def staff(self) -> Staff:
        return Staff()
