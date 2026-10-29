from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Auth Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str  # 'recruiter' or 'applicant'

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Job Schemas
class JobBase(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    min_experience_years: Optional[float] = 0

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: int
    recruiter_id: int
    jd_raw: str
    jd_structured: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Resume Schemas
class ExperienceItem(BaseModel):
    title: str
    company: str
    start: str
    end: Optional[str] = None
    description: Optional[str] = None

class EducationItem(BaseModel):
    degree: str
    institution: str
    year: str

class ProjectItem(BaseModel):
    title: str
    description: Optional[str] = None

class ResumeStructured(BaseModel):
    name: Optional[str] = None
    skills: List[str] = []
    experience: List[ExperienceItem] = []
    education: List[EducationItem] = []
    projects: List[ProjectItem] = []

class ResumeBase(BaseModel):
    file_name: str

class ResumeCreate(ResumeBase):
    pass

class Resume(ResumeBase):
    id: int
    applicant_id: int
    file_path: str
    file_hash: str
    raw_text: Optional[str] = None
    translated_text: Optional[str] = None
    structured: Optional[ResumeStructured] = None
    language: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Match Schemas
class VerificationReport(BaseModel):
    unverified_skills: List[str] = []
    timeline_flags: List[str] = []
    verified_skill_pct: float

class MatchBase(BaseModel):
    resume_id: int
    job_id: int

class Match(MatchBase):
    id: int
    semantic_score: Optional[float] = None
    skill_score: Optional[float] = None
    experience_score: Optional[float] = None
    ats_score: Optional[float] = None
    verification_report: Optional[VerificationReport] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class MatchWithDetails(Match):
    resume: Resume
    job: Job

# Personality Schemas
class PersonalityScores(BaseModel):
    id: int
    applicant_id: int
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Feedback Schemas
class FeedbackBase(BaseModel):
    job_id: int
    resume_id: int
    rejection_reason: Optional[str] = None
    suggestions: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    created_by: int
    is_llm_assisted: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# LinkedIn Profile Schemas
class LinkedInProfileBase(BaseModel):
    file_name: str
    consent_given: bool = False

class LinkedInProfileCreate(LinkedInProfileBase):
    pass

class LinkedInProfile(LinkedInProfileBase):
    id: int
    applicant_id: int
    file_path: str
    raw_text: Optional[str] = None
    structured: Optional[dict] = None
    consent_given_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
