from typing import Dict, List
from rapidfuzz import fuzz, process
from datetime import datetime

def verify_skills(resume_skills: List[str], linkedin_skills: List[str]) -> Dict:
    """
    Compare skills between resume and LinkedIn
    Returns: {
        "verified_skills": List[str],
        "unverified_skills": List[str],
        "verified_skill_pct": float
    }
    """
    if not resume_skills:
        return {
            "verified_skills": [],
            "unverified_skills": [],
            "verified_skill_pct": 0.0
        }
    
    if not linkedin_skills:
        return {
            "verified_skills": [],
            "unverified_skills": resume_skills,
            "verified_skill_pct": 0.0
        }
    
    verified_skills = []
    unverified_skills = []
    
    for res_skill in resume_skills:
        # Check for fuzzy match in LinkedIn skills
        match = process.extractOne(res_skill.lower(), [s.lower() for s in linkedin_skills], scorer=fuzz.ratio)
        if match and match[1] >= 80:  # 80% similarity threshold
            verified_skills.append(res_skill)
        else:
            unverified_skills.append(res_skill)
    
    verified_pct = len(verified_skills) / len(resume_skills) if resume_skills else 0.0
    
    return {
        "verified_skills": verified_skills,
        "unverified_skills": unverified_skills,
        "verified_skill_pct": verified_pct
    }

def parse_date(date_str: str) -> datetime:
    """Parse various date formats"""
    if not date_str:
        return None
    
    formats = ["%Y-%m", "%Y/%m", "%m-%Y", "%m/%Y", "%Y", "%b %Y", "%B %Y"]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def verify_timeline(resume_experience: List[Dict], linkedin_experience: List[Dict]) -> List[str]:
    """
    Compare experience timelines between resume and LinkedIn
    Returns list of timeline flags (inconsistencies)
    """
    flags = []
    tolerance_months = 3  # Allow 3 months difference
    
    if not resume_experience or not linkedin_experience:
        return flags
    
    # Match positions by company/title
    for res_exp in resume_experience:
        res_company = res_exp.get("company", "").lower()
        res_title = res_exp.get("title", "").lower()
        res_start = parse_date(res_exp.get("start", ""))
        res_end = parse_date(res_exp.get("end", ""))
        
        # Find matching LinkedIn entry
        for li_exp in linkedin_experience:
            li_company = li_exp.get("company", "").lower()
            li_title = li_exp.get("title", "").lower()
            li_start = parse_date(li_exp.get("start", ""))
            li_end = parse_date(li_exp.get("end", ""))
            
            # Check if this is the same position
            company_match = fuzz.ratio(res_company, li_company) >= 85
            title_match = fuzz.ratio(res_title, li_title) >= 85
            
            if company_match or title_match:
                # Compare dates
                if res_start and li_start:
                    diff_months = abs((res_start.year - li_start.year) * 12 + (res_start.month - li_start.month))
                    if diff_months > tolerance_months:
                        flags.append(
                            f"Start date mismatch for {res_exp.get('title')} at {res_exp.get('company')}: "
                            f"resume says {res_exp.get('start')}, LinkedIn says {li_exp.get('start')}"
                        )
                
                if res_end and li_end:
                    diff_months = abs((res_end.year - li_end.year) * 12 + (res_end.month - li_end.month))
                    if diff_months > tolerance_months:
                        flags.append(
                            f"End date mismatch for {res_exp.get('title')} at {res_exp.get('company')}: "
                            f"resume says {res_exp.get('end')}, LinkedIn says {li_exp.get('end')}"
                        )
                
                break
    
    return flags

def verify_resume_against_linkedin(resume_structured: Dict, linkedin_structured: Dict) -> Dict:
    """
    Perform full verification of resume against LinkedIn profile
    Returns: {
        "unverified_skills": List[str],
        "timeline_flags": List[str],
        "verified_skill_pct": float
    }
    """
    resume_skills = resume_structured.get("skills", []) if resume_structured else []
    linkedin_skills = linkedin_structured.get("skills", []) if linkedin_structured else []
    
    resume_experience = resume_structured.get("experience", []) if resume_structured else []
    linkedin_experience = linkedin_structured.get("experience", []) if linkedin_structured else []
    
    # Verify skills
    skill_verification = verify_skills(resume_skills, linkedin_skills)
    
    # Verify timeline
    timeline_flags = verify_timeline(resume_experience, linkedin_experience)
    
    return {
        "unverified_skills": skill_verification["unverified_skills"],
        "timeline_flags": timeline_flags,
        "verified_skill_pct": skill_verification["verified_skill_pct"]
    }
