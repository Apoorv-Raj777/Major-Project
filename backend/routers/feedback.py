from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Feedback, Job, Resume, User
from schemas import FeedbackCreate, Feedback as FeedbackSchema
from auth import get_current_user, get_current_recruiter

router = APIRouter()

@router.post("/", response_model=FeedbackSchema)
async def create_feedback(
    feedback: FeedbackCreate,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    # Verify job exists and belongs to recruiter
    job = db.query(Job).filter(Job.id == feedback.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add feedback for this job"
        )
    
    # Verify resume exists
    resume = db.query(Resume).filter(Resume.id == feedback.resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    db_feedback = Feedback(
        job_id=feedback.job_id,
        resume_id=feedback.resume_id,
        rejection_reason=feedback.rejection_reason,
        suggestions=feedback.suggestions,
        created_by=current_user.id,
        is_llm_assisted=False
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    return db_feedback

@router.get("/job/{job_id}", response_model=List[FeedbackSchema])
async def get_feedback_for_job(
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
            detail="Not authorized to view feedback for this job"
        )
    
    feedback_list = db.query(Feedback).filter(Feedback.job_id == job_id).all()
    
    return feedback_list

@router.get("/resume/{resume_id}", response_model=List[FeedbackSchema])
async def get_feedback_for_resume(
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
    
    # Applicants can only view their own feedback
    if current_user.role == "applicant" and resume.applicant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view feedback for this resume"
        )
    
    feedback_list = db.query(Feedback).filter(Feedback.resume_id == resume_id).all()
    
    return feedback_list

@router.post("/generate-suggestion/{match_id}")
async def generate_llm_suggestion(
    match_id: int,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Generate AI-assisted feedback suggestion using local Ollama"""
    from services.llm_service import generate_feedback_suggestion
    
    # Get match details
    from models import Match
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Verify authorization
    job = db.query(Job).filter(Job.id == match.job_id).first()
    if job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to generate suggestion for this match"
        )
    
    # Generate suggestion
    suggestion = generate_feedback_suggestion(match, job)
    
    return {"suggestion": suggestion}
