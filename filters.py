from core import hasJobs, locale, grizzcoWeapons
from objects import Job
import os.path
from typing import Tuple, List, Callable, Dict, Union, cast
import gzip
import json
import ujson
import zlib
import requests


def filterJobs(
    location, data, filterFunction: Callable, outpath
) -> Union[Tuple[str, str], Tuple[List[bytes], List[bytes]]]:
    if location == "disk":
        if not (
            os.path.exists(data[0:-6] + "/" + outpath + ".jl.gz")
            and os.path.exists(data[0:-6] + "/not" + outpath + ".jl.gz")
        ):
            with gzip.open(data) as reader:
                if hasJobs("disk", data):
                    with gzip.open(
                        data[0:-6] + "/" + outpath + ".jl.gz",
                        "at",
                        encoding="utf8",
                    ) as writerA:
                        with gzip.open(
                            data[0:-6] + "/not" + outpath + ".jl.gz",
                            "at",
                            encoding="utf8",
                        ) as writerB:
                            for line in reader:
                                job = Job(**ujson.loads(line))
                                if filterFunction(job):
                                    json.dump(
                                        job, writerA, default=lambda x: x.__dict__
                                    )
                                    writerA.write("\n")
                                else:
                                    json.dump(
                                        job, writerB, default=lambda x: x.__dict__
                                    )
                                    writerB.write("\n")
        return (
            data[0:-6] + "/" + outpath + ".jl.gz",
            data[0:-6] + "/not" + outpath + ".jl.gz",
        )
    jobsWith: List[bytes] = []
    jobsWithout: List[bytes] = []
    for line in data:
        job = Job(**ujson.loads(zlib.decompress(line)))
        if filterFunction(job):
            jobsWith.append(line)
        else:
            jobsWithout.append(line)
    return (jobsWith, jobsWithout)


def filterJobsOr(
    location, data, filterFunctions: List[Callable], outpath
) -> Union[Tuple[str, str], Tuple[List[bytes], List[bytes]]]:
    if location == "disk":
        if not (
            os.path.exists(data[0:-6] + "/" + outpath + ".jl.gz")
            and os.path.exists(data[0:-6] + "/not" + outpath + ".jl.gz")
        ):
            with gzip.open(data) as reader:
                if hasJobs("disk", data):
                    with gzip.open(
                        data[0:-6] + "/" + outpath + ".jl.gz",
                        "at",
                        encoding="utf8",
                    ) as writerA:
                        with gzip.open(
                            data[0:-6] + "/not" + outpath + ".jl.gz",
                            "at",
                            encoding="utf8",
                        ) as writerB:
                            for line in reader:
                                job = Job(**ujson.loads(line))
                                found = False
                                for funct in filterFunctions:
                                    found = found or funct(job)
                                if found:
                                    json.dump(
                                        job, writerA, default=lambda x: x.__dict__
                                    )
                                    writerA.write("\n")
                                else:
                                    json.dump(
                                        job, writerB, default=lambda x: x.__dict__
                                    )
                                    writerB.write("\n")
        return (
            data[0:-6] + "/" + outpath + ".jl.gz",
            data[0:-6] + "/not" + outpath + ".jl.gz",
        )
    jobsWith: List[bytes] = []
    jobsWithout: List[bytes] = []
    for line in data:
        job = Job(**ujson.loads(zlib.decompress(line)))
        found = False
        for funct in filterFunctions:
            found = found or funct(job)
        if found:
            jobsWith.append(line)
        else:
            jobsWithout.append(line)
    return (jobsWith, jobsWithout)


def filterJobsAnd(
    location, data, filterFunctions: List[Callable], outpath
) -> Union[Tuple[str, str], Tuple[List[bytes], List[bytes]]]:
    if location == "disk":
        if not (
            os.path.exists(data[0:-6] + "/" + outpath + ".jl.gz")
            and os.path.exists(data[0:-6] + "/not" + outpath + ".jl.gz")
        ):
            with gzip.open(data) as reader:
                if hasJobs("disk", data):
                    with gzip.open(
                        data[0:-6] + "/" + outpath + ".jl.gz",
                        "at",
                        encoding="utf8",
                    ) as writerA:
                        with gzip.open(
                            data[0:-6] + "/not" + outpath + ".jl.gz",
                            "at",
                            encoding="utf8",
                        ) as writerB:
                            for line in reader:
                                job = Job(**ujson.loads(line))
                                found = True
                                for funct in filterFunctions:
                                    found = found and funct(job)
                                if found:
                                    json.dump(
                                        job, writerA, default=lambda x: x.__dict__
                                    )
                                    writerA.write("\n")
                                else:
                                    json.dump(
                                        job, writerB, default=lambda x: x.__dict__
                                    )
                                    writerB.write("\n")
        return (
            data[0:-6] + "/" + outpath + ".jl.gz",
            data[0:-6] + "/not" + outpath + ".jl.gz",
        )
    jobsWith: List[bytes] = []
    jobsWithout: List[bytes] = []
    for line in data:
        job = Job(**ujson.loads(zlib.decompress(line)))
        found = True
        for funct in filterFunctions:
            found = found and funct(job)
        if found:
            jobsWith.append(line)
        else:
            jobsWithout.append(line)
    return (jobsWith, jobsWithout)


