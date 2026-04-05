# Mini CI Runner

Lightweight CI/CD system that executes pipeline stages asynchronously using FastAPI, Redis and background workers.

---

## 🚀 What is this?

Mini CI Runner is a simplified backend implementation of a CI/CD system inspired by GitLab CI and GitHub Actions.

It allows you to define pipelines, execute them asynchronously, and track execution results — including retries, logs, and failures.

This project focuses on **backend orchestration, job execution, and infrastructure logic**, not UI.

---

## ⚙️ Key Features

- Pipeline system with ordered stages
- Asynchronous execution using Redis + RQ workers
- Background job processing
- Retry mechanism for failed pipelines
- Stage-level timeout control
- Execution logs and exit codes
- Persistent run history

---

## 🧠 Why this project matters

This is not a CRUD app.

This project demonstrates:

- async job orchestration
- queue-based architecture
- failure handling and retries
- system design similar to real CI/CD platforms
- separation of API and worker execution

---

## 🏗️ Architecture

```text
Client → FastAPI → Redis Queue → Worker → Execution → Database
Flow
User creates a pipeline
User triggers a run
API pushes the job to Redis
Worker executes stages sequentially
Results are stored in the database
Retry logic is applied if needed
🗂️ Project Structure
app/
├── main.py
├── db.py
├── models.py
├── schemas.py
├── routes/
│   ├── pipelines.py
│   └── runs.py
└── workers/
    ├── queue.py
    └── jobs.py

tests/
├── test_pipelines.py
└── test_runs.py
🔌 API Endpoints
Pipelines
POST /pipelines
GET /pipelines
GET /pipelines/{id}
Runs
POST /runs/pipelines/{pipeline_id}
POST /runs/{run_id}/retry
GET /runs
GET /runs/{id}
📦 Example Pipeline
{
  "name": "retry-pipeline",
  "description": "Pipeline with retry and timeout",
  "max_retries": 2,
  "stages": [
    {
      "name": "build",
      "command": "echo build",
      "order": 1,
      "timeout_seconds": 5
    },
    {
      "name": "test",
      "command": "python -c \\"import sys; sys.exit(1)\\"",
      "order": 2,
      "timeout_seconds": 5
    }
  ]
}
🧪 Example Run
curl -X POST http://127.0.0.1:8000/runs/pipelines/1
🛠️ Tech Stack
FastAPI
PostgreSQL
SQLAlchemy
Redis
RQ
Pytest
Docker
▶️ Run locally
git clone git@github.com:zamafigl/mini-ci-runner.git
cd mini-ci-runner
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker compose up -d
uvicorn app.main:app --reload
PYTHONPATH=. rq worker mini-ci
🧪 Tests
pytest -v
⚠️ Limitations
Uses subprocess execution (no container isolation yet)
No authentication
No webhook triggers
No UI
🚧 Next Steps
Docker-based execution similar to real CI systems
GitHub webhook integration
Live logs streaming
Parallel stage execution
