from sqlalchemy import String, Text
from sqlalchemy.orm import RelationshipProperty

from src.database.base import Base
# Importamos los modelos para que se registren en Base.metadata
import src.models.subject
import src.models.course
import src.models.user
import src.models.theme

from src.models.subject import Subject
from src.models.course import Course
from src.models.user import User
from src.models.theme import Theme


def test_subject_table_registered():
    """La tabla 'subjects' debe estar registrada en Base.metadata."""
    assert "subjects" in Base.metadata.tables


def test_subject_columns_definition():
    """Comprueba nombres, tipos, nullabilidad, PKs y defaults de las columnas."""
    tbl = Base.metadata.tables["subjects"]
    cols = list(tbl.columns)
    expected = ["id", "name", "description"]
    assert [c.name for c in cols] == expected

    # id es PK y no nullable
    assert tbl.c.id.primary_key is True
    assert tbl.c.id.nullable is False

    # name → String(255), not null, unique, indexed
    name = tbl.c.name
    assert isinstance(name.type, String)
    assert name.type.length == 255
    assert name.nullable is False
    assert name.unique is True
    assert name.index is True

    # description → Text, nullable
    desc = tbl.c.description
    assert isinstance(desc.type, Text)
    assert desc.nullable is True


def test_subject_relationships():
    """Verifica las relaciones ORM: courses, users y themes."""
    mapper = Subject.__mapper__
    rels: dict[str, RelationshipProperty] = mapper.relationships

    # 1) courses: secondary=course_subjects, back_populates="subjects"
    assert "courses" in rels
    r_courses = rels["courses"]
    assert r_courses.mapper.class_ is Course
    assert r_courses.secondary.name == "course_subjects"
    assert r_courses.back_populates == "subjects"
    assert r_courses.uselist is True

        # 2) enrolled_users: secondary=user_enrollments, back_populates="enrolled_subjects", viewonly=True
    assert "enrolled_users" in rels
    r_users = rels["enrolled_users"]
    assert r_users.mapper.class_ is User
    assert r_users.secondary.name == "user_enrollments"
    assert r_users.viewonly is True # Clave para estas relaciones
    assert r_users.back_populates is None # No debe tener back_populates directo
    assert r_users.uselist is True
        
    # 3) themes: back_populates="subject", debe incluir delete y delete-orphan
    assert "themes" in rels
    r_themes = rels["themes"]
    assert r_themes.mapper.class_ is Theme
    assert r_themes.back_populates == "subject"

    # Comprobamos que la cascada efectivamente incluye 'delete-orphan' y 'delete'
    cascade_opts = set(r_themes.cascade)
    assert "delete-orphan" in cascade_opts
    assert "delete" in cascade_opts
