import core
import sort_by_stat
from core import (
    findPlayerIdByName,
    findRotationByWeaponsAndStage,
)
from filters import (
    hasPlayers,
    hasWeapons,
    usesWeapons,
    onStages,
    withSpecial,
    duringRotationInts,
    dangerRate,
    clearWave,
)
import ujson
from typing import List, Tuple, cast
import sys
from scipy.stats import ttest_ind
import numpy as np
import matplotlib.pyplot as plt
import gzip


def filterBy(dataList: List[List[bytes]]) -> List[List[bytes]]:
    filters: List[List[bytes]] = []
    print()
    print("Rotation")
    print("Player")
    print("Has Weapon")
    print("Uses Weapon")
    print("Stage")
    print("Danger Rate")
    print("Clear Wave")
    print("Special")
    stat: str = input("Choose an attribute to run filter on: ")
    if stat == "Player":
        playerName: str = input("Enter a player name to run analysis on: ")
        playerId: List[str] = findPlayerIdByName("mem", dataList[0], playerName)
        print(playerId)
        val: str = playerId[int(input("Pick the player id by index: "))]
        mode: str = input("Choose whether you want [With/Without/Both]: ")
        for i in range(0, len(dataList)):
            if mode == "With":
                filters.append(
                    cast(List[bytes], hasPlayers("mem", dataList[i], [val])[0])
                )
            elif mode == "Without":
                filters.append(
                    cast(List[bytes], hasPlayers("mem", dataList[i], [val])[1])
                )
            elif mode == "Both":
                result: Tuple[List[bytes], List[bytes]] = cast(
                    Tuple[List[bytes], List[bytes]],
                    hasPlayers("mem", dataList[i], [val]),
                )
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
    elif stat == "Rotation":
        weapons: List[str] = []
        for i in range(0, 4):
            weapons.append(input("Enter a weapon: "))
        stageChoice: str = input("Enter the stage: ")
        rotations: List[int] = findRotationByWeaponsAndStage(
            "mem", dataList[0], weapons=weapons, stage=stageChoice
        )
        print(rotations)
        rot: int = rotations[int(input("Pick the rotation id by index: "))]
        mode = input("Choose whether you want [With/Without/Both]: ")
        for i in range(0, len(dataList)):
            if mode == "With":
                filters.append(
                    cast(List[bytes], duringRotationInts("mem", dataList[i], [rot])[0])
                )
            elif mode == "Without":
                filters.append(
                    cast(List[bytes], duringRotationInts("mem", dataList[i], [rot])[1])
                )
            elif mode == "Both":
                result = cast(
                    Tuple[List[bytes], List[bytes]],
                    duringRotationInts("mem", dataList[i], [rot]),
                )
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
    elif stat == "Has Weapon":
        val = input("Enter a weapon: ")
        mode = input("Choose whether you want [With/Without/Both]: ")
        for i in range(0, len(dataList)):
            if mode == "With":
                filters.append(
                    cast(List[bytes], hasWeapons("mem", dataList[i], [val])[0])
                )
            elif mode == "Without":
                filters.append(
                    cast(List[bytes], hasWeapons("mem", dataList[i], [val])[1])
                )
            elif mode == "Both":
                result = cast(
                    Tuple[List[bytes], List[bytes]],
                    hasWeapons("mem", dataList[i], [val]),
                )
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
    elif stat == "Uses Weapon":
        val = input("Enter a weapon: ")
        mode = input("Choose whether you want [With/Without/Both]: ")
        for i in range(0, len(dataList)):
            if mode == "With":
                filters.append(
                    cast(List[bytes], usesWeapons("mem", dataList[i], [val])[0])
                )
            elif mode == "Without":
                filters.append(
                    cast(List[bytes], usesWeapons("mem", dataList[i], [val])[1])
                )
            elif mode == "Both":
                result = cast(
                    Tuple[List[bytes], List[bytes]],
                    usesWeapons("mem", dataList[i], [val]),
                )
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
    elif stat == "Stage":
        val = input("Enter a stage: ")
        mode = input("Choose whether you want [With/Without/Both]: ")
        for i in range(0, len(dataList)):
            if mode == "With":
                filters.append(
                    cast(List[bytes], onStages("mem", dataList[i], [val])[0])
                )
            elif mode == "Without":
                filters.append(
                    cast(List[bytes], onStages("mem", dataList[i], [val])[1])
                )
            elif mode == "Both":
                result = cast(
                    Tuple[List[bytes], List[bytes]], onStages("mem", dataList[i], [val])
                )
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
    elif stat == "Danger Rate":
        comparison: str = input("Choose whether you want [=/>/<]: ")
        val = input("Enter the danger rate: ")
        mode = input("Choose whether you want [With/Without/Both]: ")
        for i in range(0, len(dataList)):
            if mode == "With":
                filters.append(
                    cast(
                        List[bytes], dangerRate("mem", dataList[i], val, comparison)[0]
                    )
                )
            elif mode == "Without":
                filters.append(
                    cast(
                        List[bytes], dangerRate("mem", dataList[i], val, comparison)[1]
                    )
                )
            elif mode == "Both":
                result = cast(
                    Tuple[List[bytes], List[bytes]],
                    dangerRate("mem", dataList[i], val, comparison),
                )
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
    elif stat == "Clear Wave":
        comparison = input("Choose whether you want [=/>/<]: ")
        wave: int = int(input("Enter the clear wave: "))
        mode = input("Choose whether you want [With/Without/Both]: ")
        for i in range(0, len(dataList)):
            if mode == "With":
                filters.append(
                    cast(
                        List[bytes], clearWave("mem", dataList[i], wave, comparison)[0]
                    )
                )
            elif mode == "Without":
                filters.append(
                    cast(
                        List[bytes], clearWave("mem", dataList[i], wave, comparison)[1]
                    )
                )
            elif mode == "Both":
                result = cast(
                    Tuple[List[bytes], List[bytes]],
                    clearWave("mem", dataList[i], wave, comparison),
                )
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
    elif stat == "Special":
        val = input("Enter the special: ")
        mode = input("Choose whether you want [With/Without/Both]: ")
        for i in range(0, len(dataList)):
            if mode == "With":
                filters.append(
                    cast(List[bytes], withSpecial("mem", dataList[i], val)[0])
                )
            elif mode == "Without":
                filters.append(
                    cast(List[bytes], withSpecial("mem", dataList[i], val)[0])
                )
            elif mode == "Both":
                result = cast(
                    Tuple[List[bytes], List[bytes]],
                    withSpecial("mem", dataList[i], val),
                )
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
    else:
        sys.exit()
    return filters


