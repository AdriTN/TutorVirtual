from unittest.mock import Base

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

class RespuestaUsuario(Base):
    __tablename__ = 'respuestas_usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    respuesta = Column(Text, nullable=False)
    ejercicio_id = Column(Integer, ForeignKey('ejercicios.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    correcto = Column(Boolean, nullable=False)

    ejercicio = relationship('Ejercicio', back_populates='respuestas')
    user = relationship('User', back_populates='respuestas')
