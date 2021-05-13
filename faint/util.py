import functools
import json
import logging
from pathlib import Path
from urllib.parse import ParseResult, urlparse, urlunparse

from bs4 import Tag
from bs4.element import NavigableString
import click_logging
import dateparser

logger = logging.getLogger(__name__)
click_logging.basic_config(logger)

COOKIES = ["__cfduid", "a", "b"]
FA_BASE = "https://www.furaffinity.net"

def get_cookies() -> "dict[str, str]":
    cookies_path = Path(__file__).parent.parent / "cookies.json"

    with open(cookies_path) as cookies_file:
        try:
            cookies = json.load(cookies_file)
        except json.JSONDecodeError:
            cookies = {}

    for cookie in COOKIES:
        if cookie not in cookies or cookies[cookie] == "":
            cookies[cookie] = input(f"Please enter cookie {cookie}: ")
    
    # Remove any extraneous values
    with open(cookies_path, "w") as cookies_file:
        json.dump({cookie: cookies[cookie] for cookie in COOKIES}, cookies_file, indent=4)
    
    return cookies

# TODO: Parse settings page for timezone
parse_date = functools.partial(dateparser.parse, settings={"TIMEZONE": "US/Eastern"})

def format_date(date: str) -> str:
    return parse_date(date).strftime("%Y/%m/%d %H:%M")

def get_direct_text(tag: Tag) -> str:
    return [c for c in reversed(tag.contents) if type(c) is NavigableString][0].strip()

def get_subtitle_num(header: Tag) -> int:
    for word in header.a.get_text().split("(")[-1].split(")")[0].split():
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

def not_class(tag: Tag, bad: str) -> str:
    for c in tag.get_attribute_list("class"):
        if c != bad:
            return c