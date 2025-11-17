from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import pdfplumber
from docx import Document
import io
from embeddings import generate_embedding
from db import insert_proposal
from models import ProposalResponse

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

@router.post("/ingest", response_model=ProposalResponse)
async def ingest_proposal(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None)
):
    """
    Ingest a new R&D proposal document
    
    Accepts PDF or DOCX files, extracts text, generates embeddings,
    and stores in the database for future novelty comparisons.
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
    
    # Use provided title or filename
    proposal_title = title if title else file.filename
    
    # Generate embedding
    try:
        embedding = generate_embedding(full_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")
    
    # Store in database
    try:
        proposal_id = await insert_proposal(proposal_title, full_text, embedding)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing proposal: {str(e)}")
    
    return ProposalResponse(
        id=proposal_id,
        title=proposal_title,
        message=f"Proposal '{proposal_title}' ingested successfully"
    )
