from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Match, Resume, LinkedInProfile, User
from schemas import VerificationReport
from auth import get_current_user, get_current_recruiter
from services.verification_service import verify_resume_against_linkedin

router = APIRouter()

@router.post("/verify/{match_id}", response_model=VerificationReport)
async def verify_candidate(
    match_id: int,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    # Get match
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Verify authorization
    from models import Job
    job = db.query(Job).filter(Job.id == match.job_id).first()
    if job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to verify this candidate"
        )
    
    # Get resume and LinkedIn profile
    resume = db.query(Resume).filter(Resume.id == match.resume_id).first()
    linkedin = db.query(LinkedInProfile).filter(
        LinkedInProfile.applicant_id == resume.applicant_id
    ).first()
    
    if not linkedin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LinkedIn profile not found for this applicant. Cannot perform verification."
        )
    
    # Perform verification
    verification_report = verify_resume_against_linkedin(
        resume.structured,
        linkedin.structured
    )
    
    # Update match with verification report
    match.verification_report = verification_report
    db.commit()
    
    return verification_report
