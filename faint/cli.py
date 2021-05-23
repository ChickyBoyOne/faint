import sys

import click
import click_logging
from httpx import Client

from faint.data import User
from faint.gallery import get_gallery
from faint.favs import get_favs
from faint.profile import get_profile
from faint.settings import get_settings
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
@click.option("--after", "after_str", default="1970-01-01", help="Only save content after this date/time")
@click.option("--before", "before_str", default="in 2 days", help="Only save content before this date/time")
@click.option("--timezone", default="UTC", help="Convert times to this timezone (default: UTC)")
@click.option("-o", "--outfile", type=click.File("w"), default=sys.stdout, help="Output to this file (default: stdout)")
def scrape_user(username: str, profile, gallery, favs, after_str, before_str, timezone, outfile):
    user = User()
    if not any([profile, gallery, favs]):
        profile = True

    with Client(headers=HEADERS, cookies=get_cookies()) as client:
        settings = get_settings(client, username, after_str, before_str, timezone)
        if profile:
            user.profile = get_profile(client, settings)
        if gallery:
            user.gallery = get_gallery(client, settings)
        if favs:
            user.favs = get_favs(client, settings)
    
    outfile.write(user.json(indent=4))

if __name__ == "__main__":
    scrape_user()