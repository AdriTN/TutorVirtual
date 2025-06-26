import pytest
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import RelationshipProperty

from src.database.base import Base
# Importamos los modelos relacionados para que se registren en Base.metadata
import src.models.subject
import src.models.exercise
import src.models.user_theme_progress
from src.models.theme import Theme
from src.models.subject import Subject
from src.models.exercise import Exercise
from src.models.user_theme_progress import UserThemeProgress


def test_theme_table_registered():
    """La tabla 'themes' debe estar registrada en Base.metadata."""
    assert "themes" in Base.metadata.tables


def test_theme_columns_definition():
    """Verifica nombres, tipos, nullabilidad, PKs y FK de las columnas."""
    tbl = Base.metadata.tables["themes"]
    cols = list(tbl.columns)
    # Esperamos exactamente estas columnas, en este orden
    assert [c.name for c in cols] == ["id", "name", "description", "subject_id"]

    # id
    assert tbl.c.id.primary_key is True
    assert tbl.c.id.nullable is False

    # name: String(255), not null, unique, indexed
    name = tbl.c.name
    assert isinstance(name.type, String)
    assert name.type.length == 255
    assert name.nullable is False
    assert name.unique is True
    assert name.index is True

    # description: Text, nullable
    desc = tbl.c.description
    assert isinstance(desc.type, Text)
    assert desc.nullable is True

    # subject_id: FK → subjects.id, not nullable
    fk = list(tbl.c.subject_id.foreign_keys)[0]
    assert fk.column.table.name == "subjects"
    assert fk.column.name == "id"
    assert tbl.c.subject_id.nullable is True


def test_theme_relationships():
    """Verifica las relaciones ORM definidas en Theme."""
    mapper = Theme.__mapper__
    rels: dict[str, RelationshipProperty] = mapper.relationships

    # 1) subject: many-to-one
    assert "subject" in rels
    r_subj = rels["subject"]
    assert r_subj.mapper.class_ is Subject
    assert r_subj.back_populates == "themes"
    # many-to-one → uselist=False
    assert r_subj.uselist is False

    # 2) exercises: one-to-many con back_populates y cascada delete-orphan
    assert "exercises" in rels
    r_ex = rels["exercises"]
    assert r_ex.mapper.class_ is Exercise
    assert r_ex.back_populates == "theme"
    assert r_ex.uselist is True
    cascade_opts = set(r_ex.cascade)
    assert "delete-orphan" in cascade_opts
    assert "delete" in cascade_opts

    # 3) progress: one-to-many sin back_populates, cascada delete-orphan
    assert "progress" in rels
    r_pr = rels["progress"]
    assert r_pr.mapper.class_ is UserThemeProgress
    # No back_populates configurado
    assert r_pr.back_populates is None
    assert r_pr.secondary is None
    assert r_pr.uselist is True
    cascade_opts = set(r_pr.cascade)
    assert "delete-orphan" in cascade_opts
    assert "delete" in cascade_opts
