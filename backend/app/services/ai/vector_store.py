# Validated in Colab Notebook 3, Cell 4
import chromadb
import uuid
from typing import List, Dict, Optional
from app.core.config import settings
from app.services.ai.embedder import embed_texts, embed_query

_client = None

def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _client

def get_collection(user_id: int):
    return get_client().get_or_create_collection(
        name     = f"user_{user_id}",
        metadata = {"hnsw:space": "cosine"},
    )

def add_chunks(user_id: int, chunks: List[Dict]) -> int:
    if not chunks:
        return 0
    collection = get_collection(user_id)
    texts      = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)
    ids        = [str(uuid.uuid4()) for _ in chunks]
    metadatas  = [c["metadata"] for c in chunks]
    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    return len(chunks)

def search_similar(
    user_id:        int,
    query:          str,
    top_k:          int = 5,
    subject_filter: Optional[str] = None,
) -> List[Dict]:
    collection    = get_collection(user_id)
    q_vec         = embed_query(query)
    where         = {"subject": subject_filter} if subject_filter else None
    results       = collection.query(
        query_embeddings = [q_vec],
        n_results        = top_k,
        where            = where,
        include          = ["documents", "metadatas", "distances"],
    )
    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        score = round(1 - dist, 3)
        if score > 0.1:
            chunks.append({"text": doc, "metadata": meta, "score": score})
    return chunks

def delete_document_chunks(user_id: int, doc_id: int):
    try:
        get_collection(user_id).delete(where={"doc_id": str(doc_id)})
    except Exception:
        pass