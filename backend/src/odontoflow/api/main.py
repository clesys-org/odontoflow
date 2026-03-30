"""FastAPI application — ponto de entrada do OdontoFlow."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncIterator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from odontoflow.api.routers import analytics as analytics_router
from odontoflow.api.routers import auth as auth_router
from odontoflow.api.routers import billing as billing_router
from odontoflow.api.routers import clinical as clinical_router
from odontoflow.api.routers import insurance as insurance_router
from odontoflow.api.routers import inventory as inventory_router
from odontoflow.api.routers import patient as patient_router
from odontoflow.api.routers import scheduling as scheduling_router
from odontoflow.api.routers import staff as staff_router
from odontoflow.api.routers import treatment as treatment_router
from odontoflow.shared.event_bus import EventBus

load_dotenv()

VERSION = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup e shutdown da aplicacao."""
    app.state.event_bus = EventBus()
    yield


app = FastAPI(
    title="OdontoFlow API",
    description="Sistema integrado de gestao odontologica",
    version=VERSION,
    lifespan=lifespan,
)

# CORS
_default_origins = "http://localhost:3000"
_origins = os.getenv("ALLOWED_ORIGINS", _default_origins).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router.router)
app.include_router(patient_router.router)
app.include_router(patient_router.cep_router)
app.include_router(clinical_router.router)
app.include_router(scheduling_router.router)
app.include_router(treatment_router.router)
app.include_router(billing_router.router)
app.include_router(insurance_router.router)
app.include_router(inventory_router.router)
app.include_router(staff_router.router)
app.include_router(analytics_router.router)


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "odontoflow",
        "version": VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
