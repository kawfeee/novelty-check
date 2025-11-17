from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import pdfplumber
from docx import Document
import io
from embeddings import generate_embedding, calculate_novelty_score
from db import find_similar_proposals, count_proposals
from models import NoveltyRequest, NoveltyResponse, SimilarProposal

router = APIRouter()

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting PDF: {str(e)}")

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        doc = Document(io.BytesIO(file_content))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting DOCX: {str(e)}")

def get_interpretation(score: float) -> str:
    """Get human-readable interpretation of novelty score"""
    if score >= 80:
        return "Highly Novel - This proposal is very unique compared to existing proposals"
    elif score >= 60:
        return "Novel - This proposal has significant unique elements"
    elif score >= 40:
        return "Moderately Novel - This proposal has some similarities to existing work"
    elif score >= 20:
        return "Low Novelty - This proposal is quite similar to existing proposals"
    else:
        return "Very Low Novelty - This proposal is very similar to existing proposals"

@router.post("/novelty", response_model=NoveltyResponse)
async def check_novelty(request: NoveltyRequest):
    """
    Check novelty score for a proposal text
    
    Compares the input text against stored proposals using semantic similarity
    and returns a novelty score (0-100) along with the most similar proposals.
    """
    # Validate input
    if len(request.text) < 10:
        raise HTTPException(
            status_code=400,
            detail="Text is too short. Please provide at least 10 characters."
        )
    
    # Check if database has any proposals
    total_proposals = await count_proposals()
    if total_proposals == 0:
        return NoveltyResponse(
            novelty_score=100.0,
            similar_proposals=[],
            total_proposals_checked=0,
            interpretation="No proposals in database - completely novel by default"
        )
    
    # Generate embedding for input text
    try:
        embedding = generate_embedding(request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")
    
    # Find similar proposals
    try:
        similar_proposals = await find_similar_proposals(embedding, limit=5)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar proposals: {str(e)}")
    
    # Calculate novelty score
    similarities = [p["similarity"] for p in similar_proposals]
    novelty_score = calculate_novelty_score(similarities)
    
    # Convert to response model
    similar_proposal_models = [
        SimilarProposal(**proposal) for proposal in similar_proposals
    ]
    
    return NoveltyResponse(
        novelty_score=novelty_score,
        similar_proposals=similar_proposal_models,
        total_proposals_checked=total_proposals,
        interpretation=get_interpretation(novelty_score)
    )

@router.post("/novelty/file", response_model=NoveltyResponse)
async def check_novelty_from_file(file: UploadFile = File(...)):
    """
    Check novelty score for a proposal from an uploaded file
    
    Accepts PDF or DOCX files, extracts text, and compares against
    stored proposals to calculate novelty score.
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_extension = file.filename.lower().split(".")[-1]
    if file_extension not in ["pdf", "docx"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported"
        )
    
    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    # Extract text based on file type
    if file_extension == "pdf":
        full_text = extract_text_from_pdf(file_content)
    else:  # docx
        full_text = extract_text_from_docx(file_content)
    
    # Validate extracted text
    if not full_text or len(full_text) < 10:
        raise HTTPException(
            status_code=400,
            detail="Extracted text is too short or empty. Please check the file."
        )
    
    # Use the text-based novelty check
    return await check_novelty(NoveltyRequest(text=full_text))
