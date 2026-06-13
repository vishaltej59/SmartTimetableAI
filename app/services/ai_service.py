from app.config import Config
import os
import logging
import json
from groq import Groq

from app.tools.agent_tools import GROQ_TOOLS, execute_tool
from app.prompts.system_prompts import get_system_prompt


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found")
    return Groq(api_key=api_key)


def send_message_to_groq(messages):
    """
    Sends the message history to Groq, executes any requested tools,
    and returns the final response string and updated message history.
    """
    client = get_groq_client()

    # Ensure system prompt is first
    if not messages or messages[0].get("role") != "system":
        import streamlit as st
        user_context = st.session_state.get("current_user")
        messages.insert(0, {"role": "system", "content": get_system_prompt(user_context)})

    # Log the user's latest message
    user_msg = next((m for m in reversed(messages) if m.get("role") == "user"), None)
    if user_msg:
        logging.info(f"\n[CHAT] Processing new user input...")
        logging.info(f"[USER MESSAGE] {user_msg.get('content')}")
    logging.info("[MODEL] Sending request to Groq API...")

    # First call to Groq
    response = client.chat.completions.create(
        model=Config.GROQ_MODEL,
        messages=messages,
        tools=GROQ_TOOLS,
        tool_choice="auto",
        max_tokens=1024,
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        logging.info(f"[MODEL] Groq requested {len(tool_calls)} tool call(s).")
        # Append the assistant's message with tool calls to history
        messages.append(
            {
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_calls
                ],
            }
        )

        # Execute each tool
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Run the actual python function
            function_response = execute_tool(function_name, function_args)

            # Append the tool result
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(function_response),
                }
            )

        # Second call to get the final natural language response
        logging.info("[MODEL] Sending tool results back to Groq for final response...")
        second_response = client.chat.completions.create(
            model=Config.GROQ_MODEL, messages=messages, max_tokens=1024
        )

        final_message = second_response.choices[0].message
        logging.info(f"[AI RESPONSE] {final_message.content}")
        messages.append({"role": "assistant", "content": final_message.content})
        return final_message.content, messages

    else:
        # No tool calls, just append the standard response
        logging.info(f"[AI RESPONSE] {response_message.content}")
        messages.append({"role": "assistant", "content": response_message.content})
        return response_message.content, messages
