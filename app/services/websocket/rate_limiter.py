from app.services.websocket.exceptions import WebsocketTooManyRequests


async def websocket_callback(ws):
    raise WebsocketTooManyRequests("Too many requests")
