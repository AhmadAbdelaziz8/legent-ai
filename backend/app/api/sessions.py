from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncConnection
from typing import List

# Use the planned schema path
from app.api.schemas import SessionCreate, Session
from app.db import crud
# Use our safe dependency function
from app.db.database import get_db_connection
import logging
from app.service.stream_manager import stream_manager, stream_generator
from app.service.agent_service import run_agent_session

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/", response_model=Session, status_code=status.HTTP_201_CREATED)
async def create_new_session(
    session_in: SessionCreate,
    background_tasks: BackgroundTasks,
    # Use our dependency for safe connection handling
    conn: AsyncConnection = Depends(get_db_connection)
):

    new_session = await crud.create_session(conn=conn, session_data=session_in)
    if not new_session:
        # Use HTTPException for unexpected server errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create the task."
        )

    # Start the background task to run the agent session
    background_tasks.add_task(
        run_agent_session,
        session_id=new_session["id"],
        initial_prompt=session_in.initial_prompt,
        provider=session_in.provider
    )

    # Return the data directly. FastAPI will serialize it.
    return new_session


@router.get("/", response_model=List[Session])
async def read_sessions(
    skip: int = 0,
    limit: int = 100,
    conn: AsyncConnection = Depends(get_db_connection)
):
    db_sessions = await crud.get_all_sessions(conn=conn, skip=skip, limit=limit)
    return db_sessions


@router.get("/{session_id}", response_model=Session)
async def read_session(
    session_id: int,
    conn: AsyncConnection = Depends(get_db_connection)
):

    db_session = await crud.get_session_by_id(conn=conn, session_id=session_id)
    if db_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return db_session


@router.get("/{session_id}/stream")
async def stream_session_updates(session_id: int, request: Request) -> StreamingResponse:

    # Create a stream for the session if it doesn't exist (e.g., if client connects fast)
    stream_manager.create_stream(session_id)

    return StreamingResponse(
        stream_generator(session_id, request),
        media_type="text/event-stream"
    )
