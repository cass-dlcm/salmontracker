import os.path
import random
import json
import numpy as np
import requests
import utility

locale = "en_US"

api_key = json.load(open("keys.json", "r"))["statink_key"]

def fetchAll() -> list:
    headers = {'Authorization': 'Bearer {}'.format(api_key)}
    data = []
    lastId = 0
    prevLastId = 0
    params = {'order': 'asc'}
    temp = requests.get("http://stat.ink/api/v2/user-salmon", headers = headers, params = params).json()
    lastId = temp[-1]["id"]
    print(lastId)
    while lastId != prevLastId:
        for i in temp:
            data.append(i)
        params['newer_than'] = lastId
        result = requests.get("http://stat.ink/api/v2/user-salmon", headers = headers, params = params)
        print(result.url)
        print(result)
        temp = result.json()
        prevLastId = lastId
        if len(temp) > 0:
            lastId = temp[-1]["id"]
        print(lastId)
    return data

def fetchNew(recentId: int) -> list:
    headers = {'Authorization': 'Bearer {}'.format(api_key)}
    data = []
    lastId = 0
    prevLastId = 0
    params = {'order': 'asc'}
    params['newer_than'] = recentId
    temp = requests.get("http://stat.ink/api/v2/user-salmon", headers = headers, params = params).json()
    if len(temp) > 0:
        lastId = temp[-1]["id"]
        print(lastId)
        while lastId != prevLastId:
            for i in temp:
                data.append(i)
            params['newer_than'] = lastId
            result = requests.get("http://stat.ink/api/v2/user-salmon", headers = headers, params = params)
            print(result.url)
            print(result)
            temp = result.json()
            prevLastId = lastId
            if len(temp) > 0:
                lastId = temp[-1]["id"]
            print(lastId)
    return data

def hasPlayer(player: str) -> bool:
    return lambda var: var["teammates"][0]["splatnet_id"] == player or (len(var["teammates"]) > 1 and var["teammates"][1]["splatnet_id"] == player) or (len(var["teammates"]) > 2 and var["teammates"][2]["splatnet_id"] == player)

def withoutPlayer(player: str) -> bool:
    return lambda var: var["teammates"][0]["splatnet_id"] != player and ((len(var["teammates"]) > 1 and var["teammates"][1]["splatnet_id"] != player) or (len(var["teammates"]) < 2)) and ((len(var["teammates"]) > 2 and var["teammates"][2]["splatnet_id"] != player) or (len(var["teammates"]) < 3))

def hasPlayerByName(player: str) -> bool:
    return lambda var: var["teammates"][0]["name"] == player or (len(var["teammates"]) > 1 and var["teammates"][1]["name"] == player) or (len(var["teammates"]) > 2 and var["teammates"][2]["name"] == player)

def hasWeapon(weapon: str) -> bool:
    return lambda var: (
        var["my_data"]["weapons"][0]["key"] == weapon or
        (len(var["my_data"]["weapons"]) > 1 and var["my_data"]["weapons"][1]["key"] == weapon) or
        (len(var["my_data"]["weapons"]) > 2 and var["my_data"]["weapons"][2]["key"] == weapon) or
        (len(var["teammates"]) > 0 and var["teammates"][0]["weapons"] != None and (
            var["teammates"][0]["weapons"][0]["key"] == weapon or
            (len(var["teammates"][0]["weapons"]) > 1 and var["teammates"][0]["weapons"][1]["key"] == weapon) or
            (len(var["teammates"][0]["weapons"]) > 2 and var["teammates"][0]["weapons"][2]["key"] == weapon))) or
        (len(var["teammates"]) > 1 and var["teammates"][1]["weapons"] != None and (
            var["teammates"][1]["weapons"][0]["key"] == weapon or
            (len(var["teammates"][1]["weapons"]) > 1 and var["teammates"][1]["weapons"][1]["key"] == weapon) or
            (len(var["teammates"][1]["weapons"]) > 2 and var["teammates"][1]["weapons"][2]["key"] == weapon))) or
        (len(var["teammates"]) > 2 and var["teammates"][2]["weapons"] != None and (
            var["teammates"][2]["weapons"][0]["key"] == weapon or
            (len(var["teammates"][2]["weapons"]) > 1 and var["teammates"][2]["weapons"][1]["key"] == weapon) or
            (len(var["teammates"][2]["weapons"]) > 2 and var["teammates"][2]["weapons"][2]["key"] == weapon))))

def doesntHaveWeapon(weapon: str) -> bool:
    return lambda var: not (
        var["my_data"]["weapons"][0]["key"] == weapon or
        (len(var["my_data"]["weapons"]) > 1 and var["my_data"]["weapons"][1]["key"] == weapon) or
        (len(var["my_data"]["weapons"]) > 2 and var["my_data"]["weapons"][2]["key"] == weapon) or
        (len(var["teammates"]) > 0 and var["teammates"][0]["weapons"] != None and (
            var["teammates"][0]["weapons"][0]["key"] == weapon or
            (len(var["teammates"][0]["weapons"]) > 1 and var["teammates"][0]["weapons"][1]["key"] == weapon) or
            (len(var["teammates"][0]["weapons"]) > 2 and var["teammates"][0]["weapons"][2]["key"] == weapon))) or
        (len(var["teammates"]) > 1 and var["teammates"][1]["weapons"] != None and (
            var["teammates"][1]["weapons"][0]["key"] == weapon or
            (len(var["teammates"][1]["weapons"]) > 1 and var["teammates"][1]["weapons"][1]["key"] == weapon) or
            (len(var["teammates"][1]["weapons"]) > 2 and var["teammates"][1]["weapons"][2]["key"] == weapon))) or
        (len(var["teammates"]) > 2 and var["teammates"][2]["weapons"] != None and (
            var["teammates"][2]["weapons"][0]["key"] == weapon or
            (len(var["teammates"][2]["weapons"]) > 1 and var["teammates"][2]["weapons"][1]["key"] == weapon) or
            (len(var["teammates"][2]["weapons"]) > 2 and var["teammates"][2]["weapons"][2]["key"] == weapon))))

def usesWeapon(weapon: str) -> bool:
    return lambda var: (
        var["my_data"]["weapons"][0]["key"] == weapon or
        (len(var["my_data"]["weapons"]) > 1 and var["my_data"]["weapons"][1]["key"] == weapon) or
        (len(var["my_data"]["weapons"]) > 2 and var["my_data"]["weapons"][2]["key"] == weapon))

def doesntUseWeapon(weapon: str) -> bool:
    return lambda var: not (
        var["my_data"]["weapons"][0]["key"] == weapon or
        (len(var["my_data"]["weapons"]) > 1 and var["my_data"]["weapons"][1]["key"] == weapon) or
        (len(var["my_data"]["weapons"]) > 2 and var["my_data"]["weapons"][2]["key"] == weapon))

def findPlayerIdByName(data: list, player: str) -> list:
    foundIds: list = []
    matches = list(filter(hasPlayerByName(player), data))
    for match in matches:
        for teammate in match["teammates"]:
            if teammate["name"] == player and teammate["splatnet_id"] not in foundIds:
                foundIds.append(teammate["splatnet_id"])
    return foundIds

def onStage(stage: str) -> bool:
    return lambda var: var["stage_name"] == stage or var["stage_key"] == stage

def withSpecial(special: str) -> bool:
    return lambda var: var["player_special"] == special or var["player_special__1"] == special

def withWeapon(weapon: str) -> bool:
    return lambda var: var["player_w1_weapon"] == weapon or var["player_w1_weapon__1"] == weapon or var["player_w2_weapon"] == weapon or var["player_w2_weapon__1"] == weapon or var["player_w3_weapon"] == weapon or var["player_w3_weapon__1"] == weapon

def failReason(reason: str) -> bool:
    return lambda var: var["fail_reason"] == reason or var["fail_reason__1"] == reason

def rotationPeriod(rotation: int) -> bool:
    return lambda var: var["rotation_period"] == rotation

def clearWave(wave: int) -> bool:
    return lambda var: var["clear_waves"] == wave

def splatnet_number(num: int) -> bool:
    return lambda var: var["splatnet_number"] == num

def jobsCount(data: list) -> int:
    return len(data)

def avgStat(data: list, stat: str) -> float:
    return sum(float(d[stat]) for d in data) / jobsCount(data)

def avgStat2D(data: list, firstD: str, secondD: str) -> float:
    return sum(d[firstD][secondD] for d in data) / jobsCount(data)

def avgStat3D(data: list, firstD: str, secondD: str, thirdD: str) -> float:
    return sum(d[firstD][secondD][thirdD] for d in data) / jobsCount(data)

def maxStat(data: list, stat: str) -> float:
    max = data[0][stat]
    for job in data:
        if (max < job[stat]):
            max = job[stat]
    return max

def maxStat2D(data: list, firstD: str, secondD: str) -> float:
    max = data[0][firstD][secondD]
    for job in data:
        if (max < job[firstD][secondD]):
            max = job[firstD][secondD]
    return max

def maxStat3D(data: list, firstD: str, secondD: str, thirdD: str) -> float:
    max = data[0][firstD][secondD][thirdD]
    for job in data:
        if (max < job[firstD][secondD][thirdD]):
            max = job[firstD][secondD][thirdD]
    return max

def minStat(data: list, stat: str) -> float:
    min = data[0][stat]
    for job in data:
        if (min > job[stat]):
            min = job[stat]
    return min

def minStat2D(data: list, firstD: str, secondD: str) -> float:
    min = data[0][firstD][secondD]
    for job in data:
        if (min > job[firstD][secondD]):
            min = job[firstD][secondD]
    return min

def minStat3D(data: list, firstD: str, secondD: str, thirdD: str) -> float:
    min = data[0][firstD][secondD][thirdD]
    for job in data:
        if (min > job[firstD][secondD][thirdD]):
            min = job[firstD][secondD][thirdD]
    return min

def medianStat(data: list, stat: str) -> float:
    return np.median([float(x[stat]) for x in data])

def medianStat2D(data: list, firstD: str, secondD: str) -> float:
    return np.median([x[firstD][secondD] for x in data])

def medianStat3D(data: list, firstD: str, secondD: str, thirdD: str) -> float:
    return np.median([x[firstD][secondD][thirdD] for x in data])

def clearPercentage(data: list) -> float:
    return sum(d["clear_waves"] == 3 for d in data) / jobsCount(data)
    
def waveTwoPercentage(data: list) -> float:
    return sum(d["clear_waves"] >= 2 for d in data) / jobsCount(data)

def waveOnePercentage(data: list) -> float:
    return sum(d["clear_waves"] >= 1 for d in data) / jobsCount(data)

def statSummary(data: list, stat: str) -> str:
    return str(avgStat(data, stat)) + " (" + str(minStat(data, stat)) + ", " + str(medianStat(data, stat)) + ", " + str(maxStat(data, stat)) + ")"

def statSummary2D(data: list, firstD: str, secondD: str) -> str:
    return str(avgStat2D(data, firstD, secondD)) + " (" + str(minStat2D(data, firstD, secondD)) + ", " + str(medianStat2D(data, firstD, secondD)) + ", " + str(maxStat2D(data, firstD, secondD)) + ")"

def statSummary3D(data: list, firstD: str, secondD: str, thirdD: str) -> str:
    return str(avgStat3D(data, firstD, secondD, thirdD)) + " (" + str(minStat3D(data, firstD, secondD, thirdD)) + ", " + str(medianStat3D(data, firstD, secondD, thirdD)) + ", " + str(maxStat3D(data, firstD, secondD, thirdD)) + ")"

def sumStatWaves(data: dict, stat: str) -> int:
    sumVal = 0
    for w in data["waves"]:
        sumVal += w[stat]
    return sumVal

def getPlayersAttribute(data: dict, attr: str) -> str:
    attrs = "{:<16}\t".format(data["my_data"][attr] or 0)
    for p in data["teammates"]:
        attrs += "{:<16}\t".format(p[attr] or 0)
    return attrs

def getPlayersAttribute2D(data: dict, firstD: str, secondD: str) -> str:
    attrs = "{:<16}\t".format(data["my_data"][firstD][secondD] or 0)
    for p in data["teammates"]:
        attrs += "{:<16}\t".format(p[firstD][secondD] or 0)
    return attrs

def getPlayersAttribute3D(data: dict, firstD: str, secondD: str, thirdD: str) -> str:
    attrs = "{:<16}\t".format(data["my_data"][firstD][secondD][thirdD] or 0)
    for p in data["teammates"]:
        attrs += "{:<16}\t".format(p[firstD][secondD][thirdD] or 0)
    return attrs

