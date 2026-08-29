def test_create_and_manage_task(client, auth_headers):
    c_res = client.post("/api/v1/clients", json={"name": "Client Tasks"}, headers=auth_headers)
    client_id = c_res.json()["id"]

    camp_res = client.post("/api/v1/campaigns", json={"name": "Campaign Tasks", "client_id": client_id}, headers=auth_headers)
    camp_id = camp_res.json()["id"]

    task_res = client.post(
        "/api/v1/tasks",
        json={"title": "Draft Visual Assets", "campaign_id": camp_id},
        headers=auth_headers
    )
    assert task_res.status_code == 201
    task_id = task_res.json()["id"]

    patch_res = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "IN_PROGRESS"},
        headers=auth_headers
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "IN_PROGRESS"

    del_res = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert del_res.status_code == 204
