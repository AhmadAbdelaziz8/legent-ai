import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.service.agent_service import run_agent_session, agent_output_callback, tool_output_callback
from app.api.schemas import MessageCreate


class TestAgentService:
    """Test the agent service functionality."""
    
    @pytest.mark.asyncio
    async def test_agent_output_callback(self, mock_db_connection):
        """Test the agent output callback function."""
        session_id = 1
        output = {"text": "Hello from agent"}
        
        with patch('app.service.agent_service.create_message', new_callable=AsyncMock) as mock_create_message, \
             patch('app.service.stream_manager.stream_manager.send_message', new_callable=AsyncMock) as mock_send_message:
            
            mock_create_message.return_value = {"id": 1, "session_id": session_id, "role": "assistant", "content": output}
            
            await agent_output_callback(mock_db_connection, session_id, output)
            
            # Verify message was created
            mock_create_message.assert_called_once()
            call_args = mock_create_message.call_args[1]
            assert call_args["conn"] == mock_db_connection
            assert call_args["message_data"].session_id == session_id
            assert call_args["message_data"].role == "assistant"
            assert call_args["message_data"].content == output
            
            # Verify message was sent to stream
            mock_send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_tool_output_callback(self, mock_db_connection):
        """Test the tool output callback function."""
        session_id = 1
        output = {"tool": "browser", "action": "click", "result": "success"}
        
        with patch('app.service.agent_service.create_message', new_callable=AsyncMock) as mock_create_message, \
             patch('app.service.stream_manager.stream_manager.send_message', new_callable=AsyncMock) as mock_send_message:
            
            mock_create_message.return_value = {"id": 1, "session_id": session_id, "role": "tool", "content": output}
            
            await tool_output_callback(mock_db_connection, session_id, output)
            
            # Verify message was created
            mock_create_message.assert_called_once()
            call_args = mock_create_message.call_args[1]
            assert call_args["conn"] == mock_db_connection
            assert call_args["message_data"].session_id == session_id
            assert call_args["message_data"].role == "tool"
            assert call_args["message_data"].content == output
            
            # Verify message was sent to stream
            mock_send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_agent_session_success(self, mock_db_connection):
        """Test running an agent session successfully."""
        session_id = 1
        initial_prompt = "Hello, how are you?"
        provider = "anthropic"
        
        with patch('app.service.agent_service.get_db_connection') as mock_get_db, \
             patch('app.service.stream_manager.stream_manager') as mock_stream_manager, \
             patch('app.service.agent_service.crud.update_session_status', new_callable=AsyncMock) as mock_update_status, \
             patch('app.service.agent_service.sampling_loop', new_callable=AsyncMock) as mock_sampling_loop:
            
            # Mock database connection
            mock_get_db.return_value.__aenter__.return_value = mock_db_connection
            mock_get_db.return_value.__aexit__.return_value = None
            
            # Mock stream manager
            mock_stream_manager.create_stream = MagicMock()
            mock_stream_manager.send_message = AsyncMock()
            
            # Mock database operations
            mock_update_status.return_value = None
            
            # Mock the sampling loop (this is where API calls would happen)
            mock_sampling_loop.return_value = None
            
            # Run the agent session
            await run_agent_session(
                session_id=session_id,
                initial_prompt=initial_prompt,
                provider=provider
            )
            
            # Verify stream was created
            mock_stream_manager.create_stream.assert_called_once_with(session_id=session_id)
            
            # Verify status was updated
            mock_update_status.assert_called_with(conn=mock_db_connection, session_id=session_id, status='running')
            
            # Verify sampling loop was called
            mock_sampling_loop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_agent_session_with_error(self, mock_db_connection):
        """Test running an agent session with an error."""
        session_id = 1
        initial_prompt = "Hello, how are you?"
        provider = "anthropic"
        
        with patch('app.service.agent_service.get_db_connection') as mock_get_db, \
             patch('app.service.stream_manager.stream_manager') as mock_stream_manager, \
             patch('app.service.agent_service.crud.update_session_status', new_callable=AsyncMock) as mock_update_status, \
             patch('app.service.agent_service.sampling_loop', new_callable=AsyncMock) as mock_sampling_loop:
            
            # Mock database connection
            mock_get_db.return_value.__aenter__.return_value = mock_db_connection
            mock_get_db.return_value.__aexit__.return_value = None
            
            # Mock stream manager
            mock_stream_manager.create_stream = MagicMock()
            mock_stream_manager.send_message = AsyncMock()
            
            # Mock database operations
            mock_update_status.return_value = None
            
            # Mock the sampling loop to raise an exception
            mock_sampling_loop.side_effect = Exception("API key not found")
            
            # Run the agent session and expect it to raise an exception
            with pytest.raises(Exception, match="API key not found"):
                await run_agent_session(
                    session_id=session_id,
                    initial_prompt=initial_prompt,
                    provider=provider
                )
            
            # Verify status was updated to error
            mock_update_status.assert_called_with(conn=mock_db_connection, session_id=session_id, status='error')
    
    @pytest.mark.asyncio
    async def test_run_agent_session_with_custom_parameters(self, mock_db_connection):
        """Test running an agent session with custom parameters."""
        session_id = 1
        initial_prompt = "Hello, how are you?"
        provider = "anthropic"
        model = "claude-3-haiku-20240307"
        system_prompt_suffix = "You are a helpful assistant."
        max_tokens = 1000
        thinking_budget = 500
        only_n_most_recent_images = 5
        
        with patch('app.service.agent_service.get_db_connection') as mock_get_db, \
             patch('app.service.stream_manager.stream_manager') as mock_stream_manager, \
             patch('app.service.agent_service.crud.update_session_status', new_callable=AsyncMock) as mock_update_status, \
             patch('app.service.agent_service.sampling_loop', new_callable=AsyncMock) as mock_sampling_loop:
            
            # Mock database connection
            mock_get_db.return_value.__aenter__.return_value = mock_db_connection
            mock_get_db.return_value.__aexit__.return_value = None
            
            # Mock stream manager
            mock_stream_manager.create_stream = MagicMock()
            mock_stream_manager.send_message = AsyncMock()
            
            # Mock database operations
            mock_update_status.return_value = None
            
            # Mock the sampling loop
            mock_sampling_loop.return_value = None
            
            # Run the agent session with custom parameters
            await run_agent_session(
                session_id=session_id,
                initial_prompt=initial_prompt,
                provider=provider,
                model=model,
                system_prompt_suffix=system_prompt_suffix,
                max_tokens=max_tokens,
                thinking_budget=thinking_budget,
                only_n_most_recent_images=only_n_most_recent_images
            )
            
            # Verify sampling loop was called with correct parameters
            mock_sampling_loop.assert_called_once()
            call_kwargs = mock_sampling_loop.call_args[1]
            assert call_kwargs["model"] == model
            assert call_kwargs["max_tokens"] == max_tokens
            assert call_kwargs["thinking_budget"] == thinking_budget
            assert call_kwargs["only_n_most_recent_images"] == only_n_most_recent_images


