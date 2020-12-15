from salmontracker import (
    initUser,
    findPlayerIdByName,
    hasPlayer,
    withoutPlayer,
    findRotationByWeaponsAndStage,
    duringRotationInt,
    notDuringRotationInt,
    hasWeapon,
    doesntHaveWeapon,
    onStage,
    notOnStage,
    getArrayOfStat,
    getArrayOfStat2D,
)
from scipy.stats import ttest_ind
import numpy as np
import matplotlib.pyplot as plt

initUser()
path = "data/"
data = "salmon.jsonl"
print("Rotation")
print("Player")
print("Weapon")
print("Stage")
stat = input("Choose a stat to run analysis on: ")
val = ""
withVal = []
withoutVal = []
if stat == "Player":
    playerId = findPlayerIdByName(
        path, data, input("Enter a player name to run analysis on: ")
    )
    print(playerId)
    val = playerId[int(input("Pick the player id by index: "))]
    withVal = hasPlayer(path, data, val)
    withoutVal = withoutPlayer(path, data, val)
elif stat == "Rotation":
    weapons = []
    for i in range(0, 4):
        weapons.append(input("Enter a weapon: "))
    stageChoice = input("Enter the stage: ")
    rotations = findRotationByWeaponsAndStage(path + data, weapons, stageChoice)
    print(rotations)
    val = rotations[int(input("Pick the rotation id by index: "))]
    withVal = duringRotationInt(path, data, val)
    withoutVal = notDuringRotationInt(path, data, val)
elif stat == "Weapon":
    val = input("Enter a weapon: ")
    withVal = hasWeapon(path, data, val)
    withoutVal = doesntHaveWeapon(path, data, val)
elif stat == "Stage":
    val = input("Enter a stage: ")
    withVal = onStage(path, data, val)
    withoutVal = notOnStage(path, data, val)
else:
    exit()
withValClearWaves = getArrayOfStat(withVal[0] + withVal[1], "clear_waves")
withoutValClearWaves = getArrayOfStat(withoutVal[0] + withoutVal[1], "clear_waves")
t, p = ttest_ind(withValClearWaves, withoutValClearWaves, equal_var=False)
print("a - b = " + str(np.mean(withValClearWaves) - np.mean(withoutValClearWaves)))
print("t = " + str(t))
print("p = " + str(p))
print()
withValDangerRate = getArrayOfStat(withVal[0] + withVal[1], "danger_rate")
withoutValDangerRate = getArrayOfStat(withoutVal[0] + withoutVal[1], "danger_rate")
t, p = ttest_ind(withValDangerRate, withoutValDangerRate, equal_var=False)
plt.figure(1)
plt.subplot(121)
plt.hist(withValDangerRate, density=True)
plt.xlabel("Danger Rate")
plt.ylabel("Probability")
plt.subplot(122)
plt.hist(withoutValDangerRate, density=True)
plt.xlabel("Danger Rate")
plt.ylabel("Probability")
print("a - b = " + str(np.mean(withValDangerRate) - np.mean(withoutValDangerRate)))
print("t = " + str(t))
print("p = " + str(p))
print()
withValGoldenTotal = getArrayOfStat2D(
    withVal[0] + withVal[1], "my_data", "golden_egg_delivered"
)
withoutValGoldenTotal = getArrayOfStat2D(
    withoutVal[0] + withoutVal[1], "my_data", "golden_egg_delivered"
)
t, p = ttest_ind(withValGoldenTotal, withoutValGoldenTotal, equal_var=False)
plt.figure(2)
plt.subplot(121)
plt.hist(withValGoldenTotal, density=True)
plt.xlabel("Golden Eggs")
plt.ylabel("Probability")
plt.subplot(122)
plt.hist(withoutValGoldenTotal, density=True)
plt.xlabel("Golden Eggs")
plt.ylabel("Probability")
print("a - b = " + str(np.mean(withValGoldenTotal) - np.mean(withoutValGoldenTotal)))
print("t = " + str(t))
print("p = " + str(p))
print()
withValPowerTotal = getArrayOfStat2D(
    withVal[0] + withVal[1], "my_data", "power_egg_collected"
)
withoutValPowerTotal = getArrayOfStat2D(
    withoutVal[0] + withoutVal[1], "my_data", "power_egg_collected"
)
t, p = ttest_ind(withValPowerTotal, withoutValPowerTotal, equal_var=False)
plt.figure(3)
plt.subplot(121)
plt.hist(withValPowerTotal, density=True)
plt.xlabel("Power Eggs")
plt.ylabel("Probability")
plt.subplot(122)
plt.hist(withoutValPowerTotal, density=True)
plt.xlabel("Power Eggs")
plt.ylabel("Probability")
print("a - b = " + str(np.mean(withValPowerTotal) - np.mean(withoutValPowerTotal)))
print("t = " + str(t))
print("p = " + str(p))
print()
plt.show()
