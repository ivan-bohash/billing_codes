import arrow
import typing

from sqlalchemy import Column, Integer
from sqlalchemy_utils import ArrowType


class MainMixin:
    """"
    Global main mixin

    """

    default_time = arrow.utcnow()

    id = Column(Integer(), doc="ID", primary_key=True)
    created_at = Column(ArrowType(), doc="Created At", default=default_time, nullable=False)
    updated_at = Column(ArrowType(), doc="Updated At", default=default_time, nullable=False)

    # custom repr method
    def _repr(self, **kwargs):
        field_strings = []
        added_attributes = False

        for key, field in kwargs.items():
            try:
                field_strings.append(f"{key}: {field}")
            except Exception as e:
                print(e)
            else:
                added_attributes = True

        if added_attributes:
            return f"<{self.__class__.__name__}>({', '.join(field_strings)})"
        return f"<{self.__class__.__name__} {id(self)}>"
