import asyncio

from app.db.session import init_models


asyncio.run(init_models())
