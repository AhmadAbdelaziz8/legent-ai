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
from app.service.computer_use.tools.base import ToolResult
from app.routes.vnc import start_vnc_services


async def _save_and_stream_message(conn: AsyncConnection, session_id: int, role: str, content: dict) -> None:
    try:
        print(
            f"🔧 [STREAM] _save_and_stream_message called for session {session_id}, role: {role}")
        #    save to database
        message_data = MessageCreate(
            session_id=session_id, role=role, content=content)
        print(f"🔧 [STREAM] Creating message in database...")
        try:
            new_message = await create_message(conn=conn, message_data=message_data)
            print(f"✅ [STREAM] Message saved to database: {new_message}")
        except Exception as db_error:
            print(f"❌ [STREAM] Database error: {db_error}")
            raise db_error
        if not new_message:
            print(f"❌ [STREAM] Failed to create message in database")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to create the message")
        # stream to client
        stream_content = {'type': role, 'content': content}
        print(
            f"🔧 [STREAM] Sending message to stream: {json.dumps(stream_content)}")
        await stream_manager.send_message(session_id=session_id, message=json.dumps(stream_content))
        print(f"✅ [STREAM] Message sent to stream for session {session_id}")
    except Exception as e:
        print(f"❌ [STREAM] Error in _save_and_stream_message: {e}")
        raise e


async def _save_and_stream_message_with_image(conn: AsyncConnection, session_id: int, role: str, content: dict, base64_image: str = None) -> None:
    try:
        print(
            f"🔧 [STREAM] _save_and_stream_message_with_image called for session {session_id}, role: {role}")
        #    save to database with optional base64_image
        message_data = MessageCreate(
            session_id=session_id, role=role, content=content, base64_image=base64_image)
        print(f"🔧 [STREAM] Creating message in database with image...")
        try:
            new_message = await create_message(conn=conn, message_data=message_data)
            print(
                f"✅ [STREAM] Message with image saved to database: {new_message}")
        except Exception as db_error:
            print(f"❌ [STREAM] Database error: {db_error}")
            raise db_error
        if not new_message:
            print(f"❌ [STREAM] Failed to create message in database")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to create the message")
        # stream to client
        stream_content = {'type': role, 'content': content}
        if base64_image:
            stream_content['base64_image'] = base64_image
        print(
            f"🔧 [STREAM] Sending message to stream: {json.dumps(stream_content)}")
        await stream_manager.send_message(session_id=session_id, message=json.dumps(stream_content))
        print(f"✅ [STREAM] Message sent to stream for session {session_id}")
    except Exception as e:
        print(f"❌ [STREAM] Error in _save_and_stream_message_with_image: {e}")
        raise e


async def agent_output_callback(conn: AsyncConnection, session_id: int, output: dict) -> None:
    print(
        f"🔧 [CALLBACK] agent_output_callback called for session {session_id} with output: {output}")
    try:
        print(
            f"🔧 [CALLBACK] agent_output_callback called for session {session_id}")
        await _save_and_stream_message(conn=conn, session_id=session_id, role='assistant', content=output)
        print(
            f"✅ [CALLBACK] agent_output_callback completed for session {session_id}")
    except Exception as e:
        print(f"❌ [CALLBACK] Error in agent_output_callback: {e}")
        raise e


async def tool_output_callback(conn: AsyncConnection, session_id: int, output: ToolResult) -> None:
    # Extract base64_image if present in the tool result
    base64_image = None
    if hasattr(output, 'base64_image') and output.base64_image:
        base64_image = output.base64_image
        print(
            f"🖼️ [TOOL] Screenshot captured, length: {len(base64_image)} characters")

    # Create content dict for database storage
    content_dict = {
        'type': 'tool_result',
        'output': output.output if hasattr(output, 'output') else None,
        'error': output.error if hasattr(output, 'error') else None,
        'system': output.system if hasattr(output, 'system') else None
    }

    # Save message with screenshot if available
    await _save_and_stream_message_with_image(conn=conn, session_id=session_id, role='tool', content=content_dict, base64_image=base64_image)


