# FastAPI Project

## Run The Project

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

You can also keep app settings in a project-level `.env` file:

```env
APP_HOST=127.0.0.1
APP_PORT=8000
UPLOAD_DIR=uploads
JWT_SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Run with a custom host/port:

Windows:

```bash
set APP_HOST=0.0.0.0
set APP_PORT=9000
python -m app.main
```

Linux/macOS:

```bash
APP_HOST=0.0.0.0 APP_PORT=9000 python -m app.main
```

Base API prefix:

```text
/api/v1
```

## Project Structure

This project is organized into three main layers:

- `api`: route declarations, versioning, and API response formatting
- `services`: business logic
- `db`: database connection and ORM models

Current structure:

```text
app/
├── api/
│   ├── v1/
│   │   ├── __init__.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── permission.py
│   ├── __init__.py
│   └── response.py
├── db/
│   ├── __init__.py
│   ├── models.py
│   └── session.py
├── schemas/
│   ├── __init__.py
│   ├── base_schema.py
│   └── permission.py
├── services/
│   ├── __init__.py
│   └── permission_service.py
├── __init__.py
├── create_table.py
└── main.py
```

## Folder Responsibilities

### `app/main.py`

Application entry point.

- Creates the FastAPI app
- Registers versioned routers
- Runs startup and shutdown logic

### `app/api/`

HTTP layer.

- Defines shared API response models
- Organizes versioned API modules

### `app/api/v1/`

Version 1 of the public API.

- Registers routers under the `/api/v1` prefix
- Keeps version-specific API behavior isolated from future versions

### `app/api/v1/routers/permission.py`

Permission endpoints.

- Declares `/api/v1/permissions` routes
- Connects request schemas to service functions
- Adds Swagger/OpenAPI metadata such as `summary`, `description`, and `tags`

### `app/schemas/`

Pydantic schemas used for request and response validation.

- `base_schema.py`: shared base schemas such as log fields and pagination
- `permission.py`: permission request/response schemas

### `app/services/`

Business logic layer.

- Handles permission creation, listing, and update logic
- Manages transaction-related behavior with SQLAlchemy
- Keeps route handlers thin and focused

### `app/db/`

Database layer.

- `session.py`: database URL, engine, session factory, and `get_db()`
- `models.py`: SQLAlchemy ORM models

## Common API Response

All endpoints can use a shared response format like this:

```json
{
  "isSuccess": true,
  "statusCode": 200,
  "data": {},
  "message": "Success",
  "messageEn": "Success"
}
```

This format is defined in [app/api/response.py](/mnt/d/fastapi-tu/fastapi/app/api/response.py).

## Versioned Endpoints

Examples:

- `POST /api/v1/permissions`
- `GET /api/v1/permissions`
- `GET /api/v1/permissions/{id}`
- `PUT /api/v1/permissions/{id}`

## Generate ORM Models From MySQL

Generate models into `app/db/models.py`:

```bash
sqlacodegen "mysql+pymysql://root:111111@localhost:3306/fastapi" > app/db/models.py
```

After generating, update the top of `app/db/models.py` so it uses the shared `Base` from `app.db.session`:

```python
from app.db.session import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
```

If `sqlacodegen` creates its own `Base`, remove that block so all models use the same metadata object.
