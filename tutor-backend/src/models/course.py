from __future__ import annotations

from typing import List

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.models.associations import course_subjects, user_courses, user_enrollments 


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int]       = mapped_column(primary_key=True)
    title: Mapped[str]    = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    # Asignaturas que componen este curso
    subjects: Mapped[List["Subject"]] = relationship(
        secondary=course_subjects,
        back_populates="courses",
        lazy="selectin",
    )

    # Estudiantes con acceso general a este curso
    students: Mapped[List["User"]] = relationship(
        secondary=user_courses,
        back_populates="courses",
        lazy="selectin",
    )

    # Estudiantes matriculados en al menos una asignatura de este curso
    enrolled_students: Mapped[List["User"]] = relationship(
        secondary=user_enrollments,
        back_populates="enrolled_in_courses",
        viewonly=True,
        lazy="selectin"
    )
