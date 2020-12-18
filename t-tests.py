from core import (
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
import sys
import json
from typing import List, Union, Tuple

initUser(json.load(open("keys.json", "r"))["statink_key"])
path: str = "data/"
data: str = "salmon.jsonl"
print("Rotation")
print("Player")
print("Weapon")
print("Stage")
stat: str = input("Choose a stat to run analysis on: ")
withVal: Tuple[str, str] = ("", "")
withoutVal: Tuple[str, str] = ("", "")
if stat == "Player":
    playerId: List[str] = findPlayerIdByName(
        path, data, input("Enter a player name to run analysis on: ")
    )
    print(playerId)
    val: str = playerId[int(input("Pick the player id by index: "))]
    withVal = hasPlayer(path, data, val)
    withoutVal = withoutPlayer(path, data, val)
elif stat == "Rotation":
    weapons: List[str] = []
    for i in range(0, 4):
        weapons.append(input("Enter a weapon: "))
    stageChoice: str = input("Enter the stage: ")
    rotations: List[int] = findRotationByWeaponsAndStage(
        path + data, weapons, stageChoice
    )
    print(rotations)
    rot: int = rotations[int(input("Pick the rotation id by index: "))]
    withVal = duringRotationInt(path, data, rot)
    withoutVal = notDuringRotationInt(path, data, rot)
elif stat == "Weapon":
    val = input("Enter a weapon: ")
    withVal = hasWeapon(path, data, val)
    withoutVal = doesntHaveWeapon(path, data, val)
elif stat == "Stage":
    val = input("Enter a stage: ")
    withVal = onStage(path, data, val)
    withoutVal = notOnStage(path, data, val)
else:
    sys.exit()
withValClearWaves: List[float] = getArrayOfStat(withVal[0] + withVal[1], "clear_waves")
withoutValClearWaves: List[float] = getArrayOfStat(
    withoutVal[0] + withoutVal[1], "clear_waves"
)
t, p = ttest_ind(withValClearWaves, withoutValClearWaves, equal_var=False)
print("a - b = " + str(np.mean(withValClearWaves) - np.mean(withoutValClearWaves)))
print("t = " + str(t))
print("p = " + str(p))
print()
withValDangerRate: List[float] = getArrayOfStat(withVal[0] + withVal[1], "danger_rate")
withoutValDangerRate: List[float] = getArrayOfStat(
    withoutVal[0] + withoutVal[1], "danger_rate"
)
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
withValGoldenTotal: List[float] = getArrayOfStat2D(
    withVal[0] + withVal[1], "my_data", "golden_egg_delivered"
)
withoutValGoldenTotal: List[float] = getArrayOfStat2D(
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
withValPowerTotal: List[float] = getArrayOfStat2D(
    withVal[0] + withVal[1], "my_data", "power_egg_collected"
)
withoutValPowerTotal: List[float] = getArrayOfStat2D(
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
