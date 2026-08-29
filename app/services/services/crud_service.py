from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app import models, schemas, security
import logging

logger = logging.getLogger(__name__)

def create_user(db: Session, user: schemas.UserCreate):
    hashed_pwd = security.get_password_hash(user.password)
    # Role hardcoded to MANAGER to prevent role escalation on public registration
    db_user = models.User(email=user.email, hashed_password=hashed_pwd, role=models.UserRole.MANAGER)
    db.add(db_user)
    try:
        db.flush()
        log = models.ActivityLog(user_id=db_user.id, action=f"User registered as {models.UserRole.MANAGER.value}")
        db.add(log)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User registered: {db_user.email}")
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

def create_client(db: Session, client: schemas.ClientCreate):
    db_client = models.Client(name=client.name)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def get_clients_paginated(db: Session, page: int, limit: int):
    skip = (page - 1) * limit
    total = db.query(models.Client).count()
    items = db.query(models.Client).offset(skip).limit(limit).all()
    return schemas.PaginatedResponse(total=total, page=page, limit=limit, items=items)

def create_campaign(db: Session, campaign: schemas.CampaignCreate, user_id: int):
    db_campaign = models.Campaign(**campaign.model_dump(), created_by=user_id)
    db.add(db_campaign)
    db.flush()
    
    log = models.ActivityLog(user_id=user_id, action=f"Created campaign '{db_campaign.name}'", campaign_id=db_campaign.id)
    db.add(log)
    
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def get_campaigns_paginated(db: Session, page: int, limit: int, search: str | None = None, status_filter: models.CampaignStatus | None = None):
    skip = (page - 1) * limit
    query = db.query(models.Campaign).filter(models.Campaign.is_deleted == False)

    if status_filter:
        query = query.filter(models.Campaign.status == status_filter)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                models.Campaign.name.ilike(search_pattern),
                models.Campaign.description.ilike(search_pattern)
            )
        )

    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return schemas.PaginatedResponse(total=total, page=page, limit=limit, items=items)

def update_campaign_details(db: Session, campaign_id: int, campaign_update: schemas.CampaignUpdate, user_id: int, user_role: models.UserRole):
    db_campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id, models.Campaign.is_deleted == False).first()
    if not db_campaign:
        return None
    if user_role != models.UserRole.ADMIN and db_campaign.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this campaign")

    update_data = campaign_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_campaign, key, value)

    log = models.ActivityLog(user_id=user_id, action=f"Updated details for campaign '{db_campaign.name}'", campaign_id=campaign_id)
    db.add(log)

    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def update_campaign_status(db: Session, campaign_id: int, status_enum: models.CampaignStatus, user_id: int, user_role: models.UserRole):
    db_campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id, models.Campaign.is_deleted == False).first()
    if not db_campaign:
        return None
    if user_role != models.UserRole.ADMIN and db_campaign.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this campaign")
    
    old_status = db_campaign.status
    db_campaign.status = status_enum
    
    log = models.ActivityLog(user_id=user_id, action=f"Changed campaign status from {old_status} to {status_enum}", campaign_id=campaign_id)
    db.add(log)
    
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def delete_campaign_soft(db: Session, campaign_id: int, user_id: int, user_role: models.UserRole):
    db_campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id, models.Campaign.is_deleted == False).first()
    if not db_campaign:
        return False
    if user_role != models.UserRole.ADMIN and db_campaign.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this campaign")
    
    db_campaign.is_deleted = True
    
    log = models.ActivityLog(user_id=user_id, action=f"Soft deleted campaign #{campaign_id}", campaign_id=campaign_id)
    db.add(log)
    
    db.commit()
    return True

def create_task(db: Session, task: schemas.TaskCreate, user_id: int, user_role: models.UserRole):
    campaign = db.query(models.Campaign).filter(models.Campaign.id == task.campaign_id, models.Campaign.is_deleted == False).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    if user_role != models.UserRole.ADMIN and campaign.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add tasks to this campaign")

    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.flush()
    
    log = models.ActivityLog(user_id=user_id, action=f"Created task '{db_task.title}'", campaign_id=db_task.campaign_id)
    db.add(log)
    
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks_by_campaign(db: Session, campaign_id: int):
    return db.query(models.Task).filter(models.Task.campaign_id == campaign_id).all()

def update_task_status(db: Session, task_id: int, status_enum: models.TaskStatus, user_id: int, user_role: models.UserRole):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return None
    
    campaign = db.query(models.Campaign).filter(models.Campaign.id == db_task.campaign_id).first()
    if user_role != models.UserRole.ADMIN and campaign.created_by != user_id and db_task.assigned_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this task")

    db_task.status = status_enum
    log = models.ActivityLog(user_id=user_id, action=f"Updated task #{task_id} status to {status_enum}", campaign_id=db_task.campaign_id)
    db.add(log)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int, user_id: int, user_role: models.UserRole):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return False
    
    campaign = db.query(models.Campaign).filter(models.Campaign.id == db_task.campaign_id).first()
    if user_role != models.UserRole.ADMIN and campaign.created_by != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this task")

    campaign_id = db_task.campaign_id
    db.delete(db_task)
    log = models.ActivityLog(user_id=user_id, action=f"Deleted task #{task_id}", campaign_id=campaign_id)
    db.add(log)
    db.commit()
    return True

def get_activity_logs_paginated(db: Session, page: int, limit: int):
    skip = (page - 1) * limit
    total = db.query(models.ActivityLog).count()
    items = db.query(models.ActivityLog).order_by(models.ActivityLog.timestamp.desc()).offset(skip).limit(limit).all()
    return schemas.PaginatedResponse(total=total, page=page, limit=limit, items=items)
