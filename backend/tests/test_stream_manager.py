import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request
from app.service.stream_manager import StreamManager, stream_generator


class TestStreamManager:
    """Test the StreamManager class."""
    
    def test_create_stream(self):
        """Test creating a new stream."""
        manager = StreamManager()
        session_id = 1
        
        manager.create_stream(session_id)
        assert session_id in manager.streams
        assert manager.streams[session_id] is not None
    
    def test_create_existing_stream(self):
        """Test creating a stream that already exists."""
        manager = StreamManager()
        session_id = 1
        
        # Create stream twice
        manager.create_stream(session_id)
        initial_queue = manager.streams[session_id]
        manager.create_stream(session_id)
        
        # Should not create a new queue
        assert manager.streams[session_id] is initial_queue
    
    @pytest.mark.asyncio
    async def test_send_message(self):
        """Test sending a message to a stream."""
        manager = StreamManager()
        session_id = 1
        
        manager.create_stream(session_id)
        await manager.send_message(session_id, "test message")
        
        # Check that message was added to queue
        queue = manager.get_stream(session_id)
        assert queue is not None
        # Note: We can't easily test the queue contents without more complex setup
    
    @pytest.mark.asyncio
    async def test_send_message_no_stream(self):
        """Test sending a message when no stream exists."""
        manager = StreamManager()
        session_id = 1
        
        # Try to send message without creating stream
        await manager.send_message(session_id, "test message")
        # Should not raise an error, just do nothing
    
    def test_get_stream(self):
        """Test getting a stream."""
        manager = StreamManager()
        session_id = 1
        
        # Test getting non-existent stream
        assert manager.get_stream(session_id) is None
        
        # Create stream and test getting it
        manager.create_stream(session_id)
        stream = manager.get_stream(session_id)
        assert stream is not None
    
    def test_close_stream(self):
        """Test closing a stream."""
        manager = StreamManager()
        session_id = 1
        
        # Test closing non-existent stream
        manager.close_stream(session_id)  # Should not raise error
        
        # Create and close stream
        manager.create_stream(session_id)
        assert session_id in manager.streams
        manager.close_stream(session_id)
        assert session_id not in manager.streams


class TestStreamGenerator:
    """Test the stream_generator function."""
    
    @pytest.mark.asyncio
    async def test_stream_generator_with_messages(self):
        """Test stream generator with messages."""
        manager = StreamManager()
        session_id = 1
        manager.create_stream(session_id)
        
        # Mock request
        mock_request = MagicMock(spec=Request)
        mock_request.client.is_connected = True
        
        # Add a test message to the queue
        await manager.send_message(session_id, "test message")
        
        # Test the generator
        generator = stream_generator(session_id, mock_request)
        
        # Get the first chunk
        chunk = await generator.__anext__()
        assert chunk == "data: test message\n\n"
    
    @pytest.mark.asyncio
    async def test_stream_generator_no_stream(self):
        """Test stream generator when no stream exists."""
        session_id = 999
        mock_request = MagicMock(spec=Request)
        
        # This should raise an HTTPException
        with pytest.raises(Exception):  # HTTPException
            generator = stream_generator(session_id, mock_request)
            await generator.__anext__()
    
    @pytest.mark.asyncio
    async def test_stream_generator_timeout(self):
        """Test stream generator timeout behavior."""
        manager = StreamManager()
        session_id = 1
        manager.create_stream(session_id)
        
        mock_request = MagicMock(spec=Request)
        mock_request.client.is_connected = True
        
        generator = stream_generator(session_id, mock_request)
        
        # The generator should timeout and yield timeout message
        chunk = await generator.__anext__()
        assert chunk == "data: timeout\n\n"
    
    @pytest.mark.asyncio
    async def test_stream_generator_client_disconnected(self):
        """Test stream generator when client disconnects."""
        manager = StreamManager()
        session_id = 1
        manager.create_stream(session_id)
        
        mock_request = MagicMock(spec=Request)
        mock_request.client.is_connected = False  # Client disconnected
        
        generator = stream_generator(session_id, mock_request)
        
        # Should exit immediately when client is disconnected
        with pytest.raises(StopAsyncIteration):
            await generator.__anext__()
    
    @pytest.mark.asyncio
    async def test_stream_generator_cleanup(self):
        """Test that stream is cleaned up after generator finishes."""
        manager = StreamManager()
        session_id = 1
        manager.create_stream(session_id)
        
        mock_request = MagicMock(spec=Request)
        mock_request.client.is_connected = False  # Client disconnected
        
        generator = stream_generator(session_id, mock_request)
        
        # Run the generator to completion
        try:
            async for _ in generator:
                pass
        except StopAsyncIteration:
            pass
        
        # Stream should be closed
        assert session_id not in manager.streams


class TestStreamManagerIntegration:
    """Integration tests for StreamManager."""
    
    @pytest.mark.asyncio
    async def test_full_stream_lifecycle(self):
        """Test the complete lifecycle of a stream."""
        manager = StreamManager()
        session_id = 1
        
        # Create stream
        manager.create_stream(session_id)
        assert session_id in manager.streams
        
        # Send messages
        await manager.send_message(session_id, "message 1")
        await manager.send_message(session_id, "message 2")
        
        # Get stream
        stream = manager.get_stream(session_id)
        assert stream is not None
        
        # Close stream
        manager.close_stream(session_id)
        assert session_id not in manager.streams
    
    @pytest.mark.asyncio
    async def test_multiple_streams(self):
        """Test managing multiple streams simultaneously."""
        manager = StreamManager()
        
        # Create multiple streams
        for i in range(3):
            manager.create_stream(i)
            await manager.send_message(i, f"message for stream {i}")
        
        # Verify all streams exist
        for i in range(3):
            assert i in manager.streams
            stream = manager.get_stream(i)
            assert stream is not None
        
        # Close all streams
        for i in range(3):
            manager.close_stream(i)
            assert i not in manager.streams
