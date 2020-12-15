from salmontracker import (
    initAll,
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
    printOverview,
    usesWeapon,
    doesntUseWeapon,
)
import json
from typing import List, Tuple
import sys
import os


def filterBy(paths: List[str], data: List[str]) -> List[Tuple[str, str]]:
    filters: List[Tuple[str, str]] = []
    print()
    print("Rotation")
    print("Player")
    print("Has Weapon")
    print("Uses Weapon")
    print("Stage")
    print()
    mode: str = ""
    stat: str = input("Choose a stat to run analysis on: ")
    if stat == "Player":
        playerName = input("Enter a player name to run analysis on: ")
        playerId: List[str] = findPlayerIdByName(paths[0], data[0], playerName)
        print(playerId)
        val: str = playerId[int(input("Pick the player id by index: "))]
        mode = input("Choose whether you want With, Without, or Both: ")
        for i in range(0, len(paths)):
            if mode == "With":
                filters.append(hasPlayer(paths[i], data[i], val))
            elif mode == "Without":
                filters.append(withoutPlayer(paths[i], data[i], val))
            elif mode == "Both":
                filters.append(hasPlayer(paths[i], data[i], val))
                filters.append(withoutPlayer(paths[i], data[i], val))
            else:
                sys.exit()
    elif stat == "Rotation":
        weapons = []
        for i in range(0, 4):
            weapons.append(input("Enter a weapon: "))
        stageChoice = input("Enter the stage: ")
        rotations: List[int] = findRotationByWeaponsAndStage(
            paths[0] + data[0], weapons, stageChoice
        )
        print(rotations)
        rot: int = rotations[int(input("Pick the rotation id by index: "))]
        mode = input("Choose whether you want With, Without, or Both: ")
        for i in range(0, len(paths)):
            if mode == "With":
                filters.append(duringRotationInt(paths[i], data[i], rot))
            elif mode == "Without":
                filters.append(notDuringRotationInt(paths[i], data[i], rot))
            elif mode == "Both":
                filters.append(duringRotationInt(paths[i], data[i], rot))
                filters.append(notDuringRotationInt(paths[i], data[i], rot))
            else:
                sys.exit()
    elif stat == "Has Weapon":
        val = input("Enter a weapon: ")
        mode = input("Choose whether you want With, Without, or Both: ")
        for i in range(0, len(paths)):
            if mode == "With":
                filters.append(hasWeapon(paths[i], data[i], val))
            elif mode == "Without":
                filters.append(doesntHaveWeapon(path[i], data[i], val))
            elif mode == "Both":
                filters.append(hasWeapon(path[i], data[i], val))
                filters.append(doesntHaveWeapon(path, data[i], val))
            else:
                sys.exit()
    elif stat == "Uses Weapon":
        val = input("Enter a weapon: ")
        mode = input("Choose whether you want With, Without, or Both: ")
        for i in range(0, len(paths)):
            if mode == "With":
                filters.append(usesWeapon(paths[i], data[i], val))
            elif mode == "Without":
                filters.append(doesntUseWeapon(path[i], data[i], val))
            elif mode == "Both":
                filters.append(usesWeapon(path[i], data[i], val))
                filters.append(doesntUseWeapon(path, data[i], val))
            else:
                sys.exit()
    elif stat == "Stage":
        val = input("Enter a stage: ")
        mode = input("Choose whether you want With, Without, or Both: ")
        for i in range(0, len(paths)):
            if mode == "With":
                filters.append(onStage(paths[i], data[i], val))
            elif mode == "Without":
                filters.append(notOnStage(path[i], data[i], val))
            elif mode == "Both":
                filters.append(onStage(paths[i], data[i], val))
                filters.append(notOnStage(paths[i], data[i], val))
            else:
                sys.exit()
    else:
        sys.exit()
    return filters


print("All")
print("User")
scope = input("Pick an analysis scope: ")
path: str = ""
data: str = ""
if scope == "All":
    dataFile = initAll()
    path = dataFile[0]
    data = dataFile[1]
elif scope == "User":
    dataFile = initUser(json.load(open("keys.json", "r"))["statink_key"])
    path = dataFile[0]
    data = dataFile[1]
else:
    sys.exit()
currentPaths: List[str] = []
allPaths: List[str] = []
dataFiles: List[str] = []
allFiles: List[str] = []
while input("Add a filter (Y/N): ") == "Y":
    if currentPaths == []:
        filters = filterBy([path], [data])
        for f in filters:
            currentPaths.append(f[0])
            dataFiles.append(f[1])
            if f[0] not in allPaths:
                allPaths.append(f[0])
            if f[1] not in allFiles:
                allFiles.append(f[1])
    else:
        filters = filterBy(currentPaths, dataFiles)
        currentPaths = []
        dataFiles = []
        for f in filters:
            currentPaths.append(f[0])
            dataFiles.append(f[1])
            if f[0] not in allPaths:
                allPaths.append(f[0])
            if f[1] not in allFiles:
                allFiles.append(f[1])
for i in range(0, len(currentPaths)):
    printOverview(currentPaths[i], dataFiles[i])
if input("Clean (Y/N): ") == "Y":
    for i in range(0, len(allPaths)):
        os.remove(allPaths[i] + allFiles[i])
