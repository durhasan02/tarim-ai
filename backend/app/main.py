from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import auth as auth_router
from app.api.v1 import fields as fields_router
from app.api.v1 import plantings as plantings_router
from app.api.v1 import stock as stock_router
from app.api.v1 import harvests as harvests_router
from app.api.v1 import dashboard as dashboard_router
from app.api.v1 import ai as ai_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Başlangıç
    yield
    # Kapanış


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'lar
app.include_router(auth_router.router, prefix="/api/v1")

app.include_router(fields_router.router, prefix="/api/v1")
app.include_router(plantings_router.router, prefix="/api/v1")
app.include_router(stock_router.router, prefix="/api/v1")
app.include_router(harvests_router.router, prefix="/api/v1")
app.include_router(dashboard_router.router, prefix="/api/v1")
app.include_router(ai_router.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME}
