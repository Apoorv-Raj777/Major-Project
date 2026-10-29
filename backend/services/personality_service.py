from transformers import pipeline
from typing import Dict, Optional

# Load personality classification model
# Using a free Hugging Face model for Big Five personality inference
MODEL_NAME = "Minej/bert-base-personality"

def load_personality_model():
    """Load the personality classification model"""
    try:
        classifier = pipeline("text-classification", model=MODEL_NAME, top_k=None)
        return classifier
    except Exception as e:
        print(f"Error loading personality model: {e}")
        return None

def infer_big_five(linkedin_structured: dict) -> Optional[Dict[str, float]]:
    """
    Infer Big Five personality traits from LinkedIn profile text
    Returns: {
        "openness": float,
        "conscientiousness": float,
        "extraversion": float,
        "agreeableness": float,
        "neuroticism": float
    }
    """
    classifier = load_personality_model()
    if not classifier:
        return None
    
    # Combine relevant text fields
    about_text = linkedin_structured.get("about_text", "")
    recommendations_text = linkedin_structured.get("recommendations_text", "")
    combined_text = f"{about_text} {recommendations_text}"
    
    if not combined_text or len(combined_text.strip()) < 50:
        return None
    
    try:
        # Run inference
        results = classifier(combined_text[:512])  # Limit to 512 tokens
        
        # Map model outputs to Big Five traits
        # Note: The specific mapping depends on the model's label format
        # This is a simplified version - adjust based on actual model output
        
        personality_scores = {
            "openness": 0.5,
            "conscientiousness": 0.5,
            "extraversion": 0.5,
            "agreeableness": 0.5,
            "neuroticism": 0.5
        }
        
        # Parse results and map to traits
        for result in results:
            label = result.get("label", "").lower()
            score = result.get("score", 0.5)
            
            if "open" in label:
                personality_scores["openness"] = score
            elif "conscien" in label:
                personality_scores["conscientiousness"] = score
            elif "extra" in label:
                personality_scores["extraversion"] = score
            elif "agree" in label:
                personality_scores["agreeableness"] = score
            elif "neuro" in label:
                personality_scores["neuroticism"] = score
        
        return personality_scores
        
    except Exception as e:
        print(f"Error inferring personality: {e}")
        return None

# Fallback: Lexicon-based approach using free lexicons
def infer_big_five_lexicon(text: str) -> Dict[str, float]:
    """
    Fallback lexicon-based Big Five inference
    Uses simplified word lists for each trait
    """
    # Simplified lexicons (in production, use full NRC/Big-Five lexicon)
    lexicons = {
        "openness": ["creative", "innovative", "curious", "artistic", "imaginative"],
        "conscientiousness": ["organized", "disciplined", "reliable", "thorough", "meticulous"],
        "extraversion": ["outgoing", "social", "energetic", "assertive", "enthusiastic"],
        "agreeableness": ["cooperative", "helpful", "friendly", "trustworthy", "compassionate"],
        "neuroticism": ["anxious", "sensitive", "moody", "tense", "worried"]
    }
    
    text_lower = text.lower()
    scores = {}
    
    for trait, words in lexicons.items():
        count = sum(1 for word in words if word in text_lower)
        # Normalize to 0-1 range
        scores[trait] = min(count / 5.0, 1.0)
    
    return scores
