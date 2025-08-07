"""
This file defines the thesis model, which is the structure of each saved record in the database.

each thesis contains:
- the actual thesis text
- the title and URL of the post it came from
- when it was published and when it was ingested
- the embedding vector
- a theme_id to group similar theses together

"""

from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime
from typing import Optional, List

class Thesis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    theme_id: Optional[str] = None
    thesis_text: str
    post_title: str
    post_url: str
    published_at: Optional[datetime] = None
    ingested_at: datetime = Field(default_factory=datetime.utcnow)

    # add this to store vector embeddings
    embedding: Optional[List[float]] = Field(default=None, sa_column=Column(JSON))
