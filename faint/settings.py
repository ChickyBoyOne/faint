from datetime import timedelta, timezone
import sys

from bs4 import BeautifulSoup
import dateparser
from httpx import Client
from pytz.exceptions import UnknownTimeZoneError

from .data import Settings
from .util import FA_BASE, logger

def get_settings(client: Client, username: str, after_str: str, before_str: str, to_timezone: str) -> Settings:
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

    try:
        dateparser.parse("1970-01-01", date_formats=["%Y-%m-%d"], locales=["en-US"],
            settings={"TO_TIMEZONE": to_timezone})
    except UnknownTimeZoneError:
        errors.append(f"{to_timezone} is not a valid timezone! Please choose one from this list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")

    if not (after := dateparser.parse(after_str, settings={"TIMEZONE": tz, "RETURN_AS_TIMEZONE_AWARE": True})):
        errors.append(f"{after_str} is not a valid date/time!")
    if not (before := dateparser.parse(before_str, settings={"TIMEZONE": tz, "RETURN_AS_TIMEZONE_AWARE": True})):
        errors.append(f"{before_str} is not a valid date/time!")

    if errors:
        for error in errors:
            logger.error(error)
        sys.exit(1)
    else:
        return Settings(
            username=username,
            timezone=tz,
            to_timezone=to_timezone,
            after=after,
            before=before,
        )