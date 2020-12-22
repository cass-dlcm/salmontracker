import sys

sys.path.insert(0, ".")
import core
from core import locale
import numpy as np
from scipy.stats import ttest_ind
from typing import List, cast, Tuple
import matplotlib.pyplot as plt
import jsonlines
import ujson
import gzip
import filters

if __name__ == "__main__":
    data = core.init("All")
    stageList: List[str] = []
    with gzip.open(data) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            if job["stage"] is not None:
                if not (job["stage"]["name"][locale] in stageList):
                    stageList.append(job["stage"]["name"][locale])
    listOfFiles: List[Tuple[str, str]] = []
    for stage in stageList:
        listOfFiles.append(filters.onStages(data, [stage]))
    with open("reports/stages.txt", "w", encoding="utf-8") as writer:
        i: int = 1
        for stageFiles in listOfFiles:
            plt.figure(i)
            withVal: str = stageFiles[0]
            withoutVal: str = stageFiles[1]
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
            with gzip.open(withVal) as reader:
                for job in jsonlines.Reader(reader, ujson.loads):
                    withValClearWaves.append(float(job["clear_waves"]))
                    withValDangerRate.append(float(job["danger_rate"]))
                    withValGoldenTotal.append(
                        float(job["my_data"]["golden_egg_delivered"])
                    )
                    withValPowerTotal.append(
                        float(job["my_data"]["power_egg_collected"])
                    )
            with gzip.open(withoutVal) as reader:
                for job in jsonlines.Reader(reader, ujson.loads):
                    withoutValClearWaves.append(float(job["clear_waves"]))
                    withoutValDangerRate.append(float(job["danger_rate"]))
                    withoutValGoldenTotal.append(
                        float(job["my_data"]["golden_egg_delivered"])
                    )
                    withoutValPowerTotal.append(
                        float(job["my_data"]["power_egg_collected"])
                    )
            with gzip.open(data) as reader:
                for job in jsonlines.Reader(reader, ujson.loads):
                    clearWaves.append(float(job["clear_waves"]))
                    dangerRate.append(float(job["danger_rate"]))
                    goldenTotal.append(float(job["my_data"]["golden_egg_delivered"]))
                    powerTotal.append(float(job["my_data"]["power_egg_collected"]))
            diffMeansClearWaves: float = np.mean(withValClearWaves) - np.mean(
                withoutValClearWaves
            )
            t, p = ttest_ind(withValClearWaves, withoutValClearWaves, equal_var=False)
            writer.write(withVal + "\n")
            writer.write(withoutVal + "\n")
            writer.write("n_1 = " + str(len(withValClearWaves)) + "\n")
            writer.write("n_2 = " + str(len(withoutValClearWaves)) + "\n")
            writer.write("\n")
            writer.write("x\u0304_1 - x\u0304_2 = " + str(diffMeansClearWaves) + "\n")
            writer.write("d = " + str(diffMeansClearWaves / np.std(clearWaves)) + "\n")
            writer.write("t = " + str(t) + "\n")
            writer.write("p = " + str(p) + "\n")
            writer.write("\n")
            t, p = ttest_ind(withValDangerRate, withoutValDangerRate, equal_var=False)
            plt.subplot(321)
            plt.hist(withValDangerRate, density=True)
            plt.xlabel("Danger Rate")
            plt.ylabel("Probability")
            plt.subplot(322)
            plt.hist(withoutValDangerRate, density=True)
            plt.xlabel("Danger Rate")
            plt.ylabel("Probability")
            diffMeansDangerRate: float = np.mean(withValDangerRate) - np.mean(
                withoutValDangerRate
            )
            writer.write("x\u0304_1 - x\u0304_2 = " + str(diffMeansDangerRate) + "\n")
            writer.write("d = " + str(diffMeansDangerRate / np.std(dangerRate)) + "\n")
            writer.write("t = " + str(t) + "\n")
            writer.write("p = " + str(p) + "\n")
            writer.write("\n")
            t, p = ttest_ind(withValGoldenTotal, withoutValGoldenTotal, equal_var=False)
            plt.subplot(323)
            plt.hist(withValGoldenTotal, density=True)
            plt.xlabel("Golden Eggs")
            plt.ylabel("Probability")
            plt.subplot(324)
            plt.hist(withoutValGoldenTotal, density=True)
            plt.xlabel("Golden Eggs")
            plt.ylabel("Probability")
            diffMeansGoldenTotal: float = np.mean(withValGoldenTotal) - np.mean(
                withoutValGoldenTotal
            )
            writer.write("x\u0304_1 - x\u0304_2 = " + str(diffMeansGoldenTotal) + "\n")
            writer.write(
                "d = " + str(diffMeansGoldenTotal / np.std(goldenTotal)) + "\n"
            )
            writer.write("t = " + str(t) + "\n")
            writer.write("p = " + str(p) + "\n")
            writer.write("\n")
            t, p = ttest_ind(withValPowerTotal, withoutValPowerTotal, equal_var=False)
            plt.subplot(325)
            plt.hist(withValPowerTotal, density=True)
            plt.xlabel("Power Eggs")
            plt.ylabel("Probability")
            plt.subplot(326)
            plt.hist(withoutValPowerTotal, density=True)
            plt.xlabel("Power Eggs")
            plt.ylabel("Probability")
            diffMeansPowerTotal: float = np.mean(withValGoldenTotal) - np.mean(
                withoutValGoldenTotal
            )
            writer.write("x\u0304_1 - x\u0304_2 = " + str(diffMeansPowerTotal) + "\n")
            writer.write("d = " + str(diffMeansPowerTotal / np.std(powerTotal)) + "\n")
            writer.write("t = " + str(t) + "\n")
            writer.write("p = " + str(p) + "\n")
            writer.write("\n")
            i += 1
    plt.show()
