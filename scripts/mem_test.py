import sys

sys.path.insert(0, ".")
import core
from objects import Job
import ujson
import gzip
from typing import List
import psutil
import time

if __name__ == "__main__":
    tic = time.perf_counter()
    jobs: List[Job] = []
    with gzip.open("data/salmonAll.jl.gz", "r") as reader:
        for line in reader:
            jobs.append(Job(**ujson.loads(line)))
    print("Time taken: {}".format(time.perf_counter() - tic))
    print(psutil.virtual_memory().percent)
