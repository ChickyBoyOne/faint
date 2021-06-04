from datetime import datetime
from urllib.parse import ParseResult, urlparse, urlunparse

from bs4 import BeautifulSoup, Tag
from dateparser import parse as parse_date
from scrapy.selector.unified import SelectorList

from ..items import Parameters


FA_BASE = "https://www.furaffinity.net"

def cleave(s: str) -> str:
    return s.split("-")[-1]

def format_date(date: str, parameters: Parameters) -> datetime:
    return parse_date(date, settings={
        "TIMEZONE": parameters.timezone,
        "TO_TIMEZONE": parameters.to_timezone,
        "RETURN_AS_TIMEZONE_AWARE": True,
    })

def get_soup(html: str) -> Tag:
    return BeautifulSoup(html, "lxml").body.contents[0]

def get_direct_text(tag: SelectorList) -> str:
    return "".join(tag.css("::text").getall())

def get_text(tag: SelectorList) -> str:
    return "".join(tag.css("*::text").getall())

def get_subtitle_num(header: SelectorList) -> int:
    for word in get_text(header).split("(")[-1].split(")")[0].split():
        try:
            return int(word)
        except ValueError:
            continue

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse(ParseResult(
        scheme="https",
        netloc=parsed.netloc if parsed.netloc else "www.furaffinity.net",
        path=parsed.path,
        params=parsed.params,
        query=parsed.query,
        fragment=parsed.fragment,
    ))

def not_class(tag: SelectorList, bad: str) -> str:
    for c in tag.attrib.get("class", "").split(" "):
        if c not in ["", bad]:
            return c