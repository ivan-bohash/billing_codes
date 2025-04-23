from pydantic import BaseModel


class PaginationSchema(BaseModel):
    url: str


class UrlsSchema(BaseModel):
    icd_code: str
    url: str


class DetailsSchema(BaseModel):
    icd_code: str
    detail: str

