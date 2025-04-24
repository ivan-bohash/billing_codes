from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.init_db import Base
from app.db.models.abstract import MainMixin


class DetailsBaseModel(Base, MainMixin):
    """
     Base model for Billable and Non-billable details

    """

    __abstract__ = True

    icd_code: Mapped[str] = mapped_column(String, index=True, nullable=False)
    detail: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self):
        return self._repr(
            id=self.id,
            icd_code=self.icd_code,
            detail=self.detail,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def __init__(self, icd_code, detail):
        self.icd_code = icd_code
        self.detail = detail


class DetailsBillModel(DetailsBaseModel):
    """
    Billable details model

    """

    __tablename__ = "details_billable"


class DetailsNonBillModel(DetailsBaseModel):
    """
    Non-Billable details model

    """

    __tablename__ = "details_non_billable"

