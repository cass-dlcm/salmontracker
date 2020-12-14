from salmontracker import initUser, locale, hasWeapon, doesntHaveWeapon, avgStat, grizzcoWeapons
import requests
import pprint


def sortWeapons(data: list) -> None:
    weaponsList = requests.get("https://stat.ink/api/v2/weapon").json()
    for weapon in grizzcoWeapons:
        new = {
            "name": {
                locale: weapon[0]
            },
            "key": weapon[1]
        }
        weaponsList.append(new)
    results = []
    for weapon in weaponsList:
        result = {}
        withVal = list(filter(hasWeapon(weapon["name"][locale]), data))
        withoutVal = list(filter(doesntHaveWeapon(weapon["name"][locale]), data))
        if (len(withVal) > 0):
            result["name"] = weapon["name"][locale]
            result["value"] = avgStat(withVal, "clear_waves") - avgStat(withoutVal, "clear_waves")
            results.append(result)
    pprint.pprint(sorted(results, key=lambda val: val["value"]))


def sortStages(data: list, stat: str) -> None:
    stageDict = {}
    stageList = []
    for job in data:
        if not (job["stage"]["name"][locale] in stageDict):
            stageDict[job["stage"]["name"][locale]] = {
                "name": job["stage"]["name"][locale],
                "clear_waves": 0.0,
                "count": 0.0
            }
        stageDict[job["stage"]["name"][locale]][stat] += job[stat]
        stageDict[job["stage"]["name"][locale]]["count"] += 1.0
    for stage in stageDict.values():
        stageList.append({"name": stage["name"], "value": stage[stat] / stage["count"]})
    pprint.pprint(sorted(stageList, key=lambda val: val["value"]))


data = initUser()
sortStages(data, "clear_waves")
