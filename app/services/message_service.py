from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chat, Message, Users
from app.schemas.base_schema import BaseQueryPaginationRequest
from app.schemas.message import (
    MessageCreateBody,
    MessagePagination,
    MessageResponse,
    MessageUpdateBody,
)


async def create_message(
    db: AsyncSession, body: MessageCreateBody, current_user: str | None = None
) -> Message:
    user = await db.get(Users, body.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    chat = await db.get(Chat, body.chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    message = Message(
        id=str(uuid4()),
        guid=str(uuid4()),
        message_type=body.message_type,
        content=body.content,
        user_id=body.user_id,
        chat_id=body.chat_id,
        file_name=body.file_name,
        file_path=body.file_path,
    )
    message.created = datetime.utcnow()
    if current_user is not None:
        message.created_by = current_user

    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_messages(
    db: AsyncSession, pagination: BaseQueryPaginationRequest
) -> MessagePagination:
    filters = [Message.deleted == False]

    if pagination.search:
        filters.append(
            or_(
                Message.id == pagination.search,
                Message.guid == pagination.search,
                Message.content.ilike(f"%{pagination.search}%"),
            )
        )

    if pagination.active is not None:
        filters.append(Message.active == pagination.active)

    count_stmt = select(func.count()).select_from(Message)
    if filters:
        count_stmt = count_stmt.where(*filters)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    total_pages = (
        (total + pagination.page_size - 1) // pagination.page_size if total else 0
    )

    stmt = select(Message)
    if filters:
        stmt = stmt.where(*filters)

    stmt = (
        stmt.order_by(Message.created.desc())
        .offset((pagination.page - 1) * pagination.page_size)
        .limit(pagination.page_size)
    )

    result = await db.execute(stmt)
    messages = result.scalars().all()

    return MessagePagination(
        items=[MessageResponse.model_validate(message) for message in messages],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


async def get_messages_by_chat_id(
    db: AsyncSession, chat_id: str, pagination: BaseQueryPaginationRequest
) -> MessagePagination:
    chat = await db.get(Chat, chat_id)
    if chat is None or chat.deleted:
        raise HTTPException(status_code=404, detail="Chat not found")

    filters = [Message.deleted == False, Message.chat_id == chat_id]

    if pagination.search:
        filters.append(
            or_(
                Message.id == pagination.search,
                Message.guid == pagination.search,
                Message.content.ilike(f"%{pagination.search}%"),
            )
        )

    if pagination.active is not None:
        filters.append(Message.active == pagination.active)

    count_stmt = select(func.count()).select_from(Message)
    if filters:
        count_stmt = count_stmt.where(*filters)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    total_pages = (
        (total + pagination.page_size - 1) // pagination.page_size if total else 0
    )

    stmt = select(Message)
    if filters:
        stmt = stmt.where(*filters)

    stmt = (
        stmt.order_by(Message.created.desc())
        .offset((pagination.page - 1) * pagination.page_size)
        .limit(pagination.page_size)
    )

    result = await db.execute(stmt)
    messages = result.scalars().all()

    return MessagePagination(
        items=[MessageResponse.model_validate(message) for message in messages],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


async def get_message_by_id(db: AsyncSession, id: str) -> Message | None:
    result = await db.execute(
        select(Message).where(and_(Message.id == id, Message.deleted == False))
    )
    return result.scalar_one_or_none()


async def update_message(
    db: AsyncSession,
    id: str,
    body: MessageUpdateBody,
    current_user: str | None = None,
) -> Message:
    message = await get_message_by_id(db=db, id=id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")

    if body.message_type is not None:
        message.message_type = body.message_type
    if body.content is not None:
        message.content = body.content
    if body.file_name is not None:
        message.file_name = body.file_name
    if body.file_path is not None:
        message.file_path = body.file_path
    if body.active is not None:
        message.active = body.active

    message.updated = datetime.utcnow()
    if current_user is not None:
        message.updated_by = current_user

    await db.commit()
    await db.refresh(message)
    return message


async def delete_message(db: AsyncSession, id: str) -> Message:
    message = await get_message_by_id(db=db, id=id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")

    message.active = False
    message.deleted = True
    message.updated = datetime.utcnow()

    await db.commit()
    await db.refresh(message)
    return message
