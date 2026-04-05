from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class PipelineRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class StageRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    stages: Mapped[list["Stage"]] = relationship(
        "Stage",
        back_populates="pipeline",
        cascade="all, delete-orphan",
        order_by="Stage.order",
    )
    runs: Mapped[list["PipelineRun"]] = relationship(
        "PipelineRun",
        back_populates="pipeline",
        cascade="all, delete-orphan",
        order_by="PipelineRun.created_at.desc()",
    )


class Stage(Base):
    __tablename__ = "stages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pipeline_id: Mapped[int] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    command: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    pipeline: Mapped["Pipeline"] = relationship(
        "Pipeline",
        back_populates="stages",
    )


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pipeline_id: Mapped[int] = mapped_column(
        ForeignKey("pipelines.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[PipelineRunStatus] = mapped_column(
        SqlEnum(PipelineRunStatus),
        default=PipelineRunStatus.PENDING,
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    pipeline: Mapped["Pipeline"] = relationship(
        "Pipeline",
        back_populates="runs",
    )
    stage_runs: Mapped[list["StageRun"]] = relationship(
        "StageRun",
        back_populates="pipeline_run",
        cascade="all, delete-orphan",
        order_by="StageRun.id",
    )


class StageRun(Base):
    __tablename__ = "stage_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pipeline_run_id: Mapped[int] = mapped_column(
        ForeignKey("pipeline_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    stage_name: Mapped[str] = mapped_column(String(120), nullable=False)
    command: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[StageRunStatus] = mapped_column(
        SqlEnum(StageRunStatus),
        default=StageRunStatus.PENDING,
        nullable=False,
    )
    output: Mapped[str | None] = mapped_column(Text, nullable=True)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    pipeline_run: Mapped["PipelineRun"] = relationship(
        "PipelineRun",
        back_populates="stage_runs",
    )
