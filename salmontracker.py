import random
import json
import numpy as np

bosses = ("Drizzler",
    "Flyfish",
    "Goldie",
    "Griller",
    "Maws",
    "Scrapper",
    "Steel Eel",
    "Steelhead",
    "Stinger")

players = ("player", "mate1", "mate2", "mate3")

def init() -> list:
    return json.load(open("salmon.json", "r", encoding='utf-8'))

def hasPlayer(player: str) -> bool:
    return lambda var: var["mate1_id"] == player or var["mate2_id"] == player or var["mate3_id"] == player

def hasPlayerByName(player: str) -> bool:
    return lambda var: var["mate1_name"] == player or var["mate2_name"] == player or var["mate3_name"] == player

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
    return lambda var: var["clear_wave"] == wave

def splatnet_number(num: int) -> bool:
    return lambda var: var["splatnet_number"] == num

def jobsCount(data: list) -> int:
    return len(data)

def avgStat(data: list, stat: str) -> float:
    return sum(d[stat] for d in data) / jobsCount(data)

def maxStat(data: list, stat: str) -> float:
    max = data[0][stat]
    for job in data:
        if (max < job[stat]):
            max = job[stat]
    return max

def minStat(data: list, stat: str) -> float:
    min = data[0][stat]
    for job in data:
        if (min > job[stat]):
            min = job[stat]
    return min

def medianStat(data: list, stat: str) -> float:
    return np.median([x[stat] for x in data])

def avgWaves(data: list) -> float:
    return avgStat(data, "clear_wave")

def clearPercentage(data: list) -> float:
    return sum(d["clear_wave"] == 3 for d in data) / jobsCount(data)
    
def waveTwoPercentage(data: list) -> float:
    return sum(d["clear_wave"] >= 2 for d in data) / jobsCount(data)

def waveOnePercentage(data: list) -> float:
    return sum(d["clear_wave"] >= 1 for d in data) / jobsCount(data)

def statSummary(data: list, stat: str) -> str:
    return str(avgStat(data, stat)) + " (" + str(minStat(data, stat)) + ", " + str(medianStat(data, stat)) + ", " + str(maxStat(data, stat)) + ")"

def sumStatWaves(data: list, stat: str) -> int:
    return data["w1_" + stat] + int(data["w2_" + stat] or 0) + int(data["w3_" + stat] or 0)

def getPlayersAttribute(data: list, attr: str, prefix = "") -> str:
    attrs = ""
    for p in players:
        attrs += "{:<16}\t".format(data[prefix + p + "_" + attr] or 0)
    return attrs

def getWavesAttribute(data: list, attr: str) -> str:
    attrs = ""
    for w in range(1, 4):
        attrs += "{:<16}\t".format(data["w"+ str(w) + "_" + attr] or 0)
    return attrs

def getBossDataStr(data: list, boss: str) -> str:
    return "{:<16}\t{:}".format(data[boss + "_appearances"] or 0, getPlayersAttribute(data, "kills", boss + "_"))
    return "{:<16}\t{:<16}\t{:<16}\t{:<16}\t{:<16}".format(data[boss + "_appearances"] or 0, data[boss + "_player_kills"] or 0, data[boss + "_mate1_kills"] or 0, data[boss + "_mate2_kills"] or 0, data[boss + "_mate3_kills"] or 0)

def getTotalBosses(data: list, player: str) -> int:
    return sum(int(data[boss.replace(" ", "_").lower() + "_" + player] or 0) for boss in bosses)

def printOverview(data: list) -> None:
    print("Jobs: " + str(jobsCount(data)))
    print("Average Waves: " + str(avgStat(data, "clear_wave")))
    print("Clear %: " + str(clearPercentage(data)))
    print("Wave 2 %: " + str(waveTwoPercentage(data)))
    print("Wave 1 %: " + str(waveOnePercentage(data)))
    print("Golden: "+ statSummary(data, "player_golden_eggs"))
    print("Power Eggs: " + statSummary(data, "player_power_eggs"))
    print("Rescued: " + statSummary(data, "player_rescues"))
    print("Deaths: " + statSummary(data, "player_rescued"))
    print("Hazard Level: "+ statSummary(data, "hazard_level"))

def printGeneral(data: list, user: str) -> None:
    print("Stat.ink Link: https://stat.ink/@" + user + "/salmon/" + str(data["# statink_id"]))
    print("Splatnet #: {:<}".format(data["splatnet_number"]))
    print("Stage: {:}".format(data["stage_name"]))
    print("Rotation #: " + str(data["rotation_period"]))
    print("Start Date: " + data["shift_start__1"])
    print("Result: {:}".format("Cleared" if data["clear_wave"] == 3 else "Failed"))
    print("Title: {:} {:<3} -> {:} {:<3}".format(data["title_before__1"], data["title_before__2"], data["title_after__1"], data["title_after__2"]))

