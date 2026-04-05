# Mini CI Runner

Self-hosted CI/CD runner that executes stage-based pipelines asynchronously using FastAPI, PostgreSQL, Redis and RQ.

## Features

- Create pipelines with ordered stages
- Store pipeline definitions in PostgreSQL
- Trigger pipeline runs asynchronously
- Execute stages in background worker via RQ
- Persist run history and stage execution results
- Capture command output and exit codes
- Stop pipeline execution on failed stage

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- RQ
- Pytest

## Project Structure

```bash
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
Setup
1. Create virtual environment
python3 -m venv venv
source venv/bin/activate
2. Install dependencies
pip install -r requirements.txt
3. Start infrastructure
docker compose up -d
4. Run API
uvicorn app.main:app --reload
5. Run worker
PYTHONPATH=. rq worker mini-ci
Environment Variables

Create .env file:

DATABASE_URL=postgresql://postgres:postgres@localhost:5434/mini_ci
API Endpoints
Pipelines
POST /pipelines
GET /pipelines
GET /pipelines/{id}
Runs
POST /runs/pipelines/{pipeline_id}
GET /runs
GET /runs/{id}
Example Pipeline
{
  "name": "demo-pipeline",
  "description": "Simple demo pipeline",
  "stages": [
    {
      "name": "lint",
      "command": "echo lint",
      "order": 1
    },
    {
      "name": "test",
      "command": "echo test",
      "order": 2
    },
    {
      "name": "build",
      "command": "echo build",
      "order": 3
    }
  ]
}
Example Run Flow
Create pipeline
Trigger pipeline run
Background worker executes stages in order
Stage output and exit codes are stored
Pipeline run is marked as success or failed
Testing
pytest -v
Current Limitations
Commands are executed via shell on local machine
No retry support yet
No timeout handling yet
No live log streaming yet
No Docker-based isolated executor yet
Next Improvements
Retry failed runs
Stage timeout handling
Docker executor
Better structured logging
Webhook-triggered runs
