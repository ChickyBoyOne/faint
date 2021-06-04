from io import TextIOWrapper
import sys

import click
import click_logging
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from faint.scraper.spiders.user import UserSpider
from faint.utils import get_cookies, logger


@click.command()
@click_logging.simple_verbosity_option(logger)
@click.argument("username")
@click.option("-p/-np", "--profile/--no-profile", default=False, help="Enable/disable profile collection (will be enabled if all other sources are disabled")
@click.option("-g/-ng", "--gallery/--no-gallery", default=False, help="Enable/disable gallery collection")
@click.option("-s/-ns", "--scraps/--no-scraps", default=False, help="Enable/disable scraps collection")
@click.option("-d/-nd", "--folders/--no-folders", default=False, help="Enable/disable folders collection")
@click.option("-f/-nf", "--favs/--no-favs", default=False, help="Enable/disable favorites collection")
@click.option("--after", "after_str", default="1970-01-01", help="Only save content after this date/time")
@click.option("--before", "before_str", default="in 2 days", help="Only save content before this date/time")
@click.option("--timezone", default="UTC", help="Convert times to this timezone (default: UTC)")
@click.option("-o", "--outfile", type=click.File("w"), default=sys.stdout, help="Output to this file (default: stdout)")
def scrape_user(username: str, profile: bool, gallery: bool, scraps: bool, folders: bool, favs: bool,
        after_str: str, before_str: str, timezone: str, outfile: TextIOWrapper):
    # Point Scrapy to settings: https://stackoverflow.com/a/29874137
    settings = Settings()
    settings.setmodule("scraper.settings")
    process = CrawlerProcess(settings)
    process.crawl(
        UserSpider,
        cookies=get_cookies(),
        username=username,
        to_timezone=timezone,
        after=after_str,
        before=before_str,
        profile=profile,
        gallery=gallery,
        scraps=scraps,
        folders=folders,
        favs=favs,
    )
    process.start()

if __name__ == "__main__":
    scrape_user()