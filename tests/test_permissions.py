def test_viewer_role_cannot_create_campaign(client, db_session):
    from app import models, security
    # Seed a viewer directly in DB
    viewer = models.User(
        email="viewer@example.com",
        hashed_password=security.get_password_hash("ViewerPass123!"),
        role=models.UserRole.VIEWER
    )
    db_session.add(viewer)
    db_session.commit()

    login_res = client.post("/api/v1/login", data={"username": "viewer@example.com", "password": "ViewerPass123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/v1/campaigns", json={"name": "Forbidden Campaign", "client_id": 1}, headers=headers)
    assert res.status_code == 403

def test_admin_can_view_activity_logs(client, db_session):
    from app import models, security
    # Seed an admin user
    admin = models.User(
        email="admin@example.com",
        hashed_password=security.get_password_hash("AdminPass123!"),
        role=models.UserRole.ADMIN
    )
    db_session.add(admin)
    db_session.commit()

    login_res = client.post("/api/v1/login", data={"username": "admin@example.com", "password": "AdminPass123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/activity-logs", headers=headers)
    assert res.status_code == 200
    assert "items" in res.json()
