from core import initAll, getArrayOfStat, getArrayOfStat2D
import core
import matplotlib.pyplot as plt
import numpy
import ujson
from typing import List


if __name__ == "__main__":
    path: str = "data/"
    data: str = "salmonAll.jl.gz"
    dangerRates: List[float] = getArrayOfStat(path + data, "danger_rate")
    quotas: List[float] = getArrayOfStat2D(path + data, "quota", 2)
    plt.figure(1)
    plt.scatter(quotas, dangerRates)
    m, b = numpy.polyfit(quotas, dangerRates, 1)
    y: List[float] = []
    for i in quotas:
        y.append(i * m + b)
    plt.plot(quotas, y)
    plt.xlabel("Wave 3 Quota")
    plt.ylabel("Hazard Level")
    print(core.jobsCount(path + data))
    plt.show()
