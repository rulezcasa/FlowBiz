# db/connection.py

from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os

# --- Config ---
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")  

# --- Engine ---
engine = create_async_engine(
    DB_URL,
    pool_size=10,          
    max_overflow=20,       
    pool_timeout=30,
    pool_recycle=1800,    
    echo=False             
)

# --- Session ---
psqlSession = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

# --- Dependency (use for fastAPI dependency ingestion)---
def get_db():
    db = psqlSession()
    try:
        yield db
    finally:
        db.close()