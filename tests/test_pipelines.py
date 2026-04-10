def test_create_pipeline(client):
    payload = {
        "name": "demo-pipeline",
        "description": "test pipeline",
        "max_retries": 2,
        "stages": [
            {
                "name": "build",
                "command": "echo build",
                "order": 1,
                "timeout_seconds": 5,
            },
            {
                "name": "test",
                "command": "echo test",
                "order": 2,
                "timeout_seconds": 5,
            },
        ],
    }

    response = client.post("/pipelines", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "demo-pipeline"
    assert len(data["stages"]) == 2
    assert data["max_retries"] == 2


def test_list_pipelines(client):
    payload = {
        "name": "demo-pipeline",
        "description": "test pipeline",
        "max_retries": 1,
        "stages": [
            {
                "name": "build",
                "command": "echo build",
                "order": 1,
                "timeout_seconds": 5,
            }
        ],
    }

    client.post("/pipelines", json=payload)

    response = client.get("/pipelines")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "demo-pipeline"


def test_get_pipeline_by_id(client):
    payload = {
        "name": "demo-pipeline",
        "description": "test pipeline",
        "max_retries": 1,
        "stages": [
            {
                "name": "build",
                "command": "echo build",
                "order": 1,
                "timeout_seconds": 5,
            }
        ],
    }

    create_response = client.post("/pipelines", json=payload)
    pipeline_id = create_response.json()["id"]

    response = client.get(f"/pipelines/{pipeline_id}")
    assert response.status_code == 200
    assert response.json()["id"] == pipeline_id


def test_get_missing_pipeline_returns_404(client):
    response = client.get("/pipelines/999")
    assert response.status_code == 404
