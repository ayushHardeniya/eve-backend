from fastapi import FastAPI

app = FastAPI(title="EVE Backend")


@app.get("/")
def root():
    return {"message": "EVE Backend"}