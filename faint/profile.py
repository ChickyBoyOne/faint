import itertools

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
import httpx

from faint.util import FA_BASE, logger

def get_user_list(body: Tag) -> list[str]:
    if not (table := body.find("table")):
        return []
    
    return [td.get_text() for td in table.find_all("td")]

def get_profile(client: httpx.Client, username: str) -> dict[str, str]:
    r = client.get(f"{FA_BASE}/user/{username}/")
    soup = BeautifulSoup(r.text, "lxml")

    user = {}

    # TODO: Implement BBCode
    # https://www.furaffinity.net/journal/833448/
    profile_block = soup.find("div", class_="userpage-profile")
    user["profile"] = str(profile_block)

    layout = soup.find("div", class_="userpage-layout")

    for section in layout.find_all("section"):
        if not (header := section.select_one("div.section-header h2")):
            continue
        label = header.get_text()
        body = section.find("div", class_="section-body")

        if label == "Recent Watchers":
            user["watchers"] = get_user_list(body)
        elif label == "Recently Watched":
            user["watched"] = get_user_list(body)
        elif label == "Stats":
            user["stats"] = stats = {}
            lines = itertools.chain.from_iterable(cell.get_text().strip().splitlines() for cell in body.find_all("div", class_="cell"))
            nums = [int(line.split(": ")[1]) for line in lines]
            stats["views"], stats["submissions"], stats["favs"], \
                stats["comments_earned"], stats["comments_made"], stats["journals"] = nums
    
    return user