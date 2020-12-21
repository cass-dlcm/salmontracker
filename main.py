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
    failReasons,
    duringRotationInts,
    dangerRate,
    clearWave,
)
import ujson
from typing import List, Tuple
import sys
import os
import jsonlines
from scipy.stats import ttest_ind
import numpy as np
import matplotlib.pyplot as plt
import gzip


def filterBy(dataFile: List[str]) -> List[str]:
    filters: List[str] = []
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
        playerId: List[str] = findPlayerIdByName(dataFile[0], playerName)
        print(playerId)
        val: str = playerId[int(input("Pick the player id by index: "))]
        mode: str = input("Choose whether you want [With/Without/Both]: ")
        clearAfter: str = input("Choose whether you would like to clear after [Y/N]: ")
        for i in range(0, len(dataFile)):
            if mode == "With":
                filters.append(hasPlayers(dataFile[i], [val])[0])
                os.remove(dataFile[i][:-6] + "/notplayer/" + val + ".jl.gz")
            elif mode == "Without":
                filters.append(hasPlayers(dataFile[i], [val])[1])
                os.remove(dataFile[i][:-6] + "/player/" + val + ".jl.gz")
            elif mode == "Both":
                result: Tuple[str, str] = hasPlayers(dataFile[i], [val])
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
            if clearAfter == "Y" and dataFile[i][:5] != "data/":
                os.remove(dataFile[i])
    elif stat == "Rotation":
        weapons: List[str] = []
        for i in range(0, 4):
            weapons.append(input("Enter a weapon: "))
        stageChoice: str = input("Enter the stage: ")
        rotations: List[int] = findRotationByWeaponsAndStage(
            dataFile[0], weapons=weapons, stage=stageChoice
        )
        print(rotations)
        rot: int = rotations[int(input("Pick the rotation id by index: "))]
        mode = input("Choose whether you want [With/Without/Both]: ")
        clearAfter = input("Choose whether you would like to clear after [Y/N]: ")
        for i in range(0, len(dataFile)):
            if mode == "With":
                filters.append(duringRotationInts(dataFile[i], [rot])[0])
                os.remove(dataFile[i][:-6] + "/notrotations/" + str(rot) + ".jl.gz")
            elif mode == "Without":
                filters.append(duringRotationInts(dataFile[i], [rot])[1])
                os.remove(dataFile[i][:-6] + "/rotations/" + str(rot) + ".jl.gz")
            elif mode == "Both":
                result = duringRotationInts(dataFile[i], [rot])
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
            if clearAfter == "Y" and dataFile[i][:5] != "data/":
                os.remove(dataFile[i])
    elif stat == "Has Weapon":
        val = input("Enter a weapon: ")
        mode = input("Choose whether you want [With/Without/Both]: ")
        clearAfter = input("Choose whether you would like to clear after [Y/N]: ")
        for i in range(0, len(dataFile)):
            if mode == "With":
                filters.append(hasWeapons(dataFile[i], [val])[0])
                os.remove(dataFile[i][:-6] + "/notweapon/" + val + ".jl.gz")
            elif mode == "Without":
                filters.append(hasWeapons(dataFile[i], [val])[1])
                os.remove(dataFile[i][:-6] + "/weapon/" + val + ".jl.gz")
            elif mode == "Both":
                result = hasWeapons(dataFile[i], [val])
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
            if clearAfter == "Y" and dataFile[i][:5] != "data/":
                os.remove(dataFile[i])
    elif stat == "Uses Weapon":
        val = input("Enter a weapon: ")
        mode = input("Choose whether you want [With/Without/Both]: ")
        clearAfter = input("Choose whether you would like to clear after [Y/N]: ")
        for i in range(0, len(dataFile)):
            if mode == "With":
                filters.append(usesWeapons(dataFile[i], [val])[0])
                os.remove(dataFile[i][:-6] + "/notusesWeapon/" + val + ".jl.gz")
            elif mode == "Without":
                filters.append(usesWeapons(dataFile[i], [val])[1])
                os.remove(dataFile[i][:-6] + "/usesWeapon/" + val + ".jl.gz")
            elif mode == "Both":
                result = usesWeapons(dataFile[i], [val])
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
            if clearAfter == "Y" and dataFile[i][:5] != "data/":
                os.remove(dataFile[i])
    elif stat == "Stage":
        val = input("Enter a stage: ")
        mode = input("Choose whether you want [With/Without/Both]: ")
        clearAfter = input("Choose whether you would like to clear after [Y/N]: ")
        for i in range(0, len(dataFile)):
            if mode == "With":
                filters.append(onStages(dataFile[i], [val])[0])
                os.remove(dataFile[i][:-6] + "/notstage/" + val + ".jl.gz")
            elif mode == "Without":
                filters.append(onStages(dataFile[i], [val])[1])
                os.remove(dataFile[i][:-6] + "/stage/" + val + ".jl.gz")
            elif mode == "Both":
                result = onStages(dataFile[i], [val])
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
            if clearAfter == "Y" and dataFile[i][:5] != "data/":
                os.remove(dataFile[i])
    elif stat == "Danger Rate":
        comparison: str = input("Choose whether you want [=/>/<]: ")
        val = input("Enter the danger rate: ")
        mode = input("Choose whether you want [With/Without/Both]: ")
        clearAfter = input("Choose whether you would like to clear after [Y/N]: ")
        for i in range(0, len(dataFile)):
            if mode == "With":
                filters.append(dangerRate(dataFile[i], val, comparison)[0])
                if comparison == "=":
                    os.remove(
                        dataFile[i][:-6] + "dangerRate/notEquals/" + val + ".jl.gz"
                    )
                elif comparison == ">":
                    os.remove(
                        dataFile[i][:-6] + "dangerRate/notGreaterThan/" + val + ".jl.gz"
                    )
                elif comparison == "<":
                    os.remove(
                        dataFile[i][:-6] + "dangerRate/notLessThan/" + val + ".jl.gz"
                    )
                else:
                    sys.exit()
            elif mode == "Without":
                filters.append(dangerRate(dataFile[i], val, comparison)[1])
                if comparison == "=":
                    os.remove(dataFile[i][:-6] + "dangerRate/equals/" + val + ".jl.gz")
                elif comparison == ">":
                    os.remove(
                        dataFile[i][:-6] + "dangerRate/greaterThan/" + val + ".jl.gz"
                    )
                elif comparison == "<":
                    os.remove(
                        dataFile[i][:-6] + "dangerRate/lessThan/" + val + ".jl.gz"
                    )
                else:
                    sys.exit()
            elif mode == "Both":
                result = dangerRate(dataFile[i], val, comparison)
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
            if clearAfter == "Y" and dataFile[i][:5] != "data/":
                os.remove(dataFile[i])
    elif stat == "Clear Wave":
        comparison = input("Choose whether you want [=/>/<]: ")
        wave: int = int(input("Enter the clear wave: "))
        mode = input("Choose whether you want [With/Without/Both]: ")
        clearAfter = input("Choose whether you would like to clear after [Y/N]:")
        for i in range(0, len(dataFile)):
            if mode == "With":
                filters.append(clearWave(dataFile[i], wave, comparison)[0])
                if comparison == "=":
                    os.remove(
                        dataFile[i][:-6]
                        + "/clearWaves/notequal/"
                        + str(wave)
                        + ".jl.gz"
                    )
                elif comparison == ">":
                    os.remove(
                        dataFile[i][:-6]
                        + "/clearWaves/notgreaterThan/"
                        + str(wave)
                        + ".jl.gz"
                    )
                elif comparison == "<":
                    os.remove(
                        dataFile[i][:-6]
                        + "/clearWaves/notlessThan/"
                        + str(wave)
                        + ".jl.gz"
                    )
                else:
                    sys.exit()
            elif mode == "Without":
                filters.append(clearWave(dataFile[i], wave, comparison)[1])
                if comparison == "=":
                    os.remove(
                        dataFile[i][:-6] + "/clearWaves/equal/" + str(wave) + ".jl.gz"
                    )
                elif comparison == ">":
                    os.remove(
                        dataFile[i][:-6]
                        + "/clearWaves/greaterThan/"
                        + str(wave)
                        + ".jl.gz"
                    )
                elif comparison == "<":
                    os.remove(
                        dataFile[i][:-6]
                        + "/clearWaves/lessThan/"
                        + str(wave)
                        + ".jl.gz"
                    )
                else:
                    sys.exit()
            elif mode == "Both":
                result = clearWave(dataFile[i], wave, comparison)
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
            if clearAfter == "Y" and dataFile[i][:5] != "data/":
                os.remove(dataFile[i])
    elif stat == "Special":
        val = input("Enter the special: ")
        mode = input("Choose whether you want [With/Without/Both]: ")
        clearAfter = input("Choose whether you would like to clear after [Y/N]:")
        for i in range(0, len(dataFile)):
            if mode == "With":
                filters.append(withSpecial(dataFile[i], val)[0])
                os.remove(data[:-6] + "/notspecial/" + val + ".jl.gz")
            elif mode == "Without":
                filters.append(withSpecial(dataFile[i], val)[0])
                os.remove(data[:-6] + "/special/" + val + ".jl.gz")
            elif mode == "Both":
                result = withSpecial(dataFile[i], val)
                filters.append(result[0])
                filters.append(result[1])
            else:
                sys.exit()
            if clearAfter == "Y" and dataFile[i][:5] != "data/":
                os.remove(dataFile[i])
    else:
        sys.exit()
    return filters


