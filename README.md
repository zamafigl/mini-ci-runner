# Mini CI Runner

Lightweight CI/CD system that executes pipeline stages asynchronously using FastAPI, Redis and background workers.

---

## 🚀 What is this?

Mini CI Runner is a simplified backend implementation of a CI/CD system (inspired by GitLab CI / GitHub Actions).

It allows you to define pipelines, execute them asynchronously, and track execution results — including retries, logs, and failures.

This project focuses on **backend orchestration, job execution, and infrastructure logic**, not UI.

---

## ⚙️ Key Features

- Pipeline system with ordered stages
- Asynchronous execution (Redis + RQ workers)
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
- failure handling & retries
- system design similar to real CI/CD platforms
- separation of API and worker execution

---

## 🏗️ Architecture


Client → FastAPI → Redis Queue → Worker → Execution → Database


Flow:

1. User creates pipeline
2. User triggers run
3. API pushes job to Redis
4. Worker executes stages sequentially
5. Results are stored in DB
6. Retry logic is applied if needed

---

## 🗂️ Project Structure


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
├── test_pipelines.py
└── test_runs.py


---

## 🔌 API Endpoints

### Pipelines

- `POST /pipelines`
- `GET /pipelines`
- `GET /pipelines/{id}`

### Runs

- `POST /runs/pipelines/{pipeline_id}`
- `GET /runs`
- `GET /runs/{id}`

---

## 📦 Example Pipeline

```json
{
  "name": "demo",
  "max_retries": 2,
  "stages": [
    {
      "name": "step-1",
      "command": "echo hello",
      "order": 1
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
Uses subprocess (no container isolation yet)
No authentication
No webhook triggers
No UI
🚧 Next steps
Docker-based execution (like real CI)
GitHub webhook integration
Live logs streaming
Parallel stage execution
