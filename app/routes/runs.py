from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import Pipeline, PipelineRun
from app.schemas import PipelineRunRead
from app.workers.jobs import run_pipeline_job
from app.workers.queue import queue
from app.workers.jobs import run_pipeline_job
from app.workers.queue import queue

router = APIRouter(prefix="/runs", tags=["runs"])
@router.post("/{run_id}/retry")
def retry_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if run.status == "running":
        raise HTTPException(status_code=400, detail="Run is still in progress")

    job = queue.enqueue(run_pipeline_job, run.pipeline_id, 0)

    return {
        "message": "Retry started",
        "job_id": job.id,
    }

@router.post("/pipelines/{pipeline_id}", status_code=status.HTTP_202_ACCEPTED)
def run_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    job = queue.enqueue(run_pipeline_job, pipeline_id)

    return {
        "message": "Pipeline execution started",
        "job_id": job.id,
    }


@router.get("", response_model=list[PipelineRunRead])
def list_runs(db: Session = Depends(get_db)):
    runs = (
        db.query(PipelineRun)
        .options(selectinload(PipelineRun.stage_runs))
        .order_by(PipelineRun.created_at.desc())
        .all()
    )
    return runs


@router.get("/{run_id}", response_model=PipelineRunRead)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = (
        db.query(PipelineRun)
        .options(selectinload(PipelineRun.stage_runs))
        .filter(PipelineRun.id == run_id)
        .first()
    )

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return run
