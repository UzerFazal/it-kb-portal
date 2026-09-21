import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./kb_portal.db"
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    _run_light_migrations()


def _run_light_migrations():
    """Add newly introduced nullable columns to an already-existing SQLite
    file. create_all() only creates missing tables, not missing columns on
    tables that already exist (e.g. after a redeploy on a persisted DB)."""
    if not DATABASE_URL.startswith("sqlite"):
        return
    from sqlalchemy import text
    migrations = {
        "articles": [("title_cs", "VARCHAR(256)"), ("summary_cs", "TEXT"), ("content_cs", "TEXT")],
        "categories": [("name_cs", "VARCHAR(128)"), ("description_cs", "TEXT")],
    }
    with engine.connect() as conn:
        for table, cols in migrations.items():
            existing = {row[1] for row in conn.execute(text(f"PRAGMA table_info({table})"))}
            for col_name, col_type in cols:
                if col_name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"))
        conn.commit()
