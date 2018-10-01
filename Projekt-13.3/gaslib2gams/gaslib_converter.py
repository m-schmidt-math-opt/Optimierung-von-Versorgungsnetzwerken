# Global imports
import argparse

# Local imports
from gaslib_parser import GasLibParser
from gams_data_writer import GamsDataWriter

class GasLibConverter(object):
    """
    GasLib to GAMS converter.
    """

    def __init__(self, net_file, scn_file, gams_data_file):
        """Constructor."""
        self.net_file = net_file
        self.scn_file = scn_file
        self.gams_data_file = gams_data_file
        self.gaslib_parser = GasLibParser(self.net_file, self.scn_file)
        self.gams_data_writer = GamsDataWriter(self.gams_data_file)

    def parse_input_files(self):
        """Parsing of the GasLib .net file."""
        self.gaslib_parser.parse()

    def write_gams_data_file(self):
        """Writing the GAMS data file."""
        entry_data = self.gaslib_parser.entry_data
        exit_data = self.gaslib_parser.exit_data
        innode_data = self.gaslib_parser.innode_data
        pipe_data = self.gaslib_parser.pipe_data
        cs_data = self.gaslib_parser.compressor_station_data
        self.gams_data_writer.write(entry_data, exit_data, innode_data, pipe_data, cs_data)

    
def main():
    """Main function."""

    # configure command line argument parser
    parser = argparse.ArgumentParser(description='GasLib to GAMS data Converter.')
    parser.add_argument("gaslib_net_filename", help="GasLib network description filename.")
    parser.add_argument("gaslib_scn_filename", help="GasLib scenario description filename.")
    parser.add_argument("gams_data_filename", help="GAMS data filename.")
    args = parser.parse_args()

    with open(args.gaslib_net_filename, 'r') as gaslib_net_file:
        with open(args.gaslib_scn_filename, 'r') as gaslib_scn_file:
            with open(args.gams_data_filename, 'w') as gams_data_file:
                gaslib_converter = GasLibConverter(gaslib_net_file, gaslib_scn_file, gams_data_file)
                gaslib_converter.parse_input_files()
                gaslib_converter.write_gams_data_file()

            
if __name__ == "__main__":
    main()

        
        
