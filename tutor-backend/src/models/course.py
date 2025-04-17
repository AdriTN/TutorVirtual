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
from ..database.database import Base
from .user import User
from .subject import Subject

user_courses = Table(
    'user_courses',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id', ondelete='CASCADE'), primary_key=True),
    UniqueConstraint('user_id', 'course_id', name='uq_user_course')
)

course_subjects = Table(
    'course_subjects',
    Base.metadata,
    Column('course_id', Integer, ForeignKey('courses.id', ondelete='CASCADE'), primary_key=True),
    Column('subject_id', Integer, ForeignKey('subjects.id', ondelete='CASCADE'), primary_key=True),
    UniqueConstraint('course_id', 'subject_id', name='uq_course_subject')
)

class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    subjects = relationship(
        'Subject',
        secondary='course_subjects',
        back_populates='courses'
    )
    students = relationship(
        'User',
        secondary=user_courses,
        back_populates='courses'
    )

User.courses = relationship(
    'Course',
    secondary=user_courses,
    back_populates='students'
)