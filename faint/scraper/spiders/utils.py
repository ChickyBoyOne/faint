from datetime import datetime
from typing import Union
from urllib.parse import ParseResult, urlparse, urlunparse

from bs4 import BeautifulSoup, Tag
from dateparser import parse as parse_date
from scrapy.selector.unified import Selector, SelectorList

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

def not_class(tag: Union[Selector, SelectorList, Tag], bad: str) -> str:
    if isinstance(tag, (Selector, SelectorList)):
        classes = tag.attrib.get("class", "").split(" ")
    else:
        classes = tag["class"]
    
    for c in classes:
        if c not in ["", bad]:
            return c