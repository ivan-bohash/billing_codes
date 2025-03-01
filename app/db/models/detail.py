from sqlalchemy import Column, String
from app.db.init_db import Base
from app.db.models.abstract import MainMixin


class DetailModel(Base, MainMixin):
    __tablename__ = "detail"

    icd_code = Column(String, index=True, nullable=False)
    detail = Column(String, nullable=False)

    def __repr__(self):
        return f"IcdDetail(id={self.id}, code={self.icd_code}, detail={self.detail})"

    def __init__(self, icd_code, detail):
        self.icd_code = icd_code
        self.detail = detail
