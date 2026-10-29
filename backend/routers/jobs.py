from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Job, User
from schemas import JobCreate, Job as JobSchema
from auth import get_current_user, get_current_recruiter
from services.parsing_service import parse_jd

router = APIRouter()

@router.post("/", response_model=JobSchema)
async def create_job(
    job: JobCreate,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    # Parse JD and extract structured data
    jd_raw = job.description
    jd_structured = parse_jd(jd_raw, job.required_skills, job.min_experience_years)
    
    db_job = Job(
        recruiter_id=current_user.id,
        title=job.title,
        description=job.description,
        jd_raw=jd_raw,
        jd_structured=jd_structured,
        required_skills=job.required_skills,
        min_experience_years=job.min_experience_years
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return db_job

@router.get("/", response_model=List[JobSchema])
async def get_jobs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "recruiter":
        # Recruiters see only their jobs
        jobs = db.query(Job).filter(Job.recruiter_id == current_user.id).offset(skip).limit(limit).all()
    else:
        # Applicants see all jobs
        jobs = db.query(Job).offset(skip).limit(limit).all()
    
    return jobs

@router.get("/{job_id}", response_model=JobSchema)
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Recruiters can only view their own jobs
    if current_user.role == "recruiter" and job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this job"
        )
    
    return job

@router.put("/{job_id}", response_model=JobSchema)
async def update_job(
    job_id: int,
    job: JobCreate,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if db_job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this job"
        )
    
    # Reparse JD
    jd_structured = parse_jd(job.description, job.required_skills, job.min_experience_years)
    
    db_job.title = job.title
    db_job.description = job.description
    db_job.jd_raw = job.description
    db_job.jd_structured = jd_structured
    db_job.required_skills = job.required_skills
    db_job.min_experience_years = job.min_experience_years
    
    db.commit()
    db.refresh(db_job)
    
    return db_job

@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if db_job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this job"
        )
    
    db.delete(db_job)
    db.commit()
    
    return {"message": "Job deleted successfully"}
