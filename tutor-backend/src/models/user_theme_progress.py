from database.database import Base
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func


class UserThemeProgress(Base):
    """
    Snapshot de progreso de un usuario en un tema.
    Se actualiza con UPSERT cada vez que responde a un ejercicio.
    """
    __tablename__ = "user_theme_progress"

    user_id   = Column(Integer,
                       ForeignKey("users.id",  ondelete="CASCADE"),
                       primary_key=True)
    tema_id   = Column(Integer,
                       ForeignKey("temas.id",  ondelete="CASCADE"),
                       primary_key=True)

    completed = Column(Integer, nullable=False, default=0)
    correct   = Column(Integer, nullable=False, default=0)

    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(),
                        nullable=False)
