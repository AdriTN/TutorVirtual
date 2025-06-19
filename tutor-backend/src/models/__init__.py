"""
Importar aquí todos los modelos para que `alembic` los detecte sin problemas.
"""
from src.models.user import User, UserProvider, RefreshToken
from src.models.course import Course
from src.models.subject import Subject
from src.models.theme import Theme
from src.models.exercise import Exercise
from src.models.user_theme_progress import UserThemeProgress
from src.models.user_response import UserResponse
from src.models import associations
