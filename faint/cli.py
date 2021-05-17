import sys

import click
import click_logging
import dateparser
from httpx import Client

from faint.data import User
from faint.gallery import get_
from faint.favs import get_favs
from faint.profile import get_profile
from faint.util import get_cookies, logger

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; faint/0.1; https://furaffinity.net/user/WrenFing/)",
}

@click.command()
@click_logging.simple_verbosity_option(logger)
@click.argument("username")
@click.option("-p/-np", "--profile/--no-profile", default=False, help="Enable/disable profile collection (will be enabled if all other sources are disabled")
@click.option("-g/-ng", "--gallery/--no-gallery", default=False, help="Enable/disable gallery collection")
@click.option("-f/-nf", "--favs/--no-favs", default=False, help="Enable/disable favorites collection")
@click.option("--since", "since_str", default="1970-01-01", help="Only save content since this date/time")
@click.option("--until", "until_str", default="tomorrow", help="Only save content until this date/time")
@click.option("-o", "--outfile", type=click.File("w"), default=sys.stdout, help="Output to this file (default: stdout)")
def scrape_user(username: str, profile=False, gallery=False, favs=False, since_str="1970-01-01", until_str="tomorrow", outfile=sys.stdout):
    with Client(headers=HEADERS, cookies=get_cookies()) as client:
        if not any([profile, gallery, favs]):
            profile = True

        if (since := dateparser.parse(since_str)) is None:
            logger.error(f"{since_str} is not a valid date/time!")
            sys.exit(1)
        if (until := dateparser.parse(until_str)) is None:
            logger.error(f"{until_str} is not a valid date/time!")
            sys.exit(1)
        
        user = User()
        
        if profile:
            user.profile = get_profile(client, username)
        if gallery:
            user.gallery = get_
        if favs:
            user.favs = get_favs(client, username, since=since, until=until)
    
    outfile.write(user.json(indent=4))

if __name__ == "__main__":
    scrape_user()