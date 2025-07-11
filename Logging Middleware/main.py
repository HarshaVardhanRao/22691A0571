from fastapi import FastAPI, Request
from logger import Logme
import asyncio

app = FastAPI()

@app.middleware("http")
async def logging_middleware(request: Request, call_next):

    await Logme("backend", "info", "middleware", f"Incoming request: {request.method} {request.url}")
    
    response = await call_next(request)


    await Logme("backend", "info", "middleware", f"Response status: {response.status_code}")
    
    return response

@app.get("/test")
async def test():
    await Logme("backend", "error", "handler", "Something went wrong in /test")
    return {"message": "Testing log system"}
