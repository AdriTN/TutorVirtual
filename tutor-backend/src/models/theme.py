from __future__ import annotations

from typing import List

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]    = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=True)

    subject:    Mapped["Subject"]          = relationship(back_populates="themes")
    exercises:  Mapped[List["Exercise"]]   = relationship(back_populates="theme", cascade="all, delete-orphan")
    progress:   Mapped[List["UserThemeProgress"]] = relationship(cascade="all, delete-orphan")
