from app.db.database import engine, Base
from app.models import user, document, quiz, study_plan  # registers all models

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created")

if __name__ == "__main__":
    init_db()