from uuid import uuid4

from app.services.api_key_service import ApiKeyService


class FakeSession:
    def __init__(self) -> None:
        self.records = []

    def add(self, record) -> None:
        self.records.append(record)

    def commit(self) -> None:
        pass

    def refresh(self, record) -> None:
        pass


def test_create_key_returns_plaintext_once() -> None:
    db = FakeSession()
    created = ApiKeyService(db).create_key(uuid4(), "Demo key")  # type: ignore[arg-type]

    assert created.secret.startswith("sf_")
    assert created.record.name == "Demo key"
    assert created.record.key_prefix == created.secret[:12]
    assert created.record.key_hash != created.secret
