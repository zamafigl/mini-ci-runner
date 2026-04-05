def test_create_pipeline(client):
    payload = {
        "name": "demo-pipeline",
        "description": "Simple pipeline",
        "stages": [
            {"name": "lint", "command": "echo lint", "order": 1},
            {"name": "test", "command": "echo test", "order": 2},
        ],
    }

    response = client.post("/pipelines", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["name"] == "demo-pipeline"
    assert data["description"] == "Simple pipeline"
    assert len(data["stages"]) == 2
    assert data["stages"][0]["name"] == "lint"
    assert data["stages"][1]["name"] == "test"


def test_create_pipeline_duplicate_name(client):
    payload = {
        "name": "demo-pipeline",
        "description": "Simple pipeline",
        "stages": [
            {"name": "lint", "command": "echo lint", "order": 1},
        ],
    }

    first_response = client.post("/pipelines", json=payload)
    second_response = client.post("/pipelines", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Pipeline with this name already exists"


def test_list_pipelines(client):
    payload_1 = {
        "name": "pipeline-1",
        "description": "First pipeline",
        "stages": [
            {"name": "stage-1", "command": "echo one", "order": 1},
        ],
    }

    payload_2 = {
        "name": "pipeline-2",
        "description": "Second pipeline",
        "stages": [
            {"name": "stage-1", "command": "echo two", "order": 1},
        ],
    }

    client.post("/pipelines", json=payload_1)
    client.post("/pipelines", json=payload_2)

    response = client.get("/pipelines")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    names = [pipeline["name"] for pipeline in data]
    assert "pipeline-1" in names
    assert "pipeline-2" in names


def test_get_pipeline_by_id(client):
    payload = {
        "name": "demo-pipeline",
        "description": "Simple pipeline",
        "stages": [
            {"name": "lint", "command": "echo lint", "order": 1},
            {"name": "test", "command": "echo test", "order": 2},
        ],
    }

    create_response = client.post("/pipelines", json=payload)
    pipeline_id = create_response.json()["id"]

    response = client.get(f"/pipelines/{pipeline_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == pipeline_id
    assert data["name"] == "demo-pipeline"
    assert len(data["stages"]) == 2


def test_get_pipeline_not_found(client):
    response = client.get("/pipelines/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Pipeline not found"
