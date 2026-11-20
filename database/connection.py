import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from database.models import Base

logger = logging.getLogger(__name__)

def get_database_engine():
    """
    Creates the SQLAlchemy engine.
    Tries MySQL first if DB_TYPE is mysql; falls back to SQLite if MySQL is unreachable.
    """
    if settings.DB_TYPE.lower() == "mysql":
        mysql_url = (
            f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
            f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
        )
        try:
            engine = create_engine(
                mysql_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={"connect_timeout": 3}
            )
            # Test connection
            with engine.connect() as conn:
                logger.info("Successfully connected to MySQL database.")
            return engine, "mysql"
        except Exception as e:
            logger.warning(
                f"Could not connect to MySQL ({e}). "
                f"Falling back to local SQLite database at {settings.SQLITE_DB_PATH}."
            )
    
    # SQLite fallback / SQLite configuration
    sqlite_url = f"sqlite:///{settings.SQLITE_DB_PATH}"
    engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False}
    )
    logger.info(f"Using SQLite database: {sqlite_url}")
    return engine, "sqlite"

engine, active_db_dialect = get_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes all database tables defined in models."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema verified and tables initialized.")

def get_db():
    """FastAPI dependency for yielding database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
