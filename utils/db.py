import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import declarative_base

Logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Session:
    """Provide a database session to interact with the database"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database() -> None:
    """Create the database tables if they don't exist"""
    Logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    Logger.info("Database tables created successfully")
