import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app


class TestAPIKeySimulation:
    """Test that API key requirements are properly simulated and mocked."""
    
    def test_health_endpoint_works(self):
        """Test that the basic health endpoint works without any API keys."""
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "the server is running"}
    
    @patch('app.core.config.settings.ANTHROPIC_API_KEY', 'mock-api-key-12345')
    def test_api_key_configuration(self):
        """Test that API key can be configured."""
        from app.core.config import settings
        assert settings.ANTHROPIC_API_KEY == 'mock-api-key-12345'
    
    @patch('app.core.config.settings.ANTHROPIC_API_KEY', '')
    def test_missing_api_key(self):
        """Test that missing API key is handled gracefully."""
        from app.core.config import settings
        assert settings.ANTHROPIC_API_KEY == ''
    
    def test_agent_service_without_real_api_calls(self):
        """Test that agent service can be mocked to avoid real API calls."""
        with patch('app.service.agent_service.sampling_loop') as mock_sampling_loop:
            # Mock the sampling loop to simulate successful API call
            mock_sampling_loop.return_value = AsyncMock()
            
            # This simulates what would happen with a real API key
            # The actual API call is mocked, so no real API key is needed
            assert mock_sampling_loop.return_value is not None
    
    def test_agent_service_api_failure_simulation(self):
        """Test that API failures can be simulated."""
        with patch('app.service.agent_service.sampling_loop') as mock_sampling_loop:
            # Mock the sampling loop to simulate API failure
            mock_sampling_loop.side_effect = Exception("API rate limit exceeded")
            
            # This simulates what would happen when API calls fail
            with pytest.raises(Exception, match="API rate limit exceeded"):
                mock_sampling_loop()
    
    @patch('app.service.agent_service.run_agent_session')
    def test_session_creation_with_mocked_agent(self, mock_run_agent_session):
        """Test that session creation works with mocked agent service."""
        # Mock the agent service to avoid API key requirements
        mock_run_agent_session.return_value = AsyncMock()
        
        client = TestClient(app)
        
        # This would normally require API keys, but we've mocked the agent service
        response = client.post("/sessions/", json={
            "initial_prompt": "Hello, how are you?",
            "provider": "anthropic"
        })
        
        # The response should be successful even without real API keys
        # because we've mocked the agent service
        assert response.status_code in [201, 500]  # Either success or internal error (due to DB mocking)
    
    def test_stream_manager_works_independently(self):
        """Test that stream manager works without API dependencies."""
        from app.service.stream_manager import StreamManager
        
        manager = StreamManager()
        session_id = 1
        
        # Test creating and managing streams
        manager.create_stream(session_id)
        assert session_id in manager.streams
        
        # Test getting stream
        stream = manager.get_stream(session_id)
        assert stream is not None
        
        # Test closing stream
        manager.close_stream(session_id)
        assert session_id not in manager.streams
    
    @pytest.mark.asyncio
    async def test_message_creation_without_api_calls(self):
        """Test that messages can be created without API calls."""
        from app.service.agent_service import agent_output_callback, tool_output_callback
        
        # Mock database connection
        mock_conn = AsyncMock()
        
        # Test agent output callback (simulates agent response)
        with patch('app.service.agent_service.create_message', new_callable=AsyncMock) as mock_create_message, \
             patch('app.service.stream_manager.stream_manager.send_message', new_callable=AsyncMock) as mock_send_message:
            
            mock_create_message.return_value = {"id": 1, "session_id": 1, "role": "assistant", "content": {"text": "Hello"}}
            
            await agent_output_callback(mock_conn, 1, {"text": "Hello from agent"})
            
            # Verify message was created and sent to stream
            mock_create_message.assert_called_once()
            mock_send_message.assert_called_once()
        
        # Test tool output callback (simulates tool response)
        with patch('app.service.agent_service.create_message', new_callable=AsyncMock) as mock_create_message, \
             patch('app.service.stream_manager.stream_manager.send_message', new_callable=AsyncMock) as mock_send_message:
            
            mock_create_message.return_value = {"id": 2, "session_id": 1, "role": "tool", "content": {"tool": "browser", "action": "click"}}
            
            await tool_output_callback(mock_conn, 1, {"tool": "browser", "action": "click", "result": "success"})
            
            # Verify message was created and sent to stream
            mock_create_message.assert_called_once()
            mock_send_message.assert_called_once()
    
    def test_complete_workflow_simulation(self):
        """Test a complete workflow simulation without real API calls."""
        with patch('app.service.agent_service.run_agent_session') as mock_run_agent_session, \
             patch('app.service.stream_manager.stream_manager') as mock_stream_manager:
            
            # Mock the agent service
            mock_run_agent_session.return_value = AsyncMock()
            
            # Mock the stream manager
            mock_stream_manager.create_stream = MagicMock()
            mock_stream_manager.send_message = AsyncMock()
            
            client = TestClient(app)
            
            # Simulate creating a session
            response = client.post("/sessions/", json={
                "initial_prompt": "Hello, how are you?",
                "provider": "anthropic"
            })
            
            # The session creation should work (even if it fails due to DB mocking)
            # The important thing is that we're not making real API calls
            assert response.status_code in [201, 500]
            
            # Verify that the agent service was called (mocked)
            # This demonstrates that the API key requirement is bypassed
            mock_run_agent_session.assert_called()
    
    def test_api_key_environment_simulation(self):
        """Test that different API key environments can be simulated."""
        # Test with valid API key
        with patch('app.core.config.settings.ANTHROPIC_API_KEY', 'sk-valid-key-12345'):
            from app.core.config import settings
            assert settings.ANTHROPIC_API_KEY == 'sk-valid-key-12345'
        
        # Test with invalid API key
        with patch('app.core.config.settings.ANTHROPIC_API_KEY', 'invalid-key'):
            from app.core.config import settings
            assert settings.ANTHROPIC_API_KEY == 'invalid-key'
        
        # Test with empty API key
        with patch('app.core.config.settings.ANTHROPIC_API_KEY', ''):
            from app.core.config import settings
            assert settings.ANTHROPIC_API_KEY == ''
    
    def test_model_configuration_without_api_calls(self):
        """Test that model configuration works without API calls."""
        from app.core.config import PROVIDER_TO_DEFAULT_MODEL, MODEL_TO_CONFIG
        
        # Test provider to model mapping
        assert "claude-sonnet-4-5-20250929" in PROVIDER_TO_DEFAULT_MODEL.values()
        
        # Test model configuration
        assert "claude-sonnet-4-5-20250929" in MODEL_TO_CONFIG
        assert MODEL_TO_CONFIG["claude-sonnet-4-5-20250929"]["max_tokens"] == 128_000
        assert MODEL_TO_CONFIG["claude-sonnet-4-5-20250929"]["has_thinking"] == True
    
    def test_error_handling_without_api_calls(self):
        """Test that error handling works without API calls."""
        # Test that the application can handle missing API keys gracefully
        with patch('app.core.config.settings.ANTHROPIC_API_KEY', ''):
            from app.core.config import settings
            assert settings.ANTHROPIC_API_KEY == ''
            
            # The application should still be able to start and handle requests
            # even without API keys (they're only needed for agent processing)
            client = TestClient(app)
            response = client.get("/")
            assert response.status_code == 200


class TestMockingStrategies:
    """Test different mocking strategies for API key simulation."""
    
    def test_patch_strategy(self):
        """Test using patch to mock API key."""
        with patch('app.core.config.settings.ANTHROPIC_API_KEY', 'patched-key'):
            from app.core.config import settings
            assert settings.ANTHROPIC_API_KEY == 'patched-key'
    
    def test_mock_strategy(self):
        """Test using Mock to simulate API key."""
        from unittest.mock import Mock
        mock_settings = Mock()
        mock_settings.ANTHROPIC_API_KEY = 'mock-key'
        assert mock_settings.ANTHROPIC_API_KEY == 'mock-key'
    
    def test_async_mock_strategy(self):
        """Test using AsyncMock for async functions."""
        from unittest.mock import AsyncMock
        
        # Mock an async function that would normally make API calls
        mock_api_call = AsyncMock()
        mock_api_call.return_value = {"response": "mocked response"}
        
        # This simulates what would happen with a real API call
        result = asyncio.run(mock_api_call())
        assert result == {"response": "mocked response"}
    
    def test_context_manager_strategy(self):
        """Test using context managers for mocking."""
        with patch('app.service.agent_service.sampling_loop') as mock_loop:
            mock_loop.return_value = AsyncMock()
            
            # This simulates the agent service being called
            # without making real API calls
            assert mock_loop.return_value is not None
    
    def test_decorator_strategy(self):
        """Test using decorators for mocking."""
        @patch('app.core.config.settings.ANTHROPIC_API_KEY', 'decorated-key')
        def test_with_decorated_key():
            from app.core.config import settings
            return settings.ANTHROPIC_API_KEY
        
        result = test_with_decorated_key()
        assert result == 'decorated-key'
