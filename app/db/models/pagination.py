from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.init_db import Base
from app.db.models.abstract import MainMixin


class PaginationBaseModel(Base, MainMixin):
    """
    Pagination Billable model

    """

    __abstract__ = True

    url: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self):
        return self._repr(
            id=self.id,
            url=self.url,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def __init__(self, url):
        self.url = url


class PaginationBillModel(PaginationBaseModel):
    """
    Billable pagination model

    """

    __tablename__ = "pagination_billable"


class PaginationNonBillModel(PaginationBaseModel):
    """
    Non-Billable pagination model

    """

    __tablename__ = "pagination_non_billable"
