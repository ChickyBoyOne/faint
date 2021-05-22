from httpx import Client

from .data import Gallery, Settings

def get_gallery(client: Client, settings: Settings) -> Gallery:
    gallery = Gallery()

    return gallery