def printWaves(data: dict) -> None:
    print("{:16}\t{:16}\t{:16}\t{:16}\t{:16}".format("", "Wave 1", "Wave 2", "Wave 3", "Total"))
    print("{:16}\t{:<}".format("Event", getWavesAttribute(data, "event__1")))
    print("{:16}\t{:<}".format("Water Level", getWavesAttribute(data, "water__1")))
    print("{:16}\t{:<}{:<16}".format("Quota", getWavesAttribute(data, "quota"), sumStatWaves(data, "quota")))
    print("{:16}\t{:<}{:<16}".format("Delivers", getWavesAttribute(data, "delivers"), sumStatWaves(data, "delivers")))
    print("{:16}\t{:<}{:<16}".format("Appearances", getWavesAttribute(data, "appearances"), sumStatWaves(data, "appearances")))
    print("{:16}\t{:<}{:<16}".format("Power Eggs", getWavesAttribute(data, "pwr_eggs"), sumStatWaves(data, "pwr_eggs")))

def printPlayers(data: dict) -> None:
    print("{:16}\t{:}".format("ID", getPlayersAttribute(data, "id")))
    print("{:16}\t{:}".format("Name", getPlayersAttribute(data, "name")))
    print("{:16}\t{:}".format("Wave 1 Weapon", getPlayersAttribute(data, "w1_weapon__1")))
    print("{:16}\t{:}".format("Wave 2 Weapon", getPlayersAttribute(data, "w2_weapon__1")))
    print("{:16}\t{:}".format("Wave 3 Weapon", getPlayersAttribute(data, "w3_weapon__1")))
    print("{:16}\t{:}".format("Special", getPlayersAttribute(data, "special__1")))
    print("{:16}\t{:1} - {:1} - {:1}\t\t{:1} - {:1} - {:1}\t\t{:1} - {:1} - {:1}\t\t{:1} - {:1} - {:1}".format("Special Usage", data["player_w1_sp_use"], data["player_w2_sp_use"], data["player_w3_sp_use"], data["mate1_w1_sp_use"], data["mate1_w2_sp_use"], data["mate1_w3_sp_use"], data["mate2_w1_sp_use"], data["mate2_w2_sp_use"], data["mate2_w3_sp_use"], data["mate3_w1_sp_use"], data["mate3_w2_sp_use"], data["mate3_w3_sp_use"]))
    print("{:16}\t{:}".format("Rescues", getPlayersAttribute(data, "rescues")))
    print("{:16}\t{:}".format("Deaths", getPlayersAttribute(data, "rescued")))
    print("{:16}\t{:}".format("Golden Eggs", getPlayersAttribute(data, "golden_eggs")))
    print("{:16}\t{:}".format("Power Eggs", getPlayersAttribute(data, "power_eggs")))

def printBosses(data: dict) -> None:
    print("{:16}\t{:16}\t{:}".format("Boss Salmonid", "Appearances", getPlayersAttribute(data, "name")))
    print("{:16}\t{:}".format("Drizzler", getBossDataStr(data, "drizzler")))
    print("{:16}\t{:}".format("Flyfish", getBossDataStr(data, "flyfish")))
    print("{:16}\t{:}".format("Goldie", getBossDataStr(data, "goldie")))
    print("{:16}\t{:}".format("Griller", getBossDataStr(data, "griller")))
    print("{:16}\t{:}".format("Maws", getBossDataStr(data, "maws")))
    print("{:16}\t{:}".format("Scrapper", getBossDataStr(data, "scrapper")))
    print("{:16}\t{:}".format("Steel Eel", getBossDataStr(data, "steel_eel")))
    print("{:16}\t{:}".format("Steelhead", getBossDataStr(data, "steelhead")))
    print("{:16}\t{:}".format("Stinger", getBossDataStr(data, "stinger")))
    total = "{:16}\t{:<16}".format("Total", getTotalBosses(data, "appearances"))
    for p in players:
        total += "\t{:<16}".format(getTotalBosses(data, p + "_kills"))
    print(total)

data = init()
printOverview(data)
print("")
job = random.choice(data)
printGeneral(job, "MunchingCass")
print("")
printWaves(job)
print("")
printPlayers(job)
print("")
printBosses(job)