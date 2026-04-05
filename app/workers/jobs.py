import subprocess
from datetime import datetime

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import (
    Pipeline,
    PipelineRun,
    PipelineRunStatus,
    StageRun,
    StageRunStatus,
)


def run_pipeline_job(pipeline_id: int, retry_count: int = 0):
    db: Session = SessionLocal()

    try:
        pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
        if not pipeline:
            return

        pipeline_run = PipelineRun(
            pipeline_id=pipeline.id,
            status=PipelineRunStatus.RUNNING,
            retry_count=retry_count,
            started_at=datetime.utcnow(),
        )

        db.add(pipeline_run)
        db.commit()
        db.refresh(pipeline_run)

        for stage in sorted(pipeline.stages, key=lambda s: s.order):
            stage_run = StageRun(
                pipeline_run_id=pipeline_run.id,
                stage_name=stage.name,
                command=stage.command,
                status=StageRunStatus.RUNNING,
                started_at=datetime.utcnow(),
            )

            db.add(stage_run)
            db.commit()
            db.refresh(stage_run)

            try:
                result = subprocess.run(
                    stage.command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=stage.timeout_seconds,
                )

                stage_run.output = (result.stdout or "") + (result.stderr or "")
                stage_run.exit_code = result.returncode

                if result.returncode == 0:
                    stage_run.status = StageRunStatus.SUCCESS
                else:
                    stage_run.status = StageRunStatus.FAILED

            except subprocess.TimeoutExpired as e:
                stdout = e.stdout or ""
                stderr = e.stderr or ""
                stage_run.output = f"Timeout exceeded after {stage.timeout_seconds} seconds\n{stdout}{stderr}"
                stage_run.status = StageRunStatus.FAILED
                stage_run.exit_code = -1

            except Exception as e:
                stage_run.output = str(e)
                stage_run.status = StageRunStatus.FAILED
                stage_run.exit_code = -1

            stage_run.finished_at = datetime.utcnow()
            db.commit()

            if stage_run.status == StageRunStatus.FAILED:
                pipeline_run.status = PipelineRunStatus.FAILED
                pipeline_run.finished_at = datetime.utcnow()
                db.commit()

                if retry_count < pipeline.max_retries:
                    from app.workers.queue import queue
                    queue.enqueue(run_pipeline_job, pipeline_id, retry_count + 1)

                return

        pipeline_run.status = PipelineRunStatus.SUCCESS
        pipeline_run.finished_at = datetime.utcnow()
        db.commit()

    finally:
        db.close()
