from db import get_session
from models import Thesis

with get_session() as session:
    results = session.query(Thesis).all()

    for t in results:
        print(f"[{t.id}] {t.post_title} → {t.thesis_text}")
