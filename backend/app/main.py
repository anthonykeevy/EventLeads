from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.settings import settings
from .routers import (
    auth,
    events,
    invitations,
    organizations,
    canvas,
    leads,
    invoices,
    billing,
    audit,
    forms,
    verification,
    metering,
    pricing,
    admin,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    title="Event Form Builder API",
    description="API for the Event Form Builder platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "ok"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    # In a fuller app, check DB connectivity etc.
    return {"ready": True}


# Routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(invitations.router)
app.include_router(organizations.router)
app.include_router(forms.router)
app.include_router(canvas.router)
app.include_router(leads.router)
app.include_router(invoices.router)
app.include_router(billing.router)
app.include_router(audit.router)
app.include_router(verification.router)
app.include_router(metering.router)
app.include_router(pricing.router)
app.include_router(admin.router)
