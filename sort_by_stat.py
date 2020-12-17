import salmontracker
from salmontracker import (
    hasJobs,
    locale,
    hasWeapon,
    doesntHaveWeapon,
    avgStat,
    grizzcoWeapons,
)
import jsonlines
import requests
import pprint
from typing import Tuple, List, Dict, Union, cast
import ujson
import gzip
import os


def hasVal(var: List[Dict[str, str]], val: str):
    for item in var:
        if val == item["key"]:
            return True


def sortWeapons(path: str, data: str, stat: str) -> None:
    """

    :param path: str:
    :param data: str:
    :param stat: str:

    """
    weaponsList: List[Dict[str, Union[str, Dict[str, str]]]] = requests.get(
        "https://stat.ink/api/v2/weapon"
    ).json()
    for grizzWeapon in grizzcoWeapons:
        new = {
            "name": {locale: grizzWeapon[0]},
            "key": grizzWeapon[1],
            "main_ref": grizzWeapon[1],
        }
        cast(List[Dict[str, Dict[str, str]]], weaponsList).append(
            cast(Dict[str, Dict[str, str]], new)
        )
    results: List[Dict[str, Union[str, float]]] = []
    for weapon in weaponsList:
        print(weapon["key"])
        result: Dict[str, Union[str, float]] = {}
        withVal: Tuple[str, str] = hasWeapon(path, data, cast(str, weapon["main_ref"]))
        if hasJobs(withVal[0], withVal[1]) and not hasVal(
            cast(List[Dict[str, str]], results), cast(str, weapon["main_ref"])
        ):
            withoutVal: Tuple[str, str] = doesntHaveWeapon(
                path, data, cast(str, weapon["main_ref"])
            )
            if (hasJobs(withVal[0], withVal[1])) and (
                hasJobs(withoutVal[0], withoutVal[1])
            ):
                result["key"] = cast(str, weapon["main_ref"])
                result["name"] = cast(Dict[str, str], weapon["name"])[locale]
                result["value"] = avgStat(withVal[0] + withVal[1], stat) - avgStat(
                    withoutVal[0] + withoutVal[1], stat
                )
                results.append(result)
        elif not hasJobs(withVal[0], withVal[1]):
            os.remove(withVal[0] + withVal[1])
    pprint.pprint(sorted(results, key=lambda val: val["value"]))


def sortStages(data: str, stat: str) -> None:
    """

    :param data: str:
    :param stat: str:

    """
    stageDict: Dict[str, Dict[str, Union[str, float]]] = {}
    stageList: List[Dict[str, Union[str, float]]] = []
    with gzip.open(data) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            if job["stage"] is not None:
                if not (job["stage"]["name"][locale] in stageDict):
                    stageDict[job["stage"]["name"][locale]] = {
                        "name": job["stage"]["name"][locale],
                        "clear_waves": 0.0,
                        "count": 0.0,
                    }
                cast(Dict[str, float], stageDict[job["stage"]["name"][locale]])[
                    stat
                ] += cast(float, job[stat])
                cast(Dict[str, float], stageDict[job["stage"]["name"][locale]])[
                    "count"
                ] += 1.0
        for stage in stageDict.values():
            stageList.append(
                {
                    "name": stage["name"],
                    "value": cast(float, stage[stat]) / cast(float, stage["count"]),
                }
            )
        pprint.pprint(sorted(stageList, key=lambda val: val["value"]))


def sortSpecial(data: str, stat: str) -> None:
    """

    :param data: str:
    :param stat: str:

    """
    specialDict: Dict[str, Dict[str, Union[str, float]]] = {}
    specialList: List[Dict[str, Union[str, float]]] = []
    with gzip.open(data) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            if job["stage"] is not None:
                if not (job["my_data"]["special"]["name"][locale] in specialDict):
                    specialDict[job["my_data"]["special"]["name"][locale]] = {
                        "name": job["my_data"]["special"]["name"][locale],
                        "clear_waves": 0.0,
                        "count": 0.0,
                    }
                cast(
                    Dict[str, float],
                    specialDict[job["my_data"]["special"]["name"][locale]],
                )[stat] += cast(float, job[stat])
                cast(
                    Dict[str, float],
                    specialDict[job["my_data"]["special"]["name"][locale]],
                )["count"] += 1.0
        for special in specialDict.values():
            specialList.append(
                {
                    "name": special["name"],
                    "value": cast(float, special[stat]) / cast(float, special["count"]),
                }
            )
        pprint.pprint(sorted(specialList, key=lambda val: val["value"]))


def sortRotation(path: str, data: str, stat: str) -> None:
    rotationList: List[int] = []
    rotationResultsList: List[
        Dict[str, Union[int, float, Union[None, Dict[str, Union[str, List[str]]]]]]
    ] = []
    with gzip.open(path + data) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            if job["shift_start_at"]["time"] not in rotationList:
                rotationList.append(job["shift_start_at"]["time"])
    for rotation in rotationList:
        print(rotation)
        result: Dict[
            str, Union[int, float, Union[None, Dict[str, Union[str, List[str]]]]]
        ] = {}
        withVal: Tuple[str, str] = salmontracker.duringRotationInt(path, data, rotation)
        if hasJobs(withVal[0], withVal[1]):
            withoutVal: Tuple[str, str] = salmontracker.notDuringRotationInt(
                path, data, rotation
            )
            if (hasJobs(withVal[0], withVal[1])) and (
                hasJobs(withoutVal[0], withoutVal[1])
            ):
                result["name"] = rotation
                result["data"] = salmontracker.findWeaponsAndStageByRotation(
                    withVal[0] + withVal[1], rotation
                )
                result["value"] = avgStat(withVal[0] + withVal[1], stat) - avgStat(
                    withoutVal[0] + withoutVal[1], stat
                )
                rotationResultsList.append(result)
        elif not hasJobs(withVal[0], withVal[1]):
            os.remove(withVal[0] + withVal[1])
    pprint.pprint(
        sorted(rotationResultsList, key=lambda val: cast(float, val["value"]))
    )


if __name__ == "__main__":
    # fullPath: Tuple[str, str] = salmontracker.initUser(ujson.load(open("keys.json", "r"))["statink_key"])
    fullPath: Tuple[str, str] = salmontracker.initAll()
    filePath: str = fullPath[0]
    dataFile: str = fullPath[1]
    # sortStages(filePath + dataFile, "clear_waves")
    sortWeapons(filePath, dataFile, "clear_waves")
    # sortSpecial(filePath + dataFile, "clear_waves")
    # sortRotation(filePath, dataFile, "clear_waves")
