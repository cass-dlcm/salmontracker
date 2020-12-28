import os.path
import ujson
import numpy as np
import requests
import jsonlines
import sys
from typing import Tuple, List, Union, Dict, cast, Optional, Callable, Any
import gzip
import shutil
from objects import Job, Stage_WaterLevel_KnownOccurrence

locale = "en_US"

grizzcoWeapons = (
    ("Grizzco Charger", "kuma_charger", "charger"),
    ("Grizzco Brella", "kuma_brella", "brella"),
    ("Grizzco Blaster", "kuma_blaster", "blaster"),
    ("Grizzco Slosher", "kuma_slosher", "slosher"),
)


def hasJobs(data) -> bool:
    """
    Check if a given data file has data.

    :param data: the full path of the data file
    :type data: str
    :return: whether the file has jobs or not
    :rtype: bool
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> core.hasJobs("data/salmon.jl.gz")
    True
    >>> import gzip
    >>> with gzip.open("temp.jl.gz", "at", encoding="utf8") as writer:
    ...     writer.write("")
    ...
    >>> core.hasJobs("temp.jl.gz")
    False

    """
    try:
        with gzip.open(data) as reader:
            jsonlines.Reader(reader, ujson.loads).read()
            return True
    except EOFError:
        return False


def listAllUsers(data) -> List[str]:
    """

    :param data:
    :type data: str

    """
    result: List[str] = []
    with gzip.open(data) as reader:
        for line in reader:
            job = Job(**ujson.loads(line))
            if job.my_data.splatnet_id not in result:
                result.append(job.my_data.splatnet_id)
    return result


