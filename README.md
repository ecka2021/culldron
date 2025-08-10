# Culldron: RSS Insight Extractor  
By Eusila Kitur — Take-Home Assessment

---

## What This Project Does

This project takes in an RSS feed URL from any blog or news site, pulls out each article’s key idea using AI, groups similar ideas into themes using embeddings, and then lets you explore those themes and their articles via an API.

---

## My Approach

I had zero prior experience with NLP going in. Here’s how I got started:

- Read up on sentence embeddings and how modern NLP models work.  
- Used AI tools (chatGPT) to help me break down the project into manageable tasks.  
- Dug into docs and tutorials for the tools I chose — `FastAPI`, `SQLModel`, and `SentenceTransformers`.  
- Built the system step-by-step, learning as I went.

---

## Design Decisions

- **FastAPI** for a fast API server with automatic OpenAPI docs.  
- **SentenceTransformers (all-MiniLM-L6-v2)** for good sentence embeddings out-of-the-box.  
- **SQLite** for simplicity and portability.  
- **Theme Clustering:** I assign themes based on embedding cosine similarity (threshold 0.8 by default).  
- **Thesis Extraction:** I extract 1–2 core sentences per post for better clustering.  
- **Idempotency:** Duplicate posts (by URL) are skipped on ingest.  
- **Logging:** Info-level logs give insight into feed ingestion and clustering choices.

---

## How It Works (High-Level)

1. You send an RSS feed URL via the `/ingest` API.  
2. The app parses the feed and cleans article content.  
3. Extracts thesis sentences and generates embeddings.  
4. Clusters theses into themes based on similarity.  
5. Stores theses with theme IDs in a SQLite database.  
6. You query `/themes` to see all themes with counts, or `/themes/{id}` to see a timeline of posts in that theme.

---

## Files Included and What They Do

| File           | What It Does                              |
|----------------|-----------------------------------------|
| `main.py`      | FastAPI app and all API endpoints       |
| `rss.py`       | RSS parsing, content cleaning, ingestion|
| `extractor.py` | Extracts thesis sentences from content  |
| `cluster.py`   | Embeds sentences and assigns themes     |
| `models.py`    | SQLModel table definitions               |
| `db.py`        | Database setup and sessions              |
| `init_db.py`   | Creates the database tables              |
| `requirements.txt` | Python dependencies                   |
| `Dockerfile`   | Containerizes the app                    |
| `run_mock.py`  | Runs mock data ingestion for testing    |

---

## How to Run It

### Requirements

- Python 3.9+  
- (Optional) `virtualenv` for isolated environment

### Setup Steps

```bash
# 1. Get into the project folder
cd culldron

# 2. Create & activate virtual environment (optional)
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Initialize the database
python init_db.py

# 5. Start the FastAPI server
uvicorn main:app --reload

Then open your browser at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the API docs.

## How to Use

- **POST** to `/ingest` with JSON payload:

```json
{
  "feed_url": "https://blog.google/rss/"
}

- `GET /themes` to see all themes with counts.  
- `GET /themes/{theme_id}` to see all posts in a theme, in chronological order.


---
## Future Improvements
- Build a frontend for better timeline and theme visualization.
- Switch to PostgreSQL or another scalable DB for production use.
- Add rate limiting, retry logic, and error handling for feed ingestion.
- Add pagination, authentication, and other API features down the line.
