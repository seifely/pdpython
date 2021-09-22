import random

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


def init_random_graph(height, width):
    """ Build the random connections between nodes for initialisation. """


def convert_graph_to_lists(graph):
    """ Output the graph instead as an ID-keyed dict that contains vectors of each agent's initial partners. """


def init_connections(height, width, agents_list):
    maxm = (height*width)-1
    connections_list = {}
    for i in agents_list:
        #Random number of connections for each agent
        n_conns = random.randint()

    return