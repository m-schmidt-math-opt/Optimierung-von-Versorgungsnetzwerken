"""
Contains a routine to read DIMACS min cost flow files
"""

import networkx

def read_min_cost_flow(file_object):
    """
    Reads a DIMACS min cost instance file from a file

    Object nodes have a 'demand' field.

    Arcs have a lower bound 'low', an upper bound 'capacity', and a cost 'weight'.

    Keyword arguments:
    file_object -- an opened file to read from
    """

    Graph = networkx.MultiDiGraph()
    for line in file_object:
        elements = line.split()
        line_type = elements[0]
        if line_type == 'c':
            pass
        elif line_type == 'p':
            ### maybe assert correct dimacs type
            num_nodes = int(elements[2])
            Graph.add_nodes_from(range(1, num_nodes + 1), demand=0)
        elif line_type == 'n':
            node_id = int(elements[1])
            demand = int(elements[2])
            ## dimacs convention differs from networkx convention
            Graph.node[node_id]['demand'] = -demand
        elif line_type == 'a':
            src = int(elements[1])
            dst = int(elements[2])
            low = int(elements[3])
            cap = int(elements[4])
            cost = int(elements[5])
            Graph.add_edge(src, dst, lower=low, capacity=cap, weight=cost)
        else:
            raise IOError

    return Graph

# read_min_cost_flow
