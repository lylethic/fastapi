from typing import Optional

from pydantic import BaseModel

from app.db.models import MessageMessageType
from app.schemas.base_schema import BaseLogEntity, BaseModelPagination


class MessageCreateBody(BaseModel):
    message_type: MessageMessageType = MessageMessageType.TEXT
    content: str
    user_id: str
    chat_id: str
    file_name: Optional[str] = None
    file_path: Optional[str] = None


class MessageUpdateBody(BaseModel):
    message_type: Optional[MessageMessageType] = None
    content: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    active: Optional[bool] = 1


class MessageResponse(BaseLogEntity):
    id: str
    guid: str
    message_type: MessageMessageType
    content: str
    user_id: str
    chat_id: str
    file_name: Optional[str] = None
    file_path: Optional[str] = None

    model_config = {"from_attributes": True}


class MessagePagination(BaseModelPagination[MessageResponse]):
    pass
