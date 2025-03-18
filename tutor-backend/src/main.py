from fastapi import FastAPI

from src.models.user import create_users_table

app = FastAPI()

app.title = "Tutor Virtual"
app.version = "0.0.1"

@app.get("/", tags=["home"])
def home():
    return {"Hello": "World"}

@app.lifespan("startup")
def on_startup():
    create_users_table()