def printOverview(dataFile: List[str]):
    which: str = input("Would you like to print a [SpecificList/AllLists]: ")
    if which == "AllLists":
        for i in range(0, len(dataFile)):
            print(core.getOverview(dataFile[i]))
    elif which == "SpecificList":
        for i in range(0, len(dataFile)):
            print(dataFile[i])
        chosenList: int = int(input("Which list (by index): "))
        print(core.getOverview(dataFile[chosenList]))
        print()
    else:
        sys.exit()


def printAllJobs(dataFile: str):
    with gzip.open(dataFile) as reader:
        for job in jsonlines.Reader(reader, loads=ujson.loads):
            core.printGeneral(job)
            print()
            core.printWaves(job)
            print()
            core.printPlayers(job)
            print()
            core.printBosses(job)
            print()
            print()


def printJobs(dataFile: List[str]):
    which: str = input("Would you like to print from a SpecificList or AllLists: ")
    if which == "AllLists":
        for i in range(0, len(dataFile)):
            printAllJobs(dataFile[i])
    elif which == "SpecificList":
        for i in range(0, len(dataFile)):
            print(dataFile[i])
        chosenList: int = int(input("Which list (by index): "))
        printAllJobs(dataFile[chosenList])
    else:
        sys.exit()


def hypothesisTesting(dataFile: List[str]):
    for i in range(0, len(dataFile)):
        print(dataFile[i])
    first: int = int(input("Which is the first list you'd like to use (by index): "))
    second: int = int(input("Which is the first list you'd like to use (by index): "))
    stat: str = input("Which stat would you like to test: ")
    firstStat: List[float] = core.getArrayOfStat(dataFile[first], stat)
    secondStat: List[float] = core.getArrayOfStat(dataFile[second], stat)
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


