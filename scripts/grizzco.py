import sys

sys.path.insert(0, ".")
import core
import numpy
from typing import List, cast, Union, Tuple
import jsonlines
import ujson
import gzip

if __name__ == "__main__":
    data = "data/salmonAll.jl.gz"  # core.init("All")
