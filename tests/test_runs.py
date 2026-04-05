def test_run_pipeline(client):
    # create pipeline
    response = client.post("/pipelines", json={
        "name": "test-run",
        "description": "test",
        "max_retries": 0,
        "stages": [
            {
                "name": "ok",
                "command": "echo hello",
                "order": 1
            }
        ]
    })
    assert response.status_code == 201

    pipeline_id = response.json()["id"]

    # trigger run
    response = client.post(f"/runs/pipelines/{pipeline_id}")
    assert response.status_code == 202


def test_get_runs(client):
    response = client.get("/runs")
    assert response.status_code == 200


def test_retry_endpoint(client):
    # create failing pipeline
    response = client.post("/pipelines", json={
        "name": "retry-test",
        "description": "fail",
        "max_retries": 0,
        "stages": [
            {
                "name": "fail",
                "command": "python -c \"import sys; sys.exit(1)\"",
                "order": 1
            }
        ]
    })

    pipeline_id = response.json()["id"]

    # run it
    client.post(f"/runs/pipelines/{pipeline_id}")

    # retry first run (id=1 assumption можно улучшить)
    response = client.post("/runs/1/retry")

    assert response.status_code in [200, 202]
