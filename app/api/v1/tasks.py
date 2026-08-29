from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models
from app.database import get_db
from app.dependencies import RoleChecker, get_current_user
from app.services import crud_service

router = APIRouter(tags=["Tasks"])

@router.post("/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(RoleChecker([models.UserRole.ADMIN, models.UserRole.MANAGER]))):
    return crud_service.create_task(db=db, task=task, user_id=current_user.id, user_role=current_user.role)

@router.get("/campaigns/{campaign_id}/tasks", response_model=List[schemas.TaskResponse])
def read_tasks(campaign_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return crud_service.get_tasks_by_campaign(db=db, campaign_id=campaign_id)

@router.patch("/tasks/{task_id}/status", response_model=schemas.TaskResponse)
def update_task_status(task_id: int, status_update: schemas.TaskStatusUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(RoleChecker([models.UserRole.ADMIN, models.UserRole.MANAGER]))):
    updated = crud_service.update_task_status(db=db, task_id=task_id, status_enum=status_update.status, user_id=current_user.id, user_role=current_user.role)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(RoleChecker([models.UserRole.ADMIN, models.UserRole.MANAGER]))):
    if not crud_service.delete_task(db=db, task_id=task_id, user_id=current_user.id, user_role=current_user.role):
        raise HTTPException(status_code=404, detail="Task not found")
    return None
