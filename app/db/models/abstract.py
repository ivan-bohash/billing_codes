import arrow

from sqlalchemy import Column, Integer
from sqlalchemy_utils import ArrowType


class MainMixin:
    """"
    Global main mixin

    """

    id = Column(Integer(), doc="ID", primary_key=True)
    created_at = Column(ArrowType(), doc="Created At", default=arrow.utcnow(), nullable=False)
    updated_at = Column(ArrowType(), doc="Updated At", default=arrow.utcnow(), nullable=False)
