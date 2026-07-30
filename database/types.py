"""Cross-dialect column types.

Production runs on PostgreSQL; unit tests run against in-memory SQLite for
speed. These TypeDecorators let the same model definitions work on both
without leaking dialect-specific SQL into application code.
"""

import uuid

from sqlalchemy import CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TypeDecorator


class GUID(TypeDecorator):
    """Platform-independent UUID: native UUID on Postgres, CHAR(32) elsewhere."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return str(value)
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value.hex

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)
