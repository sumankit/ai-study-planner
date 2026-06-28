# Validated in Colab Notebook 2, Cell 5 — chunk_size and overlap confirmed there
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict
from app.core.config import settings

splitter = RecursiveCharacterTextSplitter(
    chunk_size    = settings.CHUNK_SIZE,
    chunk_overlap = settings.CHUNK_OVERLAP,
    separators    = ["\n\n", "\n", ". ", " ", ""],
)

def chunk_pages(pages: List[Dict], doc_id: int, filename: str, subject: str = "") -> List[Dict]:
    chunks = []
    for page_data in pages:
        for idx, text in enumerate(splitter.split_text(page_data["text"])):
            if len(text.strip()) < 50:
                continue
            chunks.append({
                "text": text.strip(),
                "metadata": {
                    "doc_id":      str(doc_id),
                    "filename":    filename,
                    "page":        page_data["page"],
                    "subject":     subject or "general",
                    "chunk_index": idx,
                },
            })
    return chunks