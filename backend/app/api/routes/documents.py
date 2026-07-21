from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/documents", tags=["Documents"])

class DocumentMetadata(BaseModel):
    """Metadata for an uploaded document."""
    id: str
    filename: str
    content_type: str
    size_bytes: int
    title: Optional[str] = None
    description: Optional[str] = None
    status: str = "uploaded"  # uploaded, processing, indexed, failed
    chunk_count: int = 0
    uploaded_at: datetime

# In-memory store
DOCUMENTS_DB: dict[str, DocumentMetadata] = {}

@router.post("/upload", response_model=DocumentMetadata, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
) -> DocumentMetadata:
    """Upload a document and store its metadata."""
    doc_id = str(uuid.uuid4())
    
    size = file.size if getattr(file, "size", None) is not None else 0
    
    doc_meta = DocumentMetadata(
        id=doc_id,
        filename=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=size,
        title=title,
        description=description,
        status="uploaded",
        chunk_count=0,
        uploaded_at=datetime.now(timezone.utc)
    )
    
    DOCUMENTS_DB[doc_id] = doc_meta
    return doc_meta

@router.get("", response_model=List[DocumentMetadata])
async def list_documents() -> List[DocumentMetadata]:
    """List all uploaded documents."""
    return list(DOCUMENTS_DB.values())

@router.get("/{document_id}", response_model=DocumentMetadata)
async def get_document(document_id: str) -> DocumentMetadata:
    """Get document details."""
    doc = DOCUMENTS_DB.get(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found."
        )
    return doc

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str) -> None:
    """Delete a document."""
    if document_id not in DOCUMENTS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found."
        )
    del DOCUMENTS_DB[document_id]
