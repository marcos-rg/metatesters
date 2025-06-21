from typing import Any
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from pydantic import BaseModel, Field

from app.agents.utils.networkx import NetworkXGraph

class Config(TypedDict):
    user_id: str
    thread_id: str

class InputState(TypedDict):
    """
    Defines the input state for the agent.
    """
    user_description: str
    valid_input: Any
    graph_before_compile: StateGraph


class OverallState(InputState):
    """
    Defines additional internal state for the agent.
    """
    compiled_graph: CompiledGraph
    summary_graph: NetworkXGraph
    execution_configs: list[Config]
    history_to_show: list[str]
    graph_description: str

class Node_description(BaseModel):
    node_description: str = Field(description="Description of the node.")

class GrpahDescription(BaseModel):
    graph_description: str = Field(description="Description of the graph.")