def hasPlayers(
    location, data, players: List[str], mode=""
) -> Union[Tuple[str, str], Tuple[List[bytes], List[bytes]]]:
    """
    Filter the jobs in the given data file to jobs that contain the chosen player.

    :param data: the full name of the data file
    :type data: str
    :param player: the Splatnet ID of the chosen player
    :type player: List[str]
    :return: the full names of the paired filtered files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist

    :Example:

    >>> import core
    >>> core.hasPlayer("data/salmonAll.jl.gz", ["aeda69d2070fafb6"])
    (
        ('data/salmonAll/playerIds/', 'aeda69d2070fafb6.jl.gz'),
        ('data/salmonAll/notplayerIds/', 'aeda69d2070fafb6.jl.gz')
    )

    """
    if location == "disk":
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/playerIds/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/notplayerIds/")
        except FileExistsError:
            pass
    outPath = "playerIds/"
    filterFunctions: List[Callable] = []
    for player in players:
        filterFunctions.append(
            lambda var, player=player: var.my_data.splatnet_id == player
            or (
                var.teammates is not None
                and (
                    (var.teammates[0].splatnet_id == player)
                    or (
                        len(var.teammates) > 1
                        and var.teammates[1].splatnet_id == player
                    )
                    or (
                        len(var.teammates) > 2
                        and var.teammates[2].splatnet_id == player
                    )
                )
            ),
        )
        outPath += player + mode
    if mode == "and":
        return filterJobsAnd(location, data, filterFunctions, outPath)
    if mode == "or":
        return filterJobsOr(location, data, filterFunctions, outPath)
    return filterJobs(location, data, filterFunctions[0], outPath)


def hasWeapons(
    location, data, weapons: List[str], mode=""
) -> Union[Tuple[str, str], Tuple[List[bytes], List[bytes]]]:
    """
    Filter the data file to only jobs that contain the chosen weapon(s).

    :param data: the full name of the data file
    :type data: str
    :param weapon: the name(s) or ID(s) of the chosen weapon(s)
    :type weapon: List[str]
    :return: the full names of the paired filtered files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist

    :Example:

    >>> import core
    >>> core.hasWeapon("data/salmonAll.jl.gz", ["kuma_charger"])
    (
        'data/salmonAll/weapons/kuma_charger.jl.gz',
        'data/salmonAll/notweapons/kuma_charger.jl.gz'
    )

    """
    if location == "disk":
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/weapons/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/notweapons/")
        except FileExistsError:
            pass
    outPath = "weapons/"
    filterFunctions = []
    for weapon in weapons:
        filterFunctions.append(
            lambda var, weapon=weapon: (
                var.my_data.weapons[0].key == weapon
                or (
                    len(var.my_data.weapons) > 1
                    and var.my_data.weapons[1].key == weapon
                )
                or (
                    len(var.my_data.weapons) > 2
                    and var.my_data.weapons[2].key == weapon
                )
                or (
                    var.teammates is not None
                    and (
                        (
                            len(var.teammates) > 0
                            and var.teammates[0].weapons is not None
                            and (
                                var.teammates[0].weapons[0].key == weapon
                                or (
                                    len(var.teammates[0].weapons) > 1
                                    and var.teammates[0].weapons[1].key == weapon
                                )
                                or (
                                    len(var.teammates[0].weapons) > 2
                                    and var.teammates[0].weapons[2].key == weapon
                                )
                            )
                        )
                        or (
                            len(var.teammates) > 1
                            and var.teammates[1].weapons is not None
                            and (
                                var.teammates[1].weapons[0].key == weapon
                                or (
                                    len(var.teammates[1].weapons) > 1
                                    and var.teammates[1].weapons[1].key == weapon
                                )
                                or (
                                    len(var.teammates[1].weapons) > 2
                                    and var.teammates[1].weapons[2].key == weapon
                                )
                            )
                        )
                        or (
                            len(var.teammates) > 2
                            and var.teammates[2].weapons is not None
                            and (
                                var.teammates[2].weapons[0].key == weapon
                                or (
                                    len(var.teammates[2].weapons) > 1
                                    and var.teammates[2].weapons[1].key == weapon
                                )
                                or (
                                    len(var.teammates[2].weapons) > 2
                                    and var.teammates[2].weapons[2].key == weapon
                                )
                            )
                        )
                    )
                )
            )
        )
        outPath += weapon + mode
    if mode == "and":
        return filterJobsAnd(location, data, filterFunctions, outPath)
    if mode == "or":
        return filterJobsOr(location, data, filterFunctions, outPath)
    return filterJobs(location, data, filterFunctions[0], outPath)


