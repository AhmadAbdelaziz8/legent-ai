from sqlalchemy import (JSON, DateTime, ForeignKey, MetaData, String,
                        Table, Column, Integer, true)
from sqlalchemy.sql import func

meta = MetaData()

sessions = Table(
    "sessions",
    meta,
    Column('id', Integer, primary_key=True, index=True),
    Column('initial_prompt', String),
    Column('status', String, default="queued"),
    Column('provider', String),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),

)

messages = Table(
    'messages',
    meta,
    Column('id', Integer, primary_key=True, index=True),
    Column('session_id', Integer, ForeignKey("sessions.id")),
    Column('role', String),
    Column('content', JSON),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)
