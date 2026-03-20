from fastapi import APIRouter, Depends, Query, status

from app.services.chat.chat_service import chatTest


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("")
def getChat():
    return chatTest()
