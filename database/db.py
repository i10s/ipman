# Database connection and session management
# File: /database/db.py
import comm.app_logging as logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from comm.config import Config  # Ensure this is properly fetching from Consul
from comm.app_logging import getLogger

# Set up logger for database interactions
logger = logging.getLogger(__name__)


# Set up the database connection, referencing the existing schema
def get_database_url():
    try:
        db_url = Config().get_db_url()
        logger.info("Successfully fetched the database URL.")
        return db_url
    except Exception as e:
        logger.error(f"Error fetching database URL: {e}")
        raise


# Create engine and session
try:
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine and session created successfully.")
except Exception as e:
    logger.error(f"Failed to create the database engine or session: {e}")
    raise


# Dependency to get the database session
def get_db_session():
    db = SessionLocal()
    try:
        yield db
        logger.debug("Database session created and used.")
    except Exception as e:
        logger.error(f"An error occurred with the database session: {e}")
        raise
    finally:
        db.close()
        logger.debug("Database session closed.")
