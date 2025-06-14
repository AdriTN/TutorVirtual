"""
Importar aquí todos los modelos para que `alembic` los detecte sin problemas.
"""
from .user import User, UserProvider, RefreshToken
from .course import Course
from .subject import Subject
from .theme import Theme
from .exercise import Exercise
from .user_theme_progress import UserThemeProgress
from .user_response import UserResponse
from . import associations
