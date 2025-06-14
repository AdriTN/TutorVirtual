from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int]        = mapped_column(primary_key=True, index=True)
    username: Mapped[str]  = mapped_column(String(120), nullable=False)
    email: Mapped[str]     = mapped_column(String(255), nullable=False, unique=True, index=True)
    password: Mapped[str]  = mapped_column(String(100), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    providers:       Mapped[List["UserProvider"]]   = relationship(back_populates="user", cascade="all, delete-orphan")
    refresh_tokens:  Mapped[List["RefreshToken"]]   = relationship(back_populates="user", cascade="all, delete-orphan")
    respuestas:      Mapped[List["UserResponse"]]   = relationship(back_populates="user", cascade="all, delete-orphan")
    progress:        Mapped[List["UserThemeProgress"]] = relationship(cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("char_length(username) >= 3", name="chk_username_minlen"),
    )


class UserProvider(Base):
    __tablename__ = "users_providers"

    id: Mapped[int]               = mapped_column(primary_key=True)
    user_id: Mapped[int]          = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    provider: Mapped[str]         = mapped_column(String(50), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)

    user: Mapped[User] = relationship(back_populates="providers")

    __table_args__ = (
        CheckConstraint("char_length(provider_user_id) > 0", name="chk_provider_uid"),
        CheckConstraint("char_length(provider) > 0",          name="chk_provider_name"),
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int]        = mapped_column(primary_key=True)
    user_id: Mapped[int]   = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str]     = mapped_column(String(255), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    user: Mapped[User] = relationship(back_populates="refresh_tokens")
