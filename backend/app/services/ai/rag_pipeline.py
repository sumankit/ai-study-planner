# Validated in Colab Notebook 4, Cell 3 and 5
import google.generativeai as genai
from typing import List, Optional
from app.core.config import settings
from app.services.ai.vector_store import search_similar
from app.schemas.chat import ChatMessage, Source

genai.configure(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = """You are an expert study assistant helping a student understand their own notes.

STRICT RULES:
1. Answer ONLY using the CONTEXT provided. Never use outside knowledge.
2. If the answer is not in the context, say: "I couldn't find this in your uploaded documents."
3. Always cite the source filename and page number.
4. Be clear, structured, and educational.
5. Use bullet points for multi-part answers."""

def rag_query(
    user_id:  int,
    question: str,
    history:  List[ChatMessage] = [],
    subject:  Optional[str]     = None,
) -> dict:
    chunks = search_similar(user_id, question, top_k=settings.TOP_K_RESULTS, subject_filter=subject)
    if not chunks:
        return {
            "answer":  "No relevant content found. Please upload study materials first.",
            "sources": [],
        }

    context_parts = [
        f"[Source: {c['metadata'].get('filename','?')}, Page {c['metadata'].get('page','?')}, Score: {c['score']}]\n{c['text']}"
        for c in chunks
    ]
    context      = "\n\n---\n\n".join(context_parts)
    history_text = "\n".join([f"{m.role.upper()}: {m.content}" for m in history[-4:]])

    prompt = f"""{SYSTEM_PROMPT}

CONVERSATION HISTORY:
{history_text}

CONTEXT FROM STUDENT'S DOCUMENTS:
{context}

STUDENT QUESTION: {question}

ANSWER:"""

    model    = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    seen    = set()
    sources = []
    for c in chunks:
        m   = c["metadata"]
        key = f"{m.get('filename')}_{m.get('page')}"
        if key not in seen and c["score"] > 0.3:
            seen.add(key)
            sources.append(Source(
                filename = m.get("filename", "?"),
                page     = m.get("page"),
                chunk_id = m.get("doc_id", ""),
            ))

    return {"answer": response.text, "sources": sources}