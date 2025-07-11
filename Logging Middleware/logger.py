import httpx

BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJodmlqYXB1cmFtQGdtYWlsLmNvbSIsImV4cCI6MTc1MjIxMzIyOSwiaWF0IjoxNzUyMjEyMzI5LCJpc3MiOiJBZmZvcmQgTWVkaWNhbCBUZWNobm9sb2dpZXMgUHJpdmF0ZSBMaW1pdGVkIiwianRpIjoiZGFjOWQ3ZjAtMDNkMi00YzNkLWE5NzMtZWRjZmVmOGUzYzg0IiwibG9jYWxlIjoiZW4tSU4iLCJuYW1lIjoidmlqYXB1cmFtIGhhcnNoYXZhcmRoYW4iLCJzdWIiOiJlZWJjMGM0Zi0zNjdhLTRhN2QtOTY0NC0xYjNhNGE4ZWQ1NTAifSwiZW1haWwiOiJodmlqYXB1cmFtQGdtYWlsLmNvbSIsIm5hbWUiOiJ2aWphcHVyYW0gaGFyc2hhdmFyZGhhbiIsInJvbGxObyI6IjIyNjkxYTA1NzEiLCJhY2Nlc3NDb2RlIjoiY2FWdk5IIiwiY2xpZW50SUQiOiJlZWJjMGM0Zi0zNjdhLTRhN2QtOTY0NC0xYjNhNGE4ZWQ1NTAiLCJjbGllbnRTZWNyZXQiOiJiaEpZd3JVQlpnUWJBcXR6In0.U9wWCRweQPWwOgR8SyYiCOhewFKvd3vIwiV3d5V7qko"

LOG_URL = "http://20.244.56.144/evaluation-service/logs"

async def Logme(stack: str, level: str, package: str, message: str):
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
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
            print(f"Log sent: {payload}")
    except httpx.RequestError as e:
        print(f"Connection error: {e}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.text}")
