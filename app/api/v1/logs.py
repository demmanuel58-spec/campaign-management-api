from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.dependencies import RoleChecker
from app.services import crud_service

router = APIRouter(prefix="/activity-logs", tags=["Activity Audit Logs"])

@router.get("", response_model=schemas.PaginatedResponse[schemas.ActivityLogResponse])
def read_activity_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: models.User = Depends(RoleChecker([models.UserRole.ADMIN]))
):
    return crud_service.get_activity_logs_paginated(db=db, page=page, limit=limit)
