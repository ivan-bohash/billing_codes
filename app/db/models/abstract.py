import arrow

from sqlalchemy import Column, Integer
from sqlalchemy_utils import ArrowType


class MainMixin:
    """"
    Global main mixin

    """

    id = Column(Integer(), doc="ID", primary_key=True)
    create_at = Column(ArrowType(), doc="Create At", default=arrow.utcnow(), nullable=False)
