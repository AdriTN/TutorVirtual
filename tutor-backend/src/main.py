from fastapi import FastAPI

from src.models.user import router as user_router

app = FastAPI()

app.title = "Tutor Virtual"
app.version = "0.0.1"

@app.get("/", tags=["home"])
def home():
    return {"Hello": "World"}

app.include_router(user_router, prefix="/api", tags=["Users"])
