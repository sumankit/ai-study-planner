import os, shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentType, ProcessingStatus
from app.schemas.document import DocumentOut
from app.services.ingestion.pdf_extractor import extract_pdf
from app.services.ingestion.ppt_extractor import extract_ppt
from app.services.ingestion.text_cleaner import clean_text
from app.services.ingestion.chunker import chunk_pages
from app.services.ai.vector_store import add_chunks, delete_document_chunks
from app.core.config import settings

router = APIRouter(prefix="/documents", tags=["documents"])

def _process(doc_id: int, file_path: str, user_id: int, subject: str, db: Session):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        return
    try:
        doc.status = ProcessingStatus.PROCESSING
        db.commit()
        pages = extract_pdf(file_path) if doc.file_type in [DocumentType.PDF, DocumentType.SYLLABUS, DocumentType.QUESTION_PAPER] else extract_ppt(file_path)
        for p in pages:
            p["text"] = clean_text(p["text"])
        pages  = [p for p in pages if len(p["text"]) > 30]
        chunks = chunk_pages(pages, doc_id, doc.original_filename, subject)
        count  = add_chunks(user_id, chunks)
        doc.chunk_count = count
        doc.status      = ProcessingStatus.COMPLETED
        db.commit()
    except Exception as e:
        doc.status        = ProcessingStatus.FAILED
        doc.error_message = str(e)
        db.commit()

@router.post("/upload", response_model=DocumentOut)
async def upload(
    background_tasks: BackgroundTasks,
    file:      UploadFile       = File(...),
    file_type: str              = Form(...),
    subject:   Optional[str]    = Form(None),
    db:        Session          = Depends(get_db),
    user:      User             = Depends(get_current_user),
):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    safe   = f"{user.id}_{file.filename.replace(' ','_')}"
    path   = os.path.join(settings.UPLOAD_DIR, safe)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    type_map = {"pdf": DocumentType.PDF, "ppt": DocumentType.PPT,
                "pptx": DocumentType.PPT, "syllabus": DocumentType.SYLLABUS,
                "question_paper": DocumentType.QUESTION_PAPER}
    doc = Document(
        user_id=user.id, filename=safe, original_filename=file.filename,
        file_type=type_map.get(file_type, DocumentType.PDF),
        subject=subject, file_path=path, status=ProcessingStatus.PENDING,
    )
    db.add(doc); db.commit(); db.refresh(doc)
    background_tasks.add_task(_process, doc.id, path, user.id, subject or "", db)
    return doc

@router.get("/", response_model=List[DocumentOut])
def list_docs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Document).filter(Document.user_id == user.id)\
        .order_by(Document.created_at.desc()).all()

@router.delete("/{doc_id}")
def delete_doc(doc_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    delete_document_chunks(user.id, doc_id)
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    db.delete(doc); db.commit()
    return {"message": "Deleted"}