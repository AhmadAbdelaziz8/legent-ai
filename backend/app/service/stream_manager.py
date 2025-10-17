import asyncio
from typing import Dict
from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse


class StreamManager:
    def __init__(self):
        self.streams: Dict[int, asyncio.Queue] = {}

    def create_stream(self, session_id: int):
        if session_id not in self.streams:
            self.streams[session_id] = asyncio.Queue()
            print(f"Stream created for session_id: {session_id}")

    async def send_message(self, session_id: int, message: str):
        if queue := self.streams.get(session_id):
            await queue.put(message)

    def get_stream(self, session_id: int) -> asyncio.Queue | None:
        return self.streams.get(session_id)

    def close_stream(self, session_id: int):
        # The main cleanup is to remove the queue from the dictionary
        if session_id in self.streams:
            del self.streams[session_id]
            print(f"Stream closed for session_id: {session_id}")


stream_manager = StreamManager()


async def stream_generator(session_id: int, request: Request) -> StreamingResponse:
    queue = stream_manager.get_stream(session_id)

    if not queue:
        raise HTTPException(status_code=404, detail="Stream not found")

    try:
        while True:
            # check if the client has closed the connection
            if not request.client.is_connected:
                break

            try:
                message = asyncio.wait_for(queue.get(), timeout=10)

                if message is None:
                    break

                yield f"data: {message}\n\n"

            except asyncio.TimeoutError:
                yield f"data: timeout\n\n"
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    except asyncio.CancelledError:
        pass
    finally:
        stream_manager.close_stream(session_id)
