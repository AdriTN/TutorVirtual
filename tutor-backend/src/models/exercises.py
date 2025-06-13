from database.database import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship


class Ejercicio(Base):
    __tablename__ = "ejercicios"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    enunciado   = Column(Text,    nullable=False)
    tipo        = Column(String(50),  nullable=False)
    dificultad  = Column(String(50),  nullable=False)

    respuesta   = Column(Text,        nullable=False)
    explicacion = Column(Text)

    created_at  = Column(DateTime(timezone=True),
                          server_default=func.now(), nullable=False)

    tema_id     = Column(Integer,
                         ForeignKey("temas.id", ondelete="CASCADE"),
                         nullable=False)

    tema        = relationship("Tema", back_populates="ejercicios")
    respuestas  = relationship("RespuestaUsuario", back_populates="ejercicio")
