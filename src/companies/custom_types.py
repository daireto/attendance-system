from typing import Any, get_args, get_origin

from sqlalchemy import JSON, TypeDecorator


def _serialize_pydantic(value: Any) -> Any:
    """Serialize a Pydantic model to a dictionary."""
    if hasattr(value, 'model_dump'):
        return value.model_dump()
    return value.dict()


class PydanticType(TypeDecorator):
    """A SQLAlchemy type that allows storing Pydantic models
    in JSON columns.

    Usage::

        from pydantic import BaseModel
        from sqlalchemy.orm import Mapped, mapped_column

        class Model(BaseModel):
            field: str

        class MyTable(Base):
            __tablename__ = 'my_table'
            pk: Mapped[int] = mapped_column(primary_key=True)
            data: Mapped[Model] = mapped_column(PydanticType(Model))
            data_list: Mapped[List[Model]] = mapped_column(PydanticType(List[Model]))
    """

    impl = JSON

    def __init__(self, pydantic_type: type) -> None:
        """Initialize the PydanticType.

        Parameters
        ----------
        pydantic_type : type
            The Pydantic model type to store.

        """
        super().__init__()
        self.pydantic_type = pydantic_type
        self.is_list = get_origin(pydantic_type) is list
        self.item_type = (
            get_args(pydantic_type)[0] if self.is_list else pydantic_type
        )

    def process_bind_param(self, value: Any, _: Any) -> Any:
        """Convert Pydantic model(s) to dict(s) for storage."""
        if value is None:
            return None

        if self.is_list:
            return [_serialize_pydantic(item) for item in value]

        return _serialize_pydantic(value)

    def process_result_value(self, value: Any, _: Any) -> Any:
        """Convert stored dict(s) back to Pydantic model(s)."""
        if value is None:
            return None

        if self.is_list:
            return [self.item_type(**item) for item in value]

        return self.pydantic_type(**value)
