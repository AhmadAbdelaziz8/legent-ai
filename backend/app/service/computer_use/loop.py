"""
Agentic sampling loop that calls the Claude API and local implementation of anthropic-defined computer use tools.
"""

import platform
from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from typing import Any, cast

import httpx
from anthropic import (
    Anthropic,
    AnthropicBedrock,
    AnthropicVertex,
    APIError,
    APIResponseValidationError,
    APIStatusError,
)
from anthropic.types.beta import (
    BetaCacheControlEphemeralParam,
    BetaContentBlockParam,
    BetaImageBlockParam,
    BetaMessage,
    BetaMessageParam,
    BetaTextBlock,
    BetaTextBlockParam,
    BetaToolResultBlockParam,
    BetaToolUseBlockParam,
)

from .tools import (
    TOOL_GROUPS_BY_VERSION,
    ToolCollection,
    ToolResult,
    ToolVersion,
)

PROMPT_CACHING_BETA_FLAG = "prompt-caching-2024-07-31"


class APIProvider(StrEnum):
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    VERTEX = "vertex"


# This system prompt is optimized for the Docker environment in this repository and
# specific tool combinations enabled.
# We encourage modifying this system prompt to ensure the model has context for the
# environment it is running in, and to provide any additional information that may be
# helpful for the task at hand.
SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are utilising an Ubuntu virtual machine using {platform.machine()} architecture with internet access.
* You can feel free to install Ubuntu applications with your bash tool. Use curl instead of wget.
* To open firefox, please just click on the firefox icon.  Note, firefox-esr is what is installed on your system.
* Using bash tool you can start GUI applications, but you need to set export DISPLAY=:1 and use a subshell. For example "(DISPLAY=:1 xterm &)". GUI apps run with bash tool will appear within your desktop environment, but they may take some time to appear. Take a screenshot to confirm it did.
* When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file and use str_replace_based_edit_tool or `grep -n -B <lines before> -A <lines after> <query> <filename>` to confirm output.
* When viewing a page it can be helpful to zoom out so that you can see everything on the page.  Either that, or make sure you scroll down to see everything before deciding something isn't available.
* When using your computer function calls, they take a while to run and send back to you.  Where possible/feasible, try to chain multiple of these calls all into one function calls request.
* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
</SYSTEM_CAPABILITY>

<VNC_AND_SCREENSHOT_CAPABILITIES>
* You have access to VNC (Virtual Network Computing) for remote desktop control and screenshot capabilities.
* You can take screenshots of the current desktop state using the computer tool's screenshot function.
* Screenshots are automatically taken before and after each computer action to provide visual feedback.
* Use screenshots to understand the current state of the desktop and plan your next actions.
* The VNC connection allows you to see and interact with the desktop environment in real-time.
* When taking screenshots, analyze them carefully to understand what's currently displayed on screen.
* Use the visual information from screenshots to make informed decisions about your next actions.
</VNC_AND_SCREENSHOT_CAPABILITIES>

