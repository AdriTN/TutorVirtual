from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import course, subject, user

from .routes.user import router as user_router
from .routes.authentication import router as login_router
from .routes.register import router as register_router
from .routes.google import router as google_router
from .routes.subjects import router as subject_router
from .routes.course import router as course_router

from dotenv import load_dotenv
import os

app = FastAPI(
    title="Tutor Virtual",
    version="0.0.1",
    openapi_components={
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer"
            }
        }
    }
)

origins = [
    f'http://localhost:{os.getenv("PORT")}',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["home"])
def home():
    return {"Hello": "World"}

app.include_router(user_router, prefix="/api", tags=["Users"])
app.include_router(login_router, prefix="/api", tags=["Login"])
app.include_router(register_router, prefix="/api", tags=["Register"])
app.include_router(google_router, prefix="/api", tags=["Google"])
app.include_router(subject_router, prefix="/api", tags=["Subjects"])
app.include_router(course_router, prefix="/api", tags=["Courses"])
