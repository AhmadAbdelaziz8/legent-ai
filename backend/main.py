from fastapi import FastAPI
from app.api.sessions import router as sessions_router
from app.api.messages import router as messages_router

app = FastAPI()

app.include_router(sessions_router, prefix="/sessions", tags=["sessions"])
app.include_router(messages_router, prefix="/messages", tags=["messages"])


@app.get("/")
def health_endpoint():
    return {"message": "the server is running"}
