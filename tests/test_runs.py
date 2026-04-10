from types import SimpleNamespace

import app.routes.runs as runs_routes


def create_pipeline(client):
    payload = {
        "name": "retry-pipeline",
        "description": "pipeline for run tests",
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
    assert response.status_code == 200
    return response.json()["id"]


def test_run_pipeline_enqueues_job(client, monkeypatch):
    pipeline_id = create_pipeline(client)
    captured = {}

    class FakeQueue:
        def enqueue(self, func, run_id, job_timeout=None):
            captured["func_name"] = func.__name__
            captured["run_id"] = run_id
            captured["job_timeout"] = job_timeout

    monkeypatch.setattr(runs_routes, "queue", FakeQueue())

    response = client.post(f"/runs/pipelines/{pipeline_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["pipeline_id"] == pipeline_id
    assert data["status"] in ["pending", "queued", "running"]
    assert captured["func_name"]


def test_list_runs(client, monkeypatch):
    pipeline_id = create_pipeline(client)

    class FakeQueue:
        def enqueue(self, func, run_id, job_timeout=None):
            return None

    monkeypatch.setattr(runs_routes, "queue", FakeQueue())
    client.post(f"/runs/pipelines/{pipeline_id}")

    response = client.get("/runs")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_run_by_id(client, monkeypatch):
    pipeline_id = create_pipeline(client)

    class FakeQueue:
        def enqueue(self, func, run_id, job_timeout=None):
            return None

    monkeypatch.setattr(runs_routes, "queue", FakeQueue())
    create_run = client.post(f"/runs/pipelines/{pipeline_id}")
    run_id = create_run.json()["id"]

    response = client.get(f"/runs/{run_id}")
    assert response.status_code == 200
    assert response.json()["id"] == run_id


def test_retry_run_returns_404_for_missing_run(client):
    response = client.post("/runs/999/retry")
    assert response.status_code == 404
