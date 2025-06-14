from __future__ import annotations

from typing import List

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base
from .associations import course_subjects, user_subjects


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int]      = mapped_column(primary_key=True)
    name: Mapped[str]    = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    courses: Mapped[List["Course"]] = relationship(
        secondary=course_subjects,
        back_populates="subjects",
        lazy="selectin",
    )

    users: Mapped[List["User"]] = relationship(
        secondary=user_subjects,
        back_populates="subjects",
        lazy="selectin",
    )

    themes: Mapped[List["Theme"]] = relationship(back_populates="subject", cascade="all, delete-orphan")
