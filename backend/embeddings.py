from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

# Load the model once at module level for efficiency
MODEL_NAME = "all-mpnet-base-v2"
model = None

def load_model():
    """Load the sentence transformer model"""
    global model
    if model is None:
        model = SentenceTransformer(MODEL_NAME)
    return model

def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for given text
    
    Args:
        text: Input text to embed
        
    Returns:
        List of floats representing the embedding vector (768 dimensions)
    """
    model = load_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity score between -1 and 1
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    
    return float(dot_product / (norm_v1 * norm_v2))

def calculate_novelty_score(similarities: List[float]) -> float:
    """
    Calculate novelty score from similarity scores
    
    Args:
        similarities: List of similarity scores (0-1)
        
    Returns:
        Novelty score (0-100)
    """
    if not similarities:
        return 100.0  # Completely novel if no similar documents
    
    avg_similarity = sum(similarities) / len(similarities)
    novelty = (1 - avg_similarity) * 100
    return round(novelty, 2)
