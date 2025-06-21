from typing import List, Callable, Any

from langchain_core.tools import tool

@tool(response_format="content")
def multiply(a: float, b: float) -> float:
    """Multiply a and b.

    Args:
        a: first float
        b: second float
    """
    return a * b

@tool(response_format="content")
def add(a: float, b: float) -> float:
    """Adds a and b.

    Args:
        a: first float
        b: second float
    """
    return a + b

@tool(response_format="content")
def divide(a: float, b: float) -> float:
    """Divides a by b.

    Args:
        a: first float
        b: second float
    """
    return a / b

tools = [add, multiply, divide]


ALL_TOOLS: List[Callable[..., Any]] = [
    add,
    multiply,
    divide,
]