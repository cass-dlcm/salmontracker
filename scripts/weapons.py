import core
from objects import Job
import filters
from core import locale
import jsonlines
import ujson
import gzip
import requests
from typing import Dict, List, Union, cast
import pprint
from itertools import combinations
from scipy.stats import ttest_ind
import numpy as np
import zlib


dataFile = cast(str, core.init("All", "data/"))
data = core.loadJobsFromFile(dataFile)
weaponsList: List[Dict[str, Union[str, Dict[str, str]]]] = requests.get(
    "https://stat.ink/api/v2/weapon"
).json()
for grizzWeapon in core.grizzcoWeapons:
    new = {
        "name": {locale: grizzWeapon[0]},
        "key": grizzWeapon[1],
        "main_ref": grizzWeapon[1],
        "type": {"key": grizzWeapon[2]},
    }
    cast(List[Dict[str, Dict[str, str]]], weaponsList).append(
        cast(Dict[str, Dict[str, str]], new)
    )
typesList: List[str] = []
for weapon in weaponsList:
    if cast(Dict[str, str], weapon["type"])["key"] not in typesList:
        typesList.append(cast(Dict[str, str], weapon["type"])["key"])
typeCombinations = combinations(typesList, 4)
typeComboDict: dict = {}
clear_waves = []
for line in data:
    job = Job(**ujson.loads(zlib.decompress(line)))
    clear_waves.append(job.clear_waves)
clear_waves_std = np.std(clear_waves)
for combo in typeCombinations:
    result = filters.hasWeaponTypes("mem", data, combo, "and")
    typeComboDict[combo] = {
        "key": "",
        "clear_waves": [],
        "not_clear_waves": [],
        "t": 0.0,
        "p": 0.0,
        "x\u0304_1 - x\u0304_2": 0.0,
        "d": 0.0,
    }
    typeComboDict[combo]["key"] = combo
    typeComboDict[combo]["clear_waves"] = core.getArrayOfStat(
        "mem", result[0], "clear_waves"
    )
    typeComboDict[combo]["not_clear_waves"] = core.getArrayOfStat(
        "mem", result[1], "clear_waves"
    )
    typeComboDict[combo]["t"], typeComboDict[combo]["p"] = ttest_ind(
        typeComboDict[combo]["clear_waves"],
        typeComboDict[combo]["not_clear_waves"],
        equal_var=False,
    )
    typeComboDict[combo]["x\u0304_1 - x\u0304_2"] = np.mean(
        typeComboDict[combo]["clear_waves"]
    ) - np.mean(typeComboDict[combo]["not_clear_waves"])
    typeComboDict[combo]["d"] = (
        typeComboDict[combo]["x\u0304_1 - x\u0304_2"] / clear_waves_std
    )
    typeComboDict[combo]["clear_waves"] = None
    typeComboDict[combo]["not_clear_waves"] = None
with open("reports/weaponTypes.txt", "wt", encoding="utf-8") as out:
    pprint.pprint(
        sorted(
            list(typeComboDict.values()),
            key=lambda val: cast(float, val["x\u0304_1 - x\u0304_2"]),
        ),
        stream=out,
    )
