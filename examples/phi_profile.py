#!/usr/bin/env python3

import sys
import numpy as np
import pyharm
from pyharm.ana import reductions
from matplotlib import pyplot as plt

dump = pyharm.load_dump(sys.argv[1])

fig, ax = plt.subplots(1,1, figsize=(10,10))
phi_at = 0.5 * reductions.shell_sum(dump, 'abs_B1')
plt.plot(dump['r1d'], phi_at)
plt.xlim(0, 50.)
fig.savefig('phi_profile.png')
