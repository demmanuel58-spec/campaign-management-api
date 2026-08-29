from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.dependencies import RoleChecker
from app.services import crud_service

router = APIRouter(prefix="/clients", tags=["Clients"])
allow_manager_or_admin = RoleChecker([models.UserRole.ADMIN, models.UserRole.MANAGER])

@router.post("", response_model=schemas.ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db), _: models.User = Depends(allow_manager_or_admin)):
    return crud_service.create_client(db=db, client=client)

@router.get("", response_model=schemas.PaginatedResponse[schemas.ClientResponse])
def read_clients(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: models.User = Depends(RoleChecker([models.UserRole.ADMIN, models.UserRole.MANAGER, models.UserRole.VIEWER]))
):
    return crud_service.get_clients_paginated(db=db, page=page, limit=limit)
