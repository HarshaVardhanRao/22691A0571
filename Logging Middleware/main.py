from fastapi import FastAPI, Request
from logger import Log
import asyncio

app = FastAPI()

@app.middleware("http")
async def logging_middleware(request: Request, call_next):

    await Log("backend", "info", "middleware", f"Incoming request: {request.method} {request.url}")
    
    response = await call_next(request)


    await Log("backend", "info", "middleware", f"Response status: {response.status_code}")
    
    return response

@app.get("/test")
async def test():
    await Log("backend", "error", "handler", "Something went wrong in /test")
    return {"message": "Testing log system"}
