###########################################################################
#              This file is part of the program and library               #
#                                                                         #
#                        Electricity Network Lib                          #
#                                                                         #
# Copyright (C) 2015                                                      #
# Friedrich-Alexander-Universitaet Erlangen-Nuremberg                     #
# Discrete Optimization                                                   #
# Contact: Martin Schmidt (mar.schmidt@fau.de)                            #
#          Lars Schewe (lars.schewe@math.uni-erlangen.de)                 #
# All rights reserved.                                                    #
###########################################################################

# Global imports
from collections import namedtuple

# Local imports
from arc import Arc


class CompressorStation(namedtuple('CompressorStationNamedTuple',
                                   Arc._fields
                                   + ('pressure_in_min',
                                      'pressure_out_max',
                                      'max_pressure_increase',
                                      'max_pressure_ratio',
                                      'min_pressure_increase',
                                      'min_pressure_ratio'))):
    """
    Compressor station of a gas transport network.
    Realized by inheritance from a suitable namedtuple.
    """
