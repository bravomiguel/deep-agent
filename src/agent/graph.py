from langgraph.prebuilt.chat_agent_executor import AgentState 
from typing_extensions import TypedDict  
from typing import NotRequired, Annotated, Sequence  
from langchain_core.messages import BaseMessage  
from langgraph.graph.message import add_messages
from deepagents.state import Todo  
from agent.create_deep_agent import create_custom_deep_agent
  
class MinimalAgentState(AgentState):  
    todos: NotRequired[list[Todo]]  

class InputState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

graph = create_custom_deep_agent(
    tools=[], 
    instructions="You are an assistant without file system access.",  
    built_in_tools=['write_todos'],  # Only include planning, no file tools  
    state_schema=MinimalAgentState,
)