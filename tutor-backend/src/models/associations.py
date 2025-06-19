"""
Tablas de unión puramente relacionales.
Se importan desde los modelos que las necesitan.
"""
from sqlalchemy import Column, ForeignKey, Integer, Table, UniqueConstraint

from src.database.base import Base

# ──────────────────────────────────────────────────────────────────────────
user_courses = Table(
    "user_courses",
    Base.metadata,
    Column("user_id",   Integer, ForeignKey("users.id",    ondelete="CASCADE"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("user_id", "course_id", name="uq_user_course"),
)

user_subjects = Table(
    "user_subjects",
    Base.metadata,
    Column("user_id",    Integer, ForeignKey("users.id",     ondelete="CASCADE"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("subjects.id",  ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("user_id", "subject_id", name="uq_user_subject"),
)

course_subjects = Table(
    "course_subjects",
    Base.metadata,
    Column("course_id",  Integer, ForeignKey("courses.id",   ondelete="CASCADE"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("subjects.id",  ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("course_id", "subject_id", name="uq_course_subject"),
)
