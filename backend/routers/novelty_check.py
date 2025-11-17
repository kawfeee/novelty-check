from fastapi import APIRouter, HTTPException
from embeddings import generate_embedding, calculate_novelty_score
from db import insert_proposal, find_similar_proposals, count_proposals
from models import NoveltyCheckRequest, NoveltyCheckResponse

router = APIRouter()

@router.post("/novelty-check", response_model=NoveltyCheckResponse)
async def check_novelty(request: NoveltyCheckRequest):
    """
    Check novelty score for a proposal
    
    Accepts application_number and extracted_text, stores it in the database,
    compares against existing proposals, and returns novelty score with similar applications.
    """
    # Validate input
    if len(request.extracted_text) < 10:
        raise HTTPException(
            status_code=400,
            detail="Extracted text is too short. Please provide at least 10 characters."
        )
    
    if not request.application_number or not request.application_number.strip():
        raise HTTPException(
            status_code=400,
            detail="Application number is required and cannot be empty."
        )
    
    # Generate embedding for input text
    try:
        embedding = generate_embedding(request.extracted_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")
    
    # Store the proposal in the database (upsert if application_number exists)
    try:
        await insert_proposal(request.application_number, request.extracted_text, embedding)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing proposal: {str(e)}")
    
    # Get total count of proposals
    try:
        total_proposals = await count_proposals()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error counting proposals: {str(e)}")
    
    # Find similar proposals (exclude the current one)
    try:
        similar_proposals_data = await find_similar_proposals(
            embedding, 
            exclude_application_number=request.application_number,
            limit=5
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar proposals: {str(e)}")
    
    # Calculate novelty score
    similarities = [p["similarity"] for p in similar_proposals_data]
    novelty_score = calculate_novelty_score(similarities)
    
    # Format similar proposals with similarity percentages
    similar_proposals_formatted = [
        {
            "application_number": p["application_number"],
            "similarity_percentage": round(p["similarity"] * 100, 2)
        }
        for p in similar_proposals_data
    ]
    
    return NoveltyCheckResponse(
        application_number=request.application_number,
        novelty_score=novelty_score,
        total_proposals_checked=total_proposals,
        similar_proposals=similar_proposals_formatted
    )
