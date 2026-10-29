from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Match, Job, Resume, User
from schemas import Match as MatchSchema, MatchWithDetails
from auth import get_current_user, get_current_recruiter
from services.matching_service import calculate_match_score

router = APIRouter()

@router.post("/{job_id}/{resume_id}", response_model=MatchSchema)
async def create_match(
    job_id: int,
    resume_id: int,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from database import SessionLocal
    
    # Verify job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Verify resume exists
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Check if match already exists
    existing_match = db.query(Match).filter(
        Match.job_id == job_id,
        Match.resume_id == resume_id
    ).first()
    
    if existing_match:
        return existing_match
    
    # Create match record
    db_match = Match(
        job_id=job_id,
        resume_id=resume_id
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    
    # Calculate score in background with fresh DB session
    def calculate_with_fresh_db(match_id):
        fresh_db = SessionLocal()
        try:
            calculate_match_score(match_id, fresh_db)
        finally:
            fresh_db.close()
    
    background_tasks.add_task(calculate_with_fresh_db, db_match.id)
    
    return db_match

@router.get("/job/{job_id}", response_model=List[MatchWithDetails])
async def get_matches_for_job(
    job_id: int,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    # Verify job exists and belongs to recruiter
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view matches for this job"
        )
    
    matches = db.query(Match).filter(Match.job_id == job_id).order_by(Match.ats_score.desc()).all()
    
    return matches

@router.get("/resume/{resume_id}", response_model=List[MatchSchema])
async def get_matches_for_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify resume exists
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Applicants can only view their own matches
    if current_user.role == "applicant" and resume.applicant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view matches for this resume"
        )
    
    matches = db.query(Match).filter(Match.resume_id == resume_id).all()
    
    return matches

@router.get("/{match_id}", response_model=MatchWithDetails)
async def get_match(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Verify authorization
    if current_user.role == "recruiter":
        job = db.query(Job).filter(Job.id == match.job_id).first()
        if job.recruiter_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this match"
            )
    elif current_user.role == "applicant":
        resume = db.query(Resume).filter(Resume.id == match.resume_id).first()
        if resume.applicant_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this match"
            )
    
    return match
