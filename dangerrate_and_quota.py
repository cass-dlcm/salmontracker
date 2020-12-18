import core
import matplotlib.pyplot as plt
import numpy
from typing import List, cast, Union
import jsonlines
import ujson
import gzip


if __name__ == "__main__":
    with gzip.open("data/salmonAll.jl.gz") as reader:
        dangerRates: List[float] = []
        quotas: List[float] = []
        count = 0
        for job in jsonlines.Reader(reader, ujson.loads):
            dangerRates.append(float(core.getValMultiDimensional(job, cast(List[Union[str, int]], ["danger_rate"]))))
            quotas.append(float(core.getValMultiDimensional(job, cast(List[Union[str, int]], ["quota", 2]))))
            count += 1
    plt.figure(1)
    plt.scatter(quotas, dangerRates)
    m, b = numpy.polyfit(quotas, dangerRates, 1)
    y: List[float] = [x * m + b for x in quotas]
    plt.plot(quotas, y)
    plt.xlabel("Wave 3 Quota")
    plt.ylabel("Hazard Level")
    print(count)
    plt.show()
