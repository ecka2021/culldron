"""
This file sets up the database connection using SQLModel and SQLite.

- defines the engine, which connects to the database file (culldron.db).
- provides the get_session() function to safely interact with the database.

other files can use get_session() to:
    - add new records
    - query existing records
    - save updates
"""

from sqlmodel import create_engine, SQLModel, Session
from models import Thesis

sqlite_file = "culldron.db"
engine = create_engine(f"sqlite:///{sqlite_file}", echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
