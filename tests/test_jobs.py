from fastapi.testclient import TestClient

WARSAW = {"latitude": 52.2297, "longitude": 21.0122}


def create_job(client: TestClient, **overrides):
    body = {"description": "Fix the fence", "location": WARSAW} | overrides
    return client.post("/jobs", json=body)


def test_create_and_get_job(client: TestClient) -> None:
    response = create_job(client)
    assert response.status_code == 201
    body = response.json()
    assert body["description"] == "Fix the fence"
    assert body["status"] == "TODO"
    assert body["location"] == WARSAW

    assert client.get(f"/jobs/{body['id']}").json() == body


def test_list_jobs(client: TestClient) -> None:
    create_job(client)
    create_job(client, status="DONE")

    jobs = client.get("/jobs").json()
    assert [j["status"] for j in jobs] == ["TODO", "DONE"]


def test_update_status(client: TestClient) -> None:
    created = create_job(client).json()

    response = client.patch(f"/jobs/{created['id']}", json={"status": "DONE"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "DONE"
    assert body["description"] == created["description"]
    assert body["location"] == created["location"]
    assert body["updated_at"] > created["updated_at"]


def test_same_status_update_is_noop(client: TestClient) -> None:
    created = create_job(client).json()
    assert client.patch(f"/jobs/{created['id']}", json={"status": "TODO"}).json() == created


def test_only_status_can_be_updated(client: TestClient) -> None:
    job_id = create_job(client).json()["id"]
    bad_bodies = [
        {},
        {"status": None},
        {"status": "DOING"},
        {"description": "New"},
        {"status": "DONE", "location": {"latitude": 0, "longitude": 0}},
    ]
    for bad in bad_bodies:
        assert client.patch(f"/jobs/{job_id}", json=bad).status_code == 422, bad
    assert client.get(f"/jobs/{job_id}").json()["status"] == "TODO"


def test_rejects_invalid_create(client: TestClient) -> None:
    bad_bodies = [
        {"description": "   "},
        {"status": "IN_PROGRESS"},
        {"location": {"latitude": 91, "longitude": 0}},
        {"location": {"latitude": 0, "longitude": -180.5}},
        {"location": {"latitude": 0}},
        {"location": None},
    ]
    for bad in bad_bodies:
        assert create_job(client, **bad).status_code == 422, bad


def test_delete_job(client: TestClient) -> None:
    job_id = create_job(client).json()["id"]
    assert client.delete(f"/jobs/{job_id}").status_code == 204
    assert client.get(f"/jobs/{job_id}").status_code == 404


def test_missing_job_returns_404(client: TestClient) -> None:
    assert client.get("/jobs/999").status_code == 404
    assert client.patch("/jobs/999", json={"status": "DONE"}).status_code == 404
    assert client.delete("/jobs/999").status_code == 404
