import zlib
import ujson
import time
import psutil
from typing import List
from objects import Job
import core


tic = time.perf_counter()
jobs: List[bytes] = core.loadJobsFromFile(core.init("All", "data/"))
print("Time taken: {}".format(time.perf_counter() - tic))
print(psutil.virtual_memory().percent)
