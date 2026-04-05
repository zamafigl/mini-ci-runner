from sqlalchemy.orm import Session, selectinload
from fastapi import APIRouter, Depends, HTTPException, status

from app.db import get_db
from app.models import Pipeline, Stage
from app.schemas import PipelineCreate, PipelineRead


router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.post("", response_model=PipelineRead, status_code=status.HTTP_201_CREATED)
def create_pipeline(payload: PipelineCreate, db: Session = Depends(get_db)):
    existing_pipeline = db.query(Pipeline).filter(Pipeline.name == payload.name).first()
    if existing_pipeline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline with this name already exists",
        )

    pipeline = Pipeline(
        name=payload.name,
        description=payload.description,
    )

    for stage_data in payload.stages:
        stage = Stage(
            name=stage_data.name,
            command=stage_data.command,
            order=stage_data.order,
        )
        pipeline.stages.append(stage)

    db.add(pipeline)
    db.commit()
    db.refresh(pipeline)

    return pipeline


@router.get("", response_model=list[PipelineRead])
def list_pipelines(db: Session = Depends(get_db)):
    pipelines = (
        db.query(Pipeline)
        .options(selectinload(Pipeline.stages))
        .order_by(Pipeline.created_at.desc())
        .all()
    )
    return pipelines


@router.get("/{pipeline_id}", response_model=PipelineRead)
def get_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    pipeline = (
        db.query(Pipeline)
        .options(selectinload(Pipeline.stages))
        .filter(Pipeline.id == pipeline_id)
        .first()
    )

    if pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found",
        )

    return pipeline
