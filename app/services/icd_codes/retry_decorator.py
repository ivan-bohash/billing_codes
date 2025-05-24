import asyncio
from functools import wraps


def retry(max_attempts=5, delay=30):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    print(f"{e}: sleep {delay} seconds")
                    attempt += 1
                    await asyncio.sleep(delay)
            raise Exception("Max retries exceeded")
        return wrapper
    return decorator



