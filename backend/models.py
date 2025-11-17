from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ProposalBase(BaseModel):
    title: str = Field(..., description="Proposal title")
    full_text: str = Field(..., description="Full proposal text content")

class ProposalCreate(ProposalBase):
    pass

class ProposalResponse(BaseModel):
    id: int
    title: str
    message: str = "Proposal ingested successfully"
    
    class Config:
        from_attributes = True

class NoveltyRequest(BaseModel):
    text: str = Field(..., description="Proposal text to check for novelty", min_length=10)

class SimilarProposal(BaseModel):
    id: int
    title: str
    similarity: float = Field(..., description="Similarity score (0-1)")

class NoveltyResponse(BaseModel):
    novelty_score: float = Field(..., description="Novelty score (0-100)")
    similar_proposals: List[SimilarProposal]
    total_proposals_checked: int
    interpretation: str

class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    model_loaded: bool
    total_proposals: int
