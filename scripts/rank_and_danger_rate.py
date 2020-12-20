import sys

sys.path.insert(0, ".")
import core
import matplotlib.pyplot as plt
import numpy
from typing import List, cast, Union, Tuple
import jsonlines
import ujson
import gzip

if __name__ == "__main__":
    data = "data/salmonAll.jl.gz"  # core.init("All")
    x = []
    y = []
    with gzip.open(data) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            if "title" in job and "title_exp" in job and job["title"] is not None:
                x.append(job["title"]["splatnet"] * 100 + job["title_exp"])
                y.append(float(job["danger_rate"]))
    plt.scatter(x, y)
    plt.xlabel("Rank")
    plt.ylabel("Hazard Level")
    log_x = numpy.log(x)
    m, b = numpy.polyfit(log_x, y, 1)
    y_equation = list(sorted([x_val * m + b for x_val in log_x]))
    print("y = {}log(x) + {}".format(m, b))
    plt.plot(list(sorted(x)), y_equation)
    plt.show()
