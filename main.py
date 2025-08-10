"""
This is the FastAPI web server that powers the API.
turns this project to a usable API

it defines 3 main endpoints:
- /themes which returns a list of theme_ids and how many theses are in each.
- /themes/{theme_id} which returns all theses grouped under a given theme, sorted by date.
- /ingest which accepts a JSON body with a feed_url, and calls parse_feed() to ingest new content.
"""

from fastapi import FastAPI, HTTPException
from sqlmodel import select
# from sqlmodel import select
from db import get_session
from models import Thesis
from typing import List
from collections import defaultdict

app = FastAPI(title="Culldron Insight Extractor")

@app.get("/themes")
def list_themes():
    """
    list all unique theme IDs with the count of posts in each.
    """
    with get_session() as session:
        results = session.exec(select(Thesis.theme_id)).all()

    theme_counts = defaultdict(int)
    for theme_id in results:
        if theme_id:
            theme_counts[theme_id] += 1

    return [{"theme_id": k, "count": v} for k, v in theme_counts.items()]


@app.get("/themes/{theme_id}")
def theme_timeline(theme_id: str):
    """
    return all posts in a given theme, sorted by publish date.
    """
    with get_session() as session:
        results = session.exec(
            select(Thesis).where(Thesis.theme_id == theme_id)
        ).all()

    if not results:
        raise HTTPException(status_code=404, detail="Theme not found")

    sorted_results = sorted(results, key=lambda x: x.published_at or x.ingested_at)

    return [
        {
            "thesis_text": t.thesis_text,
            "post_title": t.post_title,
            "post_url": t.post_url,
            "published_at": t.published_at,
            "ingested_at": t.ingested_at
        }
        for t in sorted_results
    ]

from fastapi import Request
from pydantic import BaseModel
from rss import parse_feed

class IngestRequest(BaseModel):
    feed_url: str



from collections import defaultdict
from db import get_session
from models import Thesis

def print_theme_ids_with_multiple_posts():
    with get_session() as session:
        theme_ids = session.query(Thesis.theme_id).all()

    theme_counts = defaultdict(int)
    for (theme_id,) in theme_ids:
        if theme_id:
            theme_counts[theme_id] += 1

    multiple_posts = {tid: count for tid, count in theme_counts.items() if count > 1}

    if multiple_posts:
        print("Theme IDs with more than 1 post:")
        for tid, count in multiple_posts.items():
            print(f"{tid}: {count} posts")
    else:
        print("No theme IDs with more than 1 post found.")



@app.post("/ingest")
def ingest_feed(payload: IngestRequest):
    """
    Ingest a new RSS feed by URL.
    """
    try:
        result = parse_feed(payload.feed_url)
        if result["total"] > 0 and result["total"] == result["skipped"]:
            return {"message": "This URL has already been parsed."}
        else:
            return {"message": f"Feed ingested successfully. New posts ingested: {result['ingested']}, skipped: {result['skipped']}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))








