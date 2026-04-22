#!/usr/bin/env python3

import sys
import numpy as np
import pyharm

for dumpname in sys.argv[1:]:

    dump = pyharm.load_dump(dumpname)
    print("Dump ", dumpname)

    Pg_max = np.max(dump['Pg'])
    print("Gas pressure max: ", Pg_max)
    Pb_max = np.max(dump['Pb'])
    print("Mag. pressure max: ", Pb_max)
    print("beta_min: ", Pg_max/Pb_max)

    print("sigma_max: ", np.max(dump['bsq'] / dump['rho']))
    print("global_sig_ratio", np.max(dump['bsq']) / np.max(dump['rho']))
