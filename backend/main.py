from fastapi import FastAPI
from app.api.sessions import router as sessions_router
from app.api.messages import router as messages_router
from app.routes.vnc import router as vnc_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router, prefix="/sessions", tags=["sessions"])
app.include_router(messages_router, prefix="/messages", tags=["messages"])
app.include_router(vnc_router)


@app.get("/")
def health_endpoint():
    return {"message": "the server is running"}
