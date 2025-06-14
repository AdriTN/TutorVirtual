from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import RelationshipProperty

from app.models.course import Course
from app.models.associations import course_subjects, user_courses


def test_tablename_registered():
    """La tabla debe llamarse 'courses' y estar en Base.metadata."""
    table = Course.__table__
    assert table.name == "courses"
    # también está en metadata
    assert "courses" in Course.metadata.tables


def test_columns_definition():
    """Comprueba columnas id, title y description con sus atributos."""
    table = Course.__table__

    # id
    assert "id" in table.c
    id_col = table.c.id
    assert id_col.primary_key is True
    assert isinstance(id_col.type, Integer)

    # title
    assert "title" in table.c
    title_col = table.c.title
    assert isinstance(title_col.type, String)
    assert title_col.nullable is False
    assert title_col.unique is True
    assert title_col.index is True

    # description
    assert "description" in table.c
    desc_col = table.c.description
    assert isinstance(desc_col.type, Text)
    assert desc_col.nullable is True


def test_relationship_subjects():
    """La relación 'subjects' debe usar course_subjects y back_populates correcto."""
    rels = Course.__mapper__.relationships
    assert "subjects" in rels
    rel: RelationshipProperty = rels["subjects"]

    # secundaria y back_populates
    assert rel.secondary is course_subjects
    assert rel.back_populates == "courses"
    assert rel.lazy == "selectin"

    # target class name
    target = rel.entity.class_
    assert target.__name__ == "Subject"


def test_relationship_students():
    """La relación 'students' debe usar user_courses y back_populates correcto."""
    rels = Course.__mapper__.relationships
    assert "students" in rels
    rel: RelationshipProperty = rels["students"]

    assert rel.secondary is user_courses
    assert rel.back_populates == "courses"
    assert rel.lazy == "selectin"

    target = rel.entity.class_
    assert target.__name__ == "User"
