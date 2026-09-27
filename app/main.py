from fastapi import FastAPI

from app.routers import auth, bookings, centres

app = FastAPI(title="EVE Backend")

app.include_router(auth.router)
app.include_router(centres.router)
app.include_router(bookings.router)


@app.get("/")
def root():
    return {"message": "EVE Backend"}