def findRotationByWeaponsAndStage(data: str, **kargs) -> List[int]:
    """
    Find the rotation IDs for a rotation of the given weapons and stage in the given data file.

    :param data: str: the full path of the data file
    :type data: str
    :param weapons: the chosen weapons
    :type weapons: Union[Tuple[str, str, str, str], List[str]]
    :param stage: str: the chosen stage
    :type stage: str
    :return: a list of rotation IDs
    :rtype: List[int]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> findRotationByWeaponsAndStage(
    ...     "data/salmon.jl.gz",
    ...     (
    ...         "Grizzco Charger",
    ...         "Grizzco Blaster",
    ...         "Grizzco Slosher",
    ...         "Grizzco Brella"
    ...     ),
    ...     "Ruins of Ark Polaris"
    ... )
    [1563537600, 1607752800]

    """
    foundRotations: List[int] = []
    with gzip.open(data) as reader:
        for line in reader:
            job = Job(**ujson.loads(line))
            found = kargs.get("stage") is None or (
                job.stage is not None
                and kargs.get("stage")
                in (
                    job.stage.key,
                    getattr(job.stage.name, locale),
                )
            )
            if kargs.get("weapons") is not None:
                for weapon in cast(List[str], kargs.get("weapons")):
                    found = found and (
                        job.my_data.weapons[0].key == weapon
                        or (
                            len(job.my_data.weapons) > 1
                            and job.my_data.weapons[1].key == weapon
                        )
                        or (
                            len(job.my_data.weapons) > 2
                            and job.my_data.weapons[2].key == weapon
                        )
                        or (
                            job.teammates is not None
                            and (
                                (
                                    len(job.teammates) > 0
                                    and job.teammates[0].weapons is not None
                                    and (
                                        job.teammates[0].weapons[0].key == weapon
                                        or (
                                            len(job.teammates[0].weapons) > 1
                                            and job.teammates[0].weapons[1].key
                                            == weapon
                                        )
                                        or (
                                            len(job.teammates[0].weapons) > 2
                                            and job.teammates[0].weapons[2].key
                                            == weapon
                                        )
                                    )
                                )
                                or (
                                    len(job.teammates) > 1
                                    and job.teammates[1].weapons is not None
                                    and (
                                        job.teammates[1].weapons[0].key == weapon
                                        or (
                                            len(job.teammates[1].weapons) > 1
                                            and job.teammates[1].weapons[1].key
                                            == weapon
                                        )
                                        or (
                                            len(job.teammates[1].weapons) > 2
                                            and job.teammates[1].weapons[2].key
                                            == weapon
                                        )
                                    )
                                )
                                or (
                                    len(job.teammates) > 2
                                    and job.teammates[2].weapons is not None
                                    and (
                                        job.teammates[2].weapons[0].key == weapon
                                        or (
                                            len(job.teammates[2].weapons) > 1
                                            and job.teammates[2].weapons[1].key
                                            == weapon
                                        )
                                        or (
                                            len(job.teammates[2].weapons) > 2
                                            and job.teammates[2].weapons[2].key
                                            == weapon
                                        )
                                    )
                                )
                            )
                        )
                        or getattr(job.my_data.weapons[0].name, locale) == weapon
                        or (
                            len(job.my_data.weapons) > 1
                            and getattr(job.my_data.weapons[1].name, locale) == weapon
                        )
                        or (
                            len(job.my_data.weapons) > 2
                            and getattr(job.my_data.weapons[2].name, locale) == weapon
                        )
                        or (
                            job.teammates is not None
                            and (
                                (
                                    len(job.teammates) > 0
                                    and job.teammates[0].weapons is not None
                                    and (
                                        getattr(
                                            job.teammates[0].weapons[0].name, locale
                                        )
                                        == weapon
                                        or (
                                            len(job.teammates[0].weapons) > 1
                                            and getattr(
                                                job.teammates[0].weapons[1].name, locale
                                            )
                                            == weapon
                                        )
                                        or (
                                            len(job.teammates[0].weapons) > 2
                                            and getattr(
                                                job.teammates[0].weapons[2].name, locale
                                            )
                                            == weapon
                                        )
                                    )
                                )
                                or (
                                    len(job.teammates) > 1
                                    and job.teammates[1].weapons is not None
                                    and (
                                        getattr(
                                            job.teammates[1].weapons[0].name, locale
                                        )
                                        == weapon
                                        or (
                                            len(job.teammates[1].weapons) > 1
                                            and getattr(
                                                job.teammates[1].weapons[1].name, locale
                                            )
                                            == weapon
                                        )
                                        or (
                                            len(job.teammates[1].weapons) > 2
                                            and getattr(
                                                job.teammates[1].weapons[2].name, locale
                                            )
                                            == weapon
                                        )
                                    )
                                )
                                or (
                                    len(job.teammates) > 0
                                    and job.teammates[2].weapons is not None
                                    and (
                                        getattr(
                                            job.teammates[2].weapons[0].name, locale
                                        )
                                        == weapon
                                        or (
                                            len(job.teammates[2].weapons) > 1
                                            and getattr(
                                                job.teammates[2].weapons[1].name, locale
                                            )
                                            == weapon
                                        )
                                        or (
                                            len(job.teammates[2].weapons) > 2
                                            and getattr(
                                                job.teammates[2].weapons[2].name, locale
                                            )
                                            == weapon
                                        )
                                    )
                                )
                            )
                        )
                    )
            if found and job.shift_start_at.time not in foundRotations:
                foundRotations.append(job.shift_start_at.time)
    return foundRotations


def findWeaponsAndStageByRotation(data, rotation) -> Dict[str, Union[str, List[str]]]:
    """
    Find the weapons and stage for a given rotation.

    :param data: the full path of the data file
    :type data: str
    :param rotation: the unix time of the rotation start
    :type rotation: int
    :return: the weapons and stage for that rotation
    :rtype: Dict[str, Union[str, List[str]]]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> core.findWeaponsAndStageByRotation(
    ...     "data/salmonAll.jl.gz",
    ...     1607752800
    ... )
    {
        'stage': 'Ruins of Ark Polaris',
        'weapons': [
            'Grizzco Brella',
            'Grizzco Blaster',
            'Grizzco Charger',
            'Grizzco Slosher'
        ]
    }

    """
    result: Dict[str, Union[str, List[str]]] = {}
    with gzip.open(data) as reader:
        for line in reader:
            job = Job(**ujson.loads(line))
            if job.shift_start_at.time == rotation:
                if isinstance(job.stage, Stage_WaterLevel_KnownOccurrence):
                    result["stage"] = getattr(job.stage.name, locale)
                result["weapons"] = []
                if job.my_data.weapons is not None:
                    for weapon in job.my_data.weapons:
                        if getattr(weapon.name, locale) not in result["weapons"]:
                            cast(Dict[str, List[str]], result)["weapons"].append(
                                getattr(weapon.name, locale)
                            )
                for teammate in job.teammates:
                    if teammate.weapons is not None:
                        for weapon in teammate.weapons:
                            if getattr(weapon.name, locale) not in result["weapons"]:
                                cast(Dict[str, List[str]], result)["weapons"].append(
                                    getattr(weapon.name, locale)
                                )
    return result


