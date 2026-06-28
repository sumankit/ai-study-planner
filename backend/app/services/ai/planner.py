# Validated in Colab Notebook 6, Cell 3
import json, re
from datetime import date
from typing import List
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_study_plan(
    exam_date:   date,
    daily_hours: int,
    subjects:    List[str],
    weak_topics: List[str] = [],
) -> dict:
    days_available = (exam_date - date.today()).days
    if days_available <= 0:
        raise ValueError("Exam date must be in the future")

    weak_info = (
        f"Priority topics (scored below 60%): {', '.join(weak_topics)}"
        if weak_topics else "No weak topics identified yet."
    )

    prompt = f"""You are an expert academic study planner.

CONSTRAINTS:
- Today: {str(date.today())}
- Exam date: {str(exam_date)}
- Days available: {days_available}
- Daily study hours: {daily_hours}
- Subjects: {', '.join(subjects)}
- {weak_info}

RULES:
1. Allocate 40% more time to weak topics
2. Last 2 days = full revision only
3. Mix subjects across days
4. Be specific (not just "study chapter 1")
5. Each tasks list: exactly 3 concrete items

Return ONLY valid JSON. No markdown. No code fences.

{{
  "title": "Study Plan",
  "total_days": {days_available},
  "daily_hours": {daily_hours},
  "schedule": [
    {{
      "day": 1,
      "date": "YYYY-MM-DD",
      "topic": "Specific topic",
      "subject": "Subject name",
      "hours": {daily_hours},
      "tasks": ["Task 1", "Task 2", "Task 3"],
      "priority": "high"
    }}
  ],
  "tips": ["Tip 1", "Tip 2", "Tip 3"]
}}"""

    model    = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    raw      = re.sub(r"```json\s*|```\s*", "", response.text).strip()
    return json.loads(raw)