def getPlayersAttribute4D(data: dict, firstD: str, secondD: str, thirdD: str, fourthD: str) -> str:
    attrs = "{:<16}\t".format(data["my_data"][firstD][secondD][thirdD][fourthD] or 0)
    for p in data["teammates"]:
        if secondD < len(p[firstD]):
            attrs += "{:<16}\t".format(p[firstD][secondD][thirdD][fourthD] or 0)
        else:
            attrs += "{:<16}\t".format("")
    return attrs

def getWavesAttribute(data: dict, attr: str) -> str:
    attrs = ""
    for w in data["waves"]:
        if w[attr]:
            attrs += "{:<16}\t".format(w[attr])
        else:
            attrs += "{:<16}\t".format("")
    return attrs

def getWavesAttribute3D(data: dict, firstD: str, secondD, thirdD) -> str:
    attrs = ""
    for w in data["waves"]:
        if w[firstD]:
            attrs += "{:<16}\t".format(w[firstD][secondD][thirdD])
        else:
            attrs += "{:<16}\t".format("")
    return attrs

def getBossDataStr(data: dict, boss: str) -> str:
    return "{:<16}\t{:}".format(data[boss + "_appearances"] or 0, getPlayersAttribute(data, "kills", boss + "_"))
    return "{:<16}\t{:<16}\t{:<16}\t{:<16}\t{:<16}".format(data[boss + "_appearances"] or 0, data[boss + "_player_kills"] or 0, data[boss + "_mate1_kills"] or 0, data[boss + "_mate2_kills"] or 0, data[boss + "_mate3_kills"] or 0)

def getTotalBosses(data: list, player: str) -> int:
    return sum(int(data[boss.replace(" ", "_").lower() + "_" + player] or 0) for boss in bosses)

def printOverview(data: list) -> None:
    print("Jobs: " + str(jobsCount(data)))
    print("Average Waves: " + str(avgStat(data, "clear_waves")))
    print("Clear %: " + str(clearPercentage(data)))
    print("Wave 2 %: " + str(waveTwoPercentage(data)))
    print("Wave 1 %: " + str(waveOnePercentage(data)))
    print("Golden: "+ statSummary2D(data, "my_data", "golden_egg_delivered"))
    print("Power Eggs: " + statSummary2D(data, "my_data", "power_egg_collected"))
    print("Rescued: " + statSummary2D(data, "my_data", "rescue"))
    print("Deaths: " + statSummary2D(data, "my_data", "death"))
    print("Hazard Level: "+ statSummary(data, "danger_rate"))

def printGeneral(data: list) -> None:
    print("Stat.ink Link: " + data["url"])
    print("Splatnet #: {:<}".format(data["splatnet_number"]))
    print("Stage: {:}".format(data["stage"]["name"][locale]))
    print("Rotation Start Date: " + str(data["shift_start_at"]["iso8601"]))
    print("Start Date: " + data["start_at"]["iso8601"])
    print("Result: {:}".format("Cleared" if data["clear_waves"] == 3 else "Failed"))
    print("Title: {:} {:<3} -> {:} {:<3}".format(data["title"]["name"][locale], data["title_exp"], data["title_after"]["name"][locale], data["title_exp_after"]))

def printWaves(data: dict) -> None:
    print("{:16}\t{:16}\t{:16}\t{:16}\t{:16}".format("", "Wave 1", "Wave 2", "Wave 3", "Total"))
    print("{:16}\t{:<}".format("Event", getWavesAttribute3D(data, "known_occurrence", "name", locale)))
    print("{:16}\t{:<}".format("Water Level", getWavesAttribute3D(data, "water_level", "name", locale)))
    print("{:16}\t{:<}{:<16}".format("Quota", getWavesAttribute(data, "golden_egg_quota"), sumStatWaves(data, "golden_egg_quota")))
    print("{:16}\t{:<}{:<16}".format("Delivers", getWavesAttribute(data, "golden_egg_delivered"), sumStatWaves(data, "golden_egg_delivered")))
    print("{:16}\t{:<}{:<16}".format("Appearances", getWavesAttribute(data, "golden_egg_appearances"), sumStatWaves(data, "golden_egg_appearances")))
    print("{:16}\t{:<}{:<16}".format("Power Eggs", getWavesAttribute(data, "power_egg_collected"), sumStatWaves(data, "power_egg_collected")))

def printWeapons(data: dict) -> None:
    for i in range(0, len(data["my_data"]["weapons"])):
        print("{:16}\t{:}".format("Wave {:1} Weapon".format(i+1), getPlayersAttribute4D(data, "weapons", i, "name", locale)))

