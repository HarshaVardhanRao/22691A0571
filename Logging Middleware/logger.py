import httpx

BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJodmlqYXB1cmFtQGdtYWlsLmNvbSIsImV4cCI6MTc1MjIxNDQwMSwiaWF0IjoxNzUyMjEzNTAxLCJpc3MiOiJBZmZvcmQgTWVkaWNhbCBUZWNobm9sb2dpZXMgUHJpdmF0ZSBMaW1pdGVkIiwianRpIjoiNzQ5NzA4OTktMGYzOC00ODIwLWI4OGYtNjZmNGNmZDFmMmQxIiwibG9jYWxlIjoiZW4tSU4iLCJuYW1lIjoidmlqYXB1cmFtIGhhcnNoYXZhcmRoYW4iLCJzdWIiOiJlZWJjMGM0Zi0zNjdhLTRhN2QtOTY0NC0xYjNhNGE4ZWQ1NTAifSwiZW1haWwiOiJodmlqYXB1cmFtQGdtYWlsLmNvbSIsIm5hbWUiOiJ2aWphcHVyYW0gaGFyc2hhdmFyZGhhbiIsInJvbGxObyI6IjIyNjkxYTA1NzEiLCJhY2Nlc3NDb2RlIjoiY2FWdk5IIiwiY2xpZW50SUQiOiJlZWJjMGM0Zi0zNjdhLTRhN2QtOTY0NC0xYjNhNGE4ZWQ1NTAiLCJjbGllbnRTZWNyZXQiOiJiaEpZd3JVQlpnUWJBcXR6In0.BTDsWJ8Au_8i_0pc-LtJWZOGCCm4ALjuMpg9LuNqE2M"

LOG_URL = "http://20.244.56.144/evaluation-service/logs"

async def Log(stack: str, level: str, package: str, message: str):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "stack": stack,
        "level": level,
        "package": package,
        "message": message
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(LOG_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            print(f"Log sent: {data}")
            return data
    except httpx.RequestError as e:
        print(f"Connection error: {e}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.text}")



""" 
Log sent: {'logID': 'fe56ac59-cbec-4044-bb5a-8d8f2372c19f', 'message': 'log created successfully'}
Log sent: {'logID': '5f6ab72e-28f7-4808-899b-e0ecb2163a07', 'message': 'log created successfully'}
Log sent: {'logID': 'db59b88b-43f2-485a-9337-e1952e19391d', 'message': 'log created successfully'}
"""