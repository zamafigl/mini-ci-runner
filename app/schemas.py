from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class StageCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    command: str = Field(..., min_length=1)
    order: int = Field(..., ge=1)
    timeout_seconds: int | None = Field(default=None, ge=1)


class PipelineCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = None
    max_retries: int = Field(default=0, ge=0, le=5)
    stages: list[StageCreate]

    @field_validator("stages")
    @classmethod
    def validate_stages_not_empty(cls, value: list[StageCreate]):
        if not value:
            raise ValueError("Pipeline must contain at least one stage")

        orders = [stage.order for stage in value]
        if len(orders) != len(set(orders)):
            raise ValueError("Stage order values must be unique")

        return value


class StageRead(BaseModel):
    id: int
    name: str
    command: str
    order: int
    timeout_seconds: int | None

    model_config = ConfigDict(from_attributes=True)


class PipelineRead(BaseModel):
    id: int
    name: str
    description: str | None
    max_retries: int
    created_at: datetime
    stages: list[StageRead]

    model_config = ConfigDict(from_attributes=True)


class StageRunRead(BaseModel):
    id: int
    stage_name: str
    command: str
    status: str
    output: str | None
    exit_code: int | None
    started_at: datetime | None
    finished_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class PipelineRunRead(BaseModel):
    id: int
    pipeline_id: int
    status: str
    retry_count: int
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    stage_runs: list[StageRunRead]

    model_config = ConfigDict(from_attributes=True)
