from langgraph.prebuilt import ToolNode
import networkx as nx


class NetworkXGraph:
    """
    A class to represent a NetworkX graph.
    """
    def __init__(self, langgraph_graph):
        """
        Initializes the NetworkXGraph with a LangGraph graph.
        Args:
            langgraph_graph: The LangGraph graph to be converted to NetworkX.
        """
        self.langgraph_graph = langgraph_graph
        self.nodes = self.langgraph_graph.nodes
        self.edges = self.langgraph_graph.edges
        self.graph_summary = nx.DiGraph()

        self.convert_to_networkx()

    def add_nodes(self):
        """
        Adds nodes to the NetworkX graph.
        """
        for name, node in self.nodes.items():
            tools = {}
            type_node = type(node.data)

            if type_node == ToolNode:
                for name_tool, tool in node.data.tools_by_name.items():
                    tools[name_tool] = tool.description

            self.graph_summary.add_node(name, type=type_node, runnable=node.data, tools=tools, name=name, description=None)

    def add_edges(self):
        """
        Adds edges to the NetworkX graph.
        """
        for edge in self.edges:
            self.graph_summary.add_edge(edge.source, edge.target, conditional=edge.conditional)

    def convert_to_networkx(self):
        """
        Converts the LangGraph graph to a NetworkX graph.
        """
        self.add_nodes()
        self.add_edges()

    def get_node_attribute(self, node_name, attribute):
        """
        Gets the attribute of a node in the NetworkX graph.
        Args:
            node_name: The name of the node.
            attribute: The attribute to be retrieved.
        Returns:
            The value of the attribute.
        """
        return self.graph_summary.nodes[node_name][attribute]
    
    def get_all_node_attributes(self, attribute: str):
        """
        Gets the attribute of all nodes in the NetworkX graph.
        Args:
            attribute: The attribute to be retrieved.
        Returns:
            A dictionary with node names as keys and attribute values as values.
        """
        return {self.graph_summary.nodes[node][attribute] for node in self.graph_summary.nodes}
    
    def set_node_attribute(self, node_name, attribute, value):
        """
        Sets the attribute of a node in the NetworkX graph.
        Args:
            node_name: The name of the node.
            attribute: The attribute to be set.
            value: The value to be set.
        """
        self.graph_summary.nodes[node_name][attribute] = value

    def get_graph(self):
        """
        Returns the NetworkX graph.
        Returns:
            The NetworkX graph.
        """
        return self.graph_summary
    
    def get_input_edges(self, node_name):
        """
        Gets the input edges of a node in the NetworkX graph.
        Args:
            node_name: The name of the node.
        Returns:
            The input edges of the node.
        """
        inputs = []
        for edge in self.graph_summary.in_edges(node_name):
            inputs.append(edge[0])
        return inputs

    def get_output_edges(self, node_name):
        """
        Gets the output edges of a node in the NetworkX graph.
        Args:
            node_name: The name of the node.
        Returns:
            The output edges of the node.
        """
        outputs = []
        for edge in self.graph_summary.out_edges(node_name):
            outputs.append(edge[1])
        return outputs
    
    def get_all_nodes(self):
        """
        Returns the nodes of the NetworkX graph.
        Returns:
            The nodes of the NetworkX graph.
        """
        return self.graph_summary.nodes

    def get_node_attributes(self, node_name):
        """
        Gets all attributes of a node in the NetworkX graph.
        Args:
            node_name: The name of the node.
        Returns:
            A dictionary with all attributes of the node.
        """
        return self.graph_summary.nodes[node_name]
    
    


        
        