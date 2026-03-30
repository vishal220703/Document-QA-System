from contextlib import contextmanager
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from QAWithPDF.config import get_database_url


Base = declarative_base()

engine = create_engine(get_database_url(), future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


def _fallback_to_sqlite() -> None:
    global engine
    sqlite_url = "sqlite:///./docquest_memory.db"
    engine = create_engine(sqlite_url, future=True, pool_pre_ping=True)
    SessionLocal.configure(bind=engine)
    logging.warning(
        "Falling back to SQLite memory store at %s because PostgreSQL could not be initialized.",
        sqlite_url,
    )


def init_db() -> None:
    # Import models here so metadata is registered before create_all.
    from QAWithPDF import db_models  # noqa: F401

    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        _fallback_to_sqlite()
        Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Session:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
