def test_create_campaign_unauthorized(client):
    res = client.post("/api/v1/campaigns", json={"name": "Unauth Launch", "client_id": 1})
    assert res.status_code == 401

def test_create_campaign_success(client, auth_headers):
    c_res = client.post("/api/v1/clients", json={"name": "Hanan Premium Products"}, headers=auth_headers)
    client_id = c_res.json()["id"]

    res = client.post(
        "/api/v1/campaigns",
        json={"name": "Hanan Wipes Launch", "client_id": client_id, "status": "PLANNING"},
        headers=auth_headers
    )
    assert res.status_code == 201
    assert res.json()["status"] == "PLANNING"

def test_update_campaign_status(client, auth_headers):
    c_res = client.post("/api/v1/clients", json={"name": "Client A"}, headers=auth_headers)
    camp_res = client.post(
        "/api/v1/campaigns",
        json={"name": "Summer Activation", "client_id": c_res.json()["id"]},
        headers=auth_headers
    )
    camp_id = camp_res.json()["id"]

    patch_res = client.patch(
        f"/api/v1/campaigns/{camp_id}/status",
        json={"status": "ACTIVE"},
        headers=auth_headers
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "ACTIVE"

def test_delete_campaign_soft(client, auth_headers):
    c_res = client.post("/api/v1/clients", json={"name": "Client B"}, headers=auth_headers)
    camp_res = client.post("/api/v1/campaigns", json={"name": "Promo", "client_id": c_res.json()["id"]}, headers=auth_headers)
    camp_id = camp_res.json()["id"]

    del_res = client.delete(f"/api/v1/campaigns/{camp_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # Verify campaign is excluded from standard list queries
    list_res = client.get("/api/v1/campaigns", headers=auth_headers)
    assert list_res.json()["total"] == 0
