# FastAPI Realtime Chat API

This project is a FastAPI backend focused on two main areas:

- User, role, and permission management for API access control
- Realtime direct chat between users via WebSocket and Redis Pub/Sub

The application provides both REST APIs and a WebSocket API, along with a browser-based test page for manual realtime chat testing.

## Project Overview

The system includes the following main modules:

- `Auth`: user registration and login with JWT
- `Users`: user management, profile retrieval, and image upload
- `Roles / Permissions`: role and permission assignment
- `Chat`: direct chat creation, chat listing, and message history
- `Messages`: message CRUD over HTTP
- `WebSocket`: realtime messaging, typing indicators, read status, and new chat synchronization

The current realtime chat flow works like this:

1. The client logs in and gets a JWT
2. The client connects to `/api/v1/ws/?token=...`
3. The server validates the JWT for the websocket connection
4. The websocket subscribes to the user’s existing chat rooms
5. When a new message is sent, the server stores it in the database and publishes it through Redis Pub/Sub
6. All websockets in the same chat receive the payload and update the UI in realtime

In addition to Swagger, the project includes a test page at `/chat-test` for login, websocket connection, direct chat creation, and realtime message testing.

## Tech Stack

- `Python`
- `FastAPI`
- `Uvicorn`
- `SQLAlchemy Async`
- `MySQL`
- `Redis`
- `WebSocket`
- `Pydantic`
- `JWT`
- `Docker Compose` for Redis

Declared packages in [requirements.txt](/mnt/d/fastapi-tu/fastapi/requirements.txt):

- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `pymysql`
- `sqlacodegen`
- `cryptography`
- `python-multipart`
- `passlib[bcrypt]`
- `pyjwt`
- `python-dotenv`
- `websockets`
- `argon2-cffi`
- `redis`
- `fastapi-limiter`

Practical note:

- The code in [app/db/session.py](/mnt/d/fastapi-tu/fastapi/app/db/session.py) uses the `mysql+asyncmy` driver
- If your environment does not already have `asyncmy`, install it with `pip install asyncmy`

## Main Features

- JWT-based registration and login
- HTTP authentication middleware
- Role- and permission-based access control
- User, role, permission, role-permission, and user-role management
- Direct chat creation between two users
- Chat list and message history retrieval
- Realtime messaging over websocket
- Typing indicator over websocket
- Read receipts over websocket
- Online/offline/inactive user status synchronization with Redis
- Partial Redis caching for chat and message data
- Realtime chat test page at `/chat-test`

## Project Structure

```text
app/
├── api/
│   ├── response.py
│   ├── router.py
│   └── v1/
│       ├── auth.py
│       ├── chat.py
│       ├── merchant_profile.py
│       ├── message.py
│       ├── permission.py
│       ├── role.py
│       ├── role_permission.py
│       ├── user.py
│       └── user_role.py
├── cache_utils.py
├── config.py
├── constants/
│   └── permissions.py
├── core/
│   └── config.py
├── db/
│   ├── models.py
│   └── session.py
├── dependencies.py
├── main.py
├── managers/
│   ├── pubsub_manager.py
│   └── websocket_manager.py
├── middlewares/
│   ├── auth.py
│   └── global_logging.py
├── providers/
│   └── baseProvider.py
├── repositories/
│   ├── base_repository.py
│   └── role_repository.py
├── schemas/
│   ├── base_schema.py
│   ├── chat.py
│   ├── message.py
│   ├── merchant_profile.py
│   ├── permission.py
│   ├── role.py
│   ├── rolepermission.py
│   ├── user.py
│   └── user_role.py
├── services/
│   ├── assistant_service.py
│   ├── affiliate_profile_service.py
│   ├── auth_service.py
│   ├── chat/
│   │   └── chat_service.py
│   ├── merchant_profile_service.py
│   ├── message_service.py
│   ├── permission_service.py
│   ├── role_permission_service.py
│   ├── role_service.py
│   ├── user_role_service.py
│   ├── user_service.py
│   └── websocket/
│       ├── exceptions.py
│       ├── handlers.py
│       ├── rate_limiter.py
│       ├── router.py
│       ├── schemas.py
│       └── services.py
├── static/
│   ├── chat-test.css
│   ├── chat-test.html
│   └── chat-test.js
├── utils/
│   └── cache.py
└── utils.py
```

## Directory Responsibilities

### `app/main.py`

Application entry point.

- Creates the FastAPI app
- Mounts static files and uploads
- Registers the `/api/v1` router
- Initializes DB and Redis connections during startup
- Exposes the `/chat-test` page

