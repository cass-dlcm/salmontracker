import core
from objects import Job
import numpy as np
from scipy.stats import ttest_ind
from typing import List, cast, Tuple, Optional
import matplotlib.pyplot as plt
import ujson
import zlib
import filters

dataFile: str = "data/salmonAll.jl.gz"  # core.init("All", "data/")
data: Optional[List[bytes]] = core.loadJobsFromFile(dataFile)
grizzcoRotationsInts: List[int] = core.findRotationByWeaponsAndStage(
    "mem",
    cast(List[bytes], data),
    weapons=(
        "kuma_charger",
        "kuma_blaster",
        "kuma_brella",
        "kuma_slosher",
    ),
)
result: Tuple[List[bytes], List[bytes]] = cast(
    Tuple[List[bytes], List[bytes]],
    filters.duringRotationInts("mem", data, grizzcoRotationsInts, "or"),
)
data = None
withVal: List[bytes] = result[0]
withoutVal: List[bytes] = result[1]
withValClearWaves: List[float] = []
withValDangerRate: List[float] = []
withValGoldenTotal: List[float] = []
withValPowerTotal: List[float] = []
withoutValClearWaves: List[float] = []
withoutValDangerRate: List[float] = []
withoutValGoldenTotal: List[float] = []
withoutValPowerTotal: List[float] = []
clearWaves: List[float] = []
dangerRate: List[float] = []
goldenTotal: List[float] = []
powerTotal: List[float] = []
for line in withVal:
    job = Job(**ujson.loads(zlib.decompress(line)))
    withValClearWaves.append(float(job.clear_waves))
    clearWaves.append(float(job.clear_waves))
    withValDangerRate.append(float(job.danger_rate))
    dangerRate.append(float(job.danger_rate))
    withValGoldenTotal.append(float(job.my_data.golden_egg_delivered))
    goldenTotal.append(float(job.my_data.golden_egg_delivered))
    withValPowerTotal.append(float(job.my_data.power_egg_collected))
    powerTotal.append(float(job.my_data.power_egg_collected))
for line in withoutVal:
    job = Job(**ujson.loads(line))
    withoutValClearWaves.append(float(job.clear_waves))
    clearWaves.append(float(job.clear_waves))
    withoutValDangerRate.append(float(job.danger_rate))
    dangerRate.append(float(job.danger_rate))
    withoutValGoldenTotal.append(float(job.my_data.golden_egg_delivered))
    goldenTotal.append(float(job.my_data.golden_egg_delivered))
    withoutValPowerTotal.append(float(job.my_data.power_egg_collected))
    powerTotal.append(float(job.my_data.power_egg_collected))
t, p = ttest_ind(withValClearWaves, withoutValClearWaves, equal_var=False)
diffMeansClearWaves: float = np.mean(withValClearWaves) - np.mean(withoutValClearWaves)
print("n_1 = " + str(len(withValClearWaves)))
print("n_2 = " + str(len(withoutValClearWaves)))
print()
print("x\u0304_1 - x\u0304_2 = " + str(diffMeansClearWaves))
print("d = " + str(diffMeansClearWaves / np.std(clearWaves)))
print("t = " + str(t))
print("p = " + str(p))
print()
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
diffMeansDangerRate: float = np.mean(withValDangerRate) - np.mean(withoutValDangerRate)
print("x\u0304_1 - x\u0304_2 = " + str(diffMeansDangerRate))
print("d = " + str(diffMeansDangerRate / np.std(dangerRate)))
print("t = " + str(t))
print("p = " + str(p))
print()
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
diffMeansGoldenTotal: float = np.mean(withValGoldenTotal) - np.mean(
    withoutValGoldenTotal
)
print("x\u0304_1 - x\u0304_2 = " + str(diffMeansGoldenTotal))
print("d = " + str(diffMeansGoldenTotal / np.std(goldenTotal)))
print("t = " + str(t))
print("p = " + str(p))
print()
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
diffMeansPowerEggs = np.mean(withValPowerTotal) - np.mean(withoutValPowerTotal)
print("x\u0304_1 - x\u0304_2 = " + str(diffMeansPowerEggs))
print("d = " + str(diffMeansPowerEggs / np.std(powerTotal)))
print("t = " + str(t))
print("p = " + str(p))
print()
plt.show()
