from fastapi import HTTPException
from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chat, Message, Users
from app.repositories.base_repository import BaseRepository
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.message import (
    MessagePagination,
    MessageResponse,
)


class MessageRepository(
    BaseRepository[
        Message,
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

    async def user_exists(self, db: AsyncSession, user_id: str) -> bool:
        return await db.get(Users, user_id) is not None

    async def chat_exists(self, db: AsyncSession, chat_id: str) -> bool:
        chat = await db.get(Chat, chat_id)
        return chat is not None and not bool(chat.deleted)

    async def get_by_chat_id(
        self, db: AsyncSession, chat_id: str, pagination: BaseQueryPaginationRequest
    ) -> MessagePagination:
        if not await self.chat_exists(db, chat_id):
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


message_repository = MessageRepository()
