from salmontracker import init, getArrayOfStat, getArrayOfStat2D
import matplotlib.pyplot as plt
import numpy

data = init()
dangerRates = getArrayOfStat(data, "danger_rate")
quotas = getArrayOfStat2D(data, "quota", 2)
plt.figure(1)
plt.scatter(quotas, dangerRates)
m, b = numpy.polyfit(quotas, dangerRates, 1)
y = []
for i in quotas:
    y.append(i * m + b)
plt.plot(quotas, y)
plt.show()
