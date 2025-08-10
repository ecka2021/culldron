'''
thinking logic
- embed takes in text and turns it into an embedding vector using a transformer model
- find matching theme  takes in new embeddings and compares a new sentence's vector to the existing one and decides:
    - if similar enough based on cosine similarity, group it with the existing theme
    - if not, create a new unique theme id  (uuid)
    
'''

from sentence_transformers import SentenceTransformer, util
from models import Thesis
from db import get_session
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# load embedding model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed(text: str):
    embedding = model.encode(text)
    if embedding is None:
        logger.error(f"Embedding returned None for text: {text}")
        return None
    return embedding.tolist()

def find_matching_theme(new_embedding: list[float], threshold: float = 0.8) -> str:
    with get_session() as session:
        existing = session.query(Thesis).filter(Thesis.embedding != None).all()

            # filter out any None or invalid embeddings
        filtered = [(t.embedding, t.theme_id) for t in existing if t.embedding and isinstance(t.embedding, list)]

        if not filtered:
            new_id = str(uuid.uuid4())
            logger.info(f"No existing valid theme embeddings found in the database. Creating new theme_id: {new_id}")
            return new_id

        embeddings, theme_ids = zip(*filtered)

        # compute cosine similarity
        scores = util.cos_sim([new_embedding], embeddings)[0]

        # find best match
        best_score = float(scores.max())
        best_idx = int(scores.argmax())
        best_theme_id = theme_ids[best_idx]

        if best_score >= threshold:
            logger.info(f"Found a matching theme_id={best_theme_id} with similarity={best_score:.4f}")
            return best_theme_id
        else:
            new_id = str(uuid.uuid4())
            logger.info(f"No sufficiently similar theme found (highest similarity={best_score:.4f}). Creating new theme_id: {new_id}")
            return new_id