def validate_aws_credentials():
    try:
        import boto3
        print("🔧 [AWS] Starting AWS credentials validation...")

        # Use the same approach as the legacy demo
        session = boto3.Session()
        print(f"🔧 [AWS] Created boto3 session")

        credentials = session.get_credentials()
        if not credentials:
            print("❌ [AWS] No AWS credentials found")
            return "You must have AWS credentials set up to use the Bedrock API."

        print(
            f"✅ [AWS] AWS credentials found: {credentials.access_key[:10]}...")
        print(
            f"🔧 [AWS] Testing Bedrock access in region: {settings.AWS_REGION}")

        # Test if we can access Bedrock
        bedrock = boto3.client('bedrock', region_name=settings.AWS_REGION)
        models = bedrock.list_foundation_models()
        print(
            f"✅ [AWS] Bedrock access successful! Found {len(models.get('modelSummaries', []))} models")
        return None
    except ImportError:
        print("❌ [AWS] boto3 not installed")
        return "boto3 is required for AWS Bedrock support. Install with: pip install boto3"
    except Exception as e:
        print(f"❌ [AWS] Credentials validation failed: {str(e)}")
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
    print(
        f"🚀 [AGENT] Starting agent session {session_id} with provider: {provider}")
    async for conn in get_db_connection():
        stream_manager.create_stream(session_id=session_id)
        print(f"📡 [AGENT] Stream created for session {session_id}")

        try:
            # Validate credentials based on provider
            if provider == "bedrock":
                print(f"🔧 [AGENT] Validating AWS credentials for Bedrock...")
                aws_error = validate_aws_credentials()
                if aws_error:
                    print(
                        f"❌ [AGENT] AWS credentials validation failed: {aws_error}")
                    await crud.update_session_status(conn=conn, session_id=session_id, status='error')
                    await stream_manager.send_message(session_id=session_id, message=json.dumps({'type': 'error', 'content': aws_error}))
                    return
                print(f"✅ [AGENT] AWS credentials validation passed")

            print(f"🔄 [AGENT] Updating session status to 'running'")
            await crud.update_session_status(conn=conn, session_id=session_id, status='running')
            await stream_manager.send_message(session_id=session_id, message=json.dumps({'type': 'status', 'content': 'running'}))

            # Save initial prompt as first user message
            print(f"💬 [AGENT] Saving initial prompt as first user message...")
            await _save_and_stream_message(conn=conn, session_id=session_id, role='user', content={'type': 'text', 'text': initial_prompt})
            print(f"✅ [AGENT] Initial prompt saved as user message")

            # Start VNC services for computer use
            print(f"🖥️ [AGENT] Starting VNC services for computer use...")
            await start_vnc_services()
            print(f"✅ [AGENT] VNC services started")

            provider_enum = APIProvider(provider)

            if not model:
                model = PROVIDER_TO_DEFAULT_MODEL[provider_enum]

            model_config = MODEL_TO_CONFIG.get(
                model, MODEL_TO_CONFIG["claude-3-haiku-20240307"])

            if not max_tokens:
                max_tokens = model_config["max_tokens"]

            if not thinking_budget and model_config["has_thinking"]:
                # Use the same approach as the legacy demo: thinking_budget = max_tokens / 2
                thinking_budget = max_tokens // 2
                print(
                    f"🔧 [AGENT] Set thinking_budget to {thinking_budget} (max_tokens: {max_tokens})")

            # Create wrapper functions instead of using partial
            async def output_cb(content_dict):
                print(f"🔧 [WRAPPER] output_cb called with: {content_dict}")
                await agent_output_callback(conn=conn, session_id=session_id, output=content_dict)

            async def tool_cb(result, tool_id):
                print(f"🔧 [WRAPPER] tool_cb called with: {result}, {tool_id}")
                await tool_output_callback(conn=conn, session_id=session_id, output=result)

            print(f"🔧 [AGENT] Created output_cb wrapper")
            print(f"🔧 [AGENT] Created tool_cb wrapper")

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
