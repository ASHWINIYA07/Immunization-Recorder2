"""
db_engine.py — SQLAlchemy engine and session factory.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
import logging

from config import DB_URL

logger = logging.getLogger(__name__)

engine = create_engine(
    DB_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,   # verify connections before use
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@contextmanager
def get_db():
    """Provide a transactional database session."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_all_tables():
    """Create all ORM-mapped tables if they do not already exist."""
    # Import models so SQLAlchemy registers them on Base.metadata
    import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("All database tables verified / created.")
