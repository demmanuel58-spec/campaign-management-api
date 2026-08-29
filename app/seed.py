from app.database import SessionLocal
from app.config import settings
from app import models, security

def seed_database():
    db = SessionLocal()

    if db.query(models.User).filter(models.User.email == "admin@campaigns.com").first():
        print("Database already seeded.")
        db.close()
        return

    admin_password = settings.ADMIN_SEED_PASSWORD
    admin = models.User(
        email="admin@campaigns.com",
        hashed_password=security.get_password_hash(admin_password),
        role=models.UserRole.ADMIN
    )
    manager = models.User(
        email="manager@campaigns.com",
        hashed_password=security.get_password_hash("ManagerSecurePass123!"),
        role=models.UserRole.MANAGER
    )
    db.add_all([admin, manager])
    db.commit()
    db.refresh(admin)
    db.refresh(manager)

    client1 = models.Client(name="Hanan Premium Products")
    client2 = models.Client(name="Bella Donna Cosmetics")
    db.add_all([client1, client2])
    db.commit()
    db.refresh(client1)

    campaign1 = models.Campaign(
        name="Hanan Wipes Launch",
        description="Digital activation across retail outlets",
        status=models.CampaignStatus.ACTIVE,
        client_id=client1.id,
        created_by=manager.id
    )
    db.add(campaign1)
    db.commit()
    db.refresh(campaign1)

    task1 = models.Task(
        title="Approve TVC Storyboard",
        description="Review video production storyboard draft",
        status=models.TaskStatus.IN_PROGRESS,
        campaign_id=campaign1.id,
        assigned_user_id=manager.id
    )
    db.add(task1)
    db.commit()

    db.close()
    print("Database seeded safely via Alembic schema state!")

if __name__ == "__main__":
    seed_database()
