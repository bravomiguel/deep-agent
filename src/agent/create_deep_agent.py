from typing import Sequence, Union, Callable, Any, TypeVar, Type, Optional  
from langchain_core.tools import BaseTool  
from langchain_core.language_models import LanguageModelLike  
from langgraph.types import Checkpointer  
from langgraph.prebuilt import create_react_agent  
  
from deepagents.tools import write_todos, write_file, read_file, ls, edit_file  
from deepagents.state import DeepAgentState  
from deepagents.sub_agent import _create_task_tool, SubAgent  
from deepagents.model import get_default_model  
from deepagents.interrupt import create_interrupt_hook, ToolInterruptConfig  
  
StateSchema = TypeVar("StateSchema", bound=DeepAgentState)  
StateSchemaType = Type[StateSchema]  
  
def create_custom_deep_agent(  
    tools: Sequence[Union[BaseTool, Callable, dict[str, Any]]],  
    instructions: str,  
    built_in_tools: Optional[list[str]] = None,  
    base_prompt: Optional[str] = None,  
    model: Optional[Union[str, LanguageModelLike]] = None,  
    subagents: Optional[list[SubAgent]] = None,  
    state_schema: Optional[StateSchemaType] = None,
    interrupt_config: Optional[ToolInterruptConfig] = None,  
    config_schema: Optional[Type[Any]] = None,  
    checkpointer: Optional[Checkpointer] = None,  
    post_model_hook: Optional[Callable] = None,  
):  
    """Create a customizable deep agent with granular control over components.  
      
    Args:  
        tools: Additional tools the agent should have access to  
        instructions: Custom instructions for the agent  
        built_in_tools: List of built-in tool names to include. Options:  
            ['write_todos', 'write_file', 'read_file', 'ls', 'edit_file']  
            If None, includes all built-in tools  
        base_prompt: Custom base prompt. If None, uses a minimal default  
        model: The model to use  
        subagents: Custom subagents  
        state_schema: Custom state schema (must inherit from DeepAgentState)  
        interrupt_config: Tool interrupt configuration  
        config_schema: Configuration schema  
        checkpointer: State checkpointer  
        post_model_hook: Custom post-model hook  
    """  
      
    # Available built-in tools mapping  
    available_built_in_tools = {  
        'write_todos': write_todos,  
        'write_file': write_file,  
        'read_file': read_file,  
        'ls': ls,  
        'edit_file': edit_file  
    }  
      
    # Select built-in tools  
    if built_in_tools is None:  
        # Default: include all built-in tools  
        selected_built_ins = list(available_built_in_tools.values())  
    else:  
        # Only include specified tools  
        selected_built_ins = []  
        for tool_name in built_in_tools:  
            if tool_name in available_built_in_tools:  
                selected_built_ins.append(available_built_in_tools[tool_name])  
            else:  
                raise ValueError(f"Unknown built-in tool: {tool_name}. "  
                               f"Available: {list(available_built_in_tools.keys())}")  
      
    # Create custom base prompt  
    if base_prompt is None:  
        base_prompt = _create_default_base_prompt(built_in_tools or list(available_built_in_tools.keys()))  
      
    # Combine instructions with base prompt  
    full_prompt = instructions + "\n\n" + base_prompt  
      
    # Set up model and state schema  
    if model is None:  
        model = get_default_model()  
    state_schema = state_schema or DeepAgentState  
      
    # Create task tool for sub-agents  
    task_tool = _create_task_tool(  
        list(tools) + selected_built_ins,  
        instructions,  
        subagents or [],  
        model,  
        state_schema  
    )  
      
    # Combine all tools  
    all_tools = selected_built_ins + list(tools) + [task_tool]  
      
    # Handle post-model hook configuration  
    if post_model_hook and interrupt_config:  
        raise ValueError(  
            "Cannot specify both post_model_hook and interrupt_config together. "  
            "Use either interrupt_config for tool interrupts or post_model_hook for custom post-processing."  
        )  
    elif post_model_hook is not None:  
        selected_post_model_hook = post_model_hook  
    elif interrupt_config is not None:  
        selected_post_model_hook = create_interrupt_hook(interrupt_config)  
    else:  
        selected_post_model_hook = None  
      
    # Create and return the agent  
    return create_react_agent(  
        model,  
        prompt=full_prompt,  
        tools=all_tools,  
        state_schema=state_schema,
        post_model_hook=selected_post_model_hook,  
        config_schema=config_schema,  
        checkpointer=checkpointer,  
    )  
  
def _create_default_base_prompt(included_tools: list[str]) -> str:  
    """Create a minimal base prompt based on included tools."""  
    prompt_parts = ["You have access to the following tools:\n"]  
      
    if 'write_todos' in included_tools:  
        prompt_parts.append("""  
## `write_todos`  
Use this tool to manage and plan tasks. Use it frequently to track progress and break down complex tasks into smaller steps. Mark todos as completed immediately when done.  
""")  
      
    if any(tool in included_tools for tool in ['write_file', 'read_file', 'edit_file', 'ls']):  
        prompt_parts.append("""  
## File System Tools  
You have access to file operations for persistent storage and content management.  
""")  
      
    prompt_parts.append("""  
## `task`  
Use this tool to delegate work to specialized sub-agents when appropriate.  
""")  
      
    return "".join(prompt_parts)