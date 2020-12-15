from salmontracker import (
    initUser,
    initAll,
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
from typing import Tuple, List, Dict, Union
import json
import os


def sortWeapons(path: str, data: str, stat: str) -> None:
    """

    :param path: str:
    :param data: str:
    :param stat: str:

    """
    weaponsList: List[dict] = requests.get("https://stat.ink/api/v2/weapon").json()
    for grizzWeapon in grizzcoWeapons:
        new = {"name": {locale: grizzWeapon[0]}, "key": grizzWeapon[1]}
        weaponsList.append(new)
    results: List[Dict[str, Union[str, float]]] = []
    for weapon in weaponsList:
        result: Dict[str, Union[str, float]] = {}
        withVal: Tuple[str, str] = hasWeapon(path, data, weapon["name"][locale])
        withoutVal: Tuple[str, str] = doesntHaveWeapon(
            path, data, weapon["name"][locale]
        )
        if (hasJobs(withVal[0], withVal[1])) and (
            hasJobs(withoutVal[0], withoutVal[1])
        ):
            result["name"] = weapon["name"][locale]
            result["value"] = avgStat(withVal[0] + withVal[1], stat) - avgStat(
                withoutVal[0] + withoutVal[1], stat
            )
            results.append(result)
        os.remove(withVal[0] + withVal[1])
        os.remove(withoutVal[0] + withoutVal[1])
    pprint.pprint(sorted(results, key=lambda val: val["value"]))


def sortStages(path: str, data: str, stat: str) -> None:
    """

    :param path: str:
    :param data: str:
    :param stat: str:

    """
    stageDict = {}
    stageList = []
    with jsonlines.open(path + data, "r") as reader:
        for job in reader:
            if job["stage"] is not None:
                if not (job["stage"]["name"][locale] in stageDict):
                    stageDict[job["stage"]["name"][locale]] = {
                        "name": job["stage"]["name"][locale],
                        "clear_waves": 0.0,
                        "count": 0.0,
                    }
                stageDict[job["stage"]["name"][locale]][stat] += job[stat]
                stageDict[job["stage"]["name"][locale]]["count"] += 1.0
        for stage in stageDict.values():
            stageList.append(
                {"name": stage["name"], "value": stage[stat] / stage["count"]}
            )
        pprint.pprint(sorted(stageList, key=lambda val: val["value"]))


# initUser(json.load(open("keys.json", "r"))["statink_key"])
# initAll()
filePath = "data/"
dataFile = "salmonAll.jsonl"
# sortStages(filePath, dataFile, "clear_waves")
sortWeapons(filePath, dataFile, "clear_waves")
