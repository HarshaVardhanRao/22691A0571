from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from schema import ShortenRequest, ShortenResponse
from starlette.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from datetime import datetime, timedelta
import shortuuid
import re
import time

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


from LoggingMiddleware.logger import Log

db_url = "sqlite:///./shortener.db"
engine = create_engine(db_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class LinkEntry(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow)
    expires_on = Column(DateTime)

Base.metadata.create_all(bind=engine)

def make_random_code():
    return shortuuid.ShortUUID().random(length=6)

def is_code_valid(code: str) -> bool:
    return re.fullmatch(r'[a-zA-Z0-9]{4,10}', code) is not None

class SimpleLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        await Log("backend", "info", "middleware", f"Request came in: {request.method} {request.url.path}")
        response = await call_next(request)
        time_taken = time.time() - start
        await Log("backend", "info", "middleware", f"Response: {response.status_code} in {time_taken:.2f}s")
        return response

app = FastAPI()
app.add_middleware(SimpleLoggerMiddleware)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/shorten", response_model=ShortenResponse)
async def make_short_url(user_data: ShortenRequest, db: Session = Depends(get_db)):
    short_code = user_data.custom_shortcode or make_random_code()

    if user_data.custom_shortcode:
        if not is_code_valid(short_code):
            await Log("backend", "error", "handler", "received string, expected bool")
            raise HTTPException(status_code=400, detail="Shortcode format is invalid.")
        if db.query(LinkEntry).filter(LinkEntry.short_code == short_code).first():
            await Log("backend", "error", "handler", "Shortcode already exists.")
            raise HTTPException(status_code=400, detail="Shortcode already exists.")


    while not user_data.custom_shortcode and db.query(LinkEntry).filter(LinkEntry.short_code == short_code).first():
        short_code = make_random_code()

    expiry_time = datetime.utcnow() + timedelta(minutes=user_data.validity_minutes)

    try:
        new_link = LinkEntry(
            original_url=user_data.url,
            short_code=short_code,
            expires_on=expiry_time
        )
        db.add(new_link)
        db.commit()
        db.refresh(new_link)
    except Exception as error:
        await Log("backend", "fatal", "db", f"Critical database connection failure: {str(error)}")
        raise HTTPException(status_code=500, detail="Database write error")

    await Log("backend", "info", "handler", f"Created short link: {short_code}")
    return ShortenResponse(shortcode=short_code, message="Short URL created successfully")
@app.get("/{shortcode}")
async def go_to_original(shortcode: str, db: Session = Depends(get_db)):
    link = db.query(LinkEntry).filter(LinkEntry.short_code == shortcode).first()

    if not link:
        await Log("backend", "error", "handler", f"Shortcode '{shortcode}' not found.")
        raise HTTPException(status_code=404, detail="No such shortcode found.")

    if link.expires_on < datetime.utcnow():
        await Log("backend", "error", "handler", f"Shortcode '{shortcode}' expired.")
        raise HTTPException(status_code=410, detail="This short link has expired.")

    await Log("backend", "info", "handler", f"Redirecting to {link.original_url}")
    return RedirectResponse(url=link.original_url)
