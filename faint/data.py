from typing import Optional

from pydantic import BaseModel

class EmbeddedUser(BaseModel):
    username: str
    special: Optional[dict[str, str]]
    avatar: str