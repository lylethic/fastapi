from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Message
from app.repositories.message_repository import message_repository
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.message import (
    MessageCreateBody,
    MessagePagination,
    MessageUpdateBody,
)


class MessageService:
    def __init__(self) -> None:
        self.repository = message_repository

    async def validate_create(self, db: AsyncSession, body: MessageCreateBody) -> None:
        if not await self.repository.user_exists(db, body.user_id):
            raise HTTPException(status_code=404, detail="User not found")

        if not await self.repository.chat_exists(db, body.chat_id):
            raise HTTPException(status_code=404, detail="Chat not found")

    async def create(
        self,
        db: AsyncSession,
        body: MessageCreateBody,
        current_user: str | None = None,
    ) -> Message:
        await self.validate_create(db, body)
        return await self.repository.create_from_data(
            db=db,
            data=self.repository.map_create_data(body),
            current_user=current_user,
        )

    async def get_all(
        self, db: AsyncSession, pagination: BaseQueryPaginationRequest
    ) -> MessagePagination:
        return await self.repository.get_all(db=db, pagination=pagination)

    async def get_by_chat_id(
        self, db: AsyncSession, chat_id: str, pagination: BaseQueryPaginationRequest
    ) -> MessagePagination:
        return await self.repository.get_by_chat_id(
            db=db, chat_id=chat_id, pagination=pagination
        )

    async def get_by_id(self, db: AsyncSession, id: str) -> Message | None:
        return await self.repository.get_by_id(db=db, id=id)

    async def update(
        self,
        db: AsyncSession,
        id: str,
        body: MessageUpdateBody,
        current_user: str | None = None,
    ) -> Message:
        return await self.repository.update(
            db=db, id=id, body=body, current_user=current_user
        )

    async def soft_delete(self, db: AsyncSession, id: str) -> Message:
        return await self.repository.soft_delete(db=db, id=id)


message_service = MessageService()


async def create_message(
    db: AsyncSession, body: MessageCreateBody, current_user: str | None = None
) -> Message:
    return await message_service.create(db=db, body=body, current_user=current_user)


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
