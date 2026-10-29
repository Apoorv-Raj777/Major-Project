import pdfplumber
import docx
import spacy
import re
from typing import Dict, List, Any
from rapidfuzz import process, fuzz

# Load spaCy models
nlp_en = spacy.load("en_core_web_sm")
nlp_multi = spacy.load("xx_ent_wiki_sm")

# Skills taxonomy (simplified ESCO sample - in production, load full ESCO/O*NET)
SKILLS_TAXONOMY = [
    "python", "javascript", "java", "c++", "c#", "go", "rust", "typescript",
    "react", "angular", "vue", "node.js", "django", "flask", "spring", "express",
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ansible",
    "git", "ci/cd", "jenkins", "github", "gitlab",
    "machine learning", "deep learning", "nlp", "computer vision", "data science",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "agile", "scrum", "kanban", "jira", "confluence",
    "rest api", "graphql", "microservices", "graphql",
    "html", "css", "sass", "tailwind", "bootstrap"
]

# Section headers (English, Spanish, German)
SECTION_HEADERS = {
    "experience": ["experience", "experiencia", "erfahrung", "work history", "employment"],
    "education": ["education", "educación", "bildung", "academic", "qualifications"],
    "skills": ["skills", "habilidades", "fähigkeiten", "competencies", "technologies"],
    "projects": ["projects", "proyectos", "projekte", "portfolio"]
}

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using pdfplumber"""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""
    return text

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx"""
    text = ""
    try:
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
        return ""
    return text

def detect_section(text: str, section_type: str) -> int:
    """Find the line number where a section starts"""
    lines = text.lower().split('\n')
    headers = SECTION_HEADERS.get(section_type, [])
    
    for i, line in enumerate(lines):
        for header in headers:
            if header in line:
                return i
    return -1

def extract_skills(text: str) -> List[str]:
    """Extract skills using fuzzy matching against taxonomy"""
    found_skills = set()
    text_lower = text.lower()
    
    # Direct matches
    for skill in SKILLS_TAXONOMY:
        if skill.lower() in text_lower:
            found_skills.add(skill)
    
    # Fuzzy matches for typos/variants
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
    for word in words:
        if len(found_skills) >= 50:  # Limit to avoid noise
            break
        match = process.extractOne(word.lower(), SKILLS_TAXONOMY, scorer=fuzz.ratio)
        if match and match[1] >= 85:  # 85% similarity threshold
            found_skills.add(match[0])
    
    return list(found_skills)

def extract_experience(text: str) -> List[Dict[str, Any]]:
    """Extract work experience using NER and heuristics"""
    experiences = []
    doc = nlp_en(text)
    
    # Simple heuristic: look for patterns like "Title at Company (dates)"
    pattern = r'([A-Z][A-Za-z\s]+)\s+at\s+([A-Z][A-Za-z\s]+)\s*(?:\(|(\d{4}|\d{2}))'
    matches = re.finditer(pattern, text)
    
    for match in matches:
        experiences.append({
            "title": match.group(1).strip(),
            "company": match.group(2).strip(),
            "start": "",
            "end": "",
            "description": ""
        })
    
    return experiences

def extract_education(text: str) -> List[Dict[str, Any]]:
    """Extract education information"""
    education = []
    
    # Look for degree patterns
    pattern = r'(Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.A\.|M\.A\.).*?in\s+([A-Za-z\s]+?)(?:\s+at\s+([A-Za-z\s]+?))?'
    matches = re.finditer(pattern, text, re.IGNORECASE)
    
    for match in matches:
        education.append({
            "degree": match.group(0).strip(),
            "institution": match.group(3).strip() if match.group(3) else "",
            "year": ""
        })
    
    return education

def extract_projects(text: str) -> List[Dict[str, Any]]:
    """Extract project information"""
    projects = []
    
    # Simple heuristic: lines starting with project keywords
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if any(keyword in line.lower() for keyword in ["project", "app", "application", "system"]):
            projects.append({
                "title": line.strip(),
                "description": lines[i+1].strip() if i+1 < len(lines) else ""
            })
    
    return projects

def parse_resume(file_path: str) -> Dict[str, Any]:
    """Parse resume file and return structured data"""
    from services.translation_service import process_text
    
    # Extract text based on file type
    if file_path.endswith('.pdf'):
        raw_text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        raw_text = extract_text_from_docx(file_path)
    else:
        return {"error": "Unsupported file type"}
    
    if not raw_text:
        return {"error": "Could not extract text"}
    
    # Detect language and translate if needed
    text_processing = process_text(raw_text)
    
    # Extract structured components from translated text for consistency
    text_to_parse = text_processing["translated_text"]
    
    structured = {
        "name": "",
        "skills": extract_skills(text_to_parse),
        "experience": extract_experience(text_to_parse),
        "education": extract_education(text_to_parse),
        "projects": extract_projects(text_to_parse)
    }
    
    return {
        "raw_text": raw_text,
        "translated_text": text_processing["translated_text"],
        "structured": structured,
        "language": text_processing["language_code"]
    }

def parse_jd(description: str, required_skills: List[str], min_experience: float) -> Dict[str, Any]:
    """Parse job description and return structured data"""
    structured = {
        "required_skills": required_skills,
        "min_experience_years": min_experience,
        "skills": extract_skills(description),
        "qualifications": []
    }
    
    return structured

def parse_linkedin(file_path: str) -> Dict[str, Any]:
    """Parse LinkedIn PDF export (similar to resume but with LinkedIn-specific structure)"""
    from services.translation_service import process_text
    
    raw_text = extract_text_from_pdf(file_path)
    
    if not raw_text:
        return {"error": "Could not extract text"}
    
    # Detect language and translate if needed
    text_processing = process_text(raw_text)
    text_to_parse = text_processing["translated_text"]
    
    # LinkedIn has predictable sections
    structured = {
        "about_text": "",
        "skills": extract_skills(text_to_parse),
        "experience": extract_experience(text_to_parse),
        "education": extract_education(text_to_parse),
        "recommendations_text": ""
    }
    
    # Extract About section
    about_idx = detect_section(text_to_parse, "about") if "about" in text_to_parse.lower() else -1
    if about_idx >= 0:
        lines = text_to_parse.split('\n')
        structured["about_text"] = '\n'.join(lines[about_idx:about_idx+10])  # Take next 10 lines
    
    # Extract Recommendations
    if "recommendation" in text_to_parse.lower():
        rec_idx = text_to_parse.lower().find("recommendation")
        structured["recommendations_text"] = text_to_parse[rec_idx:rec_idx+500]
    
    return {
        "raw_text": raw_text,
        "structured": structured
    }
