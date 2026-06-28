# Validated in Colab Notebook 5, Cell 2 and 3
import json, re
import google.generativeai as genai
from typing import List, Optional
from app.core.config import settings
from app.services.ai.vector_store import search_similar

genai.configure(api_key=settings.GEMINI_API_KEY)

DIFFICULTY_GUIDANCE = {
    "easy":   "Test direct recall. Questions should have one obviously correct answer found verbatim in the text.",
    "medium": "Test understanding and application. Students must understand concepts, not just memorize.",
    "hard":   "Test analysis and multi-step reasoning. Use calculations, edge cases, concept combinations.",
}

def generate_quiz(
    user_id:       int,
    topic:         str,
    num_questions: int           = 5,
    difficulty:    str           = "medium",
    subject:       Optional[str] = None,
) -> List[dict]:
    chunks = search_similar(user_id, topic, top_k=8, subject_filter=subject)
    if not chunks:
        raise ValueError("No content found for this topic. Upload relevant documents first.")

    context = "\n\n".join([c["text"] for c in chunks[:6]])

    prompt  = f"""You are an expert exam question creator.

Topic: "{topic}"
Difficulty: {difficulty} — {DIFFICULTY_GUIDANCE[difficulty]}

Source material (use ONLY this):
{context}

Generate exactly {num_questions} multiple choice questions.
Return ONLY a valid JSON array. No markdown, no code fences, no explanation.

[
  {{
    "id": 1,
    "question": "...",
    "options": [
      {{"key": "A", "text": "..."}},
      {{"key": "B", "text": "..."}},
      {{"key": "C", "text": "..."}},
      {{"key": "D", "text": "..."}}
    ],
    "correct_answer": "A",
    "explanation": "..."
  }}
]"""

    model    = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    raw      = re.sub(r"```json\s*|```\s*", "", response.text).strip()
    return json.loads(raw)