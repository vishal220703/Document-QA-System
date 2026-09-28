from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from QAWithPDF.config import get_database_url


Base = declarative_base()

engine = create_engine(get_database_url(), future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


def init_db() -> None:
    # Import models here so metadata is registered before create_all.
    from QAWithPDF import db_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_ownership_columns()


def _ensure_ownership_columns() -> None:
    columns_by_table = {
        "conversations": "owner_username",
        "query_evaluations": "owner_username",
    }
    with engine.begin() as connection:
        inspector = inspect(connection)
        for table_name, column_name in columns_by_table.items():
            columns = {column["name"] for column in inspector.get_columns(table_name)}
            if column_name not in columns:
                connection.execute(
                    text(f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" VARCHAR(64)')
                )


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