def findPlayerIdByName(data, player) -> List[str]:
    """
    Find all the recorded player IDs for a given player name.

    :param data: the full name of the data file
    :type data: str
    :param player: the player name to find
    :type player: str
    :return: the list of found player IDs
    :rtype: List[str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    >>> import core
    >>> core.findPlayerIdByName("data/salmonAll.jl.gz", "CassTheFae")
    ['aeda69d2070fafb6']

    """
    foundIds: List[str] = []
    with gzip.open(data) as reader:
        for line in reader:
            job = Job(**ujson.loads(line))
            if job.my_data.name == player and job.my_data.splatnet_id not in foundIds:
                foundIds.append(job.my_data.splatnet_id)
            if job.teammates is not None:
                for teammate in job.teammates:
                    if teammate.name == player and teammate.splatnet_id not in foundIds:
                        foundIds.append(teammate.splatnet_id)
    return foundIds


def getValMultiDimensional(data, statArr: List[Union[str, int]]) -> str:
    """
    Retrieve the chosen stat from the provided data structure, using recursion.

    :param data: the data structure to retrieve data from
    :type data: Union[list, Dict[str, Any]]
    :param statArr: the list of dimensions of the data structure needed to retrieve the stat
    :type statArr: statArr: List[Union[str, int]
    :return: the value retrieved
    :rtype: str

    """
    if data is None:
        return ""
    if len(statArr) > 1:
        if isinstance(statArr[0], int):
            if len(data) > statArr[0]:
                return getValMultiDimensional(data[statArr[0]], statArr[1:])
            return ""
        return getValMultiDimensional(getattr(data, statArr[0]), statArr[1:])
    if isinstance(statArr[0], int):
        if len(data) > statArr[0]:
            return data[statArr[0]]
        return ""
    return getattr(data, statArr[0])


def statSummary(data, stat) -> Tuple[float, float, float, float]:
    """
    Find the average, min, median, and max of a stat given a data file

    :param data: str: The full file path of the data file
    :param stat: str: The stat
    :return: The resulting average, min, median, and max
    :rtype: Tuple[float, float, float, float]

    """
    with gzip.open(data) as reader:
        statArr: List[str] = stat.split()
        sumVal: float = 0.0
        maxVal: float = 0.0
        minVal: float = sys.float_info.max
        vals: List[float] = []
        count: float = 0.0
        for job in jsonlines.Reader(reader, ujson.loads):
            val = float(
                getValMultiDimensional(
                    job,
                    list(map(lambda ele: int(ele) if ele.isdigit() else ele, statArr)),
                )
            )
            sumVal += val
            count += 1.0
            maxVal = max(maxVal, val)
            minVal = min(minVal, val)
            vals.append(val)
        return (sumVal / count, minVal, np.median(vals), maxVal)


def waveClearPercentageWithWeapon(data, weapon):
    """

    :param data:
    :type data: str
    :param weapon:
    :type weapon: str
    :return:
    :rtype: float

    """
    with gzip.open(data) as reader:
        sumVal: float = 0.0
        count: float = 0.0
        for line in reader:
            job = Job(**ujson.loads(line))
            sumVal += int(
                (
                    weapon
                    in (
                        job.my_data.weapons[0].key,
                        getattr(job.my_data.weapons[0].name, locale),
                    )
                    and job["clear_waves"] > 0
                )
                or (
                    len(job.my_data.weapons) > 1
                    and weapon
                    in (
                        job.my_data.weapons[1].key,
                        getattr(job.my_data.weapons[1].name, locale),
                    )
                    and job.clear_waves > 1
                )
                or (
                    len(job.my_data.weapons) > 2
                    and weapon
                    in (
                        job.my_data.weapons[2].key,
                        getattr(job.my_data.weapons[2].name, locale),
                    )
                    and job.clear_waves > 2
                )
            )
            count += int(
                weapon
                in (
                    job.my_data.weapons[0].key,
                    getattr(job.my_data.weapons[0].name, locale),
                )
                or (
                    len(job.my_data.weapons) > 1
                    and weapon
                    in (
                        job.my_data.weapons[1].key,
                        getattr(job.my_data.weapons[1].name, locale),
                    )
                )
                or (
                    len(job.my_data.weapons) > 2
                    and weapon
                    in (
                        job.my_data.weapons[2].key,
                        getattr(job.my_data.weapons[2].name, locale),
                    )
                )
            )
        return sumVal / count


