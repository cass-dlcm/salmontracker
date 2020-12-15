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


def sortWeapons(path: str, data: str, stat: str) -> None:
    weaponsList = requests.get("https://stat.ink/api/v2/weapon").json()
    for weapon in grizzcoWeapons:
        new = {"name": {locale: weapon[0]}, "key": weapon[1]}
        weaponsList.append(new)
    results = []
    for weapon in weaponsList:
        result = {}
        withVal = hasWeapon(path, data, weapon["name"][locale])
        withoutVal = doesntHaveWeapon(path, data, weapon["name"][locale])
        if (hasJobs(withVal[0], withVal[1])) and (
            hasJobs(withoutVal[0], withoutVal[1])
        ):
            result["name"] = weapon["name"][locale]
            result["value"] = avgStat(withVal[0] + withVal[1], stat) - avgStat(
                withoutVal[0] + withoutVal[1], stat
            )
            results.append(result)
    pprint.pprint(sorted(results, key=lambda val: val["value"]))


def sortStages(path: str, data: str, stat: str) -> None:
    stageDict = {}
    stageList = []
    with jsonlines.open(path + data, "r") as reader:
        for job in reader:
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


initUser()
path = "data/"
data = "salmon.jsonl"
sortStages(path, data, "clear_waves")
sortWeapons(path, data, "clear_waves")
