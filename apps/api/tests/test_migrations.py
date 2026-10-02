from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine

from app import models  # noqa: F401
from app.core.config import settings
from app.db.base import Base

API_DIR = Path(__file__).resolve().parents[1]


def test_migrations_build_the_model_schema_and_roll_back(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path}/migrated.db"
    monkeypatch.setattr(settings, "database_url", url)
    config = Config(str(API_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(API_DIR / "migrations"))

    command.upgrade(config, "head")
    engine = create_engine(url)
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn, opts={"render_as_batch": True}), Base.metadata)
    assert diff == []

    command.downgrade(config, "base")
    with engine.connect() as conn:
        tables = conn.exec_driver_sql("select name from sqlite_master where type='table'").fetchall()
    assert [t[0] for t in tables] == ["alembic_version"]