def sumStatWaves(data: Job, stat) -> int:
    """

    :param data:
    :type data: Job
    :param stat:
    :type stat: str
    :return:
    :rtype: int

    """
    sumVal: int = 0
    for w in data.waves:
        sumVal += getattr(w, stat)
    return sumVal


def getPlayersAttribute(data: Job, attr) -> List[str]:
    """

    :param data:
    :type data: Job
    :param attr:
    :type attr: str
    :return:
    :rtype: List[float]

    """
    attrsList: List[str] = attr.split()
    attrs: List[str] = [
        getValMultiDimensional(
            data.my_data,
            list(map(lambda ele: int(ele) if ele.isdigit() else ele, attrsList)),
        )
    ]
    for p in data.teammates:
        attrs.append(
            getValMultiDimensional(
                p, list(map(lambda ele: int(ele) if ele.isdigit() else ele, attrsList))
            )
        )
    return attrs


def getWavesAttribute(data: Job, attr) -> str:
    """

    :param data:
    :type data: Job
    :param attr:
    :type attr: str
    :return:
    :rtype: str

    """
    attrs: str = ""
    attrsList: List[str] = attr.split()
    for i in range(0, 3):
        if i < len(data.waves):
            attrs += "{:<16}\t".format(
                getValMultiDimensional(
                    data.waves[i],
                    list(
                        map(lambda ele: int(ele) if ele.isdigit() else ele, attrsList)
                    ),
                )
                or 0
            )
        else:
            attrs += "{:<16}\t".format("")
    return attrs


def getOverview(data) -> str:
    """

    :param data:
    :type data: str

    """
    result = data + "\n"
    stats = [
        "clear_waves",
        "my_data golden_egg_delivered",
        "my_data power_egg_collected",
        "my_data rescue",
        "my_data death",
        "danger_rate",
    ]
    with gzip.open(data) as reader:
        clearCount: float = 0.0
        waveTwoCount: float = 0.0
        waveOneCount: float = 0.0
        sumVal: List[float] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        maxVal: List[float] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        minVal: List[float] = [
            sys.float_info.max,
            sys.float_info.max,
            sys.float_info.max,
            sys.float_info.max,
            sys.float_info.max,
            sys.float_info.max,
        ]
        vals: List[List[float]] = [[], [], [], [], [], []]
        count: int = 0
        for line in reader:
            job = Job(**ujson.loads(line))
            count += 1
            clearCount += float(job.clear_waves == 3)
            waveTwoCount += float(job.clear_waves >= 2)
            waveOneCount += float(job.clear_waves >= 1)
            for i in range(0, len(stats)):
                val = float(
                    getValMultiDimensional(
                        job,
                        cast(List[Union[str, int]], stats[i].split()),
                    )
                )
                sumVal[i] += val
                maxVal[i] = max(maxVal[i], val)
                minVal[i] = min(minVal[i], val)
                vals[i].append(val)
    result += "Jobs: " + str(count) + "\n"
    result += "Average Waves: " + str(sumVal[0] / count) + "\n"
    result += "Clear %: " + str(clearCount / count) + "\n"
    result += "Wave 2 %: " + str(waveTwoCount / count) + "\n"
    result += "Wave 1 %: " + str(waveOneCount / count) + "\n"
    result += "Golden: {} ({}, {}, {}\n".format(
        sumVal[1] / count, minVal[1], np.median(vals[1]), maxVal[1]
    )
    result += "Power Eggs: {} ({}, {}, {})\n".format(
        sumVal[2] / count, minVal[2], np.median(vals[2]), maxVal[2]
    )
    result += "Rescued: {} ({}, {}, {})\n".format(
        sumVal[3] / count, minVal[3], np.median(vals[3]), maxVal[3]
    )
    result += "Deaths: {} ({}, {}, {})\n".format(
        sumVal[4] / count, minVal[4], np.median(vals[4]), maxVal[4]
    )
    result += "Hazard Level: {} ({}, {}, {})\n".format(
        sumVal[5] / count, minVal[5], np.median(vals[5]), maxVal[5]
    )
    return result


