from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from app.core import database
from app.core.database import check_database_connection, get_db
from app.repositories.system import SystemMetadataRepository


def test_get_db_session_lifecycle():
    with patch.object(database, "SessionLocal") as mock_session_cls:
        mock_session = mock_session_cls.return_value
        db_gen = get_db()
        session = next(db_gen)
        assert session == mock_session
        mock_session.close.assert_not_called()

        try:
            next(db_gen)
        except StopIteration:
            pass

        mock_session.close.assert_called_once()


def test_system_metadata_repository(db_session: Session):
    repo = SystemMetadataRepository(db_session)

    # Insert new entry
    created = repo.set_value("schema_version", "1.0.0", "Core schema initial version")
    assert created.key == "schema_version"
    assert created.value == "1.0.0"
    assert created.description == "Core schema initial version"
    assert created.created_at is not None
    assert created.updated_at is not None

    # Fetch by key
    retrieved = repo.get_by_key("schema_version")
    assert retrieved is not None
    assert retrieved.value == "1.0.0"

    # Update value
    updated = repo.set_value("schema_version", "1.1.0")
    assert updated.value == "1.1.0"
    assert updated.description == "Core schema initial version"

    # List entries
    all_entries = repo.list_all()
    assert len(all_entries) >= 1
    assert any(e.key == "schema_version" for e in all_entries)

    # Delete entry
    repo.delete(retrieved)
    assert repo.get_by_key("schema_version") is None


def test_check_database_connection_failure(monkeypatch):
    mock_engine = MagicMock()
    mock_engine.connect.side_effect = Exception("Simulated connection timeout")
    monkeypatch.setattr("app.core.database.engine", mock_engine)

    is_ok, err_msg = check_database_connection()
    assert is_ok is False
    assert err_msg == "Database connection unavailable or unhealthy"
