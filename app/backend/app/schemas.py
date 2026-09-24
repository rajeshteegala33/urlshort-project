from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class SignupRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ShortenRequest(BaseModel):
    original_url: HttpUrl
    custom_short: Optional[str] = None

class ShortenResponse(BaseModel):
    short: str
    original: HttpUrl

class ClickItem(BaseModel):
    timestamp: datetime
    referrer: Optional[str]
    user_agent: Optional[str]
    ip: Optional[str]

class AnalyticsResponse(BaseModel):
    short: str
    total_clicks: int
    clicks: List[ClickItem]
