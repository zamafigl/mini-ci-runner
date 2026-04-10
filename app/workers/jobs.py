import subprocess
from datetime import datetime, UTC

from sqlalchemy.orm import Session, selectinload

from app.db import SessionLocal
from app.models import (
    PipelineRun,
    PipelineRunStatus,
    StageRun,
    StageRunStatus,
)


def run_pipeline_job(run_id: int):
    db: Session = SessionLocal()
    try:
        pipeline_run = (
            db.query(PipelineRun)
            .options(selectinload(PipelineRun.pipeline).selectinload("stages"))
            .filter(PipelineRun.id == run_id)
            .first()
        )
        if not pipeline_run:
            return

        pipeline = pipeline_run.pipeline
        if not pipeline:
            pipeline_run.status = PipelineRunStatus.FAILED
            pipeline_run.finished_at = datetime.now(UTC).replace(tzinfo=None)
            db.commit()
            return

        pipeline_run.status = PipelineRunStatus.RUNNING
        pipeline_run.started_at = datetime.now(UTC).replace(tzinfo=None)
        db.commit()

        for stage in sorted(pipeline.stages, key=lambda s: s.order):
            stage_run = StageRun(
                pipeline_run_id=pipeline_run.id,
                stage_name=stage.name,
                command=stage.command,
                status=StageRunStatus.RUNNING,
                started_at=datetime.now(UTC).replace(tzinfo=None),
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

            except subprocess.TimeoutExpired as exc:
                stdout = exc.stdout or ""
                stderr = exc.stderr or ""
                stage_run.output = (
                    f"Timeout exceeded after {stage.timeout_seconds} seconds\n{stdout}{stderr}"
                )
                stage_run.status = StageRunStatus.FAILED
                stage_run.exit_code = -1

            except Exception as exc:
                stage_run.output = str(exc)
                stage_run.status = StageRunStatus.FAILED
                stage_run.exit_code = -1

            stage_run.finished_at = datetime.now(UTC).replace(tzinfo=None)
            db.commit()

            if stage_run.status == StageRunStatus.FAILED:
                pipeline_run.status = PipelineRunStatus.FAILED
                pipeline_run.finished_at = datetime.now(UTC).replace(tzinfo=None)
                db.commit()
                return

        pipeline_run.status = PipelineRunStatus.SUCCESS
        pipeline_run.finished_at = datetime.now(UTC).replace(tzinfo=None)
        db.commit()

    finally:
        db.close()
