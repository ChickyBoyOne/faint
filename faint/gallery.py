from datetime import datetime
from httpx import Client

from .data import Gallery

def get_gallery(client: Client, username: str, since: datetime, until: datetime) -> Gallery:
    gallery = Gallery()

    return gallery