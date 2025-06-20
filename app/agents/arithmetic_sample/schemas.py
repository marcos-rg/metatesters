from typing import Sequence
from dataclasses import dataclass, field
from typing_extensions import Annotated

from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage

@dataclass
class State:
    """
    Defines the state for the agent.
    """
    messages: Annotated[Sequence[AnyMessage], add_messages] = field(
        default_factory=list
    )