def printGeneral(data: Job) -> None:
    """

    :param data:
    :type data: Job

    """
    print("Stat.ink Link: {}".format(data.url))
    print("Splatnet #: {}".format(data.splatnet_number))
    if data.stage is not None:
        print("Stage: {}".format(getattr(data.stage.name, locale)))
    print("Rotation Start Date: {}".format(data.shift_start_at.iso8601))
    print("Start Date: {}".format(data.start_at.iso8601))
    print("Result: {}".format("Cleared" if data.clear_waves == 3 else "Failed"))
    print(
        "Title: {} {:<3} -> {} {:<3}".format(
            getattr(data.title.name, locale) if data.title else "",
            data.title_exp,
            getattr(data.title_after.name, locale) if data.title_after else "",
            data.title_exp_after,
        )
    )


def printWaves(data: Job) -> None:
    """

    :param data:
    :type data: Job

    """
    print(
        "{:16}\t{:16}\t{:16}\t{:16}\t{:16}".format(
            "", "Wave 1", "Wave 2", "Wave 3", "Total"
        )
    )
    print(
        "{:16}\t{:<}".format(
            "Event", getWavesAttribute(data, "known_occurrence name " + locale)
        )
    )
    print(
        "{:16}\t{:<}".format(
            "Water Level", getWavesAttribute(data, "water_level name " + locale)
        )
    )
    print(
        "{:16}\t{:<}{:<16}".format(
            "Quota",
            getWavesAttribute(data, "golden_egg_quota"),
            sumStatWaves(data, "golden_egg_quota"),
        )
    )
    print(
        "{:16}\t{:<}{:<16}".format(
            "Delivers",
            getWavesAttribute(data, "golden_egg_delivered"),
            sumStatWaves(data, "golden_egg_delivered"),
        )
    )
    print(
        "{:16}\t{:<}{:<16}".format(
            "Appearances",
            getWavesAttribute(data, "golden_egg_appearances"),
            sumStatWaves(data, "golden_egg_appearances"),
        )
    )
    print(
        "{:16}\t{:<}{:<16}".format(
            "Power Eggs",
            getWavesAttribute(data, "power_egg_collected"),
            sumStatWaves(data, "power_egg_collected"),
        )
    )


def printWeapons(data: Job) -> None:
    """

    :param data:
    :type data: Job

    """
    for i in range(
        0,
        len(data.my_data.weapons),
    ):
        weapons = getPlayersAttribute(data, "weapons " + str(i) + " name " + locale)
        print(
            "{:16}".format(
                "Wave {:1} Weapon".format(i + 1),
            )
        )
        for player in weapons:
            print("\t{:16}".format(player))


def printSpecials(data: Job) -> None:
    """

    :param data:
    :type data: Job

    """
    for i in range(0, len(data.my_data.special_uses)):
        print(
            "{:16}\t{:}".format(
                "Wave {:1} Special Use".format(i + 1),
                getPlayersAttribute(data, "special_uses " + str(i)),
            )
        )


def printPlayers(data: Job) -> None:
    """

    :param data:
    :type data: Job

    """
    print(
        "{:16}\t{:}".format(
            "ID",
            getPlayersAttribute(
                data,
                "splatnet_id",
            ),
        )
    )
    print(
        "{:16}\t{:}".format(
            "Name",
            getPlayersAttribute(
                data,
                "name",
            ),
        )
    )
    printWeapons(data)
    print(
        "{:16}\t{:}".format(
            "Special",
            getPlayersAttribute(
                data,
                "special name " + locale,
            ),
        )
    )
    printSpecials(data)
    print(
        "{:16}\t{:}".format(
            "Rescues",
            getPlayersAttribute(
                data,
                "rescue",
            ),
        )
    )
    print(
        "{:16}\t{:}".format(
            "Deaths",
            getPlayersAttribute(
                data,
                "death",
            ),
        )
    )
    print(
        "{:16}\t{:}".format(
            "Golden Eggs",
            getPlayersAttribute(
                data,
                "golden_egg_delivered",
            ),
        )
    )
    print(
        "{:16}\t{:}".format(
            "Power Eggs",
            getPlayersAttribute(
                data,
                "power_egg_collected",
            ),
        )
    )


