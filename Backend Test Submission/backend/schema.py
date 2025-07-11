from pydantic import BaseModel, HttpUrl
from typing import Optional

class ShortenRequest(BaseModel):
    url: HttpUrl
    validity_minutes: Optional[int] = 30
    custom_shortcode: Optional[str] = None

class ShortenResponse(BaseModel):
    shortcode: str
    message: str