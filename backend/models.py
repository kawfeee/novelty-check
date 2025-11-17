from pydantic import BaseModel, Field
from typing import List, Dict

class NoveltyCheckRequest(BaseModel):
    application_number: str = Field(..., description="Unique application identifier", min_length=1)
    extracted_text: str = Field(..., description="Extracted proposal text content", min_length=10)

class SimilarProposal(BaseModel):
    application_number: str
    similarity_percentage: float = Field(..., description="Similarity percentage (0-100)")

class NoveltyCheckResponse(BaseModel):
    application_number: str
    novelty_score: float = Field(..., description="Novelty score (0-100)")
    total_proposals_checked: int
    similar_proposals: List[SimilarProposal] = Field(..., description="List of similar proposals with similarity percentages")
