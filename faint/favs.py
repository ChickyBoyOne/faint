from datetime import datetime
import sys

from bs4 import BeautifulSoup
import dateparser
import httpx

from faint.util import FA_BASE

def get_favs(client: httpx.Client, username: str, since: datetime, until: datetime) -> list[dict]:
    base = f"{FA_BASE}/favorites/{username}/"
    url = base
    all_favs = []
    
    while True:
        favs_page = client.get(url)
        soup = BeautifulSoup(favs_page.text, "lxml")
        favs = soup.select("figure[data-fav-id]")

        try:
            last_fav_time = dateparser.parse(soup.select_one("div.midsection span")["title"], settings={"TIMEZONE": "US/Eastern", "TO_TIMEZONE": "US/Central"})
        except TypeError:
            if soup.find("div", id="no-images"):
                break
            else:
                print(f"User {username} not found!")
                sys.exit(1)

        url = base + favs[0]["data-fav-id"] + "/next/"
        
        if since > last_fav_time:
            break
        elif until < last_fav_time:
            continue
        
        first = favs[0]
        fav = {
            "sid": first["id"].replace("sid-", ""),
            "adult": "r-adult" in first["class"],
            "user": first["data-user"].replace("u-", ""),
            "fav_id": first["data-fav-id"],
            "fav_time": last_fav_time.strftime("%Y/%m/%d %H:%M"),
            "url": FA_BASE + first.find("a")["href"],
        }
        all_favs.append(fav)
        print(fav["fav_time"], fav["url"], f"({fav['user']})")
        
        if len(favs) == 1:
            break
        
    num_fav = len(all_favs)
    
    if num_fav:
        print()

    print(num_fav, f"favorite{'s' if num_fav != 1 else ''} found!")
    
    return all_favs