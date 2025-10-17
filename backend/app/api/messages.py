from fastapi import APIRouter, Depends, status, HTTPException
from app.api.schemas import MessageCreate, Message
from app.db.database import get_db_connection
from app.db import crud
from sqlalchemy.ext.asyncio import AsyncConnection
from typing import List
router = APIRouter()

# create message


@router.post("/", response_model=Message, status_code=status.HTTP_201_CREATED)
async def create_message(
    message: MessageCreate,
    conn: AsyncConnection = Depends(get_db_connection)
):
    new_message = await crud.create_message(conn=conn, message_data=message)
    if not new_message:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to create the message")
    return new_message


@router.get("/session/{session_id}", response_model=List[Message])
async def get_messages_by_session_id(
    session_id: int,
    conn: AsyncConnection = Depends(get_db_connection)
):
    messages = await crud.get_messages_by_session_id(conn=conn, session_id=session_id)
    if not messages:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No messages found for this session")
    return messages
