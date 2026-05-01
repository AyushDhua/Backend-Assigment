def test_create_task(client, auth_headers):
    res = client.post("/api/v1/tasks", json={
        "title": "Test Task",
        "description": "Test Desc"
    }, headers=auth_headers)
    assert res.status_code == 201
    assert res.get_json()["data"]["title"] == "Test Task"

def test_get_tasks(client, auth_headers):
    client.post("/api/v1/tasks", json={"title": "Task 1"}, headers=auth_headers)
    res = client.get("/api/v1/tasks", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.get_json()["data"]) == 1

def test_update_task(client, auth_headers):
    res = client.post("/api/v1/tasks", json={"title": "Task 1"}, headers=auth_headers)
    task_id = res.get_json()["data"]["id"]
    res2 = client.put(f"/api/v1/tasks/{task_id}", json={"status": "COMPLETED"}, headers=auth_headers)
    assert res2.status_code == 200
    assert res2.get_json()["data"]["status"] == "COMPLETED"

def test_delete_task(client, auth_headers):
    res = client.post("/api/v1/tasks", json={"title": "Task 1"}, headers=auth_headers)
    task_id = res.get_json()["data"]["id"]
    res2 = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert res2.status_code == 200
    res3 = client.get(f"/api/v1/tasks", headers=auth_headers)
    assert len(res3.get_json()["data"]) == 0

def test_cannot_access_others_tasks(client, auth_headers):
    res = client.post("/api/v1/tasks", json={"title": "Task 1"}, headers=auth_headers)
    task_id = res.get_json()["data"]["id"]

    res2 = client.post("/api/v1/auth/register", json={"email": "other@example.com", "password": "password123"})
    other_token = res2.get_json()["data"]["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    res3 = client.delete(f"/api/v1/tasks/{task_id}", headers=other_headers)
    assert res3.status_code in [403, 404]
