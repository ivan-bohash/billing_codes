from sqlalchemy import Column, String
from app.db.init_db import Base
from app.db.models.abstract import MainMixin

from sqlalchemy import Column, Integer


class UrlsBillModel(Base, MainMixin):
    __tablename__ = "urls_billable"

    icd_code = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False)

    def __repr__(self):
        return self._repr(
            id=self.id,
            icd_code=self.icd_code,
            url=self.url,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def __init__(self, icd_code, url):
        self.icd_code = icd_code
        self.url = url


class UrlsNonBillModel(Base, MainMixin):
    __tablename__ = "urls_non_billable"

    icd_code = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False)

    def __repr__(self):
        return self._repr(
            id=self.id,
            icd_code=self.icd_code,
            url=self.url,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def __init__(self, icd_code, url):
        self.icd_code = icd_code
        self.url = url


