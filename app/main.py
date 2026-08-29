import uuid
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.config import settings
from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Campaign Management API",
    description="A production-oriented FastAPI system for marketing campaign lifecycle state machine, task coordination, and audit trails.",
    version="1.0.0"
)

origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
def add_request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    response = call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

app.include_router(api_v1_router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", "N/A")
    logger.error(f"[{req_id}] Exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error.", "request_id": req_id}
    )

@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health Check"])
def health_check():
    return {"status": "healthy"}
