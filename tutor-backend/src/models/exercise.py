from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id:         Mapped[int]   = mapped_column(primary_key=True)
    statement:  Mapped[str]   = mapped_column(Text, nullable=False)
    type:       Mapped[str]   = mapped_column(String(50), nullable=False)
    difficulty: Mapped[str]   = mapped_column(String(50), nullable=False)

    answer:      Mapped[str]  = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text)

    created_at:  Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    theme_id:    Mapped[int]  = mapped_column(ForeignKey("themes.id", ondelete="CASCADE"), nullable=False)

    theme:       Mapped["Theme"]             = relationship(back_populates="exercises")
    responses:   Mapped[List["UserResponse"]] = relationship(back_populates="exercise", cascade="all, delete-orphan")
