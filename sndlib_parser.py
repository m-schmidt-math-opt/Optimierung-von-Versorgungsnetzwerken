"""
Contains a routine to read SNDlib network files in native format.
"""

import networkx

def read_sndlib(file_object):
    """
    Reads a SNDlib network file in native format.

    Keyword arguments:
    file_object -- an opened file to read from
    """

    meta = False
    nodes = False
    links = False
    demands = False
    admissible_paths = False

    meta_lines = []
    node_lines = []
    link_lines = []
    demand_lines = []
    admissible_path_lines = []

    # reading the SNDlib network file in native format
    # and store lines to corresponding lists; see above
    
    for line in file_object:
        if line[0] == "?" or line[0] == "#" or line == "":
            pass
        elif line[0] == ")":
            if meta:
                meta = False
            elif nodes:
                nodes = False
            elif links:
                links = False
            elif demands:
                demands = False
            elif admissible_paths:
                admissible_paths = False
            else:
                print("WARNING: This should never happen!")
        elif "META (" in line:
            meta = True
        elif "NODES (" in line:
            nodes = True
        elif "LINKS (" in line:
            links = True
        elif "DEMANDS (" in line:
            demands = True
        elif "ADMISSIBLE_PATHS (" in line:
            admissible_paths = True
        else:
            if admissible_paths:
                admissible_path_lines.append(line)
            elif demands:
                demand_lines.append(line)
            elif links:
                link_lines.append(line)
            elif nodes:
                node_lines.append(line)
            elif meta:
                meta_lines.append(line)

    # instantiating the network and supply graph
    # representing the SNDlib network design problem
                
    network_graph = networkx.DiGraph()
    supply_graph = networkx.DiGraph()    

    # META: ignoring everything

    # handling the NODES data
    for node_line in node_lines:
        node_data = filter(lambda x: x != '(' and x != ')', node_line.split())
        assert(len(node_data) >= 1)
        node_id = node_data[0]
        longitude = 0
        latitude = 0
        if len(node_data) > 1:
            assert(len(node_data) == 3)
            longitude = node_data[1]
            latitude = node_data[2]
        network_graph.add_node(node_id)
        network_graph.node[node_id]['longitude'] = float(longitude)
        network_graph.node[node_id]['latitude'] = float(latitude)
        supply_graph.add_node(node_id)
        supply_graph.node[node_id]['longitude'] = float(longitude)
        supply_graph.node[node_id]['latitude'] = float(latitude)

    # handling the LINKS data
    for link_line in link_lines:
        link_data = filter(lambda x: x != '(' and x != ')', link_line.split())
        assert(len(link_data) >= 7)
        link_id = link_data[0]
        source = link_data[1]
        target = link_data[2]
        pre_installed_capacity_tmp = link_data[3]
        pre_installed_capacity_cost_tmp = link_data[4]
        routing_cost_tmp = link_data[5]
        setup_cost_tmp = link_data[6]
        modules_tmp = []
        if len(link_data) > 7:
            assert((len(link_data) - 7) % 2 == 0)
            nr_modules = (len(link_data) - 7) / 2
            for i in range(nr_modules):
                module = (float(link_data[7+2*i]), float(link_data[7+2*i+1]))
                modules_tmp.append(module)
        network_graph.add_edge(source, target,
                               pre_installed_capacity = float(pre_installed_capacity_tmp),
                               pre_installed_capacity_cost = float(pre_installed_capacity_cost_tmp),
                               routing_cost = float(routing_cost_tmp),
                               setup_cost = float(setup_cost_tmp),
                               modules = modules_tmp)
        # The integration of the following edge is required for
        # the consideration of so-called "biderected" link models
        network_graph.add_edge(target, source,
                               pre_installed_capacity = float(pre_installed_capacity_tmp),
                               pre_installed_capacity_cost = float(pre_installed_capacity_cost_tmp),
                               routing_cost = float(routing_cost_tmp),
                               setup_cost = float(setup_cost_tmp),
                               modules = modules_tmp)

    # handling the DEMANDS data
    for demand_line in demand_lines:
        demand_data = filter(lambda x: x != '(' and x != ')', demand_line.split())
        assert(len(demand_data) == 6)
        edge_id = demand_data[0]
        source = demand_data[1]
        target = demand_data[2]
        routing_unit_tmp = demand_data[3]
        demand_value_tmp = demand_data[4]
        max_path_length_tmp = demand_data[5]
        supply_graph.add_edge(source, target,
                              routing_unit = float(routing_unit_tmp),
                              demand_value = float(demand_value_tmp),
                              max_path_length = max_path_length_tmp)

    # ADMISSIBLE PATHS: ignore everything

    return (network_graph, supply_graph)
# read_sndlib
