from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ICD Codes"

    # request settings
    headers: dict = {
        "User-Agent": "Mozilla/5.0 (Linux) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36"
    }
    proxy: str = "http://200.106.124.217:999"
    # proxies = {"http": "72.10.160.171:1959"}

    # main urls
    billable_url: str = "https://www.icd10data.com/ICD10CM/Codes/Rules/Billable_Specific_Codes/"
    non_billable_url: str = "https://www.icd10data.com/ICD10CM/Codes/Rules/Non_Billable_Specific_Codes"


settings = Settings()
