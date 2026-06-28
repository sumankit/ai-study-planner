# Validated in Colab Notebook 1, Cell 4
from sentence_transformers import SentenceTransformer
from typing import List
from app.core.config import settings

_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model

def embed_texts(texts: List[str]) -> List[List[float]]:
    return get_model().encode(texts, batch_size=32, show_progress_bar=False).tolist()

def embed_query(text: str) -> List[float]:
    return embed_texts([text])[0]