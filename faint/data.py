from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, HttpUrl

class Settings(BaseModel):
    username: str
    timezone: str
    since: datetime
    until: datetime

class Special(BaseModel):
    id: str
    img: HttpUrl
    title: str

class Rating(Enum):
    GENERAL = "general"
    MATURE = "mature"
    ADULT = "adult"

class ProfileSubmission(BaseModel):
    id: int
    url: HttpUrl
    img: HttpUrl
    title: Optional[str]
    rating: Rating

class GallerySubmission(BaseModel):
    id: int
    url: HttpUrl
    img: HttpUrl
    width: float
    height: float
    title: str
    username: str
    time: str
    rating: Rating

class Supporter(BaseModel):
    username: str
    url: HttpUrl
    avatar: HttpUrl

class ShinyDonation(BaseModel):
    supporter: Supporter
    message: Optional[str]

class Shinies(BaseModel):
    # Singular descriptor is not necessarily present
    singular: Optional[str]
    plural: str
    top: list[Supporter] = []
    recent: list[ShinyDonation] = []
    price: int = 5
    messages: bool = True

class WatchInfo(BaseModel):
    num: int
    recent: list[str]

class Stats(BaseModel):
    views: int
    submissions: int
    favs: int
    comments_earned: int
    comments_made: int
    journals: int

class ProfileJournal(BaseModel):
    id: int
    url: HttpUrl
    comments: int
    title: str
    time: str
    text: str

class Badge(BaseModel):
    id: int
    name: str
    img: HttpUrl
    title: str

class Question(BaseModel):
    question: str
    answer: str

class Contact(BaseModel):
    site: str
    id: str
    # str because sometimes people put ask messages and it screws with the URL validation
    url: Optional[str]

class ProfileInfo(BaseModel):
    submission: Optional[ProfileSubmission]
    trades: bool = False
    commissions: bool = False
    questions: list[Question] = []
    contacts: list[Contact] = []

class Shout(BaseModel):
    username: str
    special: Optional[Special] = ...
    avatar: str
    time: str
    text: str

class UserProfile(BaseModel):
    username: str
    status: str
    special: Optional[Special] = ...
    title: Optional[str] = ...
    joined: str
    avatar: str
    profile: str

    submission: Optional[ProfileSubmission]
    gallery: list[GallerySubmission] = []
    favorites: list[GallerySubmission] = []
    shinies: Optional[Shinies]
    watchers: Optional[WatchInfo]
    watched: Optional[WatchInfo]
    stats: Optional[Stats]
    journal: Optional[ProfileJournal]
    badges: list[Badge] = []
    info: ProfileInfo = ProfileInfo()
    shouts: list[Shout] = []

class Submission(BaseModel):
    pass

class Folder(BaseModel):
    name: str
    description: Optional[str]
    submissions: list[Submission] = []

class FolderGroup(BaseModel):
    name: str
    folders: list[Folder] = []

class Gallery(BaseModel):
    main: list[Submission] = []
    scraps: list[Submission] = []
    folder_groups: list[Union[Folder, FolderGroup]] = []

class Favorite(BaseModel):
    sid: int
    rating: Rating
    username: str
    id: int
    time: str
    url: HttpUrl

class User(BaseModel):
    profile: Optional[UserProfile]
    gallery: Optional[Gallery]
    favs: list[Favorite] = []