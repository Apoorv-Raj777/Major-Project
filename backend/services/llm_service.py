import httpx
import json
from typing import Optional

OLLAMA_BASE_URL = "http://localhost:11434"

async def generate_feedback_suggestion(match, job) -> str:
    """
    Generate constructive feedback suggestion using local Ollama LLM
    """
    try:
        # Prepare prompt
        prompt = f"""
        You are an HR assistant helping recruiters provide constructive feedback to job applicants.
        
        Job Title: {job.title}
        Job Description: {job.description}
        Required Skills: {', '.join(job.required_skills)}
        
        Candidate's Match Scores:
        - Semantic Match: {match.semantic_score:.2f}
        - Skill Match: {match.skill_score:.2f}
        - Experience Match: {match.experience_score:.2f}
        - Overall ATS Score: {match.ats_score:.2f}
        
        Verification Report: {json.dumps(match.verification_report, indent=2) if match.verification_report else "N/A"}
        
        Please provide a brief, constructive feedback message (2-3 sentences) highlighting:
        1. What the candidate did well
        2. Key skills or experience they're missing
        3. A specific suggestion for improvement
        
        Keep it professional, encouraging, and actionable.
        """
        
        # Call Ollama API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": "llama3.2:3b",  # or "phi3:mini"
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 200
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                print(f"Error calling Ollama: {response.status_code}")
                return "Unable to generate AI suggestion at this time."
                
    except Exception as e:
        print(f"Error generating feedback suggestion: {e}")
        return "Unable to generate AI suggestion at this time."

def check_ollama_available() -> bool:
    """Check if Ollama service is available"""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return response.status_code == 200
    except:
        return False
