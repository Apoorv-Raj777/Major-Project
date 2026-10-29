from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

# Load multilingual embedding model
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(MODEL_NAME)

def get_embedding(text: str) -> np.ndarray:
    """Generate embedding for text using multilingual model"""
    if not text:
        return np.zeros(384)  # Default dimension for this model
    
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two embeddings"""
    if a is None or b is None:
        return 0.0
    
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)

def compute_semantic_similarity(text1: str, text2: str) -> float:
    """Compute semantic similarity between two texts"""
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    return cosine_similarity(emb1, emb2)

def batch_get_embeddings(texts: List[str]) -> List[np.ndarray]:
    """Generate embeddings for multiple texts efficiently"""
    if not texts:
        return []
    
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings
