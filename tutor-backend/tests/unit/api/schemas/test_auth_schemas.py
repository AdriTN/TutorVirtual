from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterIn(BaseModel):
    username: str
    email:    EmailStr
    password: str
    confirm_password: str

    @field_validator("username", mode="before")
    @classmethod
    def _strip_username(cls, v: str) -> str:
        # Strip whitespace before any other checks
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("username")
    @classmethod
    def _validate_username_length(cls, v: str) -> str:
        # Enforce minimum length of 3 with the exact test-expected message
        if len(v) < 3:
            raise ValueError("ensure this value has at least 3 characters")
        return v

    @field_validator("email", mode="after")
    @classmethod
    def _cast_email_str(cls, v: str) -> EmailStr:
        # Make sure email comes back as an EmailStr instance
        return EmailStr(v)

    @field_validator("password")
    @classmethod
    def _validate_password(cls, v: str) -> str:
        # Drop the unsupported look-around regex and do it by hand
        if len(v) < 8:
            raise ValueError("ensure this value has at least 8 characters")
        if not any(c.islower() for c in v):
            raise ValueError("ensure this value has at least one lowercase letter")
        if not any(c.isupper() for c in v):
            raise ValueError("ensure this value has at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("ensure this value has at least one digit")
        if not any(not c.isalnum() for c in v):
            raise ValueError("ensure this value has at least one symbol")
        return v

    @field_validator("confirm_password")
    @classmethod
    def _match_passwords(cls, v: str, info) -> str:
        # Must exactly match `password`
        if v != info.data.get("password"):
            raise ValueError("Las contraseñas no coinciden")
        return v

    model_config = dict(
        json_schema_extra={
            "example": {
                "username": "AdaLovelace",
                "email": "ada@example.com",
                "password": "Str0ng!Pass!",
                "confirm_password": "Str0ng!Pass!",
            }
        }
    )


class RegisterOut(BaseModel):
    id:       int
    username: str
    email:    EmailStr
