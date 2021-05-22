import sys

from bs4 import BeautifulSoup
from httpx import Client

from .data import Favorite, Settings
from .util import FA_BASE, cleave, format_date, normalize_url, not_class

def get_favs(client: Client, settings: Settings) -> list[Favorite]:
    base = f"{FA_BASE}/favorites/{settings.username}/"
    url = base
    favs = []
    
    while True:
        favs_page = client.get(url)
        soup = BeautifulSoup(favs_page.text, "lxml")
        page_favs = soup.select("figure[data-fav-id]")

        try:
            last_fav_time = format_date(soup.select_one("div.midsection span")["title"])
        except TypeError:
            if soup.find("div", id="no-images"):
                break
            else:
                print(f"User {settings.username} not found!")
                sys.exit(1)

        url = base + page_favs[0]["data-fav-id"] + "/next/"
        
        if settings.since > last_fav_time:
            break
        elif settings.until < last_fav_time:
            continue
        
        first = page_favs[0]
        favs.append(Favorite(
            sid=int(first["id"].replace("sid-", "")),
            rating=cleave(not_class(first, "t-image")),
            username=first["data-user"].replace("u-", ""),
            id=first["data-fav-id"],
            time=last_fav_time.strftime("%Y/%m/%d %H:%M"),
            url=normalize_url(first.find("a")["href"]),
        ))
        
        if len(page_favs) == 1:
            break
    
    return favs