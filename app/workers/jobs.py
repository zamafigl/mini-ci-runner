import subprocess
from datetime import datetime

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import PipelineRun, StageRun, Pipeline, Stage, PipelineRunStatus, StageRunStatus


def run_pipeline_job(pipeline_id: int):
    db: Session = SessionLocal()

    try:
        pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
        if not pipeline:
            return

        pipeline_run = PipelineRun(
            pipeline_id=pipeline.id,
            status=PipelineRunStatus.RUNNING,
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
                )

                stage_run.output = result.stdout + result.stderr
                stage_run.exit_code = result.returncode

                if result.returncode == 0:
                    stage_run.status = StageRunStatus.SUCCESS
                else:
                    stage_run.status = StageRunStatus.FAILED

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
                return

        pipeline_run.status = PipelineRunStatus.SUCCESS
        pipeline_run.finished_at = datetime.utcnow()
        db.commit()

    finally:
        db.close()
