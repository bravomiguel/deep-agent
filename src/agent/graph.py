from langgraph.prebuilt.chat_agent_executor import AgentState 
from typing import NotRequired
from langchain_openai import ChatOpenAI
from deepagents.state import Todo  
from agent.create_deep_agent import create_custom_deep_agent
from agent.tools import read_attachment, list_attachments
  
class AgentState(AgentState):  
    todos: NotRequired[list[Todo]]
    attached_files: NotRequired[list[str]]  # List of file paths for attachments  

# Use the Responses API path (recommended for GPT-5 controls)
# model = ChatOpenAI(
#     model="gpt-5",                        # or "gpt-5-mini" / "gpt-5-nano"
#     use_responses_api=True,               # ensures Responses API path
#     output_version="responses/v1",        # maps Responses API output cleanly
#     reasoning={"effort": "minimal"},      # fastest; use "low" for a touch more depth
#     verbosity="low",                      # shorter answers by default
#     temperature=0                         # optional: steadier outputs
# )

# OpenAI GPT-5 model (commented out)
model = ChatOpenAI(model="gpt-5", reasoning_effort="low")

# Ollama local model
# model = init_chat_model(
#     model="ollama:gpt-oss:20b",
#     reasoning_effort="low",
# )

graph = create_custom_deep_agent(
    tools=[read_attachment, list_attachments], 
    instructions="You are an assistant for general knowledge work. When files are provided, you can use list_attachments to see what's available and read_attachment to read their contents.",  
    built_in_tools=['write_todos'],  
    state_schema=AgentState,
    model=model,
)