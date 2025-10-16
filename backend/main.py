from fastapi import FastAPI
from app.api.sessions import router as sessions_router

app = FastAPI()

app.include_router(sessions_router, prefix="/sessions", tags=["sessions"])


@app.get("/")
def health_endpoint():
    return {"message": "the server is running"}
