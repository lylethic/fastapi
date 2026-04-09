from datetime import datetime

from pydantic import UUID7, BaseModel

# TODO: Add data validation


class ReceiveMessageSchema(BaseModel):
    user_guid: UUID7
    chat_guid: UUID7
    content: str


class SendMessageSchema(BaseModel):
    type: str = "new"
    message_guid: UUID7
    user_guid: UUID7
    chat_guid: UUID7
    content: str
    created: datetime
    is_read: bool | None = False


class MessageReadSchema(BaseModel):
    type: str
    chat_guid: UUID7
    message_guid: UUID7


class UserTypingSchema(BaseModel):
    type: str
    chat_guid: UUID7
    user_guid: UUID7


class NewChatCreated(BaseModel):
    type: str = "new_chat_created"
    chat_id: int  # need to pass for guid/id mapping [chats variable]
    chat_guid: UUID7
    created: datetime
    updated: datetime | None = None
    friend: dict
    has_new_messages: bool
    new_messages_count: int


class AddUserToChatSchema(BaseModel):
    chat_guid: str  # used for websocket communication
    chat_id: int


class NotifyChatRemovedSchema(BaseModel):
    type: str = "chat_deleted"
    chat_guid: str
