from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.db.init_db import Base
from app.db.models.abstract import MainMixin


class UrlsBaseModel(Base, MainMixin):
    """
    Base model for Billable and Non-billable URLs

    """

    __abstract__ = True

    icd_code: Column[String] = Column(String, index=True, nullable=False)
    url: Column[String] = Column(String, nullable=False)

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


class UrlsBillModel(UrlsBaseModel):
    """
    Billable URLs model

    """

    __tablename__ = "urls_billable"

    history = relationship(
        "HistoryBillModel",
        back_populates="url",
        uselist=False,
        cascade="all, delete-orphan",
    )


class UrlsNonBillModel(UrlsBaseModel):
    """
    Non-Billable URLs model

    """

    __tablename__ = "urls_non_billable"

    history = relationship(
        "HistoryNonBillModel",
        back_populates="url",
        uselist=False,
        cascade="all, delete-orphan",
    )
