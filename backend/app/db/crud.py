from sqlalchemy.ext.asyncio import AsyncConnection
from app.db.models import sessions, messages
from sqlalchemy import insert, select, update
from typing import Dict, List

from app.api.schemas import SessionCreate, MessageCreate


async def create_session(conn: AsyncConnection, session_data: SessionCreate) -> Dict | None:
    # build the query
    stmt = insert(sessions).values(
        **session_data.model_dump()).returning(sessions)
    result = await conn.execute(stmt)
    # fetch the result
    new_session = result.fetchone()
    await conn.commit()
    # convert the result to a dictionary and return it if it exists
    return new_session._asdict() if new_session else None


async def get_all_sessions(conn: AsyncConnection, limit: int = 10, skip: int = 0) -> List[Dict] | None:
    # build the query
    query = select(sessions).order_by(
        sessions.c.created_at.desc()).limit(limit).offset(skip)
    # execute the query
    result = await conn.execute(query)
    session_rows = result.fetchall()
    return [session_row._asdict() for session_row in session_rows]


async def get_session_by_id(conn: AsyncConnection, session_id: int) -> Dict | None:
    # build the query
    query = select(sessions).where(sessions.c.id == session_id)
    result = await conn.execute(query)
    session_row = result.fetchone()

    # convert the result to a dictionary and return it if it exists
    return session_row._asdict() if session_row else None


async def update_session_status(conn: AsyncConnection, session_id: int, status: str) -> Dict | None:
    stmt = update(sessions).where(sessions.c.id ==
                                  session_id).values(status=status)
    result = await conn.execute(stmt)
    await conn.commit()
    # For UPDATE statements, we don't need to fetch results
    return None


# messages management


async def create_message(conn: AsyncConnection, message_data: MessageCreate) -> Dict | None:
    stmt = insert(messages).values(
        **message_data.model_dump()).returning(messages)

    result = await conn.execute(stmt)

    message_row = result.fetchone()

    await conn.commit()

    return message_row._asdict() if message_row else None


async def get_messages_by_session_id(conn: AsyncConnection, session_id: int, skip: int = 0, limit: int = 10) -> List[Dict] | None:
    query = select(messages).where(messages.c.session_id == session_id).order_by(
        messages.c.created_at.desc()).limit(limit).offset(skip)
    result = await conn.execute(query)
    message_rows = result.fetchall()
    return [message_row._asdict() for message_row in message_rows]
