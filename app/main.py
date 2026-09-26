from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="EVE Backend")

app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "EVE Backend"}