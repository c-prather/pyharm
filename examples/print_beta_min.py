#!/usr/bin/env python3

import sys
import numpy as np
import pyharm

dump = pyharm.load_dump(sys.argv[1])

Pg_max = np.max(dump['Pg'])
print("Gas pressure max: ", np.max(dump['Pg']))
Pb_max = np.max(dump['Pb'])
print("Mag. pressure max: ", np.max(dump['Pb']))
print("beta_min: ", Pg_max/Pb_max)
