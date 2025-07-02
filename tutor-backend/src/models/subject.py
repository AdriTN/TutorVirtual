from __future__ import annotations

from typing import List

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.models.associations import course_subjects, user_enrollments 


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int]      = mapped_column(primary_key=True)
    name: Mapped[str]    = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    # Cursos a los que pertenece esta asignatura
    courses: Mapped[List["Course"]] = relationship(
        secondary=course_subjects,
        back_populates="subjects",
        lazy="selectin",
    )

    # Usuarios matriculados en esta asignatura (a través de un curso específico)
    enrolled_users: Mapped[List["User"]] = relationship(
        secondary=user_enrollments,
        viewonly=True,
        lazy="selectin"
    )

    themes: Mapped[List["Theme"]] = relationship(back_populates="subject", cascade="all, delete-orphan")
