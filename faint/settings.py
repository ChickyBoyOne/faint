from datetime import timedelta, timezone
import sys

from bs4 import BeautifulSoup
import dateparser
from httpx import Client

from .data import Settings
from .util import FA_BASE, logger

def get_settings(client: Client, username: str, since_str: str, until_str: str) -> Settings:
    errors = []

    settings = client.get(f"{FA_BASE}/controls/settings/")
    soup = BeautifulSoup(settings.text, "lxml")
    tz = soup.find("select", attrs={"name": "timezone"}).find("option", selected="selected")["value"]
    negative, hours, minutes = tz[0] == "-", int(tz[1:3]), int(tz[3:5])
    tz = timedelta(hours=hours, minutes=minutes)
    if negative:
        tz = -tz
    if soup.find("input", attrs={"name": "timezone_dst"}).get("checked", ""):
        if tz.seconds // 60 // 60 == 23:
            tz = -timedelta(hours=11, minutes=60 - (tz.seconds // 60 % 60))
        else:
            tz += timedelta(hours=1)
    tz = timezone(tz).tzname(None)

    if not (since := dateparser.parse(since_str)):
        errors.append(f"{since_str} is not a valid date/time!")
    if not (until := dateparser.parse(until_str)):
        errors.append(f"{until_str} is not a valid date/time!")

    if errors:
        for error in errors:
            logger.error(error)
        sys.exit(1)
    else:
        return Settings(
            username=username,
            timezone=tz,
            since=since,
            until=until,
        )