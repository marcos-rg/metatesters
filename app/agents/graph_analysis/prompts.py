NODE_DESCRIPTION_PROMPT: str = """
You are a workflow developer tasked with characterizating a graph.
You have focused on LangChain and LangGraph frameworks in python.
Using the data below, describe what a node is for:

general graph description: {graph_description}

node name: {node_name}
type: {type}
previous node description : {node_description}

income nodes: {income_nodes}
sample_input: {input}

outcome nodes: {outcome_nodes}
sample_output: {output}

functions: {functions}

Take your time and be clrear.

First, identify the node name and its type.
Then look at the input_node, sample_input, and output_node, sample_output.
Explain how it could interact with neighboring nodes.
Explain the input and output requirements.
Combine previous description findings and current description.
Figure out what the functions are for in the graph context.
Find out how the node can contribute to achieve the graph goal.
Finally, write the description of the node in a clear and concise manner.
Avoid redundant information.
Ignore empty fields.
"""

GRAPH_DESCRIPTION_PROMPT: str = """
You are a workflow developer tasked with characterizing a graph.
You have focused on LangChain and LangGraph frameworks in python.
Using the data below, describe: what the graph is for, main characteristics, and how it works.

nodes description: {nodes_description}

sample tasks: {sample_tasks}

Take your time and be clear.
First, identify the main goal of the graph.
Identify the main components of the graph and their roles.
Finally, write the description of the graph in a clear and concise manner.
Avoid redundant information.
Be specific and detailed.
Follow this structure:
1. **Graph Goal**: Describe the main goal of the graph and target audience.
2. **Nodes**: Describe nodes.
3. **Data Flow**: Describe how data flows through the graph.
4. **User Experience**: Describe how a user would interact with the graph.
"""