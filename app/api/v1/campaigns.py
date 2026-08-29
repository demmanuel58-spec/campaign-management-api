from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.dependencies import RoleChecker, get_current_user
from app.services import crud_service

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

@router.post("", response_model=schemas.CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(campaign: schemas.CampaignCreate, db: Session = Depends(get_db), current_user: models.User = Depends(RoleChecker([models.UserRole.ADMIN, models.UserRole.MANAGER]))):
    client = db.query(models.Client).filter(models.Client.id == campaign.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return crud_service.create_campaign(db=db, campaign=campaign, user_id=current_user.id)

@router.get("", response_model=schemas.PaginatedResponse[schemas.CampaignResponse])
def read_campaigns(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, description="Search term for campaign name or description"),
    status_filter: models.CampaignStatus | None = Query(None, alias="status", description="Filter by campaign status"),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user)
):
    return crud_service.get_campaigns_paginated(db=db, page=page, limit=limit, search=search, status_filter=status_filter)

@router.patch("/{campaign_id}", response_model=schemas.CampaignResponse)
def update_campaign_details(campaign_id: int, campaign_update: schemas.CampaignUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(RoleChecker([models.UserRole.ADMIN, models.UserRole.MANAGER]))):
    updated = crud_service.update_campaign_details(db=db, campaign_id=campaign_id, campaign_update=campaign_update, user_id=current_user.id, user_role=current_user.role)
    if not updated:
        raise HTTPException(status_code=404, detail="Campaign not found or deleted")
    return updated

@router.patch("/{campaign_id}/status", response_model=schemas.CampaignResponse)
def update_campaign_status(campaign_id: int, status_update: schemas.CampaignStatusUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(RoleChecker([models.UserRole.ADMIN, models.UserRole.MANAGER]))):
    updated = crud_service.update_campaign_status(db=db, campaign_id=campaign_id, status_enum=status_update.status, user_id=current_user.id, user_role=current_user.role)
    if not updated:
        raise HTTPException(status_code=404, detail="Campaign not found or deleted")
    return updated

@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(campaign_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(RoleChecker([models.UserRole.ADMIN, models.UserRole.MANAGER]))):
    if not crud_service.delete_campaign_soft(db=db, campaign_id=campaign_id, user_id=current_user.id, user_role=current_user.role):
        raise HTTPException(status_code=404, detail="Campaign not found")
    return None
