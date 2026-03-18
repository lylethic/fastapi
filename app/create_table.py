from app.db import models
from app.db.session import engine


models.Base.metadata.create_all(bind=engine)
