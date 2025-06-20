import logging
from typing import cast

from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition


from app.agents.arithmetic_sample.schemas import State
from app.agents.config.graph_config import Configuration
from app.agents.utils.llm import load_chat_model, create_system_message
from app.agents.arithmetic_sample.tools import ALL_TOOLS
from app.agents.arithmetic_sample.prompts import ASSISTANT_PROMPT


# =====================================================================
# Nodes

def assistant(state: State, config: RunnableConfig) -> dict[str, list[AIMessage]]:
    
    logging.info("Assistant node invoked")

    configuration = Configuration.from_runnable_config(config)

    # Initialize the model with tool binding. Change the model or add more tools here.
    model = load_chat_model(configuration.model).bind_tools(ALL_TOOLS)

    system_message = PromptTemplate.from_template(ASSISTANT_PROMPT)
    system_message = system_message.invoke({}).to_string()

    response = cast(
        AIMessage,
        model.invoke([create_system_message(system_message), *state.messages], config=config)
    )

    return {"messages": [response]}

# =====================================================================
# Build the graph
arithmetic_graph = StateGraph(State, config_schema=Configuration)

# Add nodes
arithmetic_graph.add_node("assistant", assistant)
arithmetic_graph.add_node("tools", ToolNode(ALL_TOOLS))

# Add edges
arithmetic_graph.set_entry_point("assistant")

# If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
# If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
arithmetic_graph.add_conditional_edges(
    "assistant",
    tools_condition,
)
arithmetic_graph.add_edge("tools", "assistant")

# Compile workflow
arithmetic_app = arithmetic_graph.compile(name="Target Arithmetic Agent")