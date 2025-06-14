from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator

Username = Annotated[str, Field(min_length=3, strip_whitespace=True)]
Password = Annotated[
    str,
    Field(
        min_length=8,
        pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$",
        description="≥8 car., 1 mayús., 1 min., 1 dígito, 1 símbolo",
    ),
]


class RegisterIn(BaseModel):
    username: Username
    email: EmailStr
    password: Password
    confirm_password: Password

    @field_validator("confirm_password")
    @classmethod
    def _match(cls, v: str, values: dict[str, str]) -> str:
        if v != values.get("password"):
            raise ValueError("Las contraseñas no coinciden")
        return v

    model_config = dict(
        json_schema_extra={
            "example": {
                "username": "AdaLovelace",
                "email": "ada@example.com",
                "password": "Str0ng!Pass",
                "confirm_password": "Str0ng!Pass",
            }
        }
    )


class RegisterOut(BaseModel):
    id: int
    username: str
    email: EmailStr
