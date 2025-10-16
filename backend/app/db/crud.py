from sqlalchemy.ext.asyncio import AsyncConnection
from app.db.models import sessions
from sqlalchemy import insert, select
from typing import Dict, List

from app.schemas.session import SessionCreate


async def create_session(conn: AsyncConnection, session_data: SessionCreate) -> Dict | None:
    # build the query
    stmt = insert(sessions).values(
        **session_data.model_dump()).returning(sessions)
    result = await conn.execute(stmt)
    await conn.commit()
    # fetch the result
    new_session = result.fetchone()
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