def getBosses(data: Job) -> List[Union[Dict[str, str], Dict[str, int]]]:
    """

    :param data:
    :type data: Job
    :return:
    :rtype: List[Union[Dict[str, str], Dict[str, int]]]

    """
    results: List[Union[Dict[str, str], Dict[str, int]]] = []
    names: Dict[str, str] = {}
    appearances: Dict[str, int] = {"": 0}
    if data.boss_appearances is None:
        return results
    for boss in range(0, len(data.boss_appearances)):
        names[getattr(data.boss_appearances[boss].boss.name, locale)] = getattr(
            data.boss_appearances[boss].boss.name, locale
        )
        appearances[
            getattr(data.boss_appearances[boss].boss.name, locale)
        ] = data.boss_appearances[boss].count
        results.append(names)
    results.append(appearances)
    my_data: Dict[str, int] = {"": 0}
    if data.my_data.boss_kills is not None:
        for boss in range(0, len(data.my_data.boss_kills)):
            my_data[
                getattr(data.my_data.boss_kills[boss].boss.name, locale)
            ] = data.my_data.boss_kills[boss].count
    results.append(my_data)
    for teammate in range(0, len(data.teammates)):
        teammate_data: Dict[str, int] = {"": 0}
        if data.teammates[teammate].boss_kills is not None:
            for boss in range(0, len(data.teammates[teammate].boss_kills)):
                my_data[
                    getattr(data.teammates[teammate].boss_kills[boss].boss.name, locale)
                ] = (data.teammates[teammate].boss_kills[boss].count)
        results.append(teammate_data)
    return results


def getSingleJob(data, index=0) -> Optional[Job]:
    """

    :param data: the full name of the data file
    :type data: str
    :param index: the index in the list of the job to find
    :type index: int
    :return: either the found job or None if there isn't a job at that index
    :rtype: Optional[Job]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist

    """
    count = 0
    with gzip.open(data) as reader:
        for line in reader:
            if count == index:
                return Job(**ujson.loads(line))
            count += 1
    return None


def printBosses(data: Job) -> None:
    """

    :param data: the job to print boss information for
    :type data: Job

    :Example:

    >>> import core
    >>> core.printBosses(core.getSingleJob("data/salmonAll.jl.gz", 0))
    Boss Salmonid           Appearances             eli                     Razzle                  slum                    Chito
    Goldie                  3                       1                       0                       0                       0
    Steelhead               10                      4                       0                       0                       0
    Flyfish                 4                       1                       0                       0                       0
    Scrapper                8                       1                       0                       0                       0
    Steel Eel               6                       3                       0                       0                       0
    Stinger                 7                       3                       0                       0                       0
    Maws                    5                       2                       0                       0                       0
    Drizzler                5                       3                       0                       0                       0

    """
    names = getPlayersAttribute(data, "name")
    namesStr = "{:16}\t{:16}".format("Boss Salmonid", "Appearances")
    for name in names:
        namesStr += "\t{:16}".format(name)
    print(namesStr)
    bosses: List[Union[Dict[str, str], Dict[str, int]]] = getBosses(data)
    if len(bosses) > 0:
        listBosses: List[str] = list(bosses[0])
        for boss in range(0, len(bosses[0])):
            print(
                "{:16}\t{:<16}\t{:<16}\t{:<16}\t{:<16}\t{:<16}".format(
                    bosses[0][listBosses[boss]],
                    bosses[1][listBosses[boss]]
                    if listBosses[boss] in bosses[1]
                    else "0",
                    bosses[2][listBosses[boss]]
                    if listBosses[boss] in bosses[2]
                    else "0",
                    bosses[3][listBosses[boss]]
                    if (len(bosses) > 3 and listBosses[boss] in bosses[3])
                    else "0",
                    bosses[4][listBosses[boss]]
                    if (len(bosses) > 4 and listBosses[boss] in bosses[4])
                    else "0",
                    bosses[5][listBosses[boss]]
                    if (len(bosses) > 5 and listBosses[boss] in bosses[5])
                    else "0",
                )
            )


