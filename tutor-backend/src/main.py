from fastapi import FastAPI

from src.routes.user import router as user_router
from src.routes.login import router as login_router
from src.routes.register import router as register_router

app = FastAPI()

app.title = "Tutor Virtual"
app.version = "0.0.1"

@app.get("/", tags=["home"])
def home():
    return {"Hello": "World"}

app.include_router(user_router, prefix="/api", tags=["Users"])
app.include_router(login_router, prefix="/api", tags=["Login"])
app.include_router(register_router, prefix="/api", tags=["Register"])
