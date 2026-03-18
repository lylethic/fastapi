import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class BaseLogEntity(BaseModel):
    id: str
    created: datetime.datetime
    updated: Optional[datetime.datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted: bool
    active: bool


class BaseModelPagination(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
