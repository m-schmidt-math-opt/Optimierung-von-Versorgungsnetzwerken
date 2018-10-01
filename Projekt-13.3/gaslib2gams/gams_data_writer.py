class GamsDataWriter(object):
    """Class for writing GAMS data."""

    def __init__(self, gams_data_file):
        """Constructor."""
        self.gams_data_file = gams_data_file
        self.slash = " / "
        self.semicolon = " ; "

    def write(self, entry_data, exit_data, innode_data, pipe_data, cs_data):
        """Main writing method."""
        self._write_gams_line_node_data(entry_data, exit_data, innode_data)
        self._write_gams_line_arc_data(pipe_data, cs_data)

    def _write_gams_line_node_data(self, entry_data, exit_data, innode_data):
        """Writing all node specific data in GAMS compatible format."""
        list_of_node_ids = []
        list_of_entry_ids = []
        list_of_exit_ids = []
        list_of_innode_ids = []
        list_of_node_table_lines = []
        for node_id, entry_node in entry_data.items():
            list_of_node_ids.append(entry_node.node_id)
            list_of_entry_ids.append(entry_node.node_id)
            table_line = "\t" + str(entry_node.node_id).ljust(10) + "\t" + str(entry_node.height).ljust(10) + "\t" + str(entry_node.pressure_min).ljust(10) +  "\t" + str(entry_node.pressure_max).ljust(10) +  "\t" + str(entry_node.flow_min).ljust(10) + "\t" + str(entry_node.flow_max).ljust(10)
            list_of_node_table_lines.append(table_line)
        for node_id, exit_node in exit_data.items():
            list_of_node_ids.append(exit_node.node_id)
            list_of_exit_ids.append(exit_node.node_id)
            table_line = "\t" + str(exit_node.node_id).ljust(10) + "\t" + str(exit_node.height).ljust(10) + "\t" + str(exit_node.pressure_min).ljust(10) +  "\t" + str(exit_node.pressure_max).ljust(10) +  "\t" + str(-float(exit_node.flow_min)).ljust(10) +  "\t" + str(-float(exit_node.flow_max)).ljust(10)
            list_of_node_table_lines.append(table_line)
        for node_id, inner_node in innode_data.items():
            list_of_node_ids.append(inner_node.node_id)
            list_of_innode_ids.append(inner_node.node_id)
            table_line = "\t" + str(inner_node.node_id).ljust(10) + "\t" + str(inner_node.height).ljust(10) + "\t" + str(inner_node.pressure_min).ljust(10) + "\t" + str(inner_node.pressure_max).ljust(10) + "\t" + "0".ljust(10) + "\t" + "0".ljust(10)
            list_of_node_table_lines.append(table_line)
        self._write_gams_line("set nodes" + self.slash + "\n" + ",\n".join(list_of_node_ids) + self.slash + self.semicolon)        
        self._write_gams_line("set entries(nodes)" + self.slash + "\n" + ",\n".join(list_of_entry_ids) + self.slash + self.semicolon)
        self._write_gams_line("set exits(nodes)" + self.slash + "\n" + ",\n".join(list_of_exit_ids) + self.slash + self.semicolon)
        self._write_gams_line("set innodes(nodes)" + self.slash + "\n" + ",\n".join(list_of_innode_ids) + self.slash + self.semicolon)
        self._write_gams_line("Table node_data(n,*)")
        self._write_gams_line("\t\t\t" + "height".ljust(10) + "\t" + "p_min".ljust(10) + "\t" + "p_max".ljust(10) + "\t" + "flow_min".ljust(10) + "\t" + "flow_max".ljust(10))
        for table_line in list_of_node_table_lines:
            self.gams_data_file.write(table_line + "\n")
        line = ";"
        self._write_gams_line(line)
        line = "node_height(n) = node_data(n,'height')" + self.semicolon
        self._write_gams_line(line)
        line = "node_p_min(n) = node_data(n,'p_min')" + self.semicolon
        self._write_gams_line(line)
        line = "node_p_max(n) = node_data(n,'p_max')" + self.semicolon
        self._write_gams_line(line)
        self._write_gams_line("node_q_min(n) = node_data(n,'flow_min') ; ")
        self._write_gams_line("node_q_max(n) = node_data(n,'flow_max') ; ")


    def _write_gams_line_arc_data(self, pipe_data, cs_data):
        """Writing all arc specific data in GAMS compatible format."""
        self._write_gams_line("alias (*,uni);")

        self._write_gams_line("Table arc_data(*,n,m,*)")
        self._write_gams_line("\t\t\t\t\t\t\t\t\t\tflow_min\t\tflow_max")
        for arc_id, pipe in pipe_data.items():
            table_line = "\t" + pipe.arc_id.ljust(20) + "\t." + pipe.from_node.ljust(20) + "\t." + pipe.to_node.ljust(20) + "\t" + str(pipe.flow_min).ljust(20) + "\t" + str(pipe.flow_max).ljust(20)
            self._write_gams_line(table_line)
        for arc_id, cs in cs_data.items():
            table_line = "\t" + cs.arc_id.ljust(20) + "\t." + cs.from_node.ljust(20) + "\t." + cs.to_node.ljust(20) + "\t" + str(cs.flow_min).ljust(20) + "\t" + str(cs.flow_max).ljust(20)
            self._write_gams_line(table_line)
        self._write_gams_line(";")
        self._write_gams_line("arc(n,m) = sum(uni, arc_data(uni,n,m,'flow_min'));")
        self._write_gams_line("arc_flow_min(arc) = sum(uni, arc_data(uni,arc,'flow_min'));")
        self._write_gams_line("arc_flow_max(arc) = sum(uni, arc_data(uni,arc,'flow_max'));")
        
        self._write_gams_line("Table pipe_data(*,n,m,*)")
        self._write_gams_line("\t\t\t\t\t\t\t\t\t\tlength\t\t\tdiameter\t\troughness")
        for arc_id, pipe in pipe_data.items():
            table_line = "\t" + pipe.arc_id.ljust(20) + "\t." + pipe.from_node.ljust(20) + "\t." + pipe.to_node.ljust(20) + "\t" + str(1e3*pipe.length).ljust(20) + "\t" + str(1e-3*pipe.diameter).ljust(20) + "\t" + str(1e-3*pipe.roughness).ljust(20)
            self._write_gams_line(table_line)
        self._write_gams_line(";")
        self._write_gams_line("pipe(n,m) = sum(uni, pipe_data(uni,n,m,'length'));")
        self._write_gams_line("pipe_length(pipe) = sum(uni, pipe_data(uni,pipe,'length'));")
        self._write_gams_line("pipe_diameter(pipe) = sum(uni, pipe_data(uni,pipe,'diameter'));")
        self._write_gams_line("pipe_roughness(pipe) = sum(uni, pipe_data(uni,pipe,'roughness'));")
        
        self._write_gams_line("Table cs_data(*,n,m,*)")
        self._write_gams_line("\t\t\t\t\t\t\t\t\t\tmin_p_in\t\tmax_p_out\t\tmin_p_inc\t\tmax_p_inc\t\tmin_p_ratio\t\tmax_p_ratio")
        for arc_id, cs in cs_data.items():
            table_line = "\t" + cs.arc_id.ljust(20) + "\t." + cs.from_node.ljust(20) + "\t." + cs.to_node.ljust(20) + "\t" + str(cs.pressure_in_min).ljust(20) + "\t" + str(cs.pressure_out_max).ljust(20) + "\t" + str(cs.min_pressure_increase).ljust(20) + "\t" + str(cs.max_pressure_increase).ljust(20) + "\t" + str(cs.min_pressure_ratio).ljust(20) + "\t" + str(cs.max_pressure_ratio).ljust(20)
            self._write_gams_line(table_line)
        self._write_gams_line(";")
        self._write_gams_line("cs(n,m) = sum(uni, cs_data(uni,n,m,'min_p_in'));")
        self._write_gams_line("cs_min_p_in(cs) = sum(uni, cs_data(uni,cs,'min_p_in'));")
        self._write_gams_line("cs_max_p_out(cs) = sum(uni, cs_data(uni,cs,'max_p_out'));")
        self._write_gams_line("cs_min_p_inc(cs) = sum(uni, cs_data(uni,cs,'min_p_inc'));")
        self._write_gams_line("cs_max_p_inc(cs) = sum(uni, cs_data(uni,cs,'max_p_inc'));")
        self._write_gams_line("cs_min_p_ratio(cs) = sum(uni, cs_data(uni,cs,'min_p_ratio'));")
        self._write_gams_line("cs_max_p_ratio(cs) = sum(uni, cs_data(uni,cs,'max_p_ratio'));")

    def _write_gams_line(self, line):
        """Writing the given line to the GAMS data file."""
        self.gams_data_file.write(line + "\n")


