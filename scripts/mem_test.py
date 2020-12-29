import gzip
import zlib
import ujson
import time
import psutil
from typing import List
from objects import Job
import core


with gzip.open(core.init("All", "data/"), "r") as reader:
    tic = time.perf_counter()
    jobs: List[bytes] = []
    for line in reader:
        jobs.append(zlib.compress(line))
    print("Time taken: {}".format(time.perf_counter() - tic))
    print(psutil.virtual_memory().percent)
