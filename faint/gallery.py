from typing import Union

from httpx import Client

from .data import Folder, FolderGroup, Settings, Submission
from .util import FA_BASE

def get_gallery(client: Client, settings: Settings) -> list[Submission]:
    gallery_base = f"{FA_BASE}/gallery/{settings.username}/"
    page = client.get(gallery_base)
    return []

def get_scraps(client: Client, settings: Settings) -> list[Submission]:
    return []

def get_folders(client: Client, settings: Settings) -> list[Union[Folder, FolderGroup]]:
    return []