import uuid

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

    def map_create_model(self, body: MessageCreateBody) -> Message:
        return Message(
            guid=str(uuid.uuid7()),
            **body.model_dump(exclude_unset=True),
        )

    def map_update_model(self, body: MessageUpdateBody) -> tuple[Message, set[str]]:
        data = body.model_dump(exclude_unset=True)
        return Message(**data), set(data.keys())

    async def create(
        self,
        db: AsyncSession,
        body: MessageCreateBody,
        current_user: str | None = None,
    ) -> Message:
        await self.validate_create(db, body)
        return await self.repository.post(
            db=db,
            body=self.map_create_model(body),
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
        message_model, update_fields = self.map_update_model(body)
        return await self.repository.update(
            db=db,
            id=id,
            body=message_model,
            current_user=current_user,
            fields=update_fields,
        )

    async def soft_delete(self, db: AsyncSession, id: str) -> Message:
        return await self.repository.soft_delete(db=db, id=id)


message_service = MessageService()
