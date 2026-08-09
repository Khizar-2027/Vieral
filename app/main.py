from fastapi import FastAPI, Depends
from app.core.database import Base, engine
from app import models  # noqa
from app.core.deps import get_current_user

from app.models.user import User
from app.routers import auth, projects
from app.routers import auth, projects, videos

import os
from app.core.config import settings

os.makedirs(settings.storage_dir, exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vieral API")

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(videos.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}