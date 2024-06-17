from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class Author(BaseModel):
    username: str

class Attachment(BaseModel):
    url: HttpUrl
    filename: str

class Message(BaseModel):
    author: Author
    content: Optional[str]
    attachments: List[Attachment]

class Channel(BaseModel):
    id: str