def usesWeapons(
    location, data, weapons: List[str], mode=""
) -> Union[Tuple[str, str], Tuple[List[bytes], List[bytes]]]:
    """
    Filter the data file to only jobs where the player uses the chosen weapon(s).

    :param data: the file name of the data file
    :type data: str
    :param weapon: the name(s) or ID(s) of the chosen weapon(s)
    :type weapon: List[str]
    :return: the full names of the paired filtered files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist

    :Example:

    >>> import core
    >>> usesWeapon("data/", "salmonAll.jl.gz", ["Grizzco Charger"])
    (
        'data/salmonAll/usesWeapons/Grizzco Charger.jl.gz',
        'data/salmonAll/notusesWeapons/Grizzco Charger.jl.gz'
    )

    """
    if location == "disk":
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/usesWeapons/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/notusesWeapons/")
        except FileExistsError:
            pass
    outPath = "usesWeapons/"
    filterFunctions = []
    for weapon in weapons:
        filterFunctions.append(
            lambda var, weapon=weapon: (
                var.my_data.weapons[0].key == weapon
                or (
                    len(var.my_data.weapons) > 1
                    and var.my_data.weapons[1].key == weapon
                )
                or (
                    len(var.my_data.weapons) > 2
                    and var.my_data.weapons[2].key == weapon
                )
            )
        )
        outPath += weapon + mode
    if mode == "and":
        return filterJobsAnd(location, data, filterFunctions, outPath)
    if mode == "or":
        return filterJobsOr(location, data, filterFunctions, outPath)
    return filterJobs(location, data, filterFunctions[0], outPath)


def onStages(
    location, data, stages: List[str], mode=None
) -> Union[Tuple[str, str], Tuple[List[bytes], List[bytes]]]:
    """
    Filter the data file to only jobs on the chosen stage(s).

    :param data: the file name of the data file
    :type data: str
    :param stage: the name(s) or ID(s) of the chosen stage(s)
    :type stage: List[str]
    :return: the full names of the paired filtered files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist

    :Example:

    >>> import core
    >>> core.onStage("data/", "salmonAll.jl.gz", "Ruins of Ark Polaris")
    (
        'data/salmonAll/stages/Ruins of Ark Polaris.jl.gz',
        'data/salmonAll/notstages/Ruins of Ark Polaris.jl.gz'
    )

    """
    if location == "disk":
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/stages/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/notstages/")
        except FileExistsError:
            pass
    outPath = "stages/"
    filterFunctions = []
    for stage in stages:
        filterFunctions.append(
            lambda var, stage=stage: var.stage is not None and stage in (var.stage.key,)
        )
        outPath += stage + (mode if mode is not None else "")
    if mode == "or":
        return filterJobsOr(location, data, filterFunctions, outPath)
    return filterJobs(location, data, filterFunctions[0], outPath)


def withSpecial(
    location, data, special
) -> Union[Tuple[str, str], Tuple[List[bytes], List[bytes]]]:
    """
    Filter the data file to only jobs where the player had the chosen special.

    :param data: the full name of the data file
    :type data: str
    :param special: the name or ID of the chosen special
    :type special: str
    :return: the full names of the paired filtered files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist

    :Example:

    >>> import core
    >>> core.withSpecial("data/salmonAll.jl.gz", "Splashdown")
    (
        'data/salmonAll/special/Splashdown.jl.gz',
        'data/salmonAll/notspecial/Splashdown.jl.gz'
    )

    """
    if location == "disk":
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/special/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/notspecial/")
        except FileExistsError:
            pass
    return filterJobs(
        location,
        data,
        lambda var, special=special: special in (var.my_data.special.key,),
        "special/" + special,
    )


def failReasons(
    location, data, reasons: List[str], mode=""
) -> Union[Tuple[str, str], Tuple[List[bytes], List[bytes]]]:
    """
    Filter the data file to only jobs where the fail reason was the chosen reason.

    :param data: the file name of the data file
    :type data: str
    :param reasons: the chosen reasons
    :type reasons: List[str]
    :return: the path and filename of the output data file
    :rtype: Tuple[Tuple[str, str], Tuple[str, str]]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist

    :Example:

    >>> import core
    >>> core.failReason("data/", "salmonAll.jl.gz", ["None"])
    (
        'data/salmonAll/failReasons/None.jl.gz',
        'data/salmonAll/notfailReasons/None.jl.gz'
    )

    """
    if location == "disk":
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/failReasons/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/notfailReasons/")
        except FileExistsError:
            pass
    filterFunctions: List[Callable] = []
    outPath = "failReasons/"
    for reason in reasons:
        filterFunctions.append(lambda var, reason=reason: var.fail_reason == reason)
        outPath += reason + (mode if mode is not None else "")
    if mode == "or":
        return filterJobsOr(location, data, filterFunctions, outPath)
    return filterJobs(location, data, filterFunctions[0], outPath)


def duringRotationInts(
    location, data, rotations: List[int], mode=""
) -> Union[Tuple[str, str], Tuple[List[bytes], List[bytes]]]:
    """
    Filter the data file to only jobs where the rotation was the chosen rotation.

    :param data: the full name of the data file
    :type data: str
    :param rotation: the ID of the chosen rotation
    :type rotation: int
    :return: the full name of the output data files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist

    >>> import core
    >>> core.duringRotationInt("data/salmonAll.jl.gz", [1607752800])
    (
        'data/salmonAll/rotations/1607752800.jl.gz',
        'data/salmonAll/notRotations/1607752800.jl.gz'
    )

    """
    if location == "disk":
        try:
            os.mkdir(data[0:-6])
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/rotations/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/notrotations/")
        except FileExistsError:
            pass
    filterFunctions: List[Callable] = []
    outPath = "rotations/"
    for rotation in rotations:
        filterFunctions.append(
            lambda var, rotation=rotation: var.shift_start_at.time == rotation
        )
        outPath += str(rotation) + (mode if mode is not None else "")
    if mode == "or":
        return filterJobsOr(location, data, filterFunctions, outPath)
    return filterJobs(location, data, filterFunctions[0], outPath)


def clearWave(
    location, data, wave, comparison="="
) -> Union[Tuple[str, str], Tuple[List[bytes], List[bytes]]]:
    """
    Filter the data file to only jobs where the clear wave was the chosen clear wave.

    :param data: the full name of the data file
    :type data: str
    :param wave: the chosen clear wave
    :type wave: int
    :return: the full name of the output data files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist

    :Example:

    >>> import core
    >>> core.clearWave("data/salmonAll.jl.gz", 3)
    (
        ('data/salmonAll/clearWaves/equal/3.jl.gz'),
        ('data/salmonAll/clearWaves/notEqual/3.jl.gz')
    )

    """
    if location == "disk":
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/clearWaves/")
        except FileExistsError:
            pass
    outPath = "clearWaves/"
    if comparison == ">":
        outPath += "greaterThan" + str(wave)
        try:
            os.mkdir(data[0:-6] + "/clearWaves/greaterThan/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/clearWaves/notgreaterThan/")
        except FileExistsError:
            pass
        return filterJobs(
            location, data, lambda job, wave=wave: job.clear_waves > wave, outPath
        )
    if comparison == "<":
        outPath += "lessThan" + str(wave)
        try:
            os.mkdir(data[0:-6] + "/clearWaves/lessThan/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/clearWaves/notlessThan/")
        except FileExistsError:
            pass
        return filterJobs(
            location, data, lambda job, wave=wave: job.clear_waves < wave, outPath
        )
    outPath += "equal" + str(wave)
    try:
        os.mkdir(data[0:-6] + "/clearWaves/equal/")
    except FileExistsError:
        pass
    try:
        os.mkdir(data[0:-6] + "/clearWaves/notequal/")
    except FileExistsError:
        pass
    return filterJobs(
        location, data, lambda job, wave=wave: job.clear_waves == wave, outPath
    )


