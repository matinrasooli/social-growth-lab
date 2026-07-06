from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import Base, engine
from app import models  # noqa: F401 - ensures all models are registered on Base
from app.api import (
    routes_auth, routes_dashboard, routes_uploads, routes_insights,
    routes_content, routes_experiments, routes_comments, routes_competitors,
    routes_simulation, routes_compliance,
)

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "A local-first, compliant Instagram content-strategy and analytics tool. "
        "This system never automates real Instagram activity, never scrapes, and "
        "never fabricates engagement. See /docs for the full API and the README "
        "for compliance philosophy."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # For local/dev use. Production deployments should use Alembic migrations instead.
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}


app.include_router(routes_auth.router)
app.include_router(routes_dashboard.router)
app.include_router(routes_uploads.router)
app.include_router(routes_insights.router)
app.include_router(routes_content.router)
app.include_router(routes_experiments.router)
app.include_router(routes_comments.router)
app.include_router(routes_competitors.router)
app.include_router(routes_simulation.router)
app.include_router(routes_compliance.router)