def printOverview(dataList: List[List[bytes]]):
    which: str = input("Would you like to print a [SpecificList/AllLists]: ")
    if which == "AllLists":
        for i in range(0, len(dataList)):
            print(core.getOverview("mem", dataList[i]))
    elif which == "SpecificList":
        for i in range(0, len(dataList)):
            print(dataList[i])
        chosenList: int = int(input("Which list (by index): "))
        print(core.getOverview("mem", dataList[chosenList]))
        print()
    else:
        sys.exit()


def printAllJobs(dataList):
    """
    :parem dataList:
    :type dataList: str
    """
    with gzip.open(dataList) as reader:
        for line in reader:
            job = Job(**ujson.loads(line))
            core.printGeneral(job)
            print()
            core.printWaves(job)
            print()
            core.printPlayers(job)
            print()
            core.printBosses(job)
            print()
            print()


def printJobs(dataList: List[List[bytes]]):
    which: str = input("Would you like to print from a SpecificList or AllLists: ")
    if which == "AllLists":
        for i in range(0, len(dataList)):
            printAllJobs(dataList[i])
    elif which == "SpecificList":
        for i in range(0, len(dataList)):
            print(dataList[i])
        chosenList: int = int(input("Which list (by index): "))
        printAllJobs(dataList[chosenList])
    else:
        sys.exit()


