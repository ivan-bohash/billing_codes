from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    headers: dict = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.7",
        "Referer": "https://www.icd10data.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Accept-Encoding": "gzip, deflate",
        "Cache-Control": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1"
    }

    billable_url: str = "https://www.icd10data.com/ICD10CM/Codes/Rules/Billable_Specific_Codes/"
    non_billable_url: str = "https://www.icd10data.com/ICD10CM/Codes/Rules/Non_Billable_Specific_Codes/"

    redis: dict = {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "queue_name": {
            "low": "low",
            "high": "high",
        }

    }


settings = Settings()

