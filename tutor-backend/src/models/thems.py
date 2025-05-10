from unittest.mock import Base

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship


class Tema(Base):
    __tablename__ = 'temas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)

    ejercicios = relationship('Ejercicio', back_populates='tema')
