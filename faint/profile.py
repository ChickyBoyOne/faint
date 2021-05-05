import itertools

from bs4 import BeautifulSoup
from bs4.element import Tag
import httpx

from faint.bbcode import to_bbcode
from faint.util import FA_BASE, format_date, get_subtitle_num, normalize_url, not_class

def get_user_list(body: Tag) -> list[str]:
    if not (table := body.table):
        return []
    
    return [td.get_text() for td in table.find_all("td")]

def get_special(tag: Tag) -> dict[str, str]:
    if not (img := tag.img):
        return
    
    return {
        "id": not_class(img, "inline").replace("-icon", "").replace("-logo", ""),
        "image": normalize_url(img["src"]),
        "title": img["title"],
    }

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
    if (special := get_special(name_block)):
        user["special"] = special
    title_parts = user_block.find("span", class_="font-small").get_text().strip().split(" | ")
    user["title"] = None if len(title_parts) == 1 else " | ".join(title_parts[:-1])
    user["joined"] = format_date(title_parts[-1].split(": ")[-1])
    user["avatar"] = normalize_url(soup.find("img", class_="user-nav-avatar")["src"])

    profile_block = soup.find("div", class_="userpage-profile")
    user["profile"] = to_bbcode(profile_block)

    layout = soup.find("div", class_="userpage-layout")

    for section in layout.find_all("section"):
        if not (header := section.select_one("div.section-header")):
            user["shouts"] = shouts = []

            for container in section.find_all("div", class_="comment_container"):
                username = container.find("div", class_="comment_username")
                shout = {
                    "username": username.get_text(),
                    "avatar": normalize_url(container.find("img", class_="comment_useravatar")["src"]),
                    "time": format_date(container.find("span", class_="popup_date").get_text()),
                    "text": to_bbcode(container.find("div", class_="comment_text")),
                }
                if (special := get_special(username)):
                    shout["special"] = special
                shouts.append(shout)
            
            continue

        label = header.h2.get_text()
        body = section.find("div", class_="section-body")

        if label == "Recent Watchers":
            user["watchers"] = {
                "num": get_subtitle_num(header),
                "list": get_user_list(body),
            }
        elif label == "Recently Watched":
            user["watched"] = {
                "num": get_subtitle_num(header),
                "list": get_user_list(body),
            }
        elif label == "Stats":
            user["stats"] = stats = {}
            lines = itertools.chain.from_iterable(cell.get_text().strip().splitlines() for cell in body.find_all("div", class_="cell"))
            nums = [int(line.split(": ")[-1]) for line in lines]
            stats["views"], stats["submissions"], stats["favs"], \
                stats["comments_earned"], stats["comments_made"], stats["journals"] = nums
        elif label == "Recent Journal":
            link = header.a
            href = link["href"]
            user["recent_journal"] = {
                "id": int(href.split("/")[-1]),
                "url": normalize_url(href),
                "comments": get_subtitle_num(header),
                "title": body.h2.get_text(),
                "time": format_date(body.find("span", class_="popup_date")["title"]),
                "text": to_bbcode(body.div),
            }
        elif label == "Badges":
            user["badges"] = badges = []
            for badge in body.find_all("div", class_="badge"):
                img = badge.img
                badges.append({
                    "id": int(badge["id"].split("-")[-1]),
                    "name": not_class(badge, "badge"),
                    "img": normalize_url(img["src"]),
                    "title": img["title"],
                })
    
    return user