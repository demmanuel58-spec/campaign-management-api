import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean, Index
from sqlalchemy.orm import relationship
from app.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    VIEWER = "VIEWER"

class CampaignStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    DONE = "DONE"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole, native_enum=False), default=UserRole.MANAGER, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    campaigns = relationship("Campaign", back_populates="creator")
    assigned_tasks = relationship("Task", back_populates="assigned_user")
    activity_logs = relationship("ActivityLog", back_populates="user")

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    campaigns = relationship("Campaign", back_populates="client", cascade="all, delete-orphan")

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(CampaignStatus, native_enum=False), default=CampaignStatus.DRAFT, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    client = relationship("Client", back_populates="campaigns")
    creator = relationship("User", back_populates="campaigns")
    tasks = relationship("Task", back_populates="campaign", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="campaign", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_campaign_status_deleted", "status", "is_deleted"),
        Index("idx_campaign_creator", "created_by"),
        Index("idx_campaign_client", "client_id"),
    )

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(TaskStatus, native_enum=False), default=TaskStatus.TODO, nullable=False)
    deadline = Column(DateTime, nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    campaign = relationship("Campaign", back_populates="tasks")
    assigned_user = relationship("User", back_populates="assigned_tasks")

    __table_args__ = (
        Index("idx_task_campaign", "campaign_id"),
        Index("idx_task_assigned_user", "assigned_user_id"),
    )

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)

    user = relationship("User", back_populates="activity_logs")
    campaign = relationship("Campaign", back_populates="activity_logs")

    __table_args__ = (
        Index("idx_log_user", "user_id"),
        Index("idx_log_campaign", "campaign_id"),
    )
