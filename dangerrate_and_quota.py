from salmontracker import initUser, getArrayOfStat, getArrayOfStat2D
import matplotlib.pyplot as plt
import numpy

initUser()
path = "data/"
data = "salmon.jsonl"
dangerRates = getArrayOfStat(path + data, "danger_rate")
quotas = getArrayOfStat2D(path + data, "quota", 2)
plt.figure(1)
plt.scatter(quotas, dangerRates)
m, b = numpy.polyfit(quotas, dangerRates, 1)
y = []
for i in quotas:
    y.append(i * m + b)
plt.plot(quotas, y)
plt.xlabel('Wave 3 Quota')
plt.ylabel('Hazard Level')
plt.show()
