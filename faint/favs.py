import json
from pathlib import Path
import sys

from bs4 import BeautifulSoup
import click
import dateparser
import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; faint/0.1; https://furaffinity.net/user/WrenFing/)",
}
COOKIES = ["__cfduid", "a", "b"]
FA_BASE = "https://www.furaffinity.net"

def get_cookies() -> "dict[str, str]":
    cookies_path = Path(__file__).parent.parent / "cookies.json"

    with open(cookies_path) as cookies_file:
        try:
            cookies = json.load(cookies_file)
        except json.JSONDecodeError:
            cookies = {}

    for cookie in COOKIES:
        if cookie not in cookies or cookies[cookie] == "":
            cookies[cookie] = input(f"Please enter cookie {cookie}: ")
    
    # Remove any extraneous values
    with open(cookies_path, "w") as cookies_file:
        json.dump({cookie: cookies[cookie] for cookie in COOKIES}, cookies_file, indent=4)
    
    return cookies

@click.command()
@click.argument("username")
@click.option("--since", default="1970-01-01", help="Only save favorites since this date/time")
@click.option("--until", default="tomorrow", help="Only save favorites until this date/time")
@click.option("-o", "--outfile", type=click.File("w"))
def favs(username, since, until, outfile=None):
    cookies = get_cookies()
    base = FA_BASE + f"/favorites/{username}/"
    url = base
    all_favs = []
    since = dateparser.parse(since)
    until = dateparser.parse(until)
    
    with httpx.Client(headers=HEADERS, cookies=cookies) as c:
        while True:
            favs_page = c.get(url)
            soup = BeautifulSoup(favs_page.text, "lxml")
            favs = soup.select("figure[data-fav-id]")

            try:
                last_fav_time = dateparser.parse(soup.select_one("div.midsection span")["title"], settings={"TIMEZONE": "US/Eastern", "TO_TIMEZONE": "US/Central"})
            except TypeError:
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

        if outfile:
            json.dump(all_favs, outfile, indent=4)