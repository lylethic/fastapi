from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    is_success: bool
    status_code: int
    data: T
    message: str
    message_en: str


def success_response(
    data: T,
    message: str = "Thanh cong",
    message_en: str = "Success",
    status_code: int = 200,
    is_success: bool = True,
) -> ApiResponse[T]:
    return ApiResponse[T](
        is_success=is_success,
        status_code=status_code,
        data=data,
        message=message,
        message_en=message_en,
    )
