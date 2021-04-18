from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
import httpx

from faint.util import FA_BASE, logger

def get_user_list(body: Tag) -> list[str]:
    if not (table := body.find("table")):
        return []
    
    return list(map(lambda td: td.get_text(), table.find_all("td")))

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
    
    return user