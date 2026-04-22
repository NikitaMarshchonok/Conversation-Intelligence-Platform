from fastapi import APIRouter

from app.api.routes.ask import router as ask_router
from app.api.routes.ask_runs import router as ask_runs_router
from app.api.routes.documents import router as documents_router
from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.projects import router as projects_router
from app.api.routes.search import router as search_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(projects_router)
api_router.include_router(documents_router)
api_router.include_router(search_router)
api_router.include_router(ask_router)
api_router.include_router(ask_runs_router)
api_router.include_router(metrics_router)
