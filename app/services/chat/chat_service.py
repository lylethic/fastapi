from datetime import datetime
from uuid import uuid4
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from app.schemas.chat import GetDirectChatSchema, GetMessageSchema
from app.db.models import Chat, ChatChatType as ChatType, Message, ReadStatus, Users


async def _get_message_created_map(
    db: AsyncSession, message_ids: list[str | None]
) -> dict[str, datetime]:
    ids = [message_id for message_id in message_ids if message_id]
    if not ids:
        return {}

    result = await db.execute(
        select(Message.id, Message.created).where(Message.id.in_(ids))
    )
    return {message_id: created for message_id, created in result.all()}


async def create_direct_chat(
    db: AsyncSession, *, initiator_user: Users, recipient_user: Users
) -> Chat:
    try:
        chat = Chat(
            id=str(uuid4()),
            guid=str(uuid4()),
            chat_type=ChatType.DIRECT,
        )
        chat.user.append(initiator_user)
        chat.user.append(recipient_user)
        db.add(chat)
        await db.flush()

        # make empty read statuses for both users last_read_message_id = 0
        initiator_read_status = ReadStatus(
            id=str(uuid4()),
            chat_id=chat.id,
            user_id=initiator_user.id,
            last_read_message_id=None,
        )
        recipient_read_status = ReadStatus(
            id=str(uuid4()),
            chat_id=chat.id,
            user_id=recipient_user.id,
            last_read_message_id=None,
        )
        db.add_all([initiator_read_status, recipient_read_status])
        await db.commit()

    except Exception as exc_info:
        await db.rollback()
        raise exc_info

    else:
        return chat


async def get_direct_chat_by_users(
    db: AsyncSession, *, initiator_user: Users, recipient_user: Users
) -> Chat | None:
    query = select(Chat).where(
        and_(
            Chat.chat_type == ChatType.DIRECT,
            Chat.user.contains(initiator_user),
            Chat.user.contains(recipient_user),
        )
    )

    result = await db.execute(query)
    chat: Chat | None = result.scalar_one_or_none()

    return chat


async def get_chat_by_guid(db: AsyncSession, *, chat_guid: UUID) -> Chat | None:
    query = (
        select(Chat)
        .where(Chat.guid == str(chat_guid))
        .options(
            selectinload(Chat.message),
            selectinload(Chat.user),
            selectinload(Chat.read_status),
        )
    )
    result = await db.execute(query)
    chat: Chat | None = result.scalar_one_or_none()

    return chat


async def get_user_by_guid(db: AsyncSession, *, user_guid: UUID) -> Users | None:
    query = select(Users).where(Users.guid == str(user_guid))
    result = await db.execute(query)
    user: Users | None = result.scalar_one_or_none()

    return user


async def get_new_messages_per_chat(
    db: AsyncSession, chats: list[Chat], current_user: Users
) -> list[GetDirectChatSchema]:
    """
    New message are those messages that:
    - don't belong to current user
    - are not yet read by current user

    """
    # Create a dictionary with default values of 0
    new_messages_count_per_chat = {chat.id: 0 for chat in chats}

    # Create an alias for the ReadStatus table
    read_status_alias = aliased(ReadStatus)

    query = (
        select(Message.chat_id, func.count().label("message_count"))
        .join(
            read_status_alias,
            and_(
                read_status_alias.user_id == current_user.id,
                read_status_alias.chat_id == Message.chat_id,
            ),
        )
        .where(
            and_(
                Message.user_id != current_user.id,
                Message.id > func.coalesce(read_status_alias.last_read_message_id, 0),
                Message.deleted.is_(False),
                Message.chat_id.in_(new_messages_count_per_chat),
            )
        )
        .group_by(Message.chat_id)
    )

    result = await db.execute(query)
    new_messages_count = result.fetchall()

    for messages_count in new_messages_count:
        new_messages_count_per_chat[messages_count[0]] = messages_count[1]

    return [
        GetDirectChatSchema(
            chat_guid=chat.guid,
            chat_type=chat.chat_type,
            created=chat.created,
            updated=chat.updated,
            users=chat.user,
            new_messages_count=new_messages_count_per_chat[chat.id],
        )
        for chat in chats
    ]


async def get_user_direct_chats(db: AsyncSession, *, current_user: Users) -> list[Chat]:
    query = (
        select(Chat)
        .where(
            and_(
                Chat.user.contains(current_user),
                Chat.deleted.is_(False),
                Chat.chat_type == ChatType.DIRECT,
            )
        )
        .options(selectinload(Chat.user))
    ).order_by(Chat.updated.desc())
    result = await db.execute(query)

    chats: list[Chat] = result.scalars().all()

    return chats


async def direct_chat_exists(
    db: AsyncSession, *, current_user: Users, recipient_user: Users
) -> bool:
    query = select(Chat.id).where(
        and_(
            Chat.chat_type == ChatType.DIRECT,
            Chat.deleted.is_(False),
            Chat.user.contains(current_user),
            Chat.user.contains(recipient_user),
        )
    )
    result = await db.execute(query)
    existing_chat = result.scalar_one_or_none()
    return existing_chat is not None


