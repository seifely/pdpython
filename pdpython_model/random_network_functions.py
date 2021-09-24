import random
import networkx as nx
import matplotlib.pyplot as plt

def init_partner_list(height, width, id):
    """ Set ID to 0 to generate the full list of all agent IDs."""
    pardners = []
    maxm = (height*width)+1
    ids = list(range(1, maxm))
    for i in ids:
        if not i == id:
            pardners.append(i)
    return pardners


def init_pot_partner_reps(potential_partner_list, rep_type):
    return

def initRandomGraph(nodes, probability, ids):
    """ Produces a Random Erdos Renyi Graph, based on a probability of connecting to each next node, and a dict for
    each agent of who their starting partners should be. """
    N = nodes
    P = probability
    g = nx.Graph()

    edgesDict = {}

    for i in ids:
        edgesDict[i] = 0

    # Adding nodes
    g.add_nodes_from(range(1, N + 1))

    # Add edges to the graph randomly.
    for i in g.nodes():
        for j in g.nodes():
            if (i < j):

                # Take random number R.
                R = random.random()

                # Check if R<P add the edge to the graph else ignore.
                if (R < P):
                    g.add_edge(i, j)
        pos = nx.circular_layout(g)

    # for k in ids:
    #     # Get each's nodes edges into one big nested list
    #     bigList[k] = g.edges(k)

    for k in ids:
        current_edges = list(g.edges(k))
        exported_edges = []
        length = range(len(current_edges))
        for i in length:
            current_edge = current_edges[i]
            exported_edges.append(current_edge[1])
        edgesDict[k] = exported_edges

    # Export the Edge List of the graph, and Export the version Agents can understand
    return edgesDict, g

def  convert_graph_to_dict(graph, ids):

    return

def convert_dict_to_graph(dict, ids):
    return

def update_graph(graph, changes):
    """ Import the previous graph, get its data in dict form, get the current edge """


def convert_graph_to_lists(graph):
    """ Output the graph instead as an ID-keyed dict that contains vectors of each agent's initial partners. """


def init_connections(height, width, agents_list):
    maxm = (height*width)-1
    connections_list = {}
    for i in agents_list:
        #Random number of connections for each agent
        n_conns = random.randint()

    return