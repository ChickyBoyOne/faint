from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl
from pydantic.networks import AnyHttpUrl

class Special(BaseModel):
    id: str
    img: str
    title: str

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

class EmbeddedJournal(BaseModel):
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

class EmbeddedSubmission(BaseModel):
    id: int
    url: HttpUrl
    img: str

class Question(BaseModel):
    question: str
    answer: str

class Contact(BaseModel):
    site: str
    id: str
    # str because sometimes people put ask messages and it screws with the URL validation
    url: Optional[str]

class ProfileInfo(BaseModel):
    submission: Optional[EmbeddedSubmission]
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

    watchers: Optional[WatchInfo]
    watched: Optional[WatchInfo]
    stats: Optional[Stats]
    journal: Optional[EmbeddedJournal]
    badges: list[Badge] = []
    info: ProfileInfo = ProfileInfo()
    shouts: list[Shout] = []

class Rating(Enum):
    GENERAL = "general"
    MATURE = "mature"
    ADULT = "adult"

class Favorite(BaseModel):
    sid: int
    rating: Rating
    username: str
    id: int
    time: str
    url: HttpUrl

class User(BaseModel):
    profile: Optional[UserProfile]
    favs: list[Favorite] = []