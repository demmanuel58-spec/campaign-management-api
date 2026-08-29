def test_paginated_campaign_list(client, auth_headers):
    c_res = client.post("/api/v1/clients", json={"name": "Client A"}, headers=auth_headers)
    client_id = c_res.json()["id"]

    for i in range(5):
        client.post("/api/v1/campaigns", json={"name": f"Campaign {i}", "client_id": client_id}, headers=auth_headers)

    res = client.get("/api/v1/campaigns?page=1&limit=2", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["limit"] == 2
    assert len(data["items"]) == 2