async def get_chat_messages(
    db: AsyncSession, *, user_id: str, chat: Chat, size: str
) -> tuple[list[Chat], bool, Message | None]:
    query = (
        select(Message)
        .where(and_(Message.chat_id == chat.id, Message.deleted.is_(False)))
        .order_by(Message.created.desc())
        .limit(size + 1)
        .options(selectinload(Message.user), selectinload(Message.chat))
    )
    result = await db.execute(query)
    messages: list[Message] = result.scalars().all()
    # check if there are more messages
    has_more_messages = len(messages) > size
    messages = messages[:size]

    # assuming only two read statuses
    # Initialize variables to prevent NameError
    my_last_read_message_id = None
    other_user_last_read_message_id = None

    # Loop through chat.read_statuses and assign the read message IDs
    for read_status in chat.read_status:
        if read_status.user_id != user_id:
            other_user_last_read_message_id = read_status.last_read_message_id
        else:
            my_last_read_message_id = read_status.last_read_message_id

    read_created_map = await _get_message_created_map(
        db, [my_last_read_message_id, other_user_last_read_message_id]
    )
    my_last_read_created = read_created_map.get(my_last_read_message_id)
    other_user_last_read_created = read_created_map.get(other_user_last_read_message_id)

    last_read_message = (
        await db.get(Message, other_user_last_read_message_id)
        if other_user_last_read_message_id
        else None
    )

    # Construct GetMessageSchema list
    get_message_schemas = [
        GetMessageSchema(
            message_guid=message.guid,
            content=message.content,
            created=message.created,
            chat_guid=message.chat.guid,
            user_guid=message.user.guid,
            is_read=(
                message.created <= other_user_last_read_created
                if message.user.id == user_id
                else message.created <= my_last_read_created
            )
            if (
                other_user_last_read_created is not None
                if message.user.id == user_id
                else my_last_read_created is not None
            )
            else False,
        )
        for message in messages
    ]

    return get_message_schemas, has_more_messages, last_read_message


async def get_active_message_by_guid_and_chat(
    db: AsyncSession, *, chat_id: str, message_guid: UUID
) -> Message | None:
    query = select(Message).where(
        and_(
            Message.guid == str(message_guid),
            Message.deleted.is_(False),
            Message.chat_id == chat_id,
        )
    )

    result = await db.execute(query)
    message: Message | None = result.scalar_one_or_none()

    return message


async def get_older_chat_messages(
    db: AsyncSession,
    *,
    chat: Chat,
    user_id: str,
    limit: int = 10,
    created: datetime,
) -> tuple[list[Message], bool]:
    query = (
        select(Message)
        .where(
            and_(
                Message.chat_id == chat.id,
                Message.deleted.is_(False),
                Message.created < created,
            )
        )
        .order_by(Message.created.desc())
        .limit(limit + 1)  # Fetch limit + 1 messages
        .options(selectinload(Message.user), selectinload(Message.chat))
    )

    result = await db.execute(query)
    older_messages: list[Message] = result.scalars().all()

    # Determine if there are more messages
    has_more_messages = len(older_messages) > limit
    older_messages = older_messages[:limit]

    my_last_read_message_id = None
    other_user_last_read_message_id = None

    for read_status in chat.read_status:
        if read_status.user_id != user_id:
            other_user_last_read_message_id = read_status.last_read_message_id
        else:
            my_last_read_message_id = read_status.last_read_message_id

    read_created_map = await _get_message_created_map(
        db, [my_last_read_message_id, other_user_last_read_message_id]
    )
    my_last_read_created = read_created_map.get(my_last_read_message_id)
    other_user_last_read_created = read_created_map.get(other_user_last_read_message_id)

    get_message_schemas = [
        GetMessageSchema(
            message_guid=message.guid,
            content=message.content,
            created=message.created,
            chat_guid=message.chat.guid,
            user_guid=message.user.guid,
            is_read=(
                message.created <= other_user_last_read_created
                if message.user.id == user_id
                else message.created <= my_last_read_created
            )
            if (
                other_user_last_read_created is not None
                if message.user.id == user_id
                else my_last_read_created is not None
            )
            else False,
        )
        for message in older_messages
    ]

    # Return the first 'limit' messages and a flag indicating if there are more
    return get_message_schemas, has_more_messages


async def add_new_messages_stats_to_direct_chat(
    db: AsyncSession, *, current_user: Users, chat: Chat
) -> GetDirectChatSchema:
    # new non-model (chat) fields are added
    has_new_messages: bool = False
    new_messages_count: int

    # assuming chat has two read statuses
    # current user's read status is used to determine new messages count
    for read_status in chat.read_status:
        # own read status -> for new messages
        if read_status.user_id == current_user.id:
            my_last_read_message_id = read_status.last_read_message_id

    new_messages_query = select(func.count()).where(
        and_(
            Message.user_id != current_user.id,
            Message.id > my_last_read_message_id,
            Message.deleted.is_(False),
            Message.chat_id == chat.id,
        )
    )
    result = await db.execute(new_messages_query)
    new_messages_count: int = result.scalar_one_or_none()
    if new_messages_count:
        has_new_messages = True

    return GetDirectChatSchema(
        chat_guid=chat.guid,
        chat_type=chat.chat_type,
        created=chat.created,
        updated=chat.updated,
        users=chat.user,
        has_new_messages=has_new_messages,
        new_messages_count=new_messages_count,
    )


async def get_unread_messages_count(
    db: AsyncSession, *, user_id: str, chat: Chat
) -> int:
    # Get the user's last read message ID in the chat
    user_read_status = next(
        (rs for rs in chat.read_status if rs.user_id == user_id), None
    )
    if not user_read_status:
        return 0  # User has no read status in this chat

    user_last_read_message_id = user_read_status.last_read_message_id

    # Count the number of unread messages for the user
    query = select(func.count()).where(
        and_(
            Message.chat_id == chat.id,
            Message.deleted.is_(False),
            Message.id > user_last_read_message_id,
        )
    )

    result = await db.execute(query)
    unread_messages_count = result.scalar()

    return unread_messages_count
