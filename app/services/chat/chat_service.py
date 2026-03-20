from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, HTMLResponse

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Real-Time Chat</title>
</head>
<body>
    <div id="chat-container">
        <ul id="messages"></ul>
        <input type="text" id="message-input">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        var ws = new WebSocket("ws://localhost:8000/ws");

        ws.onopen = function() {
            console.log("Connected to the server");
        };

        ws.onmessage = function(event) {
            var messages = document.getElementById('messages');
            var message = document.createElement('li');
            message.textContent = event.data;
            messages.appendChild(message);
        };

        ws.onclose = function() {
            console.log("Disconnected from the server");
        };

        function sendMessage() {
            var messageInput = document.getElementById('message-input');
            var message = messageInput.value;
            ws.send(message);
            messageInput.value = '';
        }
    </script>
</body>
</html>
"""


def chatTest():
    return HTMLResponse(html)
