# Validated in Colab Notebook 2, Cell 4
import re

def clean_text(text: str) -> str:
    text = re.sub(r'\n{3,}',  '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ',  text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'\.{3,}',  '...',  text)
    return text.strip()