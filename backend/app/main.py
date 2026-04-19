from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Conversation Intelligence Platform API",
    version="0.1.0",
)
app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "conversation-intelligence-platform",
        "environment": settings.app_env,
    }
