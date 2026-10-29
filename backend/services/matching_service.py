from typing import Dict, Any
from services.embedding_service import compute_semantic_similarity
from services.parsing_service import SKILLS_TAXONOMY
from rapidfuzz import fuzz

def calculate_skill_overlap(resume_skills: list, required_skills: list) -> float:
    """Calculate skill overlap score using fuzzy matching"""
    if not required_skills:
        return 1.0  # No skills required, perfect match
    
    if not resume_skills:
        return 0.0  # No skills in resume
    
    matched_skills = 0
    for req_skill in required_skills:
        # Check for exact or fuzzy match
        for res_skill in resume_skills:
            similarity = fuzz.ratio(req_skill.lower(), res_skill.lower())
            if similarity >= 80:  # 80% similarity threshold
                matched_skills += 1
                break
    
    return matched_skills / len(required_skills)

def calculate_experience_score(resume_experience: list, min_years: float) -> float:
    """Calculate experience score based on years of relevant experience"""
    if min_years == 0:
        return 1.0  # No experience required, perfect match
    
    if not resume_experience:
        return 0.0  # No experience listed
    
    # Simple heuristic: count number of experience entries
    # In production, parse actual dates and calculate years
    experience_years = len(resume_experience) * 2  # Assume ~2 years per position
    
    if experience_years >= min_years:
        return 1.0
    
    # Normalize: partial credit for partial experience
    return min(experience_years / min_years, 1.0)

def calculate_match_score(match_id: int, db) -> Dict[str, Any]:
    """
    Calculate composite ATS score for a match
    Formula: 0.5 * semantic_score + 0.3 * skill_score + 0.2 * experience_score
    """
    from models import Match, Resume, Job
    
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        return {"error": "Match not found"}
    
    resume = db.query(Resume).filter(Resume.id == match.resume_id).first()
    job = db.query(Job).filter(Job.id == match.job_id).first()
    
    if not resume or not job:
        return {"error": "Resume or Job not found"}
    
    # Use translated text if available, otherwise raw text
    resume_text = resume.translated_text if resume.translated_text else resume.raw_text
    jd_text = job.jd_raw
    
    # Calculate semantic score
    semantic_score = compute_semantic_similarity(resume_text, jd_text)
    
    # Calculate skill overlap score
    resume_skills = resume.structured.get("skills", []) if resume.structured else []
    required_skills = job.required_skills if job.required_skills else []
    skill_score = calculate_skill_overlap(resume_skills, required_skills)
    
    # Calculate experience score
    resume_experience = resume.structured.get("experience", []) if resume.structured else []
    min_years = job.min_experience_years if job.min_experience_years else 0
    experience_score = calculate_experience_score(resume_experience, min_years)
    
    # Composite score
    ats_score = 0.5 * semantic_score + 0.3 * skill_score + 0.2 * experience_score
    
    # Update match in database
    match.semantic_score = float(semantic_score)
    match.skill_score = float(skill_score)
    match.experience_score = float(experience_score)
    match.ats_score = float(ats_score)
    
    db.commit()
    
    return {
        "semantic_score": float(semantic_score),
        "skill_score": float(skill_score),
        "experience_score": float(experience_score),
        "ats_score": float(ats_score)
    }
