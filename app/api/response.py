from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    isSuccess: bool
    statusCode: int
    data: T
    message: str
    messageEn: str


def success_response(
    data: T,
    message: str = "Thanh cong",
    messageEn: str = "Success",
    status_code: int = 200,
    isSuccess: bool = True,
) -> ApiResponse[T]:
    return ApiResponse[T](
        isSuccess=isSuccess,
        statusCode=status_code,
        data=data,
        message=message,
        messageEn=messageEn,
    )
