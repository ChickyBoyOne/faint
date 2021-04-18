import json
import logging
from pathlib import Path

import click_logging

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

logger = logging.getLogger(__name__)
click_logging.basic_config(logger)