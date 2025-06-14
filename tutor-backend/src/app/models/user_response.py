from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base


class UserResponse(Base):
    __tablename__ = "user_responses"

    id:        Mapped[int]      = mapped_column(primary_key=True)
    answer:    Mapped[str]      = mapped_column(Text, nullable=False)
    correct:   Mapped[bool]     = mapped_column(Boolean, nullable=False)
    time_sec:  Mapped[int | None]

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    user_id:     Mapped[int] = mapped_column(ForeignKey("users.id",     ondelete="CASCADE"), nullable=False)

    exercise: Mapped["Exercise"] = relationship(back_populates="responses")
    user:     Mapped["User"]     = relationship(back_populates="respuestas")

    __table_args__ = (UniqueConstraint("user_id", "exercise_id", name="uq_user_exercise"),)
