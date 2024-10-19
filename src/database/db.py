# Database connection and session management
# File: /src/database/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config  # Ensure this is properly fetching from Consul


# Set up the database connection, referencing the existing schema
def get_database_url():
    return Config().get_db_url()


# Create engine and session
engine = create_engine(get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get the database session
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
