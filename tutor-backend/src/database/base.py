from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative Base única."""
    repr = lambda self: f"<{self.__class__.__name__} {getattr(self,'id', '?')}>"
