"""
database.py — SQLite engine configuration and session management.

Configures the SQLAlchemy engine to connect to the local SQLite database,
applying concurrent execution pragmas (WAL) to prevent lock contention.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./codecompass.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # check_same_thread=False: allow the same connection across threads (required for FastAPI).
    # timeout=30: wait up to 30 s to acquire a write lock before raising OperationalError,
    # absorbing burst-traffic lock contention that would otherwise produce HTTP 500 at 5 s.
    connect_args={"check_same_thread": False, "timeout": 30}
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Fix 5: Enable Write-Ahead Logging on every new SQLite connection.
    WAL allows concurrent readers while a writer holds the lock, eliminating
    the 'database is locked' collision under parallel audit requests.
    synchronous=NORMAL is the correct paired setting for WAL — safe and
    substantially faster than the default FULL mode.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides an isolated SQLAlchemy session per request.
    Ensures the connection is safely closed after the request completes.
    
    Yields:
        Session: A bound SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()