def sortAttributeByStat(dataFile: List[str]):
    which: str = input("Would you like to print from a [SpecificList/AllLists]: ")
    stat: str = input("Enter a stat to sort by: ")
    mode: str = input("Pick a mode [Stage/Weapon/Rotation/Special]: ")
    if which == "AllLists":
        for i in range(0, len(dataFile)):
            if mode == "Stage":
                sort_by_stat.sortStages(dataFile[i], stat)
            elif mode == "Weapon":
                sort_by_stat.sortWeapons(dataFile[i], stat)
            elif mode == "Rotation":
                sort_by_stat.sortRotation(dataFile[i], stat)
            elif mode == "Special":
                sort_by_stat.sortSpecial(dataFile[i], stat)
            else:
                sys.exit()
    elif which == "SpecificList":
        for i in range(0, len(dataFile)):
            print(dataFile[i])
        chosenList: int = int(input("Which list (by index): "))
        if mode == "Stage":
            sort_by_stat.sortStages(dataFile[chosenList], stat)
        elif mode == "Weapon":
            sort_by_stat.sortWeapons(dataFile[chosenList], stat)
        elif mode == "Rotation":
            sort_by_stat.sortRotation(dataFile[chosenList], stat)
        elif mode == "Special":
            sort_by_stat.sortSpecial(dataFile[chosenList], stat)
        else:
            sys.exit()
    else:
        sys.exit()


def waveClearPercentageWithWeapon(dataFile: List[str]):
    which: str = input("Would you like to print from [SpecificList/AllLists]: ")
    weapon: str = input("Enter a weapon to test: ")
    if which == "AllLists":
        for i in range(0, len(dataFile)):
            print(
                weapon
                + ": "
                + str(core.waveClearPercentageWithWeapon(dataFile[i], weapon))
            )
    elif which == "SpecificList":
        for i in range(0, len(dataFile)):
            print(dataFile[i])
        chosenList = int(input("Which list (by index): "))
        core.waveClearPercentageWithWeapon(dataFile[chosenList], weapon)
        print()
    else:
        sys.exit()


def processData(dataFile: List[str]):
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
            printOverview(dataFile)
        elif mode == "PrintJobs":
            printJobs(dataFile)
        elif mode == "HypothesisTesting":
            hypothesisTesting(dataFile)
        elif mode == "SortAttributeByStat":
            sortAttributeByStat(dataFile)
        elif mode == "WaveClearPercentageWithWeapon":
            waveClearPercentageWithWeapon(dataFile)
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
    data: str = core.init(scope, ujson.load(open("keys.json", "r"))["statink_key"])
    dataFiles: List[str] = [data]
    allFiles: List[str] = []
    while input("Add a filter [Y/N]: ") == "Y":
        filtered = filterBy(dataFiles)
        dataFiles = []
        for f in filtered:
            dataFiles.append(f)
            allFiles.append(f)
    processData(dataFiles)
    if input("Clean [Y/N] (only if you didn't use clearAfter): ") == "Y":
        for a in range(0, len(allFiles)):
            os.remove(allFiles[a])
