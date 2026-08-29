from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Generic, TypeVar
from datetime import datetime
from app.models import CampaignStatus, TaskStatus, UserRole

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    limit: int
    items: List[T]

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one numerical digit")
        return v

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ClientBase(BaseModel):
    name: str

class ClientCreate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: int
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    deadline: Optional[datetime] = None

class TaskCreate(TaskBase):
    campaign_id: int
    assigned_user_id: Optional[int] = None

class TaskStatusUpdate(BaseModel):
    status: TaskStatus

class TaskResponse(TaskBase):
    id: int
    campaign_id: int
    assigned_user_id: Optional[int] = None
    class Config:
        from_attributes = True

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[CampaignStatus] = CampaignStatus.DRAFT
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class CampaignCreate(CampaignBase):
    client_id: int

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class CampaignStatusUpdate(BaseModel):
    status: CampaignStatus

class CampaignResponse(CampaignBase):
    id: int
    client_id: int
    created_by: int
    created_at: datetime
    tasks: List[TaskResponse] = Field(default_factory=list)
    class Config:
        from_attributes = True

class ActivityLogResponse(BaseModel):
    id: int
    action: str
    timestamp: datetime
    user_id: int
    campaign_id: Optional[int] = None
    class Config:
        from_attributes = True
