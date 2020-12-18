from core import initUser, getArrayOfStat, getArrayOfStat2D
import matplotlib.pyplot as plt
import numpy
import json
from typing import List


initUser(json.load(open("keys.json", "r"))["statink_key"])
path: str = "data/"
data: str = "salmon.jsonl"
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
plt.show()
