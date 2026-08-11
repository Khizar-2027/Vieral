from fastapi import FastAPI, Depends
from app.core.database import Base, engine
from app import models  # noqa
from app.core.deps import get_current_user

from app.models.user import User
from app.routers import auth, projects
from app.routers import auth, projects, videos

import os
from app.core.config import settings

from fastapi.middleware.cors import CORSMiddleware

os.makedirs(settings.storage_dir, exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vieral API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(videos.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}