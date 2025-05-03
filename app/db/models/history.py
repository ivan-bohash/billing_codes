from sqlalchemy import Column, String

from app.db.init_db import Base
from app.db.models.abstract import MainMixin


class HistoryBaseModel(Base, MainMixin):
    """
     Base model for Billable and Non-billable code history

    """

    __abstract__ = True

    icd_code: Column[String] = Column(String, index=True, nullable=False)
    code_history: Column[String] = Column(String, nullable=False)

    def __repr__(self):
        return self._repr(
            id=self.id,
            icd_code=self.icd_code,
            code_history=self.code_history,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def __init__(self, icd_code, code_history):
        self.icd_code = icd_code
        self.code_history = code_history


class HistoryBillModel(HistoryBaseModel):
    """
    Billable code history model

    """

    __tablename__ = "history_billable"


class HistoryNonBillModel(HistoryBaseModel):
    """
    Non-Billable code history model

    """

    __tablename__ = "history_non_billable"

