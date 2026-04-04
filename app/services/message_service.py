from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chat, Message, Users
from app.providers.baseProvider import BaseProvider
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.message import (
    MessageCreateBody,
    MessagePagination,
    MessageResponse,
    MessageUpdateBody,
)


class MessageService(
    BaseProvider[
        Message,
        MessageCreateBody,
        MessageUpdateBody,
        MessageResponse,
        MessagePagination,
    ]
):
    def __init__(self) -> None:
        super().__init__(
            model=Message,
            response_schema=MessageResponse,
            pagination_schema=MessagePagination,
            not_found_message="Message not found",
            already_exists_message="Message already exists",
            search_fields=["content"],
        )

    async def validate_create(self, db: AsyncSession, body: MessageCreateBody) -> None:
        user = await db.get(Users, body.user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        chat = await db.get(Chat, body.chat_id)
        if chat is None or chat.deleted:
            raise HTTPException(status_code=404, detail="Chat not found")

    def map_create_data(self, body: MessageCreateBody) -> dict:
        data = body.model_dump(exclude_unset=True)
        data["guid"] = str(uuid4())
        return data

    def build_search_filters(self, search: str) -> list:
        if not search:
            return []
        return [
            or_(
                Message.id == search,
                Message.guid == search,
                Message.content.ilike(f"%{search}%"),
            )
        ]

    async def get_by_chat_id(
        self, db: AsyncSession, chat_id: str, pagination: BaseQueryPaginationRequest
    ) -> MessagePagination:
        chat = await db.get(Chat, chat_id)
        if chat is None or chat.deleted:
            raise HTTPException(status_code=404, detail="Chat not found")

        filters = self.base_filters()
        filters.append(Message.chat_id == chat_id)

        if pagination.search:
            filters.extend(self.build_search_filters(pagination.search))

        if pagination.active is not None and hasattr(self.model, "active"):
            filters.append(self.model.active == pagination.active)

        total_result = await db.execute(
            select(func.count()).select_from(Message).where(*filters)
        )
        total = total_result.scalar_one()

        total_pages = (
            (total + pagination.page_size - 1) // pagination.page_size if total else 0
        )

        stmt = (
            select(Message)
            .where(*filters)
            .order_by(Message.created.desc())
            .offset((pagination.page - 1) * pagination.page_size)
            .limit(pagination.page_size)
        )
        result = await db.execute(stmt)
        items = result.scalars().all()

        return MessagePagination(
            items=[MessageResponse.model_validate(item) for item in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
        )


message_service = MessageService()


async def create_message(
    db: AsyncSession, body: MessageCreateBody, current_user: str | None = None
) -> Message:
    return await message_service.post(db=db, body=body, current_user=current_user)


async def get_messages(
    db: AsyncSession, pagination: BaseQueryPaginationRequest
) -> MessagePagination:
    return await message_service.get_all(db=db, pagination=pagination)


async def get_messages_by_chat_id(
    db: AsyncSession, chat_id: str, pagination: BaseQueryPaginationRequest
) -> MessagePagination:
    return await message_service.get_by_chat_id(
        db=db, chat_id=chat_id, pagination=pagination
    )


async def get_message_by_id(db: AsyncSession, id: str) -> Message | None:
    return await message_service.get_by_id(db=db, id=id)


async def update_message(
    db: AsyncSession,
    id: str,
    body: MessageUpdateBody,
    current_user: str | None = None,
) -> Message:
    return await message_service.update(
        db=db, id=id, body=body, current_user=current_user
    )


async def delete_message(db: AsyncSession, id: str) -> Message:
    return await message_service.soft_delete(db=db, id=id)
