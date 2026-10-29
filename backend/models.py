from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'recruiter' or 'applicant'
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    jobs_posted = relationship("Job", back_populates="recruiter")
    resumes = relationship("Resume", back_populates="applicant")
    linkedin_profiles = relationship("LinkedInProfile", back_populates="applicant")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    jd_raw = Column(Text, nullable=False)
    jd_structured = Column(JSON)  # Parsed and structured JD
    required_skills = Column(JSON)  # List of required skills
    min_experience_years = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recruiter = relationship("User", back_populates="jobs_posted")
    matches = relationship("Match", back_populates="job")
    feedback_entries = relationship("Feedback", back_populates="job")

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_hash = Column(String, unique=True, index=True)  # SHA256 for deduplication
    raw_text = Column(Text)
    translated_text = Column(Text)  # English translation if not already English
    structured = Column(JSON)  # Parsed and structured resume
    language = Column(String)  # Detected language code
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    applicant = relationship("User", back_populates="resumes")
    matches = relationship("Match", back_populates="resume")
    feedback_entries = relationship("Feedback", back_populates="resume")

class LinkedInProfile(Base):
    __tablename__ = "linkedin_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    raw_text = Column(Text)
    structured = Column(JSON)  # Parsed and structured LinkedIn data
    consent_given_at = Column(DateTime)  # When user consented to behavioural analysis
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    applicant = relationship("User", back_populates="linkedin_profiles")

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    semantic_score = Column(Float)  # 0-1
    skill_score = Column(Float)  # 0-1
    experience_score = Column(Float)  # 0-1
    ats_score = Column(Float)  # Composite 0-1
    verification_report = Column(JSON)  # Skill/timeline verification results
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="matches")
    job = relationship("Job", back_populates="matches")

class PersonalityScores(Base):
    __tablename__ = "personality_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    linkedin_profile_id = Column(Integer, ForeignKey("linkedin_profiles.id"))
    openness = Column(Float)  # 0-1
    conscientiousness = Column(Float)  # 0-1
    extraversion = Column(Float)  # 0-1
    agreeableness = Column(Float)  # 0-1
    neuroticism = Column(Float)  # 0-1
    created_at = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    rejection_reason = Column(Text)
    suggestions = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_llm_assisted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="feedback_entries")
    resume = relationship("Resume", back_populates="feedback_entries")

class FairnessMetrics(Base):
    __tablename__ = "fairness_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    language_code = Column(String, index=True)
    average_ats_score = Column(Float)
    total_resumes = Column(Integer)
    shortlisted_count = Column(Integer)
    shortlist_rate = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)
