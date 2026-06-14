from app.config import Config
import os
import logging
import json
from google import genai
from google.genai import types

from app.tools.agent_tools import GROQ_TOOLS, execute_tool
from app.prompts.system_prompts import get_system_prompt


def get_gemini_tools():
    gemini_tools = []
    for tool in GROQ_TOOLS:
        func = tool["function"]
        gemini_tools.append(
            types.FunctionDeclaration(
                name=func["name"],
                description=func["description"],
                parameters_json_schema=func.get("parameters", {"type": "object", "properties": {}})
            )
        )
    return [types.Tool(function_declarations=gemini_tools)]


def send_message_to_groq(messages):
    """
    Sends the message history to Gemini (keeping function name as send_message_to_groq 
    for compatibility), executes any requested tools, and returns the final response 
    string and updated message history.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    client = genai.Client(api_key=api_key)

    # Ensure system prompt is first
    if not messages or messages[0].get("role") != "system":
        import streamlit as st
        user_context = st.session_state.get("current_user")
        messages.insert(0, {"role": "system", "content": get_system_prompt(user_context)})

    system_instruction = messages[0].get("content")

    # Log the user's latest message
    user_msg = next((m for m in reversed(messages) if m.get("role") == "user"), None)
    if user_msg:
        logging.info(f"\n[CHAT] Processing new user input...")
        logging.info(f"[USER MESSAGE] {user_msg.get('content')}")
        
    model_name = "gemini-2.5-flash"
    
    # Construct the initial contents history from messages
    contents_history = []
    for msg in messages:
        role = msg.get("role")
        if role == "system":
            continue

        parts = []
        if msg.get("content"):
            parts.append(types.Part.from_text(text=msg["content"]))
            
        gemini_role = "model" if role == "assistant" else "user"
        contents_history.append(types.Content(role=gemini_role, parts=parts))

    while True:
        logging.info(f"[MODEL] Sending request to {model_name}...")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents_history,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=get_gemini_tools(),
                    temperature=0.0
                )
            )
        except Exception as e:
            if any(code in str(e) for code in ["429", "503"]) or "RESOURCE_EXHAUSTED" in str(e):
                if model_name == "gemini-2.5-flash":
                    logging.info("[GEMINI] 2.5-flash quota exceeded or rate-limited. Falling back to gemini-flash-latest...")
                    model_name = "gemini-flash-latest"
                    # Rebuild contents_history to ensure we don't have any mixed-model content
                    contents_history = []
                    for msg in messages:
                        role = msg.get("role")
                        if role == "system":
                            continue
                        parts = []
                        if msg.get("content"):
                            parts.append(types.Part.from_text(text=msg["content"]))
                        gemini_role = "model" if role == "assistant" else "user"
                        contents_history.append(types.Content(role=gemini_role, parts=parts))
                    continue
                else:
                    raise e
            else:
                raise e

        if response.function_calls:
            logging.info(f"[MODEL] Model requested {len(response.function_calls)} tool call(s).")
            
            # 1. Append the model's exact content response (retains thought_signature)
            contents_history.append(response.candidates[0].content)
            
            # 2. Execute function calls and build response parts
            parts = []
            for fc in response.function_calls:
                function_response = execute_tool(fc.name, fc.args)
                
                # Wrap response as dictionary
                if isinstance(function_response, str):
                    try:
                        resp_dict = json.loads(function_response)
                    except Exception:
                        resp_dict = {"result": function_response}
                elif isinstance(function_response, dict):
                    resp_dict = function_response
                else:
                    resp_dict = {"result": function_response}
                
                parts.append(
                    types.Part.from_function_response(
                        name=fc.name,
                        response=resp_dict
                    )
                )
            
            # 3. Append function responses to contents history
            contents_history.append(types.Content(role="user", parts=parts))
            logging.info("[MODEL] Sending tool results back to model for next turn...")
            continue
        
        else:
            final_text = ""
            try:
                if response.text:
                    final_text = response.text
            except Exception:
                pass
                
            logging.info(f"[AI RESPONSE] {final_text}")
            messages.append({"role": "assistant", "content": final_text})
            return final_text, messages
