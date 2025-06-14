from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database.base import Base


class UserThemeProgress(Base):
    __tablename__ = "user_theme_progress"

    user_id: Mapped[int]  = mapped_column(ForeignKey("users.id",  ondelete="CASCADE"), primary_key=True)
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id", ondelete="CASCADE"), primary_key=True)

    completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correct:   Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
