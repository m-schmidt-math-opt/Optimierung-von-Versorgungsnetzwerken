import re
from xml.etree import cElementTree

import entry
import exit
import pipe as pipe_module
import node
import compressor_station

class GasLibParser(object):
    """Class for parsing GasLib data."""

    def __init__(self, gaslib_net_file, gaslib_scn_file):
        """Constructor."""
        self.gaslib_net_file = gaslib_net_file
        self.gaslib_scn_file = gaslib_scn_file
        self.namespaces = { "framework" : "http://gaslib.zib.de/Framework", "gas" : "http://gaslib.zib.de/Gas" }
        self.net_name = None
        self.entry_data = {}
        self.exit_data = {}
        self.innode_data = {}
        self.pipe_data = {}
        self.compressor_station_data = {}

    def parse(self):
        """Main parsing method."""
        self._parse_net_file()
        self._parse_scn_file()
        
    def _parse_scn_file(self):
        etree = cElementTree.parse(self.gaslib_scn_file)
        nodes_iter = etree.iterfind(".//gas:node", self.namespaces)
        for node_element in nodes_iter:
            self._parse_scn_node(node_element)
        
    def _parse_scn_node(self, node_element):
        scn_intervals = { "pressure" : (0, float("inf")),
                          "flow" : (0, float("inf")) }
        node_id = node_element.get("id")
        node_type = node_element.get("type")
        for bound in node_element.iter():
            if self.strip_namespace(bound) == "node":
                continue
            sort = self.strip_namespace(bound)
            sense = bound.get("bound")
            value = float(str(bound.get("value")))
            if sense == "lower" or sense == "both":
                s_max = scn_intervals[sort][1]
                scn_intervals[sort] = (value, s_max)
            if sense == "upper" or sense == "both":
                s_min = scn_intervals[sort][0]
                scn_intervals[sort] = (s_min, value)
        if node_type == "exit":
            node_data = self.exit_data[node_id]._asdict()
        elif node_type == "entry":
            node_data = self.entry_data[node_id]._asdict()
        else:
            node_data = None
        net_intervals = { "pressure" : (node_data['pressure_min'], node_data['pressure_max']),
                          "flow" : (node_data['flow_min'], node_data['flow_max']) }
        result_intervals = {}
        for b_type, interval in  net_intervals.items():
            result_intervals[b_type] = self._intersect_intervals(interval,
                                                                 scn_intervals[b_type])
        
        node_data['pressure_min'] = result_intervals['pressure'][0]
        node_data['pressure_max'] = result_intervals['pressure'][1]
        node_data['flow_min'] = result_intervals['flow'][0]
        node_data['flow_max'] = result_intervals['flow'][1]
        if node_type == "exit":
            self.exit_data[node_id] = exit.Exit(**node_data)
        elif node_type == "entry":
            self.entry_data[node_id] = entry.Entry(**node_data)
        else:
            pass
                
    def _intersect_intervals(self, a_int, b_int):
        (amin, amax) = a_int
        (bmin, bmax) = b_int
        return max(amin, bmin), min(amax,bmax)
        
    def _parse_net_file(self):
        etree = cElementTree.parse(self.gaslib_net_file)
        self.net_name = etree.find(".//framework:title", self.namespaces).text
        nodes_element = etree.find("framework:nodes", self.namespaces)
        self._parse_nodes(nodes_element)
        connections_element = etree.find("framework:connections", self.namespaces)
        self._parse_connections(connections_element)
        
    def _parse_nodes(self, nodes_element):
        """parse the nodes section"""
        sources_iter = nodes_element.iterfind("gas:source", self.namespaces)
        self._parse_sources(sources_iter)
        sinks_iter = nodes_element.iterfind("gas:sink", self.namespaces)
        self._parse_sinks(sinks_iter)
        innodes_iter = nodes_element.iterfind("gas:innode", self.namespaces)
        self._parse_innodes(innodes_iter)

    def _parse_innodes(self, innodes_iter):
        for innode in innodes_iter:
            node_dict = {}
            node_dict["node_id"] = innode.get("id")
            for element in innode.iter():
                tag = self.strip_namespace(element)
                if tag == "innode":
                    continue
                else:
                    new_name = self.cc_to_us(tag)
                node_dict[new_name] = float(element.get("value"))
            i_data = node.Node(**node_dict)
            self.innode_data[i_data.node_id] = i_data

    def _parse_connections(self, connections_element):
        """parse the connections section"""
        pipes_iter = connections_element.iterfind("gas:pipe", self.namespaces)
        self._parse_pipes(pipes_iter)
        compressors_iter = connections_element.iterfind("gas:compressorStation", self.namespaces)
        self._parse_compressor_stations(compressors_iter)

    def _parse_compressor_stations(self, compressors_iter):
        for compressor in compressors_iter:
            compressor_dict = self.init_compressor()
            compressor_dict["arc_id"] = compressor.get("id")
            compressor_dict["from_node"] = compressor.get("from")
            compressor_dict["to_node"] = compressor.get("to")
            for element in compressor.iter():
                tag = self.strip_namespace(element)
                if tag == "compressorStation":
                    continue
                elif tag == "dragFactorIn" or tag == "dragFactorOut":
                    continue
                elif tag == "diameterIn" or tag == "diameterOut":
                    continue
                else:
                    new_name = self.cc_to_us(tag)
                compressor_dict[new_name] = float(element.get("value"))
            cs_data = compressor_station.CompressorStation(**compressor_dict)
            self.compressor_station_data[cs_data.arc_id] = cs_data
        
    def _parse_pipes(self, pipes_iter):
        for pipe in pipes_iter:
            pipe_dict = {}
            pipe_dict["arc_id"] = pipe.get("id")
            pipe_dict["from_node"] = pipe.get("from")
            pipe_dict["to_node"] = pipe.get("to")
            for element in pipe.iter():
                tag = self.strip_namespace(element)
                if tag == "pipe":
                    continue
                else:
                    new_name = self.cc_to_us(tag)
                pipe_dict[new_name] = float(element.get("value"))
            p_data = pipe_module.Pipe(**pipe_dict)
            self.pipe_data[p_data.arc_id] = p_data
                
    def _parse_sinks(self, sinks_iter):
        for sink in sinks_iter:
            exit_dict = {}
            exit_dict["node_id"] = sink.get("id")
            for element in sink.iter():
                tag = self.strip_namespace(element)
                if tag == "sink":
                    continue
                else:
                    new_name = self.cc_to_us(tag)
                exit_dict[new_name] = float(element.get("value"))
            e_data = exit.Exit(**exit_dict)
            self.exit_data[e_data.node_id] = e_data
            
    def _parse_sources(self, sources_iter):
        for source in sources_iter:
            entry_dict = {}
            entry_dict["node_id"] = source.get("id")
            for element in source.iter():
                tag = self.strip_namespace(element)
                if tag == "coefficient-A-heatCapacity":
                    new_name = "heat_coeff_A"
                elif tag == "coefficient-B-heatCapacity":
                    new_name = "heat_coeff_B"
                elif tag == "coefficient-C-heatCapacity":
                    new_name = "heat_coeff_C"
                elif tag == "source":
                    continue
                elif tag == "gasTemperature":
                    new_name = "gas_temp"
                else:
                    new_name = self.cc_to_us(tag)
                entry_dict[new_name] = float(element.get("value"))
            e_data = entry.Entry(**entry_dict)
            self.entry_data[e_data.node_id] = e_data

    def strip_namespace(self, element):
        tag = re.sub('[^}]*}(.*)', r'\1', element.tag)
        return tag

    def cc_to_us(self, name):
        """"""
        # taken from http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-camel-case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def init_compressor(self):
        """"""
        if self.net_name == "GasLib_40":
            compressor_dict = { "max_pressure_increase" : 24.33131262,
                                "max_pressure_ratio" : 1.521214713,
                                "min_pressure_increase" : 1.883212208,
                                "min_pressure_ratio" :  1.060722826 }
        elif self.net_name == "GasLib_135":
            compressor_dict = { "max_pressure_increase" : 31.70737918,
                                "max_pressure_ratio" : 1.806683035,
                                "min_pressure_increase" : 1.034326951,
                                "min_pressure_ratio" :  1.033351131 }

        else:
            compressor_dict = {}
        return compressor_dict
