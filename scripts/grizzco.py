import sys

sys.path.insert(0, ".")
import core
import numpy as np
from scipy.stats import ttest_ind
from typing import List, cast, Union, Tuple
import matplotlib.pyplot as plt
import jsonlines
import ujson
import gzip
import filters

if __name__ == "__main__":
    data = core.init("All")
    grizzcoRotationsInts: List[int] = core.findRotationByWeaponsAndStage(
        data,
        weapons=(
            "Grizzco Charger",
            "Grizzco Blaster",
            "Grizzco Brella",
            "Grizzco Slosher",
        ),
    )
    result = filters.duringRotationInts(data, grizzcoRotationsInts, "or")
    withVal: str = result[0]
    withoutVal: str = result[1]
    withValClearWaves: List[float] = []
    withValDangerRate: List[float] = []
    withValGoldenTotal: List[float] = []
    withValPowerTotal: List[float] = []
    withoutValClearWaves: List[float] = []
    withoutValDangerRate: List[float] = []
    withoutValGoldenTotal: List[float] = []
    withoutValPowerTotal: List[float] = []
    with gzip.open(withVal) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            withValClearWaves.append(float(job["clear_waves"]))
            withValDangerRate.append(float(job["danger_rate"]))
            withValGoldenTotal.append(float(job["my_data"]["golden_egg_delivered"]))
            withValPowerTotal.append(float(job["my_data"]["power_egg_collected"]))
    with gzip.open(withoutVal) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            withoutValClearWaves.append(float(job["clear_waves"]))
            withoutValDangerRate.append(float(job["danger_rate"]))
            withoutValGoldenTotal.append(float(job["my_data"]["golden_egg_delivered"]))
            withoutValPowerTotal.append(float(job["my_data"]["power_egg_collected"]))
    t, p = ttest_ind(withValClearWaves, withoutValClearWaves, equal_var=False)
    print("a - b = " + str(np.mean(withValClearWaves) - np.mean(withoutValClearWaves)))
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
    print("a - b = " + str(np.mean(withValDangerRate) - np.mean(withoutValDangerRate)))
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
    print(
        "a - b = " + str(np.mean(withValGoldenTotal) - np.mean(withoutValGoldenTotal))
    )
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
    print("a - b = " + str(np.mean(withValPowerTotal) - np.mean(withoutValPowerTotal)))
    print("t = " + str(t))
    print("p = " + str(p))
    print()
    plt.show()
