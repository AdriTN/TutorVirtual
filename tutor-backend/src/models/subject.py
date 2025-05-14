from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from database.database import Base

class Subject(Base):
    __tablename__ = 'subjects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    courses = relationship(
        'Course',
        secondary='course_subjects',
        back_populates='subjects'
    )
    
    students = relationship(
        'User',
        secondary='user_subjects',
        back_populates='subjects'
    )
    
    themes  = relationship(
        'Tema',
        back_populates='subject'
    )
