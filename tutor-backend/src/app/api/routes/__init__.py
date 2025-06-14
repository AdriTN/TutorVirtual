"""
Agrupa todos los routers en un único `api_router` que se importa en main.py
"""
from fastapi import APIRouter

from .auth      import router as auth_router
from .users     import router as users_router
from .courses   import router as courses_router
from .subjects  import router as subjects_router
from .themes    import router as themes_router
from .ai        import router as ai_router
from .answer   import router as answer_router
from .stats     import router as stats_router

api_router = APIRouter()
api_router.include_router(auth_router    , prefix="/auth"   , tags=["Auth"])
api_router.include_router(users_router   , prefix="/users"  , tags=["Users"])
api_router.include_router(courses_router , prefix="/courses", tags=["Courses"])
api_router.include_router(subjects_router, prefix="/subjects", tags=["Subjects"])
api_router.include_router(themes_router  , prefix="/themes" , tags=["Themes"])
api_router.include_router(ai_router      , prefix="/ai"     , tags=["Exercises"])
api_router.include_router(answer_router , prefix="/answers", tags=["Exercises"])
api_router.include_router(stats_router   , prefix="/stats"  , tags=["Stats"])
