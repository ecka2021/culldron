# Culldron: RSS Insight Extractor
Eusila Kitur Take-home Assesment

## What This Project Does

1. Takes in an RSS feed URL (blog/ news site),
2. Pulls out each article’s key idea or using AI,
3. Groups similar theses into themes using embeddings,
4. Lets you view these themes and their articles via an API.


## My Approach

I’ll be honest, I had zero prior experience with Natural Language Processing (NLP). I had worked with Python, but most of this was new to me.

To get up to speed, I:
- Read about how modern NLP models work (especially sentence embeddings),
- Used AI to help break down the tasks into simple TODOs,
- Searched docs and blog posts to understand each tool (like `FastAPI`, `SQLModel`, `Sentence Transformers`),
- And step-by-step built the system out.


# Design Decisions

- FastAPI - was chosen for its speed and built-in OpenAPI docs.
- SentenceTransformers - gave good results out-of-the-box for sentence-level embeddings (based on research, people seem to prefer this).
- SQLite - was used for simplicity and portability in a take-home context.
- Agglomerative Clustering -  was picked for grouping similar themes without needing to predefine cluster count.

## How It Works (High-Level)

1. You send an RSS feed URL (via `/ingest` endpoint).
2. The alg:
   - Parses the feed,
   - Cleans the article content,
   - Uses an AI model to summarize each article into a thesis sentence,
   - Embeds that sentence into a vector (using a pre-trained model),
   - Clusters similar theses into themes based on embedding similarity.
3. The theses are saved in a SQLite database with their theme.
4. You can view themes or the timeline of theses per theme using the API.

## Files included and what each does
main.py    -> FastAPI server with all endpoints
rss.py   ->    Parses RSS feeds, extracts content, calls embedding
extractor.py      ->  Extracts thesis sentences using NLP
cluster.py    ->      Embeds sentences and assigns them to themes
models.py      ->     SQLModel definitions (like Thesis table)
db.py        ->       Handles DB connection setup
init_db.py    ->      nitializes database tables
requirements.txt  ->  All Python dependencies
Dockerfile        ->  containerizes the app

### Files you can ignore (just for testing):
test.py –> used to test sentence extraction
view_thesis.py –>  used to manually view database entries
run_feed.py –>  helped test ingestion before we built the `/ingest` endpoint


# How to Run It (Step-by-Step)
# Prerequisites
- Python 3.9 
- `virtualenv` for isolation (optional)

# 1. Unzip the folder

unzip culldron.zip
cd culldron
# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Initialize the database
python init_db.py

# 5. Start the FastAPI server
uvicorn main:app --reload

# Now go to your browser and open:
http://127.0.0.1:8000/docs


# To ingest an RSS feed:
Go to POST /ingest in the docs
Paste in a payload like:
{
  "feed_url": "https://blog.google/rss/"
}
Click Execute

To explore themes:
GET /themes — see all themes
GET /themes/{theme_id} — view all posts under one theme

# OPTIONAL (if your docker does not give you issues like mine did)
docker build -t culldron .
docker run -p 8000:8000 culldron


# Future Work
Add a front-end to view themes and theses in a timeline.
Replace SQLite with PostgreSQL for better scalability.
Implement deduplication of near-duplicate articles.
Add rate-limiting and retry logic for ingesting flaky RSS feeds.
