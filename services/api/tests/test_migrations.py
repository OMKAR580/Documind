import os
from io import StringIO
from unittest.mock import patch

from alembic.config import Config
from alembic.script import ScriptDirectory

from alembic import command
from app.models.base import Base


def test_model_metadata_registration():
    """Verifies that all core models are properly registered on Base.metadata."""
    table_names = list(Base.metadata.tables.keys())
    assert "system_metadata" in table_names


def test_alembic_config_and_script_discovery():
    """Verifies Alembic ini and migration script directory discovery."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ini_path = os.path.join(base_dir, "alembic.ini")
    assert os.path.isfile(ini_path)

    config = Config(ini_path)
    script_dir = ScriptDirectory.from_config(config)
    heads = script_dir.get_heads()

    assert len(heads) == 1
    assert heads[0] == "0001_initial_core_schema"

    revision = script_dir.get_revision("0001_initial_core_schema")
    assert revision is not None
    assert revision.down_revision is None


def test_alembic_offline_sql_generation():
    """Verifies that Alembic can render offline PostgreSQL upgrade SQL without a running database."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ini_path = os.path.join(base_dir, "alembic.ini")

    config = Config(ini_path)
    # Redirect stdout to capture rendered SQL
    output_buffer = StringIO()
    with patch("sys.stdout", output_buffer):
        command.upgrade(config, "head", sql=True)

    sql_output = output_buffer.getvalue()
    assert "CREATE TABLE system_metadata" in sql_output
    assert "ix_system_metadata_key" in sql_output
    assert "alembic_version" in sql_output
