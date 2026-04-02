# db/connection.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
import os

# --- Config ---
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")  

# --- Engine ---
engine = create_engine(
    DB_URL,
    poolclass=QueuePool,
    pool_size=10,          
    max_overflow=20,       
    pool_timeout=30,
    pool_recycle=1800,    
    echo=False             
)

# --- Session ---
psqlSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# --- Dependency (use for fastAPI dependency ingestion)---
def get_db():
    db = psqlSession()
    try:
        yield db
    finally:
        db.close()