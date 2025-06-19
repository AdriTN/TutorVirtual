from __future__ import annotations
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator

Username = Annotated[
    str,
    Field(min_length=3, strip_whitespace=True)
]

class RegisterIn(BaseModel):
    username: Username
    email:    EmailStr
    password: str = Field(
        ...,
        min_length=8,
        description="Al menos 8 caracteres, 1 mayúscula, 1 minúscula, 1 dígito y 1 símbolo"
    )
    confirm_password: str

    @field_validator("password")
    @classmethod
    def _check_password_strength(cls, v: str) -> str:
        # longitud
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        # minúscula
        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe incluir al menos una letra minúscula")
        # mayúscula
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe incluir al menos una letra mayúscula")
        # dígito
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe incluir al menos un dígito")
        # símbolo (no alfanumérico)
        if not any(not c.isalnum() for c in v):
            raise ValueError("La contraseña debe incluir al menos un símbolo")
        return v

    @field_validator("confirm_password")
    @classmethod
    def _match_passwords(cls, v: str, info) -> str:
        if v != info.data.get("password"):
            raise ValueError("Las contraseñas no coinciden")
        return v

    model_config = dict(
        json_schema_extra={
            "example": {
                "username": "AdaLovelace",
                "email": "ada@example.com",
                "password": "Str0ng!Pass1",
                "confirm_password": "Str0ng!Pass1",
            }
        }
    )


class RegisterOut(BaseModel):
    id:       int
    username: str
    email:    EmailStr
