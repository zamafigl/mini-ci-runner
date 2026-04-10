from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import Pipeline, PipelineRun, PipelineRunStatus
from app.schemas import PipelineRunRead
from app.workers.jobs import run_pipeline_job
from app.workers.queue import queue

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("/{run_id}/retry", response_model=PipelineRunRead, status_code=status.HTTP_202_ACCEPTED)
def retry_run(run_id: int, db: Session = Depends(get_db)):
    run = (
        db.query(PipelineRun)
        .options(selectinload(PipelineRun.stage_runs))
        .filter(PipelineRun.id == run_id)
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if run.status == PipelineRunStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Run is still in progress")

    retry_run_obj = PipelineRun(
        pipeline_id=run.pipeline_id,
        status=PipelineRunStatus.PENDING,
        retry_count=run.retry_count + 1,
    )
    db.add(retry_run_obj)
    db.commit()
    db.refresh(retry_run_obj)

    queue.enqueue(run_pipeline_job, retry_run_obj.id)

    retry_run_obj = (
        db.query(PipelineRun)
        .options(selectinload(PipelineRun.stage_runs))
        .filter(PipelineRun.id == retry_run_obj.id)
        .first()
    )
    return retry_run_obj


@router.post(
    "/pipelines/{pipeline_id}",
    response_model=PipelineRunRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def run_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    pipeline_run = PipelineRun(
        pipeline_id=pipeline.id,
        status=PipelineRunStatus.PENDING,
        retry_count=0,
    )
    db.add(pipeline_run)
    db.commit()
    db.refresh(pipeline_run)

    queue.enqueue(run_pipeline_job, pipeline_run.id)

    pipeline_run = (
        db.query(PipelineRun)
        .options(selectinload(PipelineRun.stage_runs))
        .filter(PipelineRun.id == pipeline_run.id)
        .first()
    )
    return pipeline_run


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
