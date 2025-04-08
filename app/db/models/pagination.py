from sqlalchemy import Column, String
from app.db.init_db import Base
from app.db.models.abstract import MainMixin


class PaginationBillModel(Base, MainMixin):
    __tablename__ = "pagination_billable"

    url = Column(String)

    def __repr__(self):
        return self._repr(
            id=self.id,
            url=self.url,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def __init__(self, url):
        self.url = url


class PaginationNonBillModel(Base, MainMixin):
    __tablename__ = "pagination_non_billable"

    url = Column(String)

    def __repr__(self):
        return self._repr(
            id=self.id,
            url=self.url,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def __init__(self, url):
        self.url = url