<IMPORTANT>
* When using Firefox, if a startup wizard appears, IGNORE IT.  Do not even click "skip this step".  Instead, click on the address bar where it says "Search or enter address", and enter the appropriate search term or URL there.
* If the item you are looking at is a pdf, if after taking a single screenshot of the pdf it seems that you want to read the entire document instead of trying to continue to read the pdf from your screenshots + navigation, determine the URL, use curl to download the pdf, install and use pdftotext to convert it to a text file, and then read that text file directly with your str_replace_based_edit_tool.
* Always take a screenshot first to see the current state of the desktop before performing any actions.
* After each action, take another screenshot to verify the results and plan your next steps.
* When working with VNC, be patient as desktop interactions may take time to appear on screen.
* Use the screenshot function frequently to understand the current state and guide your actions.
</IMPORTANT>"""


async def sampling_loop(
    *,
    model: str,
    provider: APIProvider,
    system_prompt_suffix: str,
    messages: list[BetaMessageParam],
    output_callback: Callable[[BetaContentBlockParam], None],
    tool_output_callback: Callable[[ToolResult, str], None],
    api_response_callback: Callable[
        [httpx.Request, httpx.Response | object | None, Exception | None], None
    ],
    api_key: str,
    only_n_most_recent_images: int | None = None,
    max_tokens: int = 4096,
    tool_version: ToolVersion,
    thinking_budget: int | None = None,
    token_efficient_tools_beta: bool = False,
):
    """
    Agentic sampling loop for the assistant/tool interaction of computer use.
    """
    tool_group = TOOL_GROUPS_BY_VERSION[tool_version]
    tool_collection = ToolCollection(
        *(ToolCls() for ToolCls in tool_group.tools))
    system = BetaTextBlockParam(
        type="text",
        text=f"{SYSTEM_PROMPT}{' ' + system_prompt_suffix if system_prompt_suffix else ''}",
    )

    while True:
        enable_prompt_caching = False
        betas = [tool_group.beta_flag] if tool_group.beta_flag else []
        if token_efficient_tools_beta:
            betas.append("token-efficient-tools-2025-02-19")
        image_truncation_threshold = only_n_most_recent_images or 0
        if provider == APIProvider.ANTHROPIC:
            client = Anthropic(api_key=api_key, max_retries=4)
            enable_prompt_caching = True
        elif provider == APIProvider.VERTEX:
            client = AnthropicVertex()
        elif provider == APIProvider.BEDROCK:
            print("🔧 [BEDROCK] Initializing AnthropicBedrock client...")
            try:
                client = AnthropicBedrock()
                print("✅ [BEDROCK] AnthropicBedrock client created successfully")
            except Exception as e:
                print(
                    f"❌ [BEDROCK] Failed to create AnthropicBedrock client: {e}")
                raise

        if enable_prompt_caching:
            betas.append(PROMPT_CACHING_BETA_FLAG)
            _inject_prompt_caching(messages)
            # Because cached reads are 10% of the price, we don't think it's
            # ever sensible to break the cache by truncating images
            only_n_most_recent_images = 0
            # Use type ignore to bypass TypedDict check until SDK types are updated
            system["cache_control"] = {"type": "ephemeral"}  # type: ignore

        if only_n_most_recent_images:
            _maybe_filter_to_n_most_recent_images(
                messages,
                only_n_most_recent_images,
                min_removal_threshold=image_truncation_threshold,
            )
        extra_body = {}
        if thinking_budget:
            # Apply the fix: thinking_budget_tokens := min(thinking_budget_tokens, max_tokens)
            # This ensures max_tokens > thinking_budget as required by the API
            actual_thinking_budget = min(thinking_budget, max_tokens - 1)
            print(
                f"🔧 [API] Adjusted thinking_budget from {thinking_budget} to {actual_thinking_budget} (max_tokens: {max_tokens})")

            # Ensure we only send the required fields for thinking
            extra_body = {
                "thinking": {"type": "enabled", "budget_tokens": actual_thinking_budget}
            }

        # Call the API with streaming enabled
        # we use raw_response to provide debug information to streamlit. Your
        # implementation may be able call the SDK directly with:
        # `response = client.messages.create(...)` instead.
        try:
            # Ensure max_tokens is greater than thinking_budget for Bedrock
            if thinking_budget and max_tokens <= thinking_budget:
                # If max_tokens is too small, increase it to be at least thinking_budget + 1000
                actual_max_tokens = thinking_budget + 1000
            else:
                actual_max_tokens = max_tokens

            # Log the thinking_budget and max_tokens values for debugging
            if thinking_budget:
                print(
                    f"🔧 [API] Thinking budget: {thinking_budget}, Max tokens: {actual_max_tokens}")
                if actual_max_tokens <= thinking_budget:
                    print(
                        f"⚠️ [API] WARNING: max_tokens ({actual_max_tokens}) <= thinking_budget ({thinking_budget})")

            print(f"🔧 [API] Calling {provider} API with model: {model}")
            print(
                f"🔧 [API] Max tokens: {actual_max_tokens}, Tool version: {tool_version}")
            print(f"🔧 [API] Messages count: {len(messages)}")

            raw_response = client.beta.messages.with_raw_response.create(
                max_tokens=actual_max_tokens,
                messages=messages,
                model=model,
                system=[system],
                tools=tool_collection.to_params(),
                betas=betas,
                extra_body=extra_body,
                stream=True,  # Enable streaming for long operations
            )
            print(f"✅ [API] API call successful")
        except (APIStatusError, APIResponseValidationError) as e:
            print(f"❌ [API] API Status/Response Error: {e}")
            api_response_callback(e.request, e.response, e)
            return messages
        except APIError as e:
            print(f"❌ [API] API Error: {e}")
            api_response_callback(e.request, e.body, e)
            return messages

        api_response_callback(
            raw_response.http_response.request, raw_response.http_response, None
        )

        # Handle streaming response
        print(f"🔧 [API] Processing streaming response...")
        response = raw_response.parse()

        # Check if it's a stream or regular response
        if hasattr(response, '__iter__') and not hasattr(response, 'content'):
            # This is a streaming response
            print(f"🔧 [API] Processing stream with {type(response)}")
            response_params = []
            tool_result_content: list[BetaToolResultBlockParam] = []

            # Process each chunk in the stream
            current_text = ""
            for chunk in response:
                print(f"🔧 [API] Processing chunk: {type(chunk)}")

                # Handle different types of streaming events
                if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                    # Text delta - accumulate text
                    current_text += chunk.delta.text
                    print(f"🔧 [API] Text delta: {chunk.delta.text}")
                elif hasattr(chunk, 'type') and chunk.type == "content_block_delta":
                    # Content block delta
                    if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                        current_text += chunk.delta.text
                        print(f"🔧 [API] Content delta: {chunk.delta.text}")
                elif hasattr(chunk, 'type') and chunk.type == "content_block_stop":
                    # End of content block - finalize the text
                    if current_text:
                        text_block = {"type": "text", "text": current_text}
                        response_params.append(text_block)
                        print(
                            f"🔧 [API] Finalized text: {current_text[:100]}...")
                        current_text = ""
                elif hasattr(chunk, 'type') and chunk.type == "message_stop":
                    # End of message - finalize any remaining text
                    if current_text:
                        text_block = {"type": "text", "text": current_text}
                        response_params.append(text_block)
                        print(
                            f"🔧 [API] Finalized final text: {current_text[:100]}...")
                        current_text = ""

            print(
                f"✅ [API] Stream processed successfully, content blocks: {len(response_params)}")

            # Add assistant message
            assistant_message = {
                "role": "assistant",
                "content": response_params,
            }
            messages.append(assistant_message)

            # Call output_callback with the content to save to database
            # Wrap content blocks in a dictionary for database storage
            content_dict = {"content": response_params}
            print(
                f"🔧 [API] Calling output_callback with content_dict: {content_dict}")
            try:
                # Call output_callback with the content as a keyword argument
                # Since output_callback is partial(agent_output_callback, conn=conn, session_id=session_id)
                # we need to pass the content as the 'output' parameter
                # Note: agent_output_callback is async, so we need to await it
                await output_callback(content_dict)
                print(f"✅ [API] output_callback completed successfully")
            except Exception as e:
                print(f"❌ [API] output_callback failed: {e}")
                raise e

            # Add tool results if any
            if tool_result_content:
                messages.append(
                    {"content": tool_result_content, "role": "user"})
                return messages
            else:
                return messages
        else:
            # Handle non-streaming response (fallback)
            print(f"🔧 [API] Parsing non-streaming response...")
            response_params = _response_to_params(response)
            print(
                f"✅ [API] Response parsed successfully, content blocks: {len(response_params)}")

            assistant_message = {
                "role": "assistant",
                "content": response_params,
            }
            messages.append(assistant_message)

            # Call output_callback with the content to save to database
            # Wrap content blocks in a dictionary for database storage
            content_dict = {"content": response_params}
            print(
                f"🔧 [API] Calling output_callback with content_dict: {content_dict}")
            try:
                # Call output_callback with the content as a keyword argument
                # Since output_callback is partial(agent_output_callback, conn=conn, session_id=session_id)
                # we need to pass the content as the 'output' parameter
                # Note: agent_output_callback is async, so we need to await it
                await output_callback(content_dict)
                print(f"✅ [API] output_callback completed successfully")
            except Exception as e:
                print(f"❌ [API] output_callback failed: {e}")
                raise e

            tool_result_content: list[BetaToolResultBlockParam] = []
            for content_block in response_params:
                if isinstance(content_block, dict) and content_block.get("type") == "tool_use":
                    # Type narrowing for tool use blocks
                    tool_use_block = cast(BetaToolUseBlockParam, content_block)
                    result = await tool_collection.run(
                        name=tool_use_block["name"],
                        tool_input=cast(
                            dict[str, Any], tool_use_block.get("input", {})),
                    )
                    tool_result_content.append(
                        _make_api_tool_result(result, tool_use_block["id"])
                    )
                    tool_output_callback(result, tool_use_block["id"])

            if not tool_result_content:
                return messages

            messages.append({"content": tool_result_content, "role": "user"})


def _maybe_filter_to_n_most_recent_images(
    messages: list[BetaMessageParam],
    images_to_keep: int,
    min_removal_threshold: int,
):
    """
    With the assumption that images are screenshots that are of diminishing value as
    the conversation progresses, remove all but the final `images_to_keep` tool_result
    images in place, with a chunk of min_removal_threshold to reduce the amount we
    break the implicit prompt cache.
    """
    if images_to_keep is None:
        return messages

    tool_result_blocks = cast(
        list[BetaToolResultBlockParam],
        [
            item
            for message in messages
            for item in (
                message["content"] if isinstance(
                    message["content"], list) else []
            )
            if isinstance(item, dict) and item.get("type") == "tool_result"
        ],
    )

    total_images = sum(
        1
        for tool_result in tool_result_blocks
        for content in tool_result.get("content", [])
        if isinstance(content, dict) and content.get("type") == "image"
    )

    images_to_remove = total_images - images_to_keep
    # for better cache behavior, we want to remove in chunks
    images_to_remove -= images_to_remove % min_removal_threshold

    for tool_result in tool_result_blocks:
        if isinstance(tool_result.get("content"), list):
            new_content = []
            for content in tool_result.get("content", []):
                if isinstance(content, dict) and content.get("type") == "image":
                    if images_to_remove > 0:
                        images_to_remove -= 1
                        continue
                new_content.append(content)
            tool_result["content"] = new_content


def _response_to_params(
    response: BetaMessage,
) -> list[BetaContentBlockParam]:
    res: list[BetaContentBlockParam] = []
    for block in response.content:
        if isinstance(block, BetaTextBlock):
            if block.text:
                res.append(BetaTextBlockParam(type="text", text=block.text))
            elif getattr(block, "type", None) == "thinking":
                # Handle thinking blocks - include signature field
                thinking_block = {
                    "type": "thinking",
                    "thinking": getattr(block, "thinking", None),
                }
                if hasattr(block, "signature"):
                    thinking_block["signature"] = getattr(
                        block, "signature", None)
                res.append(cast(BetaContentBlockParam, thinking_block))
        else:
            # Handle tool use blocks normally
            res.append(cast(BetaToolUseBlockParam, block.model_dump()))
    return res


def _inject_prompt_caching(
    messages: list[BetaMessageParam],
):
    """
    Set cache breakpoints for the 3 most recent turns
    one cache breakpoint is left for tools/system prompt, to be shared across sessions
    """

    breakpoints_remaining = 3
    for message in reversed(messages):
        if message["role"] == "user" and isinstance(
            content := message["content"], list
        ):
            if breakpoints_remaining:
                breakpoints_remaining -= 1
                # Use type ignore to bypass TypedDict check until SDK types are updated
                content[-1]["cache_control"] = BetaCacheControlEphemeralParam(  # type: ignore
                    {"type": "ephemeral"}
                )
            else:
                if isinstance(content[-1], dict) and "cache_control" in content[-1]:
                    del content[-1]["cache_control"]  # type: ignore
                # we'll only every have one extra turn per loop
                break


def _make_api_tool_result(
    result: ToolResult, tool_use_id: str
) -> BetaToolResultBlockParam:
    """Convert an agent ToolResult to an API ToolResultBlockParam."""
    tool_result_content: list[BetaTextBlockParam |
                              BetaImageBlockParam] | str = []
    is_error = False
    if result.error:
        is_error = True
        tool_result_content = _maybe_prepend_system_tool_result(
            result, result.error)
    else:
        if result.output:
            tool_result_content.append(
                {
                    "type": "text",
                    "text": _maybe_prepend_system_tool_result(result, result.output),
                }
            )
        if result.base64_image:
            tool_result_content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": result.base64_image,
                    },
                }
            )
    return {
        "type": "tool_result",
        "content": tool_result_content,
        "tool_use_id": tool_use_id,
        "is_error": is_error,
    }


def _maybe_prepend_system_tool_result(result: ToolResult, result_text: str):
    if result.system:
        result_text = f"<system>{result.system}</system>\n{result_text}"
    return result_text
