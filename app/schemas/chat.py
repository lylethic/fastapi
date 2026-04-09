from datetime import datetime

from pydantic import UUID7, BaseModel, field_validator

from app.config import ENVIRONMENT, APP_HOST
from app.db.models import ChatChatType as ChatType


class ChatSchema(BaseModel):
    guid: UUID7
    chat_type: ChatType


class CreateDirectChatSchema(BaseModel):
    recipient_user_guid: UUID7


class UserSchema(BaseModel):
    guid: UUID7
    name: str
    username: str
    profile_pic: str | None

    class Config:
        from_attributes = True

    @field_validator("profile_pic")
    @classmethod
    def add_image_host(cls, image_url: str | None) -> str:
        if image_url:
            if "/uploads/" in image_url and ENVIRONMENT == "development":
                return APP_HOST + image_url
        return image_url


class MessageSchema(BaseModel):
    guid: UUID7
    content: str
    created: datetime
    user: UserSchema
    chat: ChatSchema
    is_read: bool | None = False
    is_new: bool | None = True


class DisplayDirectChatSchema(BaseModel):
    guid: UUID7
    chat_type: ChatType
    created: datetime
    updated: datetime | None = None
    users: list[UserSchema]

    class Config:
        from_attributes = True


class GetDirectChatSchema(BaseModel):
    chat_guid: UUID7
    chat_type: ChatType
    created: datetime
    updated: datetime | None = None
    users: list[UserSchema]
    new_messages_count: int

    class Config:
        from_attributes = True


class GetDirectChatsSchema(BaseModel):
    chats: list[GetDirectChatSchema]
    total_unread_messages_count: int


class LastReadMessageSchema(BaseModel):
    guid: UUID7
    content: str
    created: datetime


class GetMessageSchema(BaseModel):
    message_guid: UUID7
    user_guid: UUID7
    profile_pic: str | None = None
    name: str
    username: str
    chat_guid: UUID7
    content: str
    created: datetime
    is_read: bool | None = False


class GetMessagesSchema(BaseModel):
    messages: list[GetMessageSchema]
    has_more_messages: bool
    last_read_message: LastReadMessageSchema = None


class GetOldMessagesSchema(BaseModel):
    messages: list[GetMessageSchema]
    has_more_messages: bool
