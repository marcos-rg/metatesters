from langgraph.graph.graph import CompiledGraph
from typing import Optional, Any
import uuid
import copy

from app.agents.graph_analysis.schemas import Config

def invoke_graph(graph: CompiledGraph,
                 input: Any,
                 thread_id:Optional[str] = None,
                 user_id:Optional[str]= None) -> tuple[Config, bool, str]:


    thread_id = thread_id if thread_id else str(uuid.uuid4())
    user_id = user_id if user_id else str(uuid.uuid4())

    config = Config(thread_id=thread_id,
                    user_id=user_id)

    configurable = {"configurable": config}

    error = False
    error_message = ""

    try:
        graph.invoke(input, config=configurable, stream_mode="debug")
    except Exception as e:
        error_message = f"Graph execution failed: {e}"
        error = True

    return config, error, error_message

def obj_to_str(obj, max_depth=float('inf'), current_depth=0):
    """
    Converts any Python object into a string representation that looks like the original code.

    Args:
        obj: Any Python object
        max_depth: Maximum depth for recursion (default: infinite)
        current_depth: Current recursion depth (used internally)

    Returns:
        String representation of the object that looks like code
    """
    # Check if we've reached maximum depth
    if current_depth >= max_depth:
        return repr(obj)

    if isinstance(obj, dict):
        items = [f'"{k}": {obj_to_str(v, max_depth, current_depth + 1)}' for k, v in obj.items()]
        return '{' + ', '.join(items) + '}'
    elif isinstance(obj, (list, tuple)):
        items = [obj_to_str(item, max_depth, current_depth + 1) for item in obj]
        return '[' + ', '.join(items) + ']' if isinstance(obj, list) else '(' + ', '.join(items) + ')'
    elif isinstance(obj, str):
        return f'"{obj}"'
    elif isinstance(obj, (int, float, bool, type(None))):
        return str(obj)
    elif obj.__class__.__module__ == 'builtins':
        return repr(obj)
    else:
        # Handle custom objects by reconstructing their initialization
        class_name = obj.__class__.__name__

        # If at max_depth, just return the repr
        if current_depth >= max_depth:
            return f"{class_name}(...)"

        # Try to get the object's attributes
        try:
            # First try to get __dict__
            attrs = copy.copy(obj.__dict__)

            # more clear messages representation
            attrs.pop('additional_kwargs', None)
            attrs.pop('usage_metadata', None)
            attrs.pop('response_metadata', None)
            attrs.pop('id', None)

        except AttributeError:
            try:
                # If no __dict__, try getting slots
                attrs = {slot: getattr(obj, slot) for slot in obj.__slots__}
            except AttributeError:
                # If neither works, just use repr
                return repr(obj)

        # Convert attributes to key=value pairs
        attr_strs = []
        for key, value in attrs.items():
            # Skip private attributes (starting with _)
            if not key.startswith('_'):
                attr_strs.append(f"{key}={obj_to_str(value, max_depth, current_depth + 1)}")

        return f"{class_name}({', '.join(attr_strs)})"