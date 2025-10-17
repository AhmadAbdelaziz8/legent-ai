import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncConnection
from fastapi.testclient import TestClient
from main import app
from app.db.database import get_db_connection
from app.service.stream_manager import stream_manager


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_connection():
    """Mock database connection."""
    mock_conn = AsyncMock(spec=AsyncConnection)
    return mock_conn


@pytest.fixture
def client(mock_db_connection):
    """Create test client with mocked database connection."""
    def override_get_db():
        return mock_db_connection

    app.dependency_overrides[get_db_connection] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_stream_manager():
    """Mock stream manager."""
    with patch('app.service.stream_manager.stream_manager') as mock:
        mock.create_stream = MagicMock()
        mock.send_message = AsyncMock()
        mock.get_stream = MagicMock()
        mock.close_stream = MagicMock()
        yield mock


@pytest.fixture
def mock_agent_service():
    """Mock agent service to avoid API key requirements."""
    with patch('app.service.agent_service.run_agent_session') as mock:
        async def mock_run_agent_session(*args, **kwargs):
            # Simulate successful agent session
            session_id = args[0]
            # Simulate sending some messages
            await stream_manager.send_message(session_id, '{"type": "status", "content": "running"}')
            await stream_manager.send_message(session_id, '{"type": "assistant", "content": {"text": "Hello! I am ready to help."}}')
            await stream_manager.send_message(session_id, '{"type": "status", "content": "completed"}')

        mock.side_effect = mock_run_agent_session
        yield mock


@pytest.fixture
def sample_session_data():
    """Sample session data for testing."""
    return {
        "initial_prompt": "Hello, how are you?",
        "provider": "anthropic"
    }


@pytest.fixture
def sample_message_data():
    """Sample message data for testing."""
    return {
        "session_id": 1,
        "role": "user",
        "content": {"text": "Hello, this is a test message"}
    }
