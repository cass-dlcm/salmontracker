from salmontracker import init, fetchNew, findPlayerIdByName, hasPlayer, withoutPlayer, getArrayOfStat, getArrayOfStat2D
from scipy.stats import ttest_ind
import numpy as np
import matplotlib.pyplot as plt

data = init()
playerId = findPlayerIdByName(data, input("Enter a player name to run analysis on: "))
withPlayer = list(filter(hasPlayer(playerId[0]), data))
withoutPlayer = list(filter(withoutPlayer(playerId[0]), data))
withPlayerClearWaves = getArrayOfStat(withPlayer, "clear_waves")
withoutPlayerClearWaves = getArrayOfStat(withoutPlayer, "clear_waves")
t, p = ttest_ind(withPlayerClearWaves, withoutPlayerClearWaves, equal_var=False)
print("a - b = " + str(np.mean(withPlayerClearWaves) - np.mean(withoutPlayerClearWaves)))
print("t = " + str(t))
print("p = " + str(p))
print()
withPlayerDangerRate = getArrayOfStat(withPlayer, "danger_rate")
withoutPlayerDangerRate = getArrayOfStat(withoutPlayer, "danger_rate")
t, p = ttest_ind(withPlayerDangerRate, withoutPlayerDangerRate, equal_var=False)
plt.figure(1)
plt.subplot(121)
plt.hist(withPlayerDangerRate, density=True)
plt.xlabel('Danger Rate')
plt.ylabel('Probability')
plt.subplot(122)
plt.hist(withoutPlayerDangerRate, density=True)
plt.xlabel('Danger Rate')
plt.ylabel('Probability')
print("a - b = " + str(np.mean(withPlayerDangerRate) - np.mean(withoutPlayerDangerRate)))
print("t = " + str(t))
print("p = " + str(p))
print()
withPlayerGoldenTotal = getArrayOfStat2D(withPlayer, "my_data", "golden_egg_delivered")
withoutPlayerGoldenTotal = getArrayOfStat2D(withoutPlayer, "my_data", "golden_egg_delivered")
t, p = ttest_ind(withPlayerGoldenTotal, withoutPlayerGoldenTotal, equal_var=False)
plt.figure(2)
plt.subplot(121)
plt.hist(withPlayerGoldenTotal, density=True)
plt.xlabel('Golden Eggs')
plt.ylabel('Probability')
plt.subplot(122)
plt.hist(withoutPlayerGoldenTotal, density=True)
plt.xlabel('Golden Eggs')
plt.ylabel('Probability')
print("a - b = " + str(np.mean(withPlayerGoldenTotal) - np.mean(withoutPlayerGoldenTotal)))
print("t = " + str(t))
print("p = " + str(p))
print()
withPlayerPowerTotal = getArrayOfStat2D(withPlayer, "my_data", "power_egg_collected")
withoutPlayerPowerTotal = getArrayOfStat2D(withoutPlayer, "my_data", "power_egg_collected")
t, p = ttest_ind(withPlayerPowerTotal, withoutPlayerPowerTotal, equal_var=False)
plt.figure(3)
plt.subplot(121)
plt.hist(withPlayerPowerTotal, density=True)
plt.xlabel('Power Eggs')
plt.ylabel('Probability')
plt.subplot(122)
plt.hist(withoutPlayerPowerTotal, density=True)
plt.xlabel('Power Eggs')
plt.ylabel('Probability')
print("a - b = " + str(np.mean(withPlayerPowerTotal) - np.mean(withoutPlayerPowerTotal)))
print("t = " + str(t))
print("p = " + str(p))
print()
plt.show()