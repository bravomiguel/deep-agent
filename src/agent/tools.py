from langchain_core.tools import tool
from pathlib import Path
from typing import Annotated
from langgraph.prebuilt import InjectedState


def clean_file_path(file_path: str) -> str:
    """Clean up file paths that may have extra quotes or brackets."""
    # Remove surrounding brackets, quotes (both straight and curly)
    cleaned = file_path.strip()
    cleaned = cleaned.strip("[]")
    cleaned = cleaned.strip("'\"''""")
    cleaned = cleaned.strip()
    return cleaned


@tool
def list_attachments(
    state: Annotated[dict, InjectedState]
) -> str:
    """
    List all files currently attached to this conversation.
    
    Returns:
        A formatted list of attached files with their names and full paths.
    """
    attached_files = state.get("attached_files", [])
    
    if not attached_files:
        return "No files are currently attached."
    
    file_list = []
    for i, file_path in enumerate(attached_files, 1):
        cleaned_path = clean_file_path(file_path)
        path_obj = Path(cleaned_path)
        file_name = path_obj.name
        file_list.append(f"{i}. {file_name} (path: {cleaned_path})")
    
    return f"Attached files:\n" + "\n".join(file_list)


@tool
def read_attachment(
    file_name: Annotated[str, "Name or path of the file to read"],
    state: Annotated[dict, InjectedState]
) -> str:
    """
    Read content from an attached text file (up to 2000 lines).
    
    Args:
        file_name: Name or path of the file to read
        state: Injected agent state containing attached_files list
        
    Returns:
        Content of the file as a string (up to 2000 lines)
    """
    attached_files = state.get("attached_files", [])
    
    if not attached_files:
        return "No files are currently attached."
    
    # Clean the input file name
    cleaned_input = clean_file_path(file_name)
    file_name_only = Path(cleaned_input).name
    
    # Find matching file path
    matching_file = None
    
    for attached_path in attached_files:
        cleaned_attached = clean_file_path(attached_path)
        attached_path_obj = Path(cleaned_attached)
        # Match by full path or just filename
        if cleaned_attached == cleaned_input or attached_path_obj.name == file_name_only:
            matching_file = cleaned_attached
            break
    
    if not matching_file:
        available = [Path(clean_file_path(f)).name for f in attached_files]
        return f"File '{cleaned_input}' not found in attached files. Available files: {', '.join(available)}"
    
    # Check if file exists
    file_path = Path(matching_file)
    if not file_path.exists():
        return f"Error: File '{matching_file}' does not exist on the filesystem."
    
    if not file_path.is_file():
        return f"Error: '{matching_file}' is not a file."
    
    try:
        # Read file content (up to 2000 lines)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= 2000:
                    lines.append(f"\n[File truncated - only first 2000 lines shown]")
                    break
                lines.append(line)
            
            content = ''.join(lines)
        
        if content:
            return f"Content of '{file_path.name}':\n\n{content}"
        else:
            return f"File '{file_path.name}' appears to be empty."
            
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= 2000:
                        lines.append(f"\n[File truncated - only first 2000 lines shown]")
                        break
                    lines.append(line)
                
                content = ''.join(lines)
            return f"Content of '{file_path.name}' (latin-1 encoding):\n\n{content}"
        except Exception:
            return f"Error reading file '{matching_file}': Unable to decode file content"
    except Exception as e:
        return f"Error reading file '{matching_file}': {str(e)}"