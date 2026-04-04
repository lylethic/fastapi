import asyncio
import logging
from json.decoder import JSONDecodeError

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi_limiter.depends import WebSocketRateLimiter
from jose import JWTError, jwt
from pyrate_limiter import Duration, InMemoryBucket, Limiter, Rate
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ALGORITHM, JWT_SECRET_KEY
from app.db.session import get_db
from app.dependencies import get_cache, get_cache_setting
from app.db.models import Users as User
from app.services.websocket.exceptions import WebsocketTooManyRequests
from app.services.websocket.handlers import socket_manager
from app.services.websocket.rate_limiter import websocket_callback
from app.services.websocket.services import (
    check_user_statuses,
    get_user_active_direct_chats,
    mark_user_as_offline,
    mark_user_as_online,
)

logger = logging.getLogger(__name__)


websocket_router = APIRouter()
ws_rate_limiter = WebSocketRateLimiter(
    limiter=Limiter(InMemoryBucket([Rate(50, 10 * Duration.SECOND)])),
    callback=websocket_callback,
    blocking=False,
)


async def get_current_ws_user(
    websocket: WebSocket,
    db_session: AsyncSession,
) -> User:
    authorization = websocket.headers.get("Authorization")
    if not authorization and (token := websocket.query_params.get("token")):
        authorization = f"Bearer {token}"
    if not authorization:
        await websocket.close(code=1008, reason="Missing authorization header")
        raise WebSocketDisconnect()

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        await websocket.close(code=1008, reason="Invalid authorization header")
        raise WebSocketDisconnect()

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        await websocket.close(code=1008, reason="Invalid token or token expired")
        raise WebSocketDisconnect()

    user_id = payload.get("id")
    if not user_id:
        await websocket.close(code=1008, reason="Invalid token payload")
        raise WebSocketDisconnect()

    result = await db_session.execute(
        select(User).where(
            and_(User.id == user_id, User.active == True, User.deleted == False)
        )
    )
    current_user = result.scalar_one_or_none()
    if current_user is None:
        await websocket.close(code=1008, reason="User not found")
        raise WebSocketDisconnect()

    return current_user


@websocket_router.websocket("/ws/")
async def websocket_endpoint(
    websocket: WebSocket,
    db_session: AsyncSession = Depends(get_db),
    cache: aioredis.Redis = Depends(get_cache),
    cache_enabled: bool = Depends(get_cache_setting),
):
    current_user = await get_current_ws_user(websocket=websocket, db_session=db_session)
    await socket_manager.connect_socket(websocket=websocket)
    logger.info("Websocket connection is established")

    # add user's socket connection {user_guid: {ws1, ws2}}
    await socket_manager.add_user_socket_connection(str(current_user.guid), websocket)

    # Update the user's status in Redis with a new TTL
    await mark_user_as_online(cache=cache, current_user=current_user)
    # get all users direct chats and subscribe to each
    # guid/id key-value pair to easily get chat_id based on chat_guid later
    if chats := await get_user_active_direct_chats(
        db_session, current_user=current_user
    ):
        # subscribe this websocket instance to all Redis PubSub channels
        for chat_guid in chats:
            await socket_manager.add_user_to_chat(chat_guid, websocket)
    else:
        chats = dict()

    # task for sending status messages, not dependent on cache_enabled
    user_status_task = asyncio.create_task(
        check_user_statuses(cache, socket_manager, current_user, chats)
    )

    try:
        while True:
            try:
                incoming_message = await websocket.receive_json()
                await ws_rate_limiter(websocket)

                message_type = incoming_message.get("type")
                if not message_type:
                    await socket_manager.send_error(
                        "You should provide message type", websocket
                    )
                    continue

                handler = socket_manager.handlers.get(message_type)

                if not handler:
                    logger.error(f"No handler [{message_type}] exists")
                    await socket_manager.send_error(
                        f"Type: {message_type} was not found", websocket
                    )
                    continue

                await handler(
                    websocket=websocket,
                    db_session=db_session,
                    cache=cache,
                    incoming_message=incoming_message,
                    chats=chats,
                    current_user=current_user,
                    cache_enabled=cache_enabled,
                )

            except (JSONDecodeError, AttributeError) as excinfo:
                logger.exception(f"Websocket error, detail: {excinfo}")
                await socket_manager.send_error("Wrong message format", websocket)
                continue
            except ValueError as excinfo:
                logger.exception(f"Websocket error, detail: {excinfo}")
                await socket_manager.send_error(
                    "Could not validate incoming message", websocket
                )

            except WebsocketTooManyRequests:
                logger.exception(f"User: {current_user} sent too many ws requests")
                await socket_manager.send_error(
                    "You have sent too many requests", websocket
                )

    except WebSocketDisconnect:
        logging.info("Websocket is disconnected")
        # unsubscribe user websocket connection from all chats
        if chats:
            for chat_guid in chats:
                await socket_manager.remove_user_from_chat(chat_guid, websocket)
                await mark_user_as_offline(
                    cache=cache,
                    socket_manager=socket_manager,
                    current_user=current_user,
                    chat_guid=chat_guid,
                )
            await socket_manager.pubsub_client.disconnect()

        user_status_task.cancel()
        await socket_manager.remove_user_guid_to_websocket(
            user_guid=str(current_user.guid), websocket=websocket
        )
