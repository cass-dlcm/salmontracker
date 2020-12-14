from salmontracker import initUser, locale, hasWeapon, doesntHaveWeapon, avgStat
from utility import grizzcoWeapons
import requests

data = initUser()
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
print(sorted(results, key = lambda val: val["value"]))
