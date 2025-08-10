from datetime import datetime
import numpy as np
from cluster import embed, find_matching_theme
from extractor import extract_thesis
from db import get_session
from models import Thesis

# Mock posts simulating related content with similar themes
mock_posts = [
    {
        "post_title": "AI Revolution in Healthcare",
        "post_url": "http://example.com/post1",
        "published_parsed": (2025, 8, 9, 10, 0, 0, 0, 0, 0),
        "thesis_text": "Artificial intelligence is transforming healthcare by enabling faster diagnosis."
    },
    {
        "post_title": "How AI Is Changing Healthcare",
        "post_url": "http://example.com/post2",
        "published_parsed": (2025, 8, 9, 12, 0, 0, 0, 0, 0),
        "thesis_text": "AI is revolutionizing healthcare with quicker and more accurate diagnosis."
    },
    {
        "post_title": "New Advances in AI for Medicine",
        "post_url": "http://example.com/post3",
        "published_parsed": (2025, 8, 9, 14, 0, 0, 0, 0, 0),
        "thesis_text": "The healthcare industry benefits greatly from artificial intelligence in diagnosis speed."
    }
]

def parse_mock_posts(posts=mock_posts):
    ingested_count = 0
    skipped_count = 0

    with get_session() as session:
        for entry in posts:
            exists = session.query(Thesis).filter(Thesis.post_url == entry["post_url"]).first()
            if exists:
                skipped_count += 1
                continue

            content = entry["thesis_text"]
            thesis_sentences = extract_thesis(content)

            theme_id_counts = {}
            sentence_embeddings = []

            for sentence in thesis_sentences:
                embedding_vec = embed(sentence)
                if embedding_vec is None:
                    continue
                sentence_embeddings.append(embedding_vec)
                theme_id = find_matching_theme(embedding_vec)
                theme_id_counts[theme_id] = theme_id_counts.get(theme_id, 0) + 1

            if not sentence_embeddings:
                avg_embedding = embed(content)
            else:
                avg_embedding = np.mean(sentence_embeddings, axis=0).tolist()

            theme_id = max(theme_id_counts.items(), key=lambda x: x[1])[0]

            published = datetime(*entry["published_parsed"][:6])

            thesis_record = Thesis(
                thesis_text="; ".join(thesis_sentences),
                post_title=entry["post_title"],
                post_url=entry["post_url"],
                published_at=published,
                embedding=avg_embedding,
                theme_id=theme_id,
            )
            session.add(thesis_record)
            ingested_count += 1

        session.commit()

    return {"ingested": ingested_count, "skipped": skipped_count, "total": len(posts)}
