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

    proxies: list = [
        # "http://38.153.152.244:9594",
        # "http://86.38.234.176:6630",
        # "http://173.211.0.148:6641",
        # "http://216.10.27.159:6837",
        # "http://154.36.110.199:6853",
        # "http://173.0.9.70:5653",
        # "http://198.105.101.92:5721",
        # "http://161.123.152.115:6360",
        # "http://38.154.227.167:5868",
        # "http://45.151.162.198:6600"
    ]

    proxy_auth: dict = {
        "login": "wizitbfg",
        "password": "1m30nbigz04a"
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

# proxy: str = "http://23.224.189.161:3128"
# proxies = {"http": "72.10.160.171:1959"}
# headers: dict = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    #     "Accept-Language": "en-US,en;q=0.5",
    #     "Referer": "https://www.icd10data.com/",
    #     "Connection": "keep-alive",
    #     "Upgrade-Insecure-Requests": "1"
    # }
