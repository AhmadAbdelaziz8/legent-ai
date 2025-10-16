from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncConnection
from typing import List

# Use the planned schema path
from app.schemas.session import SessionCreate, Session
from app.db import crud
# Use our safe dependency function
from app.db.database import get_db_connection

router = APIRouter()


@router.post("/", response_model=Session, status_code=status.HTTP_201_CREATED)
async def create_new_session(
    session_in: SessionCreate,
    # Use our dependency for safe connection handling
    conn: AsyncConnection = Depends(get_db_connection)
):
    """
    Create a new task.
    """
    new_session = await crud.create_session(conn=conn, session_data=session_in)
    if not new_session:
        # Use HTTPException for unexpected server errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create the task."
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