def printSpecials(data: dict) -> None:
    for i in range(0, len(data["my_data"]["special_uses"])):
        print("{:16}\t{:}".format("Wave {:1} Special Use".format(i+1), getPlayersAttribute2D(data, "special_uses", i)))

def printPlayers(data: dict) -> None:
    print("{:16}\t{:}".format("ID", getPlayersAttribute(data, "splatnet_id")))
    print("{:16}\t{:}".format("Name", getPlayersAttribute(data, "name")))
    printWeapons(data)
    print("{:16}\t{:}".format("Special", getPlayersAttribute3D(data, "special", "name", locale)))
    printSpecials(data)
    print("{:16}\t{:}".format("Rescues", getPlayersAttribute(data, "rescue")))
    print("{:16}\t{:}".format("Deaths", getPlayersAttribute(data, "death")))
    print("{:16}\t{:}".format("Golden Eggs", getPlayersAttribute(data, "golden_egg_delivered")))
    print("{:16}\t{:}".format("Power Eggs", getPlayersAttribute(data, "power_egg_collected")))

def getBosses(data: dict) -> list:
    results = []
    names = {}
    appearances = {"": 0}
    for boss in range(0, len(data["boss_appearances"])):
        names[data["boss_appearances"][boss]["boss"]["name"][locale]] = data["boss_appearances"][boss]["boss"]["name"][locale]
        appearances[data["boss_appearances"][boss]["boss"]["name"][locale]] = data["boss_appearances"][boss]["count"]
    results.append(names)
    results.append(appearances)
    my_data = {"": 0}
    if data["my_data"]["boss_kills"] != None:
        for boss in range(0, len(data["my_data"]["boss_kills"])):
            my_data[data["my_data"]["boss_kills"][boss]["boss"]["name"][locale]] = data["my_data"]["boss_kills"][boss]["count"]
    results.append(my_data)
    for teammate in range(0, len(data["teammates"])):
        teammate_data = {"": 0}
        if data["teammates"][teammate]["boss_kills"] != None:
            for boss in range(0, len(data["teammates"][teammate]["boss_kills"])):
                my_data[data["teammates"][teammate]["boss_kills"][boss]["boss"]["name"][locale]] = data["teammates"][teammate]["boss_kills"][boss]["count"]
        results.append(teammate_data)
    return results

def printBosses(data: dict) -> None:
    print("{:16}\t{:16}\t{:}".format("Boss Salmonid", "Appearances", getPlayersAttribute(data, "name")))
    bosses = getBosses(data)
    listBosses = list(bosses[0])
    for boss in range(0, len(bosses[0])):
        print("{:16}\t{:<16}\t{:<16}\t{:<16}\t{:<16}\t{:<16}".format(bosses[0][listBosses[boss]], bosses[1][listBosses[boss] if listBosses[boss] in bosses[1] else ""], bosses[2][listBosses[boss] if listBosses[boss] in bosses[2] else ""], bosses[3][listBosses[boss] if listBosses[boss] in bosses[3] else ""], bosses[4][listBosses[boss] if listBosses[boss] in bosses[4] else ""], bosses[5][listBosses[boss] if listBosses[boss] in bosses[5] else ""]))
    getBosses(data)

def getArrayOfStat(data: list, stat) -> list:
    results = []
    for job in data:
        results.append(float(job[stat]))
    return results

def getArrayOfStat2D(data: list, firstD, secondD) -> list:
    results = []
    for job in data:
        results.append(float(job[firstD][secondD]))
    return results

def init() -> list:
    data = []
    if os.path.exists("salmon.json"):
        data = json.load(open("salmon.json", "r"))
        new = fetchNew(data[-1]["id"])
        for i in new:
            data.append(i)
        json.dump(data, open("salmon.json", "w"), indent=4)
    else:
        data = fetchAll()
        json.dump(data, open("salmon.json", "w"), indent=4)
    return data
        


#json.dump(data, open("salmon.json", "w"))
data = init()
hasChosenWeapon = list(filter(doesntUseWeapon(utility.weaponNameToKey("Grizzco Charger", locale)), data))
printOverview(hasChosenWeapon)
"""for job in data:
    printGeneral(job)
    print()
    printWaves(job)
    print()
    printPlayers(job)
    print()
    printBosses(job)
    print()
    print()"""