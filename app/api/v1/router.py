from fastapi import APIRouter
from app.api.v1 import auth, clients, campaigns, tasks, logs

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth.router)
api_v1_router.include_router(clients.router)
api_v1_router.include_router(campaigns.router)
api_v1_router.include_router(tasks.router)
api_v1_router.include_router(logs.router)
