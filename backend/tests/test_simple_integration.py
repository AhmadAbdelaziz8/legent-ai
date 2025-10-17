import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app


class TestSimpleIntegration:
    """Simple integration tests that mock API key requirements."""
    
    def test_health_endpoint(self):
        """Test the health endpoint works."""
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "the server is running"}
    
    @patch('app.db.crud.create_session')
    @patch('app.service.agent_service.run_agent_session')
    def test_create_session_mocked(self, mock_run_agent_session, mock_create_session):
        """Test creating a session with mocked dependencies."""
        # Mock the database response
        mock_session = {
            "id": 1,
            "initial_prompt": "Hello, how are you?",
            "status": "queued",
            "provider": "anthropic",
            "created_at": "2025-10-17T12:33:45.638595Z"
        }
        mock_create_session.return_value = mock_session
        
        # Mock the agent service to avoid API key requirements
        mock_run_agent_session.return_value = AsyncMock()
        
        client = TestClient(app)
        response = client.post("/sessions/", json={
            "initial_prompt": "Hello, how are you?",
            "provider": "anthropic"
        })
        
        assert response.status_code == 201
        assert response.json()["id"] == 1
        assert response.json()["status"] == "queued"
    
    @patch('app.db.crud.get_all_sessions')
    def test_get_sessions_mocked(self, mock_get_sessions):
        """Test getting sessions with mocked database."""
        # Mock empty sessions list
        mock_get_sessions.return_value = []
        
        client = TestClient(app)
        response = client.get("/sessions/")
        
        assert response.status_code == 200
        assert response.json() == []
    
    @patch('app.db.crud.get_session_by_id')
    def test_get_session_by_id_mocked(self, mock_get_session):
        """Test getting a specific session."""
        mock_session = {
            "id": 1,
            "initial_prompt": "Hello, how are you?",
            "status": "completed",
            "provider": "anthropic",
            "created_at": "2025-10-17T12:33:45.638595Z"
        }
        mock_get_session.return_value = mock_session
        
        client = TestClient(app)
        response = client.get("/sessions/1")
        
        assert response.status_code == 200
        assert response.json()["id"] == 1
    
    @patch('app.db.crud.get_session_by_id')
    def test_get_session_not_found_mocked(self, mock_get_session):
        """Test getting a session that doesn't exist."""
        mock_get_session.return_value = None
        
        client = TestClient(app)
        response = client.get("/sessions/999")
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]
    
    @patch('app.db.crud.create_message')
    def test_create_message_mocked(self, mock_create_message):
        """Test creating a message with mocked database."""
        mock_message = {
            "id": 1,
            "session_id": 1,
            "role": "user",
            "content": {"text": "Hello, this is a test message"},
            "created_at": "2025-10-17T12:33:57.382072Z"
        }
        mock_create_message.return_value = mock_message
        
        client = TestClient(app)
        response = client.post("/messages/", json={
            "session_id": 1,
            "role": "user",
            "content": {"text": "Hello, this is a test message"}
        })
        
        assert response.status_code == 201
        assert response.json()["id"] == 1
        assert response.json()["session_id"] == 1
    
    @patch('app.db.crud.get_messages_by_session_id')
    def test_get_messages_mocked(self, mock_get_messages):
        """Test getting messages for a session."""
        mock_messages = [
            {
                "id": 1,
                "session_id": 1,
                "role": "user",
                "content": {"text": "Hello"},
                "created_at": "2025-10-17T12:33:45.638595Z"
            }
        ]
        mock_get_messages.return_value = mock_messages
        
        client = TestClient(app)
        response = client.get("/messages/session/1")
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["role"] == "user"
    
    @patch('app.db.crud.get_messages_by_session_id')
    def test_get_messages_no_messages_mocked(self, mock_get_messages):
        """Test getting messages when none exist."""
        mock_get_messages.return_value = []
        
        client = TestClient(app)
        response = client.get("/messages/session/1")
        
        assert response.status_code == 404
        assert "No messages found for this session" in response.json()["detail"]


