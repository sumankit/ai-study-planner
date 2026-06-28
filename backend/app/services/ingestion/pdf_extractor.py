# Validated in Colab Notebook 2, Cell 3
import fitz
from typing import List, Dict

def extract_pdf(file_path: str) -> List[Dict]:
    doc   = fitz.open(file_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text").strip()
        if len(text) > 30:
            pages.append({"page": i + 1, "text": text})
    doc.close()
    return pages