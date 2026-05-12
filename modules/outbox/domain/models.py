from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid

from core import Base


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    aggregate_type: Mapped[str] = mapped_column(String(256), nullable=False)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    published_at = mapped_column(DateTime(timezone=True), nullable=True)