def hypothesisTesting(dataList: List[List[bytes]]):
    for i in range(0, len(dataList)):
        print(dataList[i])
    first: int = int(input("Which is the first list you'd like to use (by index): "))
    second: int = int(input("Which is the first list you'd like to use (by index): "))
    stat: str = input("Which stat would you like to test: ")
    firstStat: List[float] = core.getArrayOfStat("mem", dataList[first], stat)
    secondStat: List[float] = core.getArrayOfStat("mem", dataList[second], stat)
    t, p = ttest_ind(firstStat, secondStat, equal_var=False)
    print("a - b = " + str(np.mean(firstStat) - np.mean(secondStat)))
    print("t = " + str(t))
    print("p = " + str(p))
    plt.subplot(121)
    plt.hist(firstStat, density=True)
    plt.xlabel(stat)
    plt.ylabel("Probability")
    plt.subplot(122)
    plt.hist(secondStat, density=True)
    plt.xlabel(stat)
    plt.ylabel("Probability")
    plt.show()


def sortAttributeByStat(dataList: List[List[bytes]]):
    which: str = input("Would you like to print from a [SpecificList/AllLists]: ")
    stat: str = input("Enter a stat to sort by: ")
    mode: str = input("Pick a mode [Stage/Weapon/Rotation/Special]: ")
    if which == "AllLists":
        for i in range(0, len(dataList)):
            if mode == "Stage":
                sort_by_stat.sortStages(dataList[i], stat)
            elif mode == "Weapon":
                sort_by_stat.sortWeapons(dataList[i], stat)
            elif mode == "Rotation":
                sort_by_stat.sortRotation(dataList[i], stat)
            elif mode == "Special":
                sort_by_stat.sortSpecial(dataList[i], stat)
            else:
                sys.exit()
    elif which == "SpecificList":
        for i in range(0, len(dataList)):
            print(dataList[i])
        chosenList: int = int(input("Which list (by index): "))
        if mode == "Stage":
            sort_by_stat.sortStages(dataList[chosenList], stat)
        elif mode == "Weapon":
            sort_by_stat.sortWeapons(dataList[chosenList], stat)
        elif mode == "Rotation":
            sort_by_stat.sortRotation(dataList[chosenList], stat)
        elif mode == "Special":
            sort_by_stat.sortSpecial(dataList[chosenList], stat)
        else:
            sys.exit()
    else:
        sys.exit()


def waveClearPercentageWithWeapon(dataList: List[List[bytes]]):
    which: str = input("Would you like to print from [SpecificList/AllLists]: ")
    weapon: str = input("Enter a weapon to test: ")
    if which == "AllLists":
        for i in range(0, len(dataList)):
            print(
                weapon
                + ": "
                + str(core.waveClearPercentageWithWeapon("mem", dataList[i], weapon))
            )
    elif which == "SpecificList":
        for i in range(0, len(dataList)):
            print(dataList[i])
        chosenList = int(input("Which list (by index): "))
        core.waveClearPercentageWithWeapon("mem", dataList[chosenList], weapon)
        print()
    else:
        sys.exit()


def processData(dataList: List[List[bytes]]):
    print()
    print("PrintOverview")
    print("PrintJobs")
    print("HypothesisTesting")
    print("SortAttributeByStat")
    print("WaveClearPercentageWithWeapon")
    print("Quit")
    mode: str = input("What would you like to do: ")
    while mode != "Quit":
        if mode == "PrintOverview":
            printOverview(dataList)
        elif mode == "PrintJobs":
            printJobs(dataList)
        elif mode == "HypothesisTesting":
            hypothesisTesting(dataList)
        elif mode == "SortAttributeByStat":
            sortAttributeByStat(dataList)
        elif mode == "WaveClearPercentageWithWeapon":
            waveClearPercentageWithWeapon(dataList)
        else:
            sys.exit()
        print()
        print("PrintOverview")
        print("PrintJobs")
        print("HypothesisTesting")
        print("SortAttributeByStat")
        print("WaveClearPercentageWithWeapon")
        print("Quit")
        mode = input("What would you like to do: ")


if __name__ == "__main__":
    print("All")
    print("User")
    scope: str = input("Pick an analysis scope: ")
    dataFile: str = core.init(scope, ujson.load(open("keys.json", "r"))["statink_key"])
    data: List[List[bytes]] = [core.loadJobsFromFile(dataFile)]
    while input("Add a filter [Y/N]: ") == "Y":
        data = filterBy(data)
    processData(data)
