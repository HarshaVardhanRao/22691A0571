from pydantic import BaseModel, HttpUrl
from typing import Optional

class ShortenRequest(BaseModel):
    url: HttpUrl
    validity_minutes: int
    custom_shortcode: Optional[str] = None

class ShortenResponse(BaseModel):
    shortcode: str
    message: str
