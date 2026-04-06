import datetime
from typing import Generic, Optional, TypeVar

from fastapi import Query
from pydantic import BaseModel


T = TypeVar("T")


class BaseLogEntity(BaseModel):
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


class BaseQueryPaginationRequest:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        active: bool | None = Query(True),
        search: Optional[str] = Query(None),
    ) -> None:
        self.page = page
        self.page_size = page_size
        self.active = active
        self.search = search
