import pytest
from sqlalchemy import Table, MetaData, UniqueConstraint

from src.database.base import Base
from src.models.associations import user_courses, user_enrollments, course_subjects

@pytest.fixture(scope="module")
def metadata() -> MetaData:
    # Cargamos el MetaData a partir de Base
    return Base.metadata

@pytest.mark.parametrize("tbl, name, col_defs, fk_defs, uq_cols", [
    (
        user_courses, 
        "user_courses",
        ["user_id", "course_id"],
        [("user_id", "users.id"), ("course_id", "courses.id")],
        [("user_id", "course_id")]
    ),
    (
        user_enrollments, 
        "user_enrollments",
        ["user_id", "subject_id", "course_id"],
        [("user_id", "users.id"), ("subject_id", "subjects.id"), ("course_id", "courses.id")],
        [("user_id", "subject_id", "course_id")]
    ),
    (
        course_subjects, 
        "course_subjects",
        ["course_id", "subject_id"],
        [("course_id", "courses.id"), ("subject_id", "subjects.id")],
        [("course_id", "subject_id")]
    ),
])
def test_relational_table_definition(metadata, tbl: Table, name: str, col_defs, fk_defs, uq_cols):
    # 1) La tabla está registrada en Base.metadata
    assert name in metadata.tables
    tbl_meta: Table = metadata.tables[name]
    
    # 2) Las columnas existen y son PK
    cols = list(tbl_meta.columns)
    assert [c.name for c in cols] == col_defs
    for c in cols:
        assert c.primary_key, f"{name}.{c.name} debería ser primary key"
    
    # 3) Cada ForeignKey apunta a la tabla/columna correcta
    fk_constraints = [
        (fk.parent.name, fk.column.table.name + "." + fk.column.name)
        for fk in tbl_meta.foreign_key_constraints
        for fk in [fk]  # flatten
        for fk in fk.elements
    ]
    # reconvertimos foreign key elements
    found = []
    for fk in tbl_meta.foreign_key_constraints:
        for elem in fk.elements:
            found.append((elem.parent.name, f"{elem.column.table.name}.{elem.column.name}"))
    assert sorted(found) == sorted(fk_defs)
    
    # 4) El UniqueConstraint existe sobre esas columnas
    uqs = [c for c in tbl_meta.constraints if isinstance(c, UniqueConstraint)]
    # sólo esperamos un único UniqueConstraint
    assert len(uqs) == 1
    uq = uqs[0]
    assert tuple(uq.columns.keys()) == uq_cols[0]

