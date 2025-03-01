from sqlalchemy import Column, String
from app.db.init_db import Base
from app.db.models.abstract import MainMixin


class PaginationModel(Base, MainMixin):
    __tablename__ = "pagination"

    url = Column(String)

    def __repr__(self):
        return f"PaginationModel({self.url})"

    def __init__(self, url):
        self.url = url