def dangerRate(
    location, data, rate, comparison="="
) -> Union[Tuple[str, str], Tuple[List[bytes], List[bytes]]]:
    """
    Filter the data file to only jobs where the danger rate was the chosen danger rate.

    :param data: the full name of the data file
    :type data: str
    :param rate: the chosen danger rate
    :type rate: float
    :return: the full names of the paired filtered files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist

    :Example:

    >>> import core
    >>> core.dangerRate("data/salmonAll.jl.gz", "200.0")
    (
        'data/salmonAll/dangerRate/equal/200.0.jl.gz',
        'data/salmonAll/dangerRate/notEqual/200.0.jl.gz'
    )

    """
    if location == "disk":
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/dangerRate/")
        except FileExistsError:
            pass
    outPath = "dangerRate/"
    if comparison == ">":
        if location == "disk":
            outPath += "greaterThan" + str(rate)
            try:
                os.mkdir(data[0:-6] + "/dangerRate/greaterThan/")
            except FileExistsError:
                pass
            try:
                os.mkdir(data[0:-6] + "/dangerRate/notgreaterThan/")
            except FileExistsError:
                pass
        return filterJobs(
            location,
            data,
            lambda job, rate=rate: float(job.danger_rate) > rate,
            outPath,
        )
    if comparison == "<":
        if location == "disk":
            outPath += "lessThan" + str(rate)
            try:
                os.mkdir(data[0:-6] + "/dangerRate/lessThan/")
            except FileExistsError:
                pass
            try:
                os.mkdir(data[0:-6] + "/dangerRate/notlessThan/")
            except FileExistsError:
                pass
        return filterJobs(
            location,
            data,
            lambda job, rate=rate: float(job.danger_rate) < rate,
            outPath,
        )
    if location == "disk":
        outPath += "equal" + str(rate)
        try:
            os.mkdir(data[0:-6] + "/dangerRate/equal/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/dangerRate/notequal/")
        except FileExistsError:
            pass
    return filterJobs(
        location, data, lambda job, rate=rate: float(job.danger_rate) == rate, outPath
    )


def hasTides(
    location, data, tides: List[str], mode=""
) -> Union[Tuple[str, str], Tuple[List[bytes], List[bytes]]]:
    """
    Filter the data file to only jobs where the tide of at least one wave is the chosen tide.

    :param data: the full name of the data file
    :type data: str
    :param tides: the chosen tides (as either "normal", "low", or "high")
    :type tides: List[str]
    :return: the full name of the output data files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist

    >>> import core
    >>> core.hasTides("data/salmonAll.jl.gz", ["high"])
    (
        "data/salmonAll/tides/high.jl.gz",
        "data/salmonAll/nottides/high.jl.gz"
    )

    """
    if location == "disk":
        try:
            os.mkdir(data[0:-6])
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/tides/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/nottides/")
        except FileExistsError:
            pass
    filterFunctions: List[Callable] = []
    outPath = "tides/"
    for tide in tides:
        filterFunctions.append(
            lambda var, tide=tide: (
                var.waves[0].water_level == tide
                or (len(var.waves) > 1 and var.waves[1].water_level == tide)
                or (len(var.waves) > 2 and var.waves[2].water_level == tide)
            )
        )
        outPath += tide + (mode if mode is not None else "")
    if mode == "and":
        return filterJobsAnd(location, data, filterFunctions, outPath)
    if mode == "or":
        return filterJobsOr(location, data, filterFunctions, outPath)
    return filterJobs(location, data, filterFunctions[0], outPath)


def hasEvents(
    location, data, events: List[str], mode=""
) -> Union[Tuple[str, str], Tuple[List[bytes], List[bytes]]]:
    """
    Filter the data file to only jobs where the event of at least one wave is the chosen event.

    :param data: the full name of the data file
    :type data: str
    :param events: the chosen event ("mothership", "fog", "rush", "cohock_charge", "griller", "goldie_seeking")
    :type events: List[str]
    :return: the full name of the output data files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist

    >>> import core
    >>> core.hasEvents("data/salmonAll.jl.gz", ["fog"])
    (
        "data/salmonAll/tides/fog.jl.gz",
        "data/salmonAll/nottides/fog.jl.gz"
    )

    """
    if location == "disk":
        try:
            os.mkdir(data[0:-6])
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/events/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/notevents/")
        except FileExistsError:
            pass
    filterFunctions: List[Callable] = []
    outPath = "events/"
    for event in events:
        filterFunctions.append(
            lambda var, event=event: (
                (
                    var.waves[0].known_occurrence is not None
                    and var.waves[0].known_occurrence.key == event
                )
                or (
                    len(var.waves) > 1
                    and var.waves[1].known_occurrence is not None
                    and var.waves[1].known_occurrence.key == event
                )
                or (
                    len(var.waves) > 2
                    and var.waves[2].known_occurrence is not None
                    and var.waves[2].known_occurrence.key == event
                )
            )
        )
        outPath += event + (mode if mode is not None else "")
    if mode == "and":
        return filterJobsAnd(location, data, filterFunctions, outPath)
    if mode == "or":
        return filterJobsOr(location, data, filterFunctions, outPath)
    return filterJobs(location, data, filterFunctions[0], outPath)


