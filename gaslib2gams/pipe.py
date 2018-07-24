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


class Pipe(namedtuple('PipeNamedTuple',
                       Arc._fields
                       + ('length', 'diameter',
                          'roughness', 'pressure_max',
                          'heat_transfer_coefficient'))):
    """
    Pipe of a gas transport network.
    Realized by inheritance from a suitable namedtuple.
    """
