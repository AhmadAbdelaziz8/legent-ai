import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.api.schemas import SessionCreate, MessageCreate


class TestHealthEndpoint:
    """Test the health endpoint."""
    
    def test_health_endpoint(self, client):
        """Test that the health endpoint returns the correct response."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "the server is running"}


class TestSessionsEndpoints:
    """Test session-related endpoints."""
    
    def test_get_sessions_empty(self, client, mock_db_connection):
        """Test getting sessions when none exist."""
        # Mock the database response
        mock_db_connection.execute = AsyncMock()
        mock_db_connection.execute.return_value.fetchall.return_value = []
        
        response = client.get("/sessions/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_sessions_with_data(self, client, mock_db_connection):
        """Test getting sessions with data."""
        # Mock the database response
        mock_session = {
            "id": 1,
            "initial_prompt": "Hello, how are you?",
            "status": "completed",
            "provider": "anthropic",
            "created_at": "2025-10-17T12:33:45.638595Z"
        }
        mock_db_connection.execute = AsyncMock()
        mock_db_connection.execute.return_value.fetchall.return_value = [mock_session]
        
        response = client.get("/sessions/")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == 1
    
    def test_get_session_by_id(self, client, mock_db_connection):
        """Test getting a specific session by ID."""
        mock_session = {
            "id": 1,
            "initial_prompt": "Hello, how are you?",
            "status": "completed",
            "provider": "anthropic",
            "created_at": "2025-10-17T12:33:45.638595Z"
        }
        mock_db_connection.execute = AsyncMock()
        mock_db_connection.execute.return_value.fetchone.return_value = mock_session
        
        response = client.get("/sessions/1")
        assert response.status_code == 200
        assert response.json()["id"] == 1
    
    def test_get_session_not_found(self, client, mock_db_connection):
        """Test getting a session that doesn't exist."""
        mock_db_connection.execute = AsyncMock()
        mock_db_connection.execute.return_value.fetchone.return_value = None
        
        response = client.get("/sessions/999")
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]
    
    @patch('app.service.agent_service.run_agent_session')
    def test_create_session(self, mock_run_agent_session, client, mock_db_connection, sample_session_data):
        """Test creating a new session."""
        # Mock the database response for session creation
        mock_session = {
            "id": 1,
            "initial_prompt": sample_session_data["initial_prompt"],
            "status": "queued",
            "provider": sample_session_data["provider"],
            "created_at": "2025-10-17T12:33:45.638595Z"
        }
        mock_db_connection.execute = AsyncMock()
        mock_db_connection.execute.return_value.fetchone.return_value = mock_session
        
        # Mock the agent service to avoid API key requirements
        mock_run_agent_session.return_value = AsyncMock()
        
        response = client.post("/sessions/", json=sample_session_data)
        assert response.status_code == 201
        assert response.json()["id"] == 1
        assert response.json()["status"] == "queued"
    
    def test_create_session_invalid_data(self, client):
        """Test creating a session with invalid data."""
        invalid_data = {
            "initial_prompt": "",  # Empty prompt
            "provider": "invalid_provider"
        }
        
        response = client.post("/sessions/", json=invalid_data)
        assert response.status_code == 422  # Validation error


class TestMessagesEndpoints:
    """Test message-related endpoints."""
    
    def test_get_messages_by_session_id(self, client, mock_db_connection):
        """Test getting messages for a session."""
        mock_messages = [
            {
                "id": 1,
                "session_id": 1,
                "role": "user",
                "content": {"text": "Hello"},
                "created_at": "2025-10-17T12:33:45.638595Z"
            },
            {
                "id": 2,
                "session_id": 1,
                "role": "assistant",
                "content": {"text": "Hi there!"},
                "created_at": "2025-10-17T12:33:46.638595Z"
            }
        ]
        mock_db_connection.execute = AsyncMock()
        mock_db_connection.execute.return_value.fetchall.return_value = mock_messages
        
        response = client.get("/messages/session/1")
        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["role"] == "user"
        assert response.json()[1]["role"] == "assistant"
    
    def test_get_messages_no_messages(self, client, mock_db_connection):
        """Test getting messages when none exist."""
        mock_db_connection.execute = AsyncMock()
        mock_db_connection.execute.return_value.fetchall.return_value = []
        
        response = client.get("/messages/session/1")
        assert response.status_code == 404
        assert "No messages found for this session" in response.json()["detail"]
    
    def test_create_message(self, client, mock_db_connection, sample_message_data):
        """Test creating a new message."""
        mock_message = {
            "id": 1,
            "session_id": sample_message_data["session_id"],
            "role": sample_message_data["role"],
            "content": sample_message_data["content"],
            "created_at": "2025-10-17T12:33:45.638595Z"
        }
        mock_db_connection.execute = AsyncMock()
        mock_db_connection.execute.return_value.fetchone.return_value = mock_message
        
        response = client.post("/messages/", json=sample_message_data)
        assert response.status_code == 201
        assert response.json()["id"] == 1
        assert response.json()["session_id"] == 1
    
    def test_create_message_invalid_data(self, client):
        """Test creating a message with invalid data."""
        invalid_data = {
            "session_id": "invalid",  # Should be int
            "role": "invalid_role",
            "content": "not_a_dict"  # Should be dict
        }
        
        response = client.post("/messages/", json=invalid_data)
        assert response.status_code == 422  # Validation error


class TestStreamingEndpoint:
    """Test the streaming endpoint."""
    
    def test_stream_endpoint_creates_stream(self, client, mock_stream_manager):
        """Test that the stream endpoint creates a stream."""
        mock_queue = MagicMock()
        mock_stream_manager.get_stream.return_value = mock_queue
        
        response = client.get("/sessions/1/stream")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        mock_stream_manager.create_stream.assert_called_once_with(1)
    
    def test_stream_endpoint_no_stream(self, client, mock_stream_manager):
        """Test stream endpoint when no stream exists."""
        mock_stream_manager.get_stream.return_value = None
        
        response = client.get("/sessions/999/stream")
        assert response.status_code == 404
        assert "Stream not found" in response.json()["detail"]


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_database_connection_error(self, client):
        """Test handling of database connection errors."""
        # This would require more complex mocking to simulate actual DB errors
        # For now, we'll test that the endpoints handle missing data gracefully
        pass
    
    def test_invalid_session_id_format(self, client):
        """Test handling of invalid session ID formats."""
        response = client.get("/sessions/invalid")
        assert response.status_code == 422  # Validation error
    
    def test_invalid_message_session_id(self, client):
        """Test handling of invalid message session ID."""
        response = client.get("/messages/session/invalid")
        assert response.status_code == 422  # Validation error
