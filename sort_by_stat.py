import core
from core import (
    hasJobs,
    locale,
    statSummary,
)
from objects import Job, Stage_WaterLevel_KnownOccurrence
import filters
import requests
import pprint
from typing import Tuple, List, Dict, Union, cast
import ujson
import zlib


def hasVal(var: List[Dict[str, str]], val) -> bool:
    """

    :param var:
    :type var: List[Dict[str, str]]
    :param val:

    """
    for item in var:
        if val == item["key"]:
            return True
    return False


def sortWeapons(data, stat) -> None:
    """

    :param data:
    :type data: str
    :param stat:
    :type stat: str

    """
    weaponsList: List[Dict[str, Union[str, Dict[str, str]]]] = requests.get(
        "https://stat.ink/api/v2/weapon"
    ).json()
    for grizzWeapon in core.grizzcoWeapons:
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
        filterPaths: Tuple[List[bytes], List[bytes]] = cast(
            Tuple[List[bytes], List[bytes]],
            filters.hasWeapons("mem", data, cast(List[str], [weapon["main_ref"]])),
        )
        withVal: List[bytes] = filterPaths[0]
        withoutVal: List[bytes] = filterPaths[1]
        if hasJobs("mem", withVal) and not hasVal(
            cast(List[Dict[str, str]], results), cast(str, weapon["main_ref"])
        ):
            if (hasJobs("mem", withVal)) and (hasJobs("mem", withoutVal)):
                result["key"] = cast(str, weapon["main_ref"])
                result["name"] = cast(Dict[str, str], weapon["name"])[locale]
                result["value"] = (
                    statSummary("mem", withVal, stat)[0]
                    - statSummary("mem", withoutVal, stat)[0]
                )
                results.append(result)
    pprint.pprint(sorted(results, key=lambda val: val["value"]))


def sortStages(data, stat) -> None:
    """

    ::param data:
    :type data: str
    :param stat:
    :type stat: str

    """
    stageDict: Dict[str, Dict[str, Union[str, float]]] = {}
    stageList: List[Dict[str, Union[str, float]]] = []
    for line in data:
        job = Job(**ujson.loads(zlib.decompress(line)))
        if job.has_stage():
            if not (
                getattr(cast(Stage_WaterLevel_KnownOccurrence, job.stage).name, locale)
                in stageDict
            ):
                stageDict[
                    getattr(
                        cast(Stage_WaterLevel_KnownOccurrence, job.stage).name,
                        locale,
                    )
                ] = {
                    "name": getattr(
                        cast(Stage_WaterLevel_KnownOccurrence, job.stage).name,
                        locale,
                    ),
                    stat: 0.0,
                    "count": 0.0,
                }
            cast(
                Dict[str, float],
                stageDict[
                    getattr(
                        cast(Stage_WaterLevel_KnownOccurrence, job.stage).name,
                        locale,
                    )
                ],
            )[stat] += cast(float, core.getValMultiDimensional(job, [stat]))
            cast(
                Dict[str, float],
                stageDict[
                    getattr(
                        cast(Stage_WaterLevel_KnownOccurrence, job.stage).name,
                        locale,
                    )
                ],
            )["count"] += 1.0
    for stage in stageDict.values():
        stageList.append(
            {
                "name": stage["name"],
                "value": cast(float, stage[stat]) / cast(float, stage["count"]),
            }
        )
    pprint.pprint(sorted(stageList, key=lambda val: val["value"]))


def sortSpecial(data, stat) -> None:
    """

    :param data:
    :type data: str
    :param stat:
    :type stat: str

    """
    specialDict: Dict[str, Dict[str, Union[str, float]]] = {}
    specialList: List[Dict[str, Union[str, float]]] = []
    for line in data:
        job = Job(**ujson.loads(zlib.decompress(line)))
        if not (getattr(job.my_data.special.name, locale) in specialDict):
            specialDict[getattr(job.my_data.special.name, locale)] = {
                "name": getattr(job.my_data.special.name, locale),
                stat: 0.0,
                "count": 0.0,
            }
        cast(Dict[str, float], specialDict[getattr(job.my_data.special.name, locale)],)[
            stat
        ] += cast(float, core.getValMultiDimensional(job, [stat]))
        cast(
            Dict[str, float],
            specialDict[getattr(job.my_data.special.name, locale)],
        )["count"] += 1.0
    for special in specialDict.values():
        specialList.append(
            {
                "name": special["name"],
                "value": cast(float, special[stat]) / cast(float, special["count"]),
            }
        )
    pprint.pprint(sorted(specialList, key=lambda val: val["value"]))


def sortRotation(data, stat) -> None:
    """
    Print the sorted rotations by the average of the given stat.

    :param data: the data file name
    :type data: str
    :param stat: the statistic to sort by
    :type stat: str

    """
    rotationList: List[int] = []
    rotationResultsList: List[
        Dict[str, Union[int, float, Union[None, Dict[str, Union[str, List[str]]]]]]
    ] = []
    for line in data:
        job = Job(**ujson.loads(zlib.decompress(line)))
        if job.shift_start_at.time not in rotationList:
            rotationList.append(job.shift_start_at.time)
    for rotation in rotationList:
        print(rotation)
        result: Dict[
            str, Union[int, float, Union[None, Dict[str, Union[str, List[str]]]]]
        ] = {}
        filterPaths: Tuple[List[bytes], List[bytes]] = cast(
            Tuple[List[bytes], List[bytes]],
            filters.duringRotationInts("mem", data, [rotation]),
        )
        withVal: List[bytes] = filterPaths[0]
        withoutVal: List[bytes] = filterPaths[1]
        if hasJobs("mem", withVal):
            if (hasJobs("mem", withVal)) and (hasJobs("mem", withoutVal)):
                result["name"] = rotation
                result["data"] = core.findWeaponsAndStageByRotation(
                    "mem", withVal, rotation
                )
                result["value"] = (
                    statSummary("mem", withVal, stat)[0]
                    - statSummary("mem", withoutVal, stat)[0]
                )
                rotationResultsList.append(result)
    pprint.pprint(
        sorted(rotationResultsList, key=lambda val: cast(float, val["value"]))
    )


if __name__ == "__main__":
    # fullPath: str = core.init("User", "disk", ujson.load(open("keys.json", "r"))["statink_key"])
    fullPath: str = cast(str, core.init("All", "disk"))
    # sortStages(core.loadJobsFromFile(fullPath), "clear_waves")
    sortWeapons(core.loadJobsFromFile(fullPath), "clear_waves")
    # sortSpecial(core.loadJobsFromFile(fullPath), "clear_waves")
    # sortRotation(core.loadJobsFromFile(fullPath), "clear_waves")
