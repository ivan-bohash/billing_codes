from pydantic import BaseModel
from datetime import datetime


class IcdSchema(BaseModel):
    icd_code: str
    rule: str
    updated: datetime
    url: str
    code_history: str


class UrlSchema(BaseModel):
    icd_code: str
    url: str
