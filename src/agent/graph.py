from langgraph.prebuilt.chat_agent_executor import AgentState 
from typing_extensions import TypedDict  
from typing import NotRequired, Annotated, Sequence  
from langchain_core.messages import BaseMessage  
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from deepagents.state import Todo  
from agent.create_deep_agent import create_custom_deep_agent
  
class MinimalAgentState(AgentState):  
    todos: NotRequired[list[Todo]]  

# # Use the Responses API path (recommended for GPT-5 controls)
# model = ChatOpenAI(
#     model="gpt-5",                        # or "gpt-5-mini" / "gpt-5-nano"
#     use_responses_api=True,               # ensures Responses API path
#     output_version="responses/v1",        # maps Responses API output cleanly
#     reasoning={"effort": "minimal"},      # fastest; use "low" for a touch more depth
#     verbosity="low",                      # shorter answers by default
#     temperature=0                         # optional: steadier outputs
# )

model = ChatOpenAI(model="gpt-5", reasoning_effort="low")

graph = create_custom_deep_agent(
    tools=[], 
    instructions="You are an assistant without file system access.",  
    built_in_tools=['write_todos'],  # Only include planning, no file tools  
    state_schema=MinimalAgentState,
    model=model,
)