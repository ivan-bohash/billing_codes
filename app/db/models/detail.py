from sqlalchemy import Column, String
from app.db.init_db import Base
from app.db.models.abstract import MainMixin


class DetailBillModel(Base, MainMixin):
    __tablename__ = "detail_billable"

    icd_code = Column(String, index=True, nullable=False)
    detail = Column(String, nullable=False)

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


class DetailNonBillModel(Base, MainMixin):
    __tablename__ = "detail_non_billable"

    icd_code = Column(String, index=True, nullable=False)
    detail = Column(String, nullable=False)

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
