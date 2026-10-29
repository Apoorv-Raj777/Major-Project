from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import os
from database import get_db
from models import LinkedInProfile, PersonalityScores, User
from schemas import LinkedInProfileCreate, LinkedInProfile as LinkedInProfileSchema, PersonalityScores as PersonalityScoresSchema
from auth import get_current_user, get_current_applicant
from services.parsing_service import parse_linkedin
from services.personality_service import infer_big_five

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-linkedin", response_model=LinkedInProfileSchema)
async def upload_linkedin(
    file: UploadFile = File(...),
    consent_given: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_applicant),
    db: Session = Depends(get_db)
):
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed for LinkedIn exports"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Check file size (5MB limit)
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit"
        )
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"linkedin_{current_user.id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Create LinkedIn profile record
    consent_timestamp = datetime.utcnow() if consent_given else None
    db_linkedin = LinkedInProfile(
        applicant_id=current_user.id,
        file_name=file.filename,
        file_path=file_path,
        consent_given_at=consent_timestamp
    )
    db.add(db_linkedin)
    db.commit()
    db.refresh(db_linkedin)
    
    # Add processing task to background
    background_tasks.add_task(process_linkedin, db_linkedin.id, file_path, consent_given, db)
    
    return db_linkedin

def process_linkedin(linkedin_id: int, file_path: str, consent_given: bool, db: Session):
    """Background task to parse LinkedIn and infer personality"""
    from database import SessionLocal
    db = SessionLocal()
    
    try:
        linkedin = db.query(LinkedInProfile).filter(LinkedInProfile.id == linkedin_id).first()
        if linkedin:
            # Parse the LinkedIn profile
            parsed_data = parse_linkedin(file_path)
            linkedin.raw_text = parsed_data.get("raw_text")
            linkedin.structured = parsed_data.get("structured")
            db.commit()
            
            # Infer personality if consent was given
            if consent_given:
                personality_scores = infer_big_five(parsed_data.get("structured"))
                if personality_scores:
                    db_personality = PersonalityScores(
                        applicant_id=linkedin.applicant_id,
                        linkedin_profile_id=linkedin.id,
                        **personality_scores
                    )
                    db.add(db_personality)
                    db.commit()
    finally:
        db.close()

@router.get("/my-profile", response_model=LinkedInProfileSchema)
async def get_my_linkedin(
    current_user: User = Depends(get_current_applicant),
    db: Session = Depends(get_db)
):
    linkedin = db.query(LinkedInProfile).filter(
        LinkedInProfile.applicant_id == current_user.id
    ).first()
    
    if not linkedin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LinkedIn profile not found"
        )
    
    return linkedin

@router.get("/my-personality", response_model=PersonalityScoresSchema)
async def get_my_personality(
    current_user: User = Depends(get_current_applicant),
    db: Session = Depends(get_db)
):
    personality = db.query(PersonalityScores).filter(
        PersonalityScores.applicant_id == current_user.id
    ).first()
    
    if not personality:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personality scores not found. Please upload LinkedIn profile with consent."
        )
    
    return personality
