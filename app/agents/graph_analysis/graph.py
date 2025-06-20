import logging

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import PromptTemplate

from app.agents.utils.networkx import NetworkXGraph
from app.agents.graph_analysis.schemas import InputState, OverallState, Node_description, GrpahDescription
from app.agents.config.graph_config import Configuration
from app.agents.utils.llm import load_chat_model, create_structured_llm, create_system_message
from app.agents.graph_analysis.utils import invoke_graph, obj_to_str
from app.agents.graph_analysis.prompts import NODE_DESCRIPTION_PROMPT, GRAPH_DESCRIPTION_PROMPT

# =====================================================================
# Nodes
def static_test(state: InputState, config: RunnableConfig):
    logging.info("Static test node invoked")

    memory = MemorySaver() # it could be a SQLite database
    graph_after_compile = state["graph_before_compile"].compile(checkpointer=memory, name="Target Arithmetic Agent being analyzed")

    graph_object = graph_after_compile.get_graph()

    networkx_graph = NetworkXGraph(graph_object)
    

    return {"compiled_graph": graph_after_compile,
             "summary_graph": networkx_graph
             }

def generate_node_descriptions(state: OverallState, config: RunnableConfig):
    logging.info("Generate node descriptions node invoked")

    configuration = Configuration.from_runnable_config(config)
    model = load_chat_model(configuration.model)
    structured_llm = create_structured_llm(model, Node_description)

    configuration, error, error_message  = invoke_graph(graph=state["compiled_graph"],
                                                 input=state["valid_input"])
    
    if error:
        raise Exception(f"Graph execution failed: {error_message}")
    
    configurable = {"configurable": configuration}

    history = list(state["compiled_graph"].get_state_history(configurable))
    history.reverse()

    node_name_in_tasks = [item.tasks[0].name for item in history if item.tasks]
    node_name_in_tasks.remove('__start__')

    node_tasks_in_tasks = [item.tasks[0].result for item in history if item.tasks]

    summary_graph = state["summary_graph"]

    for index, node_name in enumerate(node_name_in_tasks):
        current_description = summary_graph.get_node_attribute(node_name, "description")
        functions = summary_graph.get_node_attribute(node_name, "tools")

        actual_input = node_tasks_in_tasks[index]
        actual_output = node_tasks_in_tasks[index+1]

        prompt = PromptTemplate.from_template(NODE_DESCRIPTION_PROMPT)
        prompt = prompt.invoke({
            "graph_description": state["user_description"],
            "node_name": node_name,
            "type": str(summary_graph.get_node_attribute(node_name, "type")),
            "node_description": current_description,
            "income_nodes": str(summary_graph.get_input_edges(node_name)),
            "input": obj_to_str(actual_input),
            "outcome_nodes": str(summary_graph.get_output_edges(node_name)),
            "output": obj_to_str(actual_output),
            "functions": functions
        })
        prompt = prompt.to_string()

        llm_description = structured_llm.invoke([create_system_message(prompt)])

        summary_graph.set_node_attribute(node_name, "description", llm_description.node_description)

    history_to_show = []
    for item in node_tasks_in_tasks:
        history_to_show.append(obj_to_str(item))

    return {"execution_configs": [config],
            "summary_graph": summary_graph,
            "history_to_show": history_to_show}

def generate_graph_description(state: OverallState, config: RunnableConfig):
    logging.info("Generate graph description node invoked")

    configuration = Configuration.from_runnable_config(config)
    model = load_chat_model(configuration.model)
    structured_llm = create_structured_llm(model, GrpahDescription)

    prompt = PromptTemplate.from_template(GRAPH_DESCRIPTION_PROMPT)
    prompt = prompt.invoke({
        "nodes_description": state["summary_graph"].get_all_node_attributes("description"),
        "sample_tasks": state["history_to_show"]
    }).to_string()

    llm_description = structured_llm.invoke([create_system_message(prompt)])

    return {"graph_description": llm_description.graph_description}

# =====================================================================
# Build the graph
builder = StateGraph(state_schema=OverallState, 
                     input=InputState,
                     config_schema=Configuration)

# Add nodes
builder.add_node("static_test", static_test)
builder.add_node("generate_node_descriptions", generate_node_descriptions)
builder.add_node("generate_graph_description", generate_graph_description)

# Add edges
builder.set_entry_point("static_test")
builder.add_edge("static_test", "generate_node_descriptions")
builder.add_edge("generate_node_descriptions", "generate_graph_description")
builder.set_finish_point("generate_graph_description")

# Compile workflow
graph_analysis_app = builder.compile(name="Graph Gather Information Agent")
    
