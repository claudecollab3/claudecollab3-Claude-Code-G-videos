"""Cross-dialect column types.

Production runs on PostgreSQL; unit tests run against in-memory SQLite for
speed. These TypeDecorators let the same model definitions work on both
without leaking dialect-specific SQL into application code.
"""

import enum
import uuid

from sqlalchemy import CHAR, Enum
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


def str_enum(enum_cls: type[enum.Enum], *, name: str) -> Enum:
    """A native Postgres ENUM whose stored values are the Python Enum
    members' `.value` (matching what the Alembic migrations declare as the
    literal enum labels), not SQLAlchemy's default of `.name`. Left at the
    default, a str-Enum member like `Role.TRADER` (value `"trader"`) would
    be sent to Postgres as the literal string `"TRADER"`, which the
    migration never created as a valid label -- a mismatch SQLite's
    generic Enum type doesn't enforce the same way, so it only surfaces
    against a real Postgres database.
    """
    return Enum(enum_cls, name=name, values_callable=lambda cls: [member.value for member in cls])
