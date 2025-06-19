from pydantic import BaseModel, Field


class LogoutIn(BaseModel):
    """Payload que envía el cliente para cerrar sesión."""
    refresh_token: str = Field(..., min_length=10, example="8dd9e7b0…")