def hasWeaponTypes(
    location, data, types: Union[List[str], Tuple[str, str, str, str]], mode=""
) -> Union[Tuple[str, str], Tuple[List[bytes], List[bytes]]]:
    if location == "disk":
        try:
            os.mkdir(data[0:-6])
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/weaponTypes/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/notweaponTypes/")
        except FileExistsError:
            pass
    weaponList = requests.get("https://stat.ink/api/v2/weapon").json()
    for grizzWeapon in grizzcoWeapons:
        new = {
            "name": {locale: grizzWeapon[0]},
            "key": grizzWeapon[1],
            "main_ref": grizzWeapon[1],
            "type": {"key": grizzWeapon[2]},
        }
        cast(List[Dict[str, Dict[str, str]]], weaponList).append(
            cast(Dict[str, Dict[str, str]], new)
        )
    weaponDict = {}
    for i in weaponList:
        weaponDict[i["key"]] = i
    filterFunctions: List[Callable] = []
    outPath = "weaponTypes/"
    for wtype in types:
        filterFunctions.append(
            lambda var, wtype=wtype, weaponDict=weaponDict: (
                weaponDict[var.my_data.weapons[0].key]["type"]["key"] == wtype
                or (
                    len(var.my_data.weapons) > 1
                    and weaponDict[var.my_data.weapons[1].key]["type"]["key"] == wtype
                )
                or (
                    len(var.my_data.weapons) > 2
                    and weaponDict[var.my_data.weapons[2].key]["type"]["key"] == wtype
                )
                or (
                    var.teammates is not None
                    and (
                        (
                            len(var.teammates) > 0
                            and var.teammates[0].weapons is not None
                            and (
                                weaponDict[var.teammates[0].weapons[0].key]["type"][
                                    "key"
                                ]
                                == wtype
                                or (
                                    len(var.teammates[0].weapons) > 1
                                    and weaponDict[var.teammates[0].weapons[1].key][
                                        "type"
                                    ]["key"]
                                    == wtype
                                )
                                or (
                                    len(var.teammates[0].weapons) > 2
                                    and weaponDict[var.teammates[0].weapons[2].key][
                                        "type"
                                    ]["key"]
                                    == wtype
                                )
                            )
                        )
                        or (
                            len(var.teammates) > 1
                            and var.teammates[1].weapons is not None
                            and (
                                weaponDict[var.teammates[1].weapons[0].key]["type"][
                                    "key"
                                ]
                                == wtype
                                or (
                                    len(var.teammates[1].weapons) > 1
                                    and weaponDict[var.teammates[1].weapons[1].key][
                                        "type"
                                    ]["key"]
                                    == wtype
                                )
                                or (
                                    len(var.teammates[1].weapons) > 2
                                    and weaponDict[var.teammates[1].weapons[2].key][
                                        "type"
                                    ]["key"]
                                    == wtype
                                )
                            )
                        )
                        or (
                            len(var.teammates) > 2
                            and var.teammates[2].weapons is not None
                            and (
                                weaponDict[var.teammates[2].weapons[0].key]["type"][
                                    "key"
                                ]
                                == wtype
                                or (
                                    len(var.teammates[2].weapons) > 1
                                    and weaponDict[var.teammates[2].weapons[1].key][
                                        "type"
                                    ]["key"]
                                    == wtype
                                )
                                or (
                                    len(var.teammates[2].weapons) > 2
                                    and weaponDict[var.teammates[2].weapons[2].key][
                                        "type"
                                    ]["key"]
                                    == wtype
                                )
                            )
                        )
                    )
                )
            )
        )
        outPath += wtype + (mode if mode is not None else "")
    if mode == "and":
        return filterJobsAnd(location, data, filterFunctions, outPath)
    if mode == "or":
        return filterJobsOr(location, data, filterFunctions, outPath)
    return filterJobs(location, data, filterFunctions[0], outPath)
