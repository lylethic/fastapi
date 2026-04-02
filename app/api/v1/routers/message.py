from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.response import ApiResponse, success_response
from app.db.session import get_db
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.message import (
    MessageCreateBody,
    MessagePagination,
    MessageResponse,
    MessageUpdateBody,
)
from app.services.assistant_service import get_current_user
from app.services.message_service import (
    create_message,
    delete_message,
    get_message_by_id,
    get_messages_by_chat_id,
    get_messages,
    update_message,
)


router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post(
    "",
    response_model=ApiResponse[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Create message",
)
async def create_message_api(
    payload: MessageCreateBody,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    data = await create_message(db=db, body=payload, current_user=current_user["id"])
    return success_response(
        data=MessageResponse.model_validate(data),
        message="Thành công",
        message_en="Message created successfully",
        status_code=status.HTTP_200_OK,
    )


@router.get(
    "",
    response_model=ApiResponse[MessagePagination],
    summary="Get messages",
)
async def get_messages_api(
    db: AsyncSession = Depends(get_db),
    pagination: BaseQueryPaginationRequest = Depends(),
):
    data = await get_messages(db=db, pagination=pagination)
    return success_response(
        data=data,
        message="Thành công",
        message_en="Messages retrieved successfully",
    )


@router.get(
    "/chat/{chat_id}",
    response_model=ApiResponse[MessagePagination],
    summary="Get messages by chat id",
)
async def get_messages_by_chat_id_api(
    chat_id: str,
    db: AsyncSession = Depends(get_db),
    pagination: BaseQueryPaginationRequest = Depends(),
):
    data = await get_messages_by_chat_id(db=db, chat_id=chat_id, pagination=pagination)
    return success_response(
        data=data,
        message="Thành công",
        message_en="Messages retrieved successfully",
    )


@router.get(
    "/{id}",
    response_model=ApiResponse[MessageResponse | None],
    summary="Get message by id",
)
async def get_message_by_id_api(id: str, db: AsyncSession = Depends(get_db)):
    data = await get_message_by_id(db=db, id=id)
    if not data:
        return success_response(
            is_success=False,
            status_code=404,
            data=None,
            message="Không tìm thấy message",
            message_en="Message not found",
        )
    return success_response(
        data=MessageResponse.model_validate(data),
        message="Thành công",
        message_en="Message retrieved successfully",
    )


@router.put(
    "/{id}",
    response_model=ApiResponse[MessageResponse],
    summary="Update message",
)
async def update_message_api(
    id: str,
    payload: MessageUpdateBody,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    data = await update_message(
        db=db, id=id, body=payload, current_user=current_user["id"]
    )
    return success_response(
        data=MessageResponse.model_validate(data),
        message="Thành công",
        message_en="Message updated successfully",
    )


@router.delete(
    "/{id}",
    response_model=ApiResponse[MessageResponse],
    summary="Delete message",
)
async def delete_message_api(
    id: str,
    db: AsyncSession = Depends(get_db),
):
    data = await delete_message(db=db, id=id)
    return success_response(
        data=MessageResponse.model_validate(data),
        message="Thành công",
        message_en="Message deleted successfully",
    )
