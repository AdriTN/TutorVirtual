from database.database import Base
from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.orm import relationship


class RespuestaUsuario(Base):
    __tablename__ = "respuestas_usuarios"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    respuesta    = Column(Text,     nullable=False)
    correcto     = Column(Boolean,  nullable=False)

    tiempo_seg   = Column(Integer)
    respondida_en= Column(DateTime(timezone=True),
                           server_default=func.now(), nullable=False)

    ejercicio_id = Column(Integer,
                           ForeignKey("ejercicios.id", ondelete="CASCADE"),
                           nullable=False)
    user_id      = Column(Integer,
                           ForeignKey("users.id",      ondelete="CASCADE"),
                           nullable=False)

    ejercicio = relationship("Ejercicio", back_populates="respuestas")
    user      = relationship("User",      back_populates="respuestas")

    __table_args__ = (
        UniqueConstraint("user_id", "ejercicio_id", name="uq_user_ejercicio"),
    )
