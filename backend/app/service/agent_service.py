from sqlalchemy.ext.asyncio import AsyncConnection
from app.db.models import messages
from app.db.crud import create_message
from app.service.stream_manager import stream_manager
from app.api.schemas import MessageCreate
from fastapi import HTTPException, status
import json
from functools import partial
import app.db.crud as crud


from app.core.config import settings, PROVIDER_TO_DEFAULT_MODEL, MODEL_TO_CONFIG
from app.db.database import get_db_connection

from app.service.computer_use.loop import sampling_loop, APIProvider
from app.service.computer_use.tools import ToolVersion


async def _save_and_stream_message(conn: AsyncConnection, session_id: int, role: str, content: dict) -> None:
    #    save to database
    message_data = MessageCreate(
        session_id=session_id, role=role, content=content)
    new_message = await create_message(conn=conn, message_data=message_data)
    if not new_message:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to create the message")
    # stream to client
    stream_content = {'type': role, 'content': content}
    await stream_manager.send_message(session_id=session_id, message=json.dumps(stream_content))


async def agent_output_callback(conn: AsyncConnection, session_id: int, output: dict) -> None:
    await _save_and_stream_message(conn=conn, session_id=session_id, role='assistant', content=output)


async def tool_output_callback(conn: AsyncConnection, session_id: int, output: dict) -> None:
    await _save_and_stream_message(conn=conn, session_id=session_id, role='tool', content=output)


def validate_aws_credentials():
    try:
        import boto3
        session = boto3.Session()
        credentials = session.get_credentials()
        if not credentials:
            return "You must have AWS credentials set up to use the Bedrock API."

        # Test if we can access Bedrock
        bedrock = boto3.client('bedrock', region_name=settings.AWS_REGION)
        bedrock.list_foundation_models()
        return None
    except ImportError:
        return "boto3 is required for AWS Bedrock support. Install with: pip install boto3"
    except Exception as e:
        return f"AWS credentials validation failed: {str(e)}"


async def run_agent_session(
    session_id: int,
    initial_prompt: str,
    provider: str = "anthropic",
    model: str = None,
    system_prompt_suffix: str = "",
    max_tokens: int = None,
    thinking_budget: int = None,
    only_n_most_recent_images: int = 3
):
    async for conn in get_db_connection():
        stream_manager.create_stream(session_id=session_id)

        try:
            # Validate credentials based on provider
            if provider == "bedrock":
                aws_error = validate_aws_credentials()
                if aws_error:
                    await crud.update_session_status(conn=conn, session_id=session_id, status='error')
                    await stream_manager.send_message(session_id=session_id, message=json.dumps({'type': 'error', 'content': aws_error}))
                    return

            await crud.update_session_status(conn=conn, session_id=session_id, status='running')
            await stream_manager.send_message(session_id=session_id, message=json.dumps({'type': 'status', 'content': 'running'}))

            provider_enum = APIProvider(provider)

            if not model:
                model = PROVIDER_TO_DEFAULT_MODEL[provider_enum]

            model_config = MODEL_TO_CONFIG.get(
                model, MODEL_TO_CONFIG["claude-3-haiku-20240307"])

            if not max_tokens:
                max_tokens = model_config["max_tokens"]

            if not thinking_budget and model_config["has_thinking"]:
                thinking_budget = max_tokens // 2

            output_cb = partial(agent_output_callback,
                                conn=conn, session_id=session_id)
            tool_cb = partial(tool_output_callback,
                              conn=conn, session_id=session_id)

            # Set API key based on provider
            api_key = ""
            if provider_enum == APIProvider.ANTHROPIC:
                api_key = settings.ANTHROPIC_API_KEY
            elif provider_enum == APIProvider.BEDROCK:
                # Bedrock uses AWS credentials, no API key needed
                api_key = ""
            elif provider_enum == APIProvider.VERTEX:
                # Vertex uses Google Cloud credentials, no API key needed
                api_key = ""

            await sampling_loop(
                model=model,
                provider=provider_enum,
                system_prompt_suffix=system_prompt_suffix,
                messages=[{"role": "user", "content": initial_prompt}],
                output_callback=output_cb,
                tool_output_callback=tool_cb,
                api_response_callback=lambda r, re, e: None,
                api_key=api_key,
                tool_version=model_config["tool_version"],
                max_tokens=max_tokens,
                thinking_budget=thinking_budget,
                only_n_most_recent_images=only_n_most_recent_images,
            )

        except Exception as e:
            await crud.update_session_status(conn=conn, session_id=session_id, status='error')
            raise e
