from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import Job, JobCreate, JobRead, JobUpdate, Location, utcnow

router = APIRouter(prefix="/jobs", tags=["jobs"])

SessionDep = Annotated[Session, Depends(get_session)]


def get_job_or_404(session: Session, job_id: int) -> Job:
    job = session.get(Job, job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "job not found")
    return job


def to_read(job: Job) -> JobRead:
    return JobRead(
        **job.model_dump(exclude={"latitude", "longitude"}),
        location=Location(latitude=job.latitude, longitude=job.longitude),
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_job(body: JobCreate, session: SessionDep) -> JobRead:
    job = Job(
        description=body.description,
        status=body.status,
        latitude=body.location.latitude,
        longitude=body.location.longitude,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return to_read(job)


@router.get("")
def list_jobs(session: SessionDep) -> list[JobRead]:
    return [to_read(job) for job in session.exec(select(Job).order_by(Job.id))]


@router.get("/{job_id}")
def get_job(job_id: int, session: SessionDep) -> JobRead:
    return to_read(get_job_or_404(session, job_id))


@router.patch("/{job_id}")
def update_job(job_id: int, body: JobUpdate, session: SessionDep) -> JobRead:
    job = get_job_or_404(session, job_id)
    if job.status != body.status:
        job.status = body.status
        job.updated_at = utcnow()
        session.add(job)
        session.commit()
        session.refresh(job)
    return to_read(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, session: SessionDep) -> None:
    session.delete(get_job_or_404(session, job_id))
    session.commit()
