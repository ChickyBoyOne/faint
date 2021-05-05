import itertools

from bs4 import BeautifulSoup
from bs4.element import Tag
import httpx

from faint.bbcode import to_bbcode
from faint.util import FA_BASE, format_date, normalize_url

def get_user_list(body: Tag) -> list[str]:
    if not (table := body.find("table")):
        return []
    
    return [td.get_text() for td in table.find_all("td")]

def get_profile(client: httpx.Client, username: str) -> dict[str, str]:
    r = client.get(f"{FA_BASE}/user/{username}/")
    soup = BeautifulSoup(r.text, "lxml")

    user = {}
    user_block = soup.find("div", class_="username")
    name_block = user_block.select_one("h2 span")
    user["username"] = name_block.get_text().strip()
    if user["username"][0] in "~!∞":
        user["username"] = user["username"][1:]
    user["status"] = name_block["title"].split(": ")[-1].lower()
    if (img := user_block.find("img")):
        user["special"] = [c for c in img["class"] if c != "inline"][0]
    else:
        user["special"] = ""
    title_parts = user_block.find("span", class_="font-small").get_text().strip().split(" | ")
    user["title"] = None if len(title_parts) == 1 else " | ".join(title_parts[:-1])
    user["joined"] = format_date(title_parts[-1].split(": ")[-1])
    user["avatar"] = normalize_url(soup.find("img", class_="user-nav-avatar")["src"])

    profile_block = soup.find("div", class_="userpage-profile")
    user["profile"] = to_bbcode(profile_block)

    layout = soup.find("div", class_="userpage-layout")

    for section in layout.find_all("section"):
        if not (header := section.select_one("div.section-header h2")):
            shouts = []

            for div in section.find_all("div", class_="comment_container"):
                shouts.append({
                    "name": div.find("div", class_="comment_username").get_text(),
                    "avatar": normalize_url(div.find("img", class_="comment_useravatar")["src"]),
                    "time": format_date(div.find("span", class_="popup_date").get_text()),
                    "text": to_bbcode(div.find("div", class_="comment_text")),
                })
            
            user["shouts"] = shouts
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
            nums = [int(line.split(": ")[-1]) for line in lines]
            stats["views"], stats["submissions"], stats["favs"], \
                stats["comments_earned"], stats["comments_made"], stats["journals"] = nums
    
    return user