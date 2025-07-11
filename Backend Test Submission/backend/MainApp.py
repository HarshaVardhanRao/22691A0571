from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from starlette.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Optional
import shortuuid
import re
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from LoggingMiddleware.logger import Log

DATABASE_URL = "sqlite:///./shortener.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def trim(msg: str, max_len: int = 48):
    return msg if len(msg) <= max_len else msg[:45] + "..."

class LinkEntry(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String(2048), nullable=False)
    short_code = Column(String(20), unique=True, nullable=False)
    expires_on = Column(DateTime)
    created_on = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def make_random_code():
    return shortuuid.ShortUUID().random(length=6)

def is_code_valid(code: str) -> bool:
    return re.fullmatch(r'[a-zA-Z0-9]{4,10}', code) is not None

class ShortenRequest(BaseModel):
    encoded_url: str = Field(..., alias="url")
    validity_minutes: int
    custom_shortcode: Optional[str] = None

    class Config:
        allow_population_by_field_name = True

class ShortenResponse(BaseModel):
    shortcode: str
    message: str

class UrlStatsResponse(BaseModel):
    original_url: str
    short_code: str
    created_on: datetime
    expires_on: datetime

class SimpleLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        await Log("backend", "info", "middleware", trim(f"Request: {request.method} {request.url.path}"))
        response = await call_next(request)
        duration = time.time() - start
        await Log("backend", "info", "middleware", trim(f"Response: {response.status_code} in {duration:.2f}s"))
        return response

app = FastAPI()
app.add_middleware(SimpleLoggerMiddleware)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/shorturls", response_model=ShortenResponse)
async def make_short_url(user_data: ShortenRequest, db: Session = Depends(get_db)):
    short_code = user_data.custom_shortcode or make_random_code()

    if user_data.custom_shortcode:
        if not is_code_valid(short_code):
            await Log("backend", "error", "handler", trim("Invalid shortcode format."))
            raise HTTPException(status_code=400, detail="Shortcode format is invalid.")
        if db.query(LinkEntry).filter(LinkEntry.short_code == short_code).first():
            await Log("backend", "error", "handler", trim("Shortcode already exists."))
            raise HTTPException(status_code=400, detail="Shortcode already exists.")

    while not user_data.custom_shortcode and db.query(LinkEntry).filter(LinkEntry.short_code == short_code).first():
        short_code = make_random_code()

    expires_at = datetime.now() + timedelta(minutes=user_data.validity_minutes)

    formatted_url = f"http://{user_data.encoded_url.replace('-', '/')}"

    try:
        new_link = LinkEntry(
            original_url=formatted_url,
            short_code=short_code,
            expires_on=expires_at
        )
        db.add(new_link)
        db.commit()
        db.refresh(new_link)
    except Exception as error:
        await Log("backend", "fatal", "db", trim(f"Database error: {str(error)}"))
        raise HTTPException(status_code=500, detail="Database write error")

    await Log("backend", "info", "handler", trim(f"Created short link: {short_code}"))
    return ShortenResponse(shortcode=short_code, message="Short URL created successfully")

@app.get("/{shortcode}")
async def go_to_original(shortcode: str, db: Session = Depends(get_db)):
    link = db.query(LinkEntry).filter(LinkEntry.short_code == shortcode).first()

    if not link:
        await Log("backend", "error", "handler", trim(f"Shortcode '{shortcode}' not found."))
        raise HTTPException(status_code=404, detail="No such shortcode found.")

    if link.expires_on < datetime.utcnow():
        await Log("backend", "error", "handler", trim(f"Shortcode '{shortcode}' expired."))
        raise HTTPException(status_code=410, detail="This short link has expired.")

    await Log("backend", "info", "handler", trim(f"Redirecting to {link.original_url}"))
    return RedirectResponse(url=link.original_url)


@app.get("/shorturls/{shortcode}", response_model=UrlStatsResponse)
async def get_short_url_stats(shortcode: str, db: Session = Depends(get_db)):
    link = db.query(LinkEntry).filter(LinkEntry.short_code == shortcode).first()

    if not link:
        await Log("backend", "error", "handler", trim(f"Stats for '{shortcode}' not found."))
        raise HTTPException(status_code=404, detail="Shortcode not found.")

    await Log("backend", "info", "handler", trim(f"Stats retrieved for {shortcode}"))
    return UrlStatsResponse(
        original_url=link.original_url,
        short_code=link.short_code,
        created_on=link.created_on,
        expires_on=link.expires_on
    )