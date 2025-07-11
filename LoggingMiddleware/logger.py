import httpx

BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJodmlqYXB1cmFtQGdtYWlsLmNvbSIsImV4cCI6MTc1MjIxODc2NCwiaWF0IjoxNzUyMjE3ODY0LCJpc3MiOiJBZmZvcmQgTWVkaWNhbCBUZWNobm9sb2dpZXMgUHJpdmF0ZSBMaW1pdGVkIiwianRpIjoiYjIxODdiOGMtMjA2MS00MTkwLTljOWItZTFkZjllNWZmOGZjIiwibG9jYWxlIjoiZW4tSU4iLCJuYW1lIjoidmlqYXB1cmFtIGhhcnNoYXZhcmRoYW4iLCJzdWIiOiJlZWJjMGM0Zi0zNjdhLTRhN2QtOTY0NC0xYjNhNGE4ZWQ1NTAifSwiZW1haWwiOiJodmlqYXB1cmFtQGdtYWlsLmNvbSIsIm5hbWUiOiJ2aWphcHVyYW0gaGFyc2hhdmFyZGhhbiIsInJvbGxObyI6IjIyNjkxYTA1NzEiLCJhY2Nlc3NDb2RlIjoiY2FWdk5IIiwiY2xpZW50SUQiOiJlZWJjMGM0Zi0zNjdhLTRhN2QtOTY0NC0xYjNhNGE4ZWQ1NTAiLCJjbGllbnRTZWNyZXQiOiJiaEpZd3JVQlpnUWJBcXR6In0.5HzNKS42i1p6GLUmmvhjSUr7DXPmP1xC-4cB09mUKOw"
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
Log sent: {'logID': 'd1db5aaa-f0e4-425e-8b58-3bd56356efde', 'message': 'log created successfully'}
Log sent: {'logID': 'ccd90261-3765-4b15-96e1-18ccc671a1f1', 'message': 'log created successfully'}
Log sent: {'logID': '4799334c-2e86-46d9-9249-0d4670f8a08d', 'message': 'log created successfully'}
"""