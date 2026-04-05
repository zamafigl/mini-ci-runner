# Mini CI Runner

Self-hosted CI/CD runner that executes stage-based pipelines asynchronously using FastAPI, PostgreSQL, Redis and RQ.

---

## Overview

Mini CI Runner is a backend-focused infrastructure project that allows you to:

- Create pipelines with ordered stages
- Execute pipelines asynchronously
- Run commands in background workers
- Store execution history and logs
- Retry failed pipelines
- Apply timeout control per stage

The project simulates core behavior of CI/CD systems like GitLab CI or GitHub Actions on a simplified level.

---

## Features

- Pipeline CRUD
- Ordered stage execution
- Asynchronous execution (Redis + RQ)
- Run history tracking
- Stage-level logs and exit codes
- Automatic retry support
- Stage timeout handling
- Basic API tests (pytest)

---

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- RQ (Redis Queue)
- Pytest
- Docker Compose

---

## Project Structure


app/
├── main.py
├── db.py
├── models.py
├── schemas.py
├── routes/
│ ├── pipelines.py
│ └── runs.py
└── workers/
├── queue.py
└── jobs.py

tests/
├── conftest.py
├── test_pipelines.py
└── test_runs.py


---

## How It Works

1. A pipeline is created via API.
2. Each pipeline contains ordered stages (commands).
3. A run request is sent.
4. The API enqueues a job into Redis.
5. RQ worker executes stages sequentially.
6. Each stage stores:
   - status
   - output
   - exit code
   - timestamps
7. If a stage fails:
   - pipeline stops
   - retry is triggered (if configured)
8. If timeout is exceeded:
   - stage is terminated
   - marked as failed

---

## API Endpoints

### Pipelines

- `POST /pipelines`
- `GET /pipelines`
- `GET /pipelines/{id}`

### Runs

- `POST /runs/pipelines/{pipeline_id}`
- `GET /runs`
- `GET /runs/{id}`

---

## Example Pipeline

```json
{
  "name": "demo-pipeline",
  "description": "Simple demo pipeline",
  "max_retries": 1,
  "stages": [
    {
      "name": "lint",
      "command": "echo lint",
      "order": 1,
      "timeout_seconds": 5
    },
    {
      "name": "test",
      "command": "echo test",
      "order": 2,
      "timeout_seconds": 5
    }
  ]
}
Local Setup
1. Clone repository
git clone git@github.com:zamafigl/mini-ci-runner.git
cd mini-ci-runner
2. Create virtual environment
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Create .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5434/mini_ci
Run Project
Start infrastructure
docker compose up -d
Run API
uvicorn app.main:app --reload
Run worker
PYTHONPATH=. rq worker mini-ci
Example Usage
Create pipeline
curl -X POST "http://127.0.0.1:8000/pipelines" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "retry-pipeline",
    "description": "Pipeline with retry",
    "max_retries": 2,
    "stages": [
      {
        "name": "fail-stage",
        "command": "python -c \"import sys; sys.exit(1)\"",
        "order": 1,
        "timeout_seconds": 5
      }
    ]
  }'
Run pipeline
curl -X POST "http://127.0.0.1:8000/runs/pipelines/1"
Get runs
curl "http://127.0.0.1:8000/runs"
Testing
pytest -v
Current Limitations
Uses local subprocess execution
No Docker isolation yet
No authentication
No webhook triggers
No live logs streaming
Future Improvements
Docker-based executor
Webhook trigger (GitHub push → run)
Manual retry endpoint
Structured logging
Stage environment variables
Live logs streaming
