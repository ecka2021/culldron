'''
contains parse_feed which:
- takes an rss feed url (like a blog)
- using feedparser, downloads latest articles
- cleans the article content (remove html)
- uses nlp model to extract the most important theme sentences
- converts the sentences into number vectors (embeddings)
- checks if sentence is similar to something already in the db
    - if yes, groups into an existing theme under existing theme id
    - if not, generates a new theme id
- saves the info into the db
'''
import feedparser
from extractor import extract_thesis
from db import get_session
from models import Thesis
from cluster import embed, find_matching_theme

import re
from html import unescape
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# helper to clean HTML
def clean_html(raw_html):
    clean_text = re.sub(r'<.*?>', '', raw_html)
    return unescape(clean_text.strip())

def parse_feed(url: str):
    logger.info(f"📥 Ingesting feed: {url}")
    feed = feedparser.parse(url)

    if not feed.entries:
        logger.warning(f"No entries found in feed: {url}")
        return

    logger.info(f"Found {len(feed.entries)} entries in: {feed.feed.title}")

    with get_session() as session:
        for entry in feed.entries:
            logger.info(f"Parsing entry: {entry.title} — {entry.link}")

            # extract and clean content
            content = entry.get("summary", "") or entry.get("content", [{}])[0].get("value", "")
            content = clean_html(content)

            if not content:
                logger.warning(f"Skipping: No content in post '{entry.title}'")
                continue

            # extract thesis sentences
            thesis_sentences = extract_thesis(content)

            for sentence in thesis_sentences:
                logger.info(f"Extracted thesis: {sentence}")

                # generate sentence embedding
                embedding_vec = embed(sentence)

                # find theme_id based on similarity to existing embeddings
                theme_id = find_matching_theme(embedding_vec)

                logger.info(f"Assigned theme_id: {theme_id}")

                #convert published_at to datetime (if available)
                published = None
                if entry.get("published_parsed"):
                    published = datetime(*entry.published_parsed[:6])

                # save to db
                thesis_record = Thesis(
                    thesis_text=sentence,
                    post_title=entry.title,
                    post_url=entry.link,
                    published_at=published,
                    embedding=embedding_vec,
                    theme_id=theme_id,
                )

                session.add(thesis_record)

        session.commit()
        logger.info(f"Ingested feed '{feed.feed.title}' successfully.")
