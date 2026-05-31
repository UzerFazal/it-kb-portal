from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.database import init_db
import markupsafe

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="IT Knowledge Base", lifespan=lifespan)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except Exception:
    pass

# Include routers AFTER app is created
from app.routes import user, auth, admin
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(admin.router)