### `app/api`

Defines REST endpoints by domain:

- `auth.py`: register, login
- `user.py`: user CRUD, profile, image upload
- `chat.py`: direct chat creation, chat listing, message history
- `message.py`: message CRUD over HTTP
- `role.py`, `permission.py`, `role_permission.py`, `user_role.py`: RBAC

### `app/services`

Service layer.

- Contains business logic, validation, data mapping, and orchestration across repositories
- Keeps router/controller code thin
- Calls repositories for persistence and querying
- Example: `role_service.py` validates duplicate role names and normalizes input before saving

### `app/repositories`

Repository layer.

- Contains database access and persistence logic
- Encapsulates SQLAlchemy queries and reusable CRUD operations
- `base_repository.py` provides generic CRUD helpers
- `role_repository.py` is the first module migrated to the repository layer

### `app/providers`

Legacy base data-access abstraction used by older services that have not been migrated yet.

- `baseProvider.py` still supports several existing modules
- New refactors should prefer `repositories` over adding more logic to `providers`

### `app/db`

Infrastructure and ORM mapping layer.

- `session.py`: async engine, session factory, Redis pool
- `models.py`: ORM models for users, chats, messages, read status, roles, and permissions

### `app/services/websocket`

Contains the realtime messaging flow.

- `router.py`: websocket endpoint `/api/v1/ws/`
- `handlers.py`: handlers for message types such as `new_message`, `message_read`, and `user_typing`
- `services.py`: realtime-related business logic
- `schemas.py`: websocket payload schemas
- `rate_limiter.py`: websocket rate limiting

### `app/managers`

Connection management for realtime messaging.

- `websocket_manager.py`: connection, room, and broadcast management
- `pubsub_manager.py`: Redis publish/subscribe integration

### `app/middlewares`

- `auth.py`: reads JWT from HTTP headers and attaches user information to request state
- `global_logging.py`: global request logging

### `app/static`

Manual frontend test tools for realtime chat.

- login
- load profile
- load chats
- connect websocket
- send realtime messages
- send typing events
- mark messages as read

## High-Level Architecture

```text
Client
  ├─ HTTP REST API
  │   ├─ /api/v1/auth/*
  │   ├─ /api/v1/users/*
  │   ├─ /api/v1/chat/*
  │   └─ /api/v1/messages/*
  └─ WebSocket
      └─ /api/v1/ws/

FastAPI App
  ├─ Routers
  ├─ Services (business logic, validation, orchestration)
  ├─ Repositories (query and persistence)
  ├─ SQLAlchemy Async / ORM Models
  ├─ WebSocket Handlers
  └─ Redis Pub/Sub

Infrastructure
  ├─ MySQL
  └─ Redis
```

### Request Flow by Layer

The project is being organized around a layered architecture:

1. `API layer` (`app/api`): receives HTTP requests, resolves dependencies, and returns response schemas.
2. `Service layer` (`app/services`): contains business rules, validation, data transformation, and cross-module orchestration.
3. `Repository layer` (`app/repositories`): performs database reads/writes and owns persistence logic.
4. `Database layer` (`app/db`): defines SQLAlchemy models, sessions, and infrastructure wiring.

Current migration status:

- `role` already follows the new flow: `API -> Service -> Repository -> DB`
- Some older modules still use `BaseProvider` directly inside services
- The codebase is in a transition phase, so both patterns currently exist

## Environment Requirements

- Python 3.11+ is recommended
- MySQL
- Redis
- Docker and Docker Compose if you want to run Redis in a container

## Installation

### 1. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
pip install asyncmy
```

### 3. Configure `.env`

Create a `.env` file at the project root:

```env
APP_HOST=127.0.0.1
APP_PORT=8000
UPLOAD_DIR=uploads

JWT_SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

MYSQL_USER=root
MYSQL_PASSWORD=111111
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=fastapi

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_CACHE_EXPIRATION_SECONDS=300
CACHE_ENABLED=true
```

These variables are loaded in [app/config.py](/mnt/d/fastapi-tu/fastapi/app/config.py).

### 4. Run Redis

The project includes [docker-compose.yml](/mnt/d/fastapi-tu/fastapi/docker-compose.yml) for Redis:

```bash
docker compose up -d redis
```

### 5. Start the server

```bash
python -m app.main
```

Default server address:

```text
http://127.0.0.1:8000
```

## Usage

### Swagger

After starting the app:

```text
http://127.0.0.1:8000/docs
```

### Base API prefix

```text
/api/v1
```

### Realtime chat test page

Open:

```text
http://127.0.0.1:8000/chat-test
```

Quick test flow:

1. Log in with email and password
2. Click `Load Me`
3. Create a direct chat or `Refresh` the chat list
4. Click `Connect WS`
5. Select a chat
6. Send a realtime message

Actual websocket endpoint used for chat:

```text
ws://127.0.0.1:8000/api/v1/ws/?token=<JWT>
```

## Representative Endpoints

### Auth

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

### Users

- `GET /api/v1/users`
- `GET /api/v1/users/me`
- `GET /api/v1/users/{id}`
- `POST /api/v1/users`
- `PUT /api/v1/users/{id}`
- `DELETE /api/v1/users/{id}`
- `POST /api/v1/users/{id}/upload`

### Chat

- `POST /api/v1/chat/direct`
- `GET /api/v1/chat/chats/direct`
- `GET /api/v1/chat/{chat_guid}/messages`
- `GET /api/v1/chat/{chat_guid}/messages/old/{message_guid}`
- `DELETE /api/v1/chat/chats/direct/{chat_guid}`

### Messages

- `POST /api/v1/messages`
- `GET /api/v1/messages`
- `GET /api/v1/messages/chat/{chat_id}`
- `GET /api/v1/messages/{id}`
- `PUT /api/v1/messages/{id}`
- `DELETE /api/v1/messages/{id}`

### WebSocket message types

Sent by the client:

- `new_message`
- `message_read`
- `user_typing`

Broadcast by the server:

- `new`
- `message_read`
- `user_typing`
- `new_chat_created`
- `chat_deleted`
- `status`

## Example WebSocket Payloads

### Send a new message

```json
{
  "type": "new_message",
  "chat_guid": "6086d625-3b41-428c-ba1b-b381a611f2c3",
  "user_guid": "f9eaf4f1-d742-4a76-952e-6073757639f0",
  "content": "Hello"
}
```

### Send a typing event

```json
{
  "type": "user_typing",
  "chat_guid": "6086d625-3b41-428c-ba1b-b381a611f2c3",
  "user_guid": "f9eaf4f1-d742-4a76-952e-6073757639f0"
}
```

### Mark the last message as read

```json
{
  "type": "message_read",
  "chat_guid": "6086d625-3b41-428c-ba1b-b381a611f2c3",
  "message_guid": "96fc0dfb-9b4b-4d1b-b66f-6feb0b7d84ca"
}
```

## Common Response Format

HTTP endpoints use a unified response format defined in [app/api/response.py](/mnt/d/fastapi-tu/fastapi/app/api/response.py):

```json
{
  "is_success": true,
  "status_code": 200,
  "data": {},
  "message": "Success",
  "message_en": "Success"
}
```

Notes:

- Some business errors may still return HTTP status `200`, while `is_success` is `false`
- Global exception handling is configured in [app/main.py](/mnt/d/fastapi-tu/fastapi/app/main.py)

## Authorization Model

The project uses RBAC:

- A user can have multiple roles
- A role can have multiple permissions
- Some APIs require permissions such as `SYS_ADMIN`, `WRITE`, `EDIT`, and `DELETE`

Relevant logic lives in:

- [app/services/assistant_service.py](/mnt/d/fastapi-tu/fastapi/app/services/assistant_service.py)
- [app/constants/permissions.py](/mnt/d/fastapi-tu/fastapi/app/constants/permissions.py)

## Files and Uploads

- Uploaded files are stored in the `uploads/` directory
- That directory is exposed through the `/uploads` route

## Redis Usage

Redis is used for:

- Chat and message caching
- Pub/Sub for websocket broadcasting
- Online/offline user status tracking

## Suggested Improvements

- Add automated tests for REST APIs and WebSocket flows
- Split configuration by environment such as `dev`, `staging`, and `prod`
- Add database migrations with Alembic
- Add a Dockerfile for the backend service
- Align `requirements.txt` with the actual runtime dependencies

## Useful Commands

Run the app:

```bash
python -m app.main
```

Run Redis:

```bash
docker compose up -d redis
```

Regenerate models from MySQL:

```bash
sqlacodegen "mysql+pymysql://root:111111@0.0.0.0:3306/fastapi" > app/db/models.py
```

After regenerating models, make sure [app/db/models.py](/mnt/d/fastapi-tu/fastapi/app/db/models.py) still uses the shared project `Base`.
