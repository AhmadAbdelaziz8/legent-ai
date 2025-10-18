import asyncio
import json
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
        else:
            print(f"Stream already exists for session_id: {session_id}")

    async def send_message(self, session_id: int, message: str):
        print(f"🔧 [STREAM] send_message called for session {session_id}")
        if queue := self.streams.get(session_id):
            print(
                f"✅ [STREAM] Queue found for session {session_id}, putting message")
            await queue.put(message)
            print(f"✅ [STREAM] Message queued for session {session_id}")
        else:
            print(f"❌ [STREAM] No queue found for session {session_id}")

    def get_stream(self, session_id: int) -> asyncio.Queue | None:
        return self.streams.get(session_id)

    def close_stream(self, session_id: int):
        # The main cleanup is to remove the queue from the dictionary
        if session_id in self.streams:
            del self.streams[session_id]
            print(f"Stream closed for session_id: {session_id}")


stream_manager = StreamManager()


async def stream_generator(session_id: int, request: Request):
    print(f"🔗 [STREAM] Starting stream generator for session {session_id}")
    queue = stream_manager.get_stream(session_id)

    if not queue:
        print(f"❌ [STREAM] No stream found for session {session_id}")
        raise HTTPException(status_code=404, detail="Stream not found")

    print(f"✅ [STREAM] Stream found for session {session_id}, starting loop")
    try:
        while True:
            # Check if the client has closed the connection
            # Note: request.client.is_connected may not be available in all FastAPI versions
            try:
                if hasattr(request.client, 'is_connected') and not request.client.is_connected:
                    break
            except AttributeError:
                # If is_connected is not available, we'll rely on the timeout mechanism
                pass

            try:
                # Use a shorter timeout and proper SSE format
                print(
                    f"🔧 [STREAM] Waiting for message from queue for session {session_id}")
                message = await asyncio.wait_for(queue.get(), timeout=1.0)
                print(f"✅ [STREAM] Received message from queue: {message}")

                if message is None:
                    print(f"🔧 [STREAM] Received None message, breaking")
                    break

                # Proper SSE format with proper line endings
                print(f"🔧 [STREAM] Yielding message to client: {message}")
                yield f"data: {message}\n\n"

            except asyncio.TimeoutError:
                # Send a keep-alive ping to maintain connection
                ping_data = {"type": "ping",
                             "timestamp": asyncio.get_event_loop().time()}
                yield f"data: {json.dumps(ping_data)}\n\n"
            except Exception as e:
                print(f"Stream error for session {session_id}: {e}")
                error_data = {"type": "error", "message": str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
                break
    except asyncio.CancelledError:
        print(f"Stream cancelled for session {session_id}")
    except Exception as e:
        print(f"Stream generator error for session {session_id}: {e}")
    finally:
        stream_manager.close_stream(session_id)
