import sys

sys.path.insert(0, ".")
import core
from objects import Job
import matplotlib.pyplot as plt
import numpy
from typing import List, cast, Union, Tuple
import jsonlines
import ujson
import gzip


if __name__ == "__main__":
    core.init("All")
    with gzip.open("data/salmonAll.jl.gz") as reader:
        dangerRates: List[float] = []
        quotas: Tuple[List[float], List[float], List[float]] = ([], [], [])
        count = 0
        for line in reader:
            job = Job(**ujson.loads(line))
            dangerRates.append(float(job.danger_rate))
            quotas[0].append(float(job.quota[0]))
            quotas[1].append(float(job.quota[1]))
            quotas[2].append(float(job.quota[2]))
            count += 1
    plt.figure(1)
    plt.subplot(131)
    plt.scatter(dangerRates, quotas[0])
    m, b = numpy.polyfit(dangerRates, quotas[0], 1)
    y: List[float] = [x * m + b for x in dangerRates]
    print("y = {}x + {}".format(m, b))
    plt.plot(dangerRates, y)
    plt.xlabel("Hazard Level")
    plt.ylabel("Wave 1 Quota")
    plt.yticks(list(range(3, 22)))
    plt.subplot(132)
    plt.scatter(dangerRates, quotas[1])
    m, b = numpy.polyfit(dangerRates, quotas[1], 1)
    y = [x * m + b for x in dangerRates]
    print("y = {}x + {}".format(m, b))
    plt.plot(dangerRates, y)
    plt.xlabel("Hazard Level")
    plt.ylabel("Wave 2 Quota")
    plt.yticks(list(range(4, 24)))
    plt.subplot(133)
    plt.scatter(dangerRates, quotas[2])
    m, b = numpy.polyfit(dangerRates, quotas[2], 1)
    y = [x * m + b for x in dangerRates]
    print("y = {}x + {}".format(m, b))
    plt.plot(dangerRates, y)
    plt.xlabel("Hazard Level")
    plt.ylabel("Wave 3 Quota")
    plt.yticks(list(range(5, 26)))
    print(count)
    plt.show()
