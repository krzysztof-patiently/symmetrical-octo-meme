from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints
from pydantic import Field as PydanticField
from sqlmodel import Field, SQLModel

Description = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


def utcnow() -> datetime:
    return datetime.now(UTC)


class JobStatus(StrEnum):
    TODO = "TODO"
    DONE = "DONE"


class Location(BaseModel):
    latitude: float = PydanticField(ge=-90, le=90)
    longitude: float = PydanticField(ge=-180, le=180)


class Job(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    description: str
    status: JobStatus = JobStatus.TODO
    # stored flat; the API exposes them as a nested Location
    latitude: float
    longitude: float
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class JobCreate(BaseModel):
    description: Description
    status: JobStatus = JobStatus.TODO
    location: Location


class JobUpdate(BaseModel):
    # only the status can change after creation
    model_config = ConfigDict(extra="forbid")

    status: JobStatus


class JobRead(BaseModel):
    id: int
    description: str
    status: JobStatus
    location: Location
    created_at: datetime
    updated_at: datetime
