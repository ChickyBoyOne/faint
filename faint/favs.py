from datetime import datetime
import sys

from bs4 import BeautifulSoup
import dateparser
import httpx

from .data import Favorite, Rating
from .util import FA_BASE, normalize_url, not_class

def get_favs(client: httpx.Client, username: str, since: datetime, until: datetime) -> list[Favorite]:
    base = f"{FA_BASE}/favorites/{username}/"
    url = base
    favs = []
    
    while True:
        favs_page = client.get(url)
        soup = BeautifulSoup(favs_page.text, "lxml")
        page_favs = soup.select("figure[data-fav-id]")

        try:
            last_fav_time = dateparser.parse(soup.select_one("div.midsection span")["title"], settings={"TIMEZONE": "US/Eastern", "TO_TIMEZONE": "US/Central"})
        except TypeError:
            if soup.find("div", id="no-images"):
                break
            else:
                print(f"User {username} not found!")
                sys.exit(1)

        url = base + page_favs[0]["data-fav-id"] + "/next/"
        
        if since > last_fav_time:
            break
        elif until < last_fav_time:
            continue
        
        first = page_favs[0]
        favs.append(Favorite(
            sid=int(first["id"].replace("sid-", "")),
            rating=not_class(first, "t-image"),
            username=first["data-user"].replace("u-", ""),
            id=first["data-fav-id"],
            time=last_fav_time.strftime("%Y/%m/%d %H:%M"),
            url=normalize_url(first.find("a")["href"]),
        ))
        
        if len(page_favs) == 1:
            break
    
    return favs