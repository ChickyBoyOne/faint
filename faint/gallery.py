from faint.cli import scrape_user
from pprint import pprint
from typing import Union

from httpx import Client

from .data import Folder, FolderGroup, Settings, Submission
from .util import FA_BASE, get_page_soup

def scrape_folder(client: Client, folder: str) -> list[Submission]:
    url = FA_BASE + folder
    first = True
    submission_urls = []

    while True:
        soup = get_page_soup(client, url)
        buttons = soup.find("div", class_="submission-list").div.find_all("form")
        if len(buttons) < 2 and (not first or len(buttons) == 0):
            break
        first = False

        submissions = soup.select("figure u a")
        submission_urls += [FA_BASE + a["href"] for a in submissions]
        url = FA_BASE + buttons[-1]["action"]

    pprint(submission_urls)

    return []

def get_gallery(client: Client, settings: Settings) -> list[Submission]:
    return scrape_folder(client, f"/gallery/{settings.username}/")

def get_scraps(client: Client, settings: Settings) -> list[Submission]:
    return scrape_folder(client, f"/scraps/{settings.username}/")

def get_folders(client: Client, settings: Settings) -> list[Union[Folder, FolderGroup]]:
    return []