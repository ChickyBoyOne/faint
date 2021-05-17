from httpx import Client

from .data import Gallery

def get_gallery(client: Client, username: str) -> Gallery:
    gallery = Gallery()

    return gallery