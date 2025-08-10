# '''
# contains parse_feed which:
# - takes an rss feed url (like a blog)
# - using feedparser, downloads latest articles
# - cleans the article content (remove html)
# - uses nlp model to extract the most important theme sentences
# - converts the sentences into number vectors (embeddings)
# - checks if sentence is similar to something already in the db
#     - if yes, groups into an existing theme under existing theme id
#     - if not, generates a new theme id
# - saves the info into the db
# '''
# import feedparser
# from extractor import extract_thesis
# from db import get_session
# from models import Thesis
# from cluster import embed, find_matching_theme

# import re
# from html import unescape
# from datetime import datetime
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # helper to clean HTML
# def clean_html(raw_html):
#     clean_text = re.sub(r'<.*?>', '', raw_html)
#     return unescape(clean_text.strip())

# def parse_feed(url: str):
#     logger.info(f"Ingesting feed: {url}")
#     feed = feedparser.parse(url)

#     if not feed.entries:
#         logger.warning(f"No entries found in feed: {url}")
#         return

#     logger.info(f"Found {len(feed.entries)} entries in: {feed.feed.title}")

#     with get_session() as session:
#         for entry in feed.entries:
#             # check if post was already ingested
#             existing_post = session.query(Thesis).filter(Thesis.post_url == entry.link).first()
#             if existing_post:
#                 logger.info(f"Skipping duplicate post: {entry.link}")
#                 continue

#             logger.info(f"Parsing entry: {entry.title} — {entry.link}")

#             # extract and clean content
#             content = entry.get("summary", "") or entry.get("content", [{}])[0].get("value", "")
#             content = clean_html(content)

#             if not content:
#                 logger.warning(f"Skipping: No content in post '{entry.title}'")
#                 continue

#             # extract thesis sentences
#             thesis_sentences = extract_thesis(content)

#             for sentence in thesis_sentences:
#                 logger.info(f"Extracted thesis: {sentence}")

#                 # generate sentence embedding
#                 embedding_vec = embed(sentence)

#                 # find theme_id based on similarity to existing embeddings
#                 theme_id = find_matching_theme(embedding_vec)

#                 logger.info(f"Assigned theme_id: {theme_id}")

#                 #convert published_at to datetime (if available)
#                 published = None
#                 if entry.get("published_parsed"):
#                     published = datetime(*entry.published_parsed[:6])

#                 # save to db
#                 thesis_record = Thesis(
#                     thesis_text=sentence,
#                     post_title=entry.title,
#                     post_url=entry.link,
#                     published_at=published,
#                     embedding=embedding_vec,
#                     theme_id=theme_id,
#                 )

#                 session.add(thesis_record)

#         session.commit()
#         logger.info(f"Ingested feed '{feed.feed.title}' successfully.")

# # def parse_feed(url: str):
# #     logger.info(f"📥 Ingesting feed: {url}")
# #     feed = feedparser.parse(url)

# #     total_entries = len(feed.entries) if feed.entries else 0

# #     if not feed.entries:
# #         logger.warning(f"No entries found in feed: {url}")
# #         return {"ingested": 0, "skipped": 0, "total": 0}

# #     logger.info(f"Found {total_entries} entries in: {feed.feed.title}")

# #     ingested_count = 0
# #     skipped_count = 0

# #     with get_session() as session:
# #         for entry in feed.entries:
# #             existing_post = session.query(Thesis).filter(Thesis.post_url == entry.link).first()
# #             if existing_post:
# #                 logger.info(f"Skipping duplicate post: {entry.link}")
# #                 skipped_count += 1
# #                 continue

# #             # (your ingestion code here)
# #             logger.info(f"Parsing entry: {entry.title} — {entry.link}")

# #             # extract and clean content
# #             content = entry.get("summary", "") or entry.get("content", [{}])[0].get("value", "")
# #             content = clean_html(content)

# #             if not content:
# #                 logger.warning(f"Skipping: No content in post '{entry.title}'")
# #                 continue

# #             # extract thesis sentences
# #             thesis_sentences = extract_thesis(content)

# #             for sentence in thesis_sentences:
# #                 logger.info(f"Extracted thesis: {sentence}")

# #                 # generate sentence embedding
# #                 embedding_vec = embed(sentence)

# #                 # find theme_id based on similarity to existing embeddings
# #                 theme_id = find_matching_theme(embedding_vec)

# #                 logger.info(f"Assigned theme_id: {theme_id}")

# #                 #convert published_at to datetime (if available)
# #                 published = None
# #                 if entry.get("published_parsed"):
# #                     published = datetime(*entry.published_parsed[:6])

# #                 # save to db
# #                 thesis_record = Thesis(
# #                     thesis_text=sentence,
# #                     post_title=entry.title,
# #                     post_url=entry.link,
# #                     published_at=published,
# #                     embedding=embedding_vec,
# #                     theme_id=theme_id,
# #                 )

# #                 session.add(thesis_record)


# #             ingested_count += 1

# #         session.commit()
# #         logger.info(f"Ingested feed '{feed.feed.title}' successfully.")

# #     return {"ingested": ingested_count, "skipped": skipped_count, "total": total_entries}


import feedparser
from extractor import extract_thesis
from db import get_session
from models import Thesis
from cluster import embed, find_matching_theme
import re
from html import unescape
from datetime import datetime
import logging
import numpy as np
import uuid
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_html(raw_html: str) -> str:
    clean_text = re.sub(r'<.*?>', '', raw_html)
    return unescape(clean_text.strip())

def parse_feed(url: str):
    try:
        logger.info(f"📥 Ingesting feed: {url}")
        feed = feedparser.parse(url)

        if not feed.entries:
            logger.warning(f"No entries found in feed: {url}")
            return {"ingested": 0, "skipped": 0, "total": 0}

        total_entries = len(feed.entries)
        ingested_count = 0
        skipped_count = 0

        with get_session() as session:
            for entry in feed.entries:
                # Skip duplicate posts by URL
                exists = session.query(Thesis).filter(Thesis.post_url == entry.link).first()
                if exists:
                    logger.info(f"Skipping duplicate post: {entry.link}")
                    skipped_count += 1
                    continue

                content = entry.get("summary", "") or entry.get("content", [{}])[0].get("value", "")
                content = clean_html(content)

                if not content:
                    logger.warning(f"Skipping: No content in post '{entry.title}'")
                    skipped_count += 1
                    continue

                thesis_sentences = extract_thesis(content)

                if not thesis_sentences:
                    logger.warning(f"Skipping: No thesis sentences extracted for post '{entry.title}'")
                    skipped_count += 1
                    continue

                theme_id_counts = {}
                sentence_embeddings = []

                for sentence in thesis_sentences:
                    embedding_vec = embed(sentence)
                    if embedding_vec is None:
                        logger.warning(f"Skipping sentence with None embedding: '{sentence}'")
                        continue  # skip this sentence
                    sentence_embeddings.append(embedding_vec)
                    theme_id = find_matching_theme(embedding_vec)
                    theme_id_counts[theme_id] = theme_id_counts.get(theme_id, 0) + 1
                    logger.info(f"Extracted thesis: '{sentence}' with theme_id: {theme_id}")


                if not sentence_embeddings:
                    logger.warning(f"No valid embeddings found for post '{entry.title}', embedding whole content instead.")
                    avg_embedding = embed(content)
                else:
                    avg_embedding = np.mean(sentence_embeddings, axis=0).tolist()

                # Debug logs for embedding shape and sample values
                logger.info(f"Embedding type: {type(avg_embedding)}")
                logger.info(f"Embedding length: {len(avg_embedding)}")
                logger.info(f"Embedding sample (first 5 floats): {avg_embedding[:5]}")

                # Parse published date
                published = None
                if entry.get("published_parsed"):
                    published = datetime(*entry.published_parsed[:6])

                thesis_record = Thesis(
                    thesis_text="; ".join(thesis_sentences),
                    post_title=entry.title,
                    post_url=entry.link,
                    published_at=published,
                    embedding=avg_embedding,
                    theme_id=theme_id,
                )
                session.add(thesis_record)
                ingested_count += 1

            session.commit()
            logger.info(f"Ingested feed '{feed.feed.title}' successfully.")

        return {"ingested": ingested_count, "skipped": skipped_count, "total": total_entries}
    except Exception as e:
        logger.error(f"Exception in parse_feed: {e}")
        logger.error(traceback.format_exc())
        raise