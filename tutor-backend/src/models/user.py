import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, Boolean, CheckConstraint, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import relationship

from database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(120), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    is_admin = Column(Boolean, nullable=False, server_default="false")
    
    __table_args__ = (
        CheckConstraint("char_length(username) >= 3", name="chk_name_min_length"),
        CheckConstraint("password ~* '^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[^a-zA-Z0-9]).{8,}$'", 
                        name="chk_password_complexity"),
    )
    
    providers = relationship("UserProvider", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

class UserProvider(Base):
    __tablename__ = "users_providers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    
    __table_args__ = (
        UniqueConstraint("provider_user_id", "provider", name="uq_provider_user_id_provider"),
    )
    
    user = relationship("User", back_populates="providers")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship("User", back_populates="refresh_tokens")