def getArrayOfStat(data, stat) -> List[float]:
    """
    Collect all the values of a single stat for a given list of jobs.

    :param data: the full path to the data file
    :type data: str
    :param stat: the stat to retrieve
    :type stat: str
    :return: the stat for each job in the data
    :rtype: List[float]

    :Example:

    >>> import core
    >>> min(core.getArrayOfStat("data/salmonAll.jl.gz", "quota 0"))
    3.0

    """
    with gzip.open(data) as reader:
        results = []
        for line in reader:
            job = Job(**ujson.loads(line))
            results.append(
                float(
                    getValMultiDimensional(
                        job,
                        cast(
                            List[Union[str, int]],
                            list(
                                map(
                                    lambda ele: int(ele) if ele.isdigit() else ele,
                                    stat.split(),
                                )
                            ),
                        ),
                    )
                )
            )
        return results


def init(mode, api_key="") -> str:
    """
    Fetch the data sets from stat.ink

    :param mode: whether to fetch data for all users or a single user
    :type mode: str
    :param api_key: the stat.ink API key for the user to fetch
    :type api_key: str
    :return: the resulting data file path
    :rtype: str

    :Example:

    >>> import core
    >>> core.init("All")
    'data/salmonAll.jl.gz'
    >>> import ujson
    >>> core.init(
    ...     "User",
    ...     ujson.load(
    ...         open(
    ...             "keys.json",
    ...             "r"
    ...         )
    ...     )["statink_key"]
    ... )
    'data/salmon.jl.gz'

    """
    headers: Dict[str, str] = {}
    if mode == "All":
        fileName: str = "data/salmonAll.jl.gz"
        url: str = "http://stat.ink/api/v2/salmon"
    elif mode == "User":
        fileName = "data/salmon.jl.gz"
        url = "http://stat.ink/api/v2/user-salmon"
        headers = {"Authorization": "Bearer {}".format(api_key)}
    if os.path.exists(fileName):
        recentId = 0
        try:
            with gzip.open(fileName) as reader:
                try:
                    os.remove(fileName[0:-6] + "Temp.jl.gz")
                except FileNotFoundError:
                    pass
                with gzip.open(
                    fileName[0:-6] + "Temp.jl.gz", "at", encoding="utf8"
                ) as writer:
                    for line in jsonlines.Reader(reader, ujson.loads):
                        ujson.dump(line, writer)
                        writer.write("\n")
                        recentId = line["id"]
            os.remove(fileName[0:-6] + "Temp.jl.gz")
        except jsonlines.jsonlines.InvalidLineError:
            os.replace(fileName[0:-6] + "Temp.jl.gz", fileName)
        prevLastId: int = 0
        params: Dict[str, str] = {"order": "asc", "newer_than": str(recentId)}
        temp: List[Job] = requests.get(url, headers=headers, params=params).json()
        if len(temp) > 0:
            try:
                shutil.rmtree(fileName[0:-6])
            except FileNotFoundError:
                pass
            lastId: int = cast(List[Dict[str, int]], temp)[-1]["id"]
            print(lastId)
            with gzip.open(fileName, "at", encoding="utf8") as writer:
                while lastId != prevLastId:
                    for job in temp:
                        ujson.dump(job, writer)
                        writer.write("\n")
                    params["newer_than"] = str(lastId)
                    result = requests.get(
                        url,
                        headers=headers,
                        params=params,
                    )
                    print(result.url)
                    print(result)
                    temp = result.json()
                    prevLastId = lastId
                    if len(temp) > 0:
                        lastId = cast(List[Dict[str, int]], temp)[-1]["id"]
                    print(lastId)
    else:
        prevLastId = 0
        params = {"order": "asc"}
        temp = requests.get(url, headers=headers, params=params).json()
        lastId = cast(List[Dict[str, int]], temp)[-1]["id"]
        print(lastId)
        with gzip.open(fileName, "at", encoding="utf8") as writer:
            while lastId != prevLastId:
                for job in temp:
                    ujson.dump(job, writer)
                    writer.write("\n")
                params["newer_than"] = str(lastId)
                result = requests.get(url, headers=headers, params=params)
                print(result.url)
                print(result)
                temp = result.json()
                prevLastId = lastId
                if len(temp) > 0:
                    lastId = cast(List[Dict[str, int]], temp)[-1]["id"]
                print(lastId)
    return fileName


def loadJobsFromFile(data) -> List[Job]:
    jobs: List[Job] = []
    with gzip.open(data, "r") as reader:
        for line in reader:
            jobs.append(Job(**ujson.loads(line)))
    return jobs
