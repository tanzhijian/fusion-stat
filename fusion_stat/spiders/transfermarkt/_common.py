from datetime import datetime

from parsel import Selector

from ...utils import get_element_text

BASE_URL = "https://www.transfermarkt.com"
HEADERS = {"User-Agent": "firefox"}


def convert_date_format(s: str) -> str:
    """
    'Aug 17, 1993 (30)' => '1993-08-17'
    """
    date_string = s.split(" (")[0]
    date_object = datetime.strptime(date_string, "%b %d, %Y")
    formatted_date = date_object.strftime("%Y-%m-%d")
    return formatted_date


def get_market_value(selector: Selector) -> str:
    a = selector.xpath('//a[@class="data-header__market-value-wrapper"]')
    currency = get_element_text(a.xpath("./span[1]/text()"))
    number = get_element_text(a.xpath("./text()"))
    scale = get_element_text(a.xpath("./span[2]/text()"))
    market_values = f"{currency}{number}{scale}"
    return market_values
