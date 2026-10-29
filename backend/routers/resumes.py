from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import hashlib
import os
from database import get_db
from models import Resume, User
from schemas import ResumeCreate, Resume as ResumeSchema
from auth import get_current_user, get_current_applicant
from services.parsing_service import parse_resume

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def compute_file_hash(file_content: bytes) -> str:
    return hashlib.sha256(file_content).hexdigest()

@router.post("/upload", response_model=ResumeSchema)
async def upload_resume(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_applicant),
    db: Session = Depends(get_db)
):
    # Validate file type
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are allowed"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Check file size (5MB limit)
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit"
        )
    
    # Compute file hash for deduplication
    file_hash = compute_file_hash(file_content)
    
    # Check for duplicate
    existing_resume = db.query(Resume).filter(Resume.file_hash == file_hash).first()
    if existing_resume:
        return existing_resume
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{current_user.id}_{file_hash}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Create resume record
    db_resume = Resume(
        applicant_id=current_user.id,
        file_name=file.filename,
        file_path=file_path,
        file_hash=file_hash
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    
    # Add parsing task to background
    background_tasks.add_task(process_resume, db_resume.id, file_path, db)
    
    return db_resume

def process_resume(resume_id: int, file_path: str, db: Session):
    """Background task to parse resume"""
    from database import SessionLocal
    db = SessionLocal()
    
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            # Parse the resume
            parsed_data = parse_resume(file_path)
            resume.raw_text = parsed_data.get("raw_text")
            resume.translated_text = parsed_data.get("translated_text")
            resume.structured = parsed_data.get("structured")
            resume.language = parsed_data.get("language")
            db.commit()
    finally:
        db.close()

@router.get("/", response_model=List[ResumeSchema])
async def get_resumes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_applicant),
    db: Session = Depends(get_db)
):
    resumes = db.query(Resume).filter(
        Resume.applicant_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return resumes

@router.get("/{resume_id}", response_model=ResumeSchema)
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_applicant),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if resume.applicant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this resume"
        )
    
    return resume
