# AI Agent System

## Architecture
Powered by Groq's fast inference API utilizing the `llama-3.1-8b-instant` model. The logic resides in `app/services/ai_service.py`.

## Prompting
System instructions (`app/prompts/system_prompts.py`) explicitly instruct the model not to invent data, but to rely entirely on provided tools.

## Tool Calling Workflow
1. User types query in `chat.py`.
2. `ai_service.py` appends user query to chat history and sends to Groq along with the tool schema (`agent_tools.py`).
3. Groq replies with a `tool_calls` request (e.g., `tool_get_study_progress`).
4. The service executes the Python function locally.
5. The JSON response is sent back to Groq.
6. Groq formulates the final natural language answer.
