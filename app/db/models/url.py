from sqlalchemy import Column, String
from app.db.init_db import Base
from app.db.models.abstract import MainMixin


class UrlModel(Base, MainMixin):
    __tablename__ = "url"

    icd_code = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False)

    def __repr__(self):
        return f"UrlModel(id={self.id}, code={self.icd_code}, url={self.url})"

    def __init__(self, icd_code, url):
        self.icd_code = icd_code
        self.url = url


