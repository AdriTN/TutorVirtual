from __future__ import annotations

from typing import List

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.models.associations import course_subjects, user_courses


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int]       = mapped_column(primary_key=True)
    title: Mapped[str]    = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    subjects: Mapped[List["Subject"]] = relationship(
        secondary=course_subjects,
        back_populates="courses",
        lazy="selectin",
    )
    students: Mapped[List["User"]] = relationship(
        secondary=user_courses,
        back_populates="courses",
        lazy="selectin",
    )