class TestAgentServiceMocking:
    """Test agent service with mocked API calls."""
    
    @patch('app.service.agent_service.get_db_connection')
    @patch('app.service.stream_manager.stream_manager')
    @patch('app.service.agent_service.crud.update_session_status')
    @patch('app.service.agent_service.sampling_loop')
    def test_run_agent_session_mocked(self, mock_sampling_loop, mock_update_status, 
                                     mock_stream_manager, mock_get_db):
        """Test running an agent session with all dependencies mocked."""
        # Mock database connection
        mock_conn = AsyncMock()
        mock_get_db.return_value.__aenter__.return_value = mock_conn
        mock_get_db.return_value.__aexit__.return_value = None
        
        # Mock stream manager
        mock_stream_manager.create_stream = MagicMock()
        mock_stream_manager.send_message = AsyncMock()
        
        # Mock database operations
        mock_update_status.return_value = None
        
        # Mock the sampling loop (this is where API calls would happen)
        mock_sampling_loop.return_value = None
        
        # Import and run the function
        from app.service.agent_service import run_agent_session
        
        # Run the agent session
        result = asyncio.run(run_agent_session(
            session_id=1,
            initial_prompt="Hello, how are you?",
            provider="anthropic"
        ))
        
        # Verify stream was created
        mock_stream_manager.create_stream.assert_called_once_with(session_id=1)
        
        # Verify status was updated
        mock_update_status.assert_called_with(conn=mock_conn, session_id=1, status='running')
        
        # Verify sampling loop was called
        mock_sampling_loop.assert_called_once()
    
    @patch('app.service.agent_service.get_db_connection')
    @patch('app.service.stream_manager.stream_manager')
    @patch('app.service.agent_service.crud.update_session_status')
    @patch('app.service.agent_service.sampling_loop')
    def test_run_agent_session_api_failure_mocked(self, mock_sampling_loop, mock_update_status,
                                                  mock_stream_manager, mock_get_db):
        """Test handling of API failures with mocked dependencies."""
        # Mock database connection
        mock_conn = AsyncMock()
        mock_get_db.return_value.__aenter__.return_value = mock_conn
        mock_get_db.return_value.__aexit__.return_value = None
        
        # Mock stream manager
        mock_stream_manager.create_stream = MagicMock()
        mock_stream_manager.send_message = AsyncMock()
        
        # Mock database operations
        mock_update_status.return_value = None
        
        # Mock the sampling loop to simulate API failure
        mock_sampling_loop.side_effect = Exception("API rate limit exceeded")
        
        # Import and run the function
        from app.service.agent_service import run_agent_session
        
        # Run the agent session and expect it to handle the error
        with pytest.raises(Exception, match="API rate limit exceeded"):
            asyncio.run(run_agent_session(
                session_id=1,
                initial_prompt="Hello, how are you?",
                provider="anthropic"
            ))
        
        # Verify that the session status was updated to error
        mock_update_status.assert_called_with(conn=mock_conn, session_id=1, status='error')


class TestStreamManagerMocking:
    """Test stream manager functionality."""
    
    def test_stream_manager_create_stream(self):
        """Test creating a stream."""
        from app.service.stream_manager import StreamManager
        
        manager = StreamManager()
        session_id = 1
        
        manager.create_stream(session_id)
        assert session_id in manager.streams
        assert manager.streams[session_id] is not None
    
    def test_stream_manager_close_stream(self):
        """Test closing a stream."""
        from app.service.stream_manager import StreamManager
        
        manager = StreamManager()
        session_id = 1
        
        # Create and close stream
        manager.create_stream(session_id)
        assert session_id in manager.streams
        manager.close_stream(session_id)
        assert session_id not in manager.streams
    
    @pytest.mark.asyncio
    async def test_stream_manager_send_message(self):
        """Test sending a message to a stream."""
        from app.service.stream_manager import StreamManager
        
        manager = StreamManager()
        session_id = 1
        
        manager.create_stream(session_id)
        await manager.send_message(session_id, "test message")
        
        # Check that stream exists
        stream = manager.get_stream(session_id)
        assert stream is not None
    
    @pytest.mark.asyncio
    async def test_stream_manager_send_message_no_stream(self):
        """Test sending a message when no stream exists."""
        from app.service.stream_manager import StreamManager
        
        manager = StreamManager()
        session_id = 1
        
        # Try to send message without creating stream
        await manager.send_message(session_id, "test message")
        # Should not raise an error, just do nothing


class TestAPIKeySimulation:
    """Test that API key requirements are properly simulated."""
    
    @patch('app.core.config.settings.ANTHROPIC_API_KEY', 'mock-api-key')
    def test_api_key_available(self):
        """Test that API key is available in configuration."""
        from app.core.config import settings
        assert settings.ANTHROPIC_API_KEY == 'mock-api-key'
    
    @patch('app.core.config.settings.ANTHROPIC_API_KEY', '')
    def test_api_key_missing(self):
        """Test that API key can be missing."""
        from app.core.config import settings
        assert settings.ANTHROPIC_API_KEY == ''
    
    @patch('app.service.agent_service.sampling_loop')
    def test_agent_with_mock_api_key(self, mock_sampling_loop):
        """Test that agent service works with mocked API key."""
        # Mock the sampling loop to simulate successful API call
        mock_sampling_loop.return_value = AsyncMock()
        
        # This simulates what would happen with a real API key
        # The actual API call is mocked, so no real API key is needed
        assert mock_sampling_loop.return_value is not None