class TestAgentServiceMocking:
    """Test agent service with mocked API dependencies."""
    
    @pytest.mark.asyncio
    async def test_mock_api_calls(self, mock_db_connection):
        """Test that API calls are properly mocked."""
        session_id = 1
        initial_prompt = "Hello, how are you?"
        provider = "anthropic"
        
        with patch('app.service.agent_service.get_db_connection') as mock_get_db, \
             patch('app.service.stream_manager.stream_manager') as mock_stream_manager, \
             patch('app.service.agent_service.crud.update_session_status', new_callable=AsyncMock) as mock_update_status, \
             patch('app.service.agent_service.sampling_loop', new_callable=AsyncMock) as mock_sampling_loop, \
             patch('app.core.config.settings.ANTHROPIC_API_KEY', 'mock-api-key'):
            
            # Mock database connection
            mock_get_db.return_value.__aenter__.return_value = mock_db_connection
            mock_get_db.return_value.__aexit__.return_value = None
            
            # Mock stream manager
            mock_stream_manager.create_stream = MagicMock()
            mock_stream_manager.send_message = AsyncMock()
            
            # Mock database operations
            mock_update_status.return_value = None
            
            # Mock the sampling loop to simulate successful API call
            async def mock_sampling_loop(*args, **kwargs):
                # Simulate sending some messages
                await mock_stream_manager.send_message(session_id, '{"type": "status", "content": "running"}')
                await mock_stream_manager.send_message(session_id, '{"type": "assistant", "content": {"text": "Hello! I am ready to help."}}')
                await mock_stream_manager.send_message(session_id, '{"type": "status", "content": "completed"}')
            
            mock_sampling_loop.side_effect = mock_sampling_loop
            
            # Run the agent session
            await run_agent_session(
                session_id=session_id,
                initial_prompt=initial_prompt,
                provider=provider
            )
            
            # Verify that the sampling loop was called (simulating API call)
            mock_sampling_loop.assert_called_once()
            
            # Verify that messages were sent to the stream
            assert mock_stream_manager.send_message.call_count >= 3  # At least 3 messages sent
    
    @pytest.mark.asyncio
    async def test_mock_api_failure(self, mock_db_connection):
        """Test handling of API failures."""
        session_id = 1
        initial_prompt = "Hello, how are you?"
        provider = "anthropic"
        
        with patch('app.service.agent_service.get_db_connection') as mock_get_db, \
             patch('app.service.stream_manager.stream_manager') as mock_stream_manager, \
             patch('app.service.agent_service.crud.update_session_status', new_callable=AsyncMock) as mock_update_status, \
             patch('app.service.agent_service.sampling_loop', new_callable=AsyncMock) as mock_sampling_loop:
            
            # Mock database connection
            mock_get_db.return_value.__aenter__.return_value = mock_db_connection
            mock_get_db.return_value.__aexit__.return_value = None
            
            # Mock stream manager
            mock_stream_manager.create_stream = MagicMock()
            mock_stream_manager.send_message = AsyncMock()
            
            # Mock database operations
            mock_update_status.return_value = None
            
            # Mock the sampling loop to simulate API failure
            mock_sampling_loop.side_effect = Exception("API rate limit exceeded")
            
            # Run the agent session and expect it to handle the error
            with pytest.raises(Exception, match="API rate limit exceeded"):
                await run_agent_session(
                    session_id=session_id,
                    initial_prompt=initial_prompt,
                    provider=provider
                )
            
            # Verify that the session status was updated to error
            mock_update_status.assert_called_with(conn=mock_db_connection, session_id=session_id, status='error')
