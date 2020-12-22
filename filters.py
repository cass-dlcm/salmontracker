from core import hasJobs, locale
import os.path
from typing import Tuple, List, Callable
import gzip
import jsonlines
import ujson


def filterJobs(data: str, outpath: str, filterFunction: Callable) -> Tuple[str, str]:
    if not (
        os.path.exists(data[0:-6] + "/" + outpath + ".jl.gz")
        and os.path.exists(data[0:-6] + "/not" + outpath + ".jl.gz")
    ):
        with gzip.open(data) as reader:
            if hasJobs(data):
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
                        for job in jsonlines.Reader(reader, ujson.loads):
                            if filterFunction(job):
                                ujson.dump(job, writerA)
                                writerA.write("\n")
                            else:
                                ujson.dump(job, writerB)
                                writerB.write("\n")
    return (
        data[0:-6] + "/" + outpath + ".jl.gz",
        data[0:-6] + "/not" + outpath + ".jl.gz",
    )


def filterJobsOr(
    data: str, outpath: str, filterFunctions: List[Callable]
) -> Tuple[str, str]:
    if not (
        os.path.exists(data[0:-6] + "/" + outpath + ".jl.gz")
        and os.path.exists(data[0:-6] + "/not" + outpath + ".jl.gz")
    ):
        with gzip.open(data) as reader:
            if hasJobs(data):
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
                        for job in jsonlines.Reader(reader, ujson.loads):
                            found = False
                            for funct in filterFunctions:
                                found = found or funct(job)
                            if found:
                                ujson.dump(job, writerA)
                                writerA.write("\n")
                            else:
                                ujson.dump(job, writerB)
                                writerB.write("\n")
    return (
        data[0:-6] + "/" + outpath + ".jl.gz",
        data[0:-6] + "/not" + outpath + ".jl.gz",
    )


def filterJobsAnd(
    data: str, outpath: str, filterFunctions: List[Callable]
) -> Tuple[str, str]:
    if not (
        os.path.exists(data[0:-6] + "/" + outpath + ".jl.gz")
        and os.path.exists(data[0:-6] + "/not" + outpath + ".jl.gz")
    ):
        with gzip.open(data) as reader:
            if hasJobs(data):
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
                        for job in jsonlines.Reader(reader, ujson.loads):
                            found = True
                            for funct in filterFunctions:
                                found = found and funct(job)
                            if found:
                                ujson.dump(job, writerA)
                                writerA.write("\n")
                            else:
                                ujson.dump(job, writerB)
                                writerB.write("\n")
    return (
        data[0:-6] + "/" + outpath + ".jl.gz",
        data[0:-6] + "/not" + outpath + ".jl.gz",
    )


def hasPlayers(data: str, players: List[str], mode: str = None) -> Tuple[str, str]:
    """
    Filter the jobs in the given data file to jobs that contain the chosen player.

    :param data: the full name of the data file
    :type data: str
    :param player: the Splatnet ID of the chosen player
    :type player: str
    :return: the full names of the paired filtered files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> core.hasPlayer("data/salmonAll.jl.gz", ["aeda69d2070fafb6"])
    (
        ('data/salmonAll/playerIds/', 'aeda69d2070fafb6.jl.gz'),
        ('data/salmonAll/notplayerIds/', 'aeda69d2070fafb6.jl.gz')
    )

    """
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
            lambda var, player=player: var["my_data"]["splatnet_id"] == player
            or (
                var["teammates"] is not None
                and (
                    (var["teammates"][0]["splatnet_id"] == player)
                    or (
                        len(var["teammates"]) > 1
                        and var["teammates"][1]["splatnet_id"] == player
                    )
                    or (
                        len(var["teammates"]) > 2
                        and var["teammates"][2]["splatnet_id"] == player
                    )
                )
            ),
        )
        outPath += player + (mode if mode is not None else "")
    if mode == "and":
        return filterJobsAnd(
            data,
            outPath,
            filterFunctions,
        )
    if mode == "or":
        return filterJobsOr(
            data,
            outPath,
            filterFunctions,
        )
    return filterJobs(data, outPath, filterFunctions[0])


def hasWeapons(data: str, weapons: List[str], mode: str = None) -> Tuple[str, str]:
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
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> core.hasWeapon("data/salmonAll.jl.gz", ["Grizzco Charger"])
    (
        'data/salmonAll/weapons/Grizzco Charger.jl.gz',
        'data/salmonAll/notweapons/Grizzco Charger.jl.gz'
    )

    """
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
                var["my_data"]["weapons"][0]["key"] == weapon
                or (
                    len(var["my_data"]["weapons"]) > 1
                    and var["my_data"]["weapons"][1]["key"] == weapon
                )
                or (
                    len(var["my_data"]["weapons"]) > 2
                    and var["my_data"]["weapons"][2]["key"] == weapon
                )
                or (
                    var["teammates"] is not None
                    and (
                        (
                            len(var["teammates"]) > 0
                            and var["teammates"][0]["weapons"] is not None
                            and (
                                var["teammates"][0]["weapons"][0]["key"] == weapon
                                or (
                                    len(var["teammates"][0]["weapons"]) > 1
                                    and var["teammates"][0]["weapons"][1]["key"]
                                    == weapon
                                )
                                or (
                                    len(var["teammates"][0]["weapons"]) > 2
                                    and var["teammates"][0]["weapons"][2]["key"]
                                    == weapon
                                )
                            )
                        )
                        or (
                            len(var["teammates"]) > 1
                            and var["teammates"][1]["weapons"] is not None
                            and (
                                var["teammates"][1]["weapons"][0]["key"] == weapon
                                or (
                                    len(var["teammates"][1]["weapons"]) > 1
                                    and var["teammates"][1]["weapons"][1]["key"]
                                    == weapon
                                )
                                or (
                                    len(var["teammates"][1]["weapons"]) > 2
                                    and var["teammates"][1]["weapons"][2]["key"]
                                    == weapon
                                )
                            )
                        )
                        or (
                            len(var["teammates"]) > 2
                            and var["teammates"][2]["weapons"] is not None
                            and (
                                var["teammates"][2]["weapons"][0]["key"] == weapon
                                or (
                                    len(var["teammates"][2]["weapons"]) > 1
                                    and var["teammates"][2]["weapons"][1]["key"]
                                    == weapon
                                )
                                or (
                                    len(var["teammates"][2]["weapons"]) > 2
                                    and var["teammates"][2]["weapons"][2]["key"]
                                    == weapon
                                )
                            )
                        )
                    )
                )
                or (var["my_data"]["weapons"][0]["name"][locale] == weapon)
                or (
                    len(var["my_data"]["weapons"]) > 1
                    and var["my_data"]["weapons"][1]["name"][locale] == weapon
                )
                or (
                    len(var["my_data"]["weapons"]) > 2
                    and var["my_data"]["weapons"][2]["name"][locale] == weapon
                )
                or (
                    var["teammates"] is not None
                    and (
                        (
                            len(var["teammates"]) > 0
                            and var["teammates"][0]["weapons"] is not None
                            and (
                                var["teammates"][0]["weapons"][0]["name"][locale]
                                == weapon
                                or (
                                    len(var["teammates"][0]["weapons"]) > 1
                                    and var["teammates"][0]["weapons"][1]["name"][
                                        locale
                                    ]
                                    == weapon
                                )
                                or (
                                    len(var["teammates"][0]["weapons"]) > 2
                                    and var["teammates"][0]["weapons"][2]["name"][
                                        locale
                                    ]
                                    == weapon
                                )
                            )
                        )
                        or (
                            len(var["teammates"]) > 1
                            and var["teammates"][1]["weapons"] is not None
                            and (
                                var["teammates"][1]["weapons"][0]["name"][locale]
                                == weapon
                                or (
                                    len(var["teammates"][1]["weapons"]) > 1
                                    and var["teammates"][1]["weapons"][1]["name"][
                                        locale
                                    ]
                                    == weapon
                                )
                                or (
                                    len(var["teammates"][1]["weapons"]) > 2
                                    and var["teammates"][1]["weapons"][2]["name"][
                                        locale
                                    ]
                                    == weapon
                                )
                            )
                        )
                        or (
                            len(var["teammates"]) > 2
                            and var["teammates"][2]["weapons"] is not None
                            and (
                                var["teammates"][2]["weapons"][0]["name"][locale]
                                == weapon
                                or (
                                    len(var["teammates"][2]["weapons"]) > 1
                                    and var["teammates"][2]["weapons"][1]["name"][
                                        locale
                                    ]
                                    == weapon
                                )
                                or (
                                    len(var["teammates"][2]["weapons"]) > 2
                                    and var["teammates"][2]["weapons"][2]["name"][
                                        locale
                                    ]
                                    == weapon
                                )
                            )
                        )
                    )
                )
            )
        )
        outPath += weapon + (mode if mode is not None else "")
    if mode == "and":
        return filterJobsAnd(
            data,
            outPath,
            filterFunctions,
        )
    if mode == "or":
        return filterJobsOr(
            data,
            outPath,
            filterFunctions,
        )
    return filterJobs(data, outPath, filterFunctions[0])


def usesWeapons(data: str, weapons: List[str], mode: str = None) -> Tuple[str, str]:
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
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> usesWeapon("data/", "salmonAll.jl.gz", ["Grizzco Charger"])
    (
        'data/salmonAll/usesWeapons/Grizzco Charger.jl.gz',
        'data/salmonAll/notusesWeapons/Grizzco Charger.jl.gz'
    )

    """
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
                var["my_data"]["weapons"][0]["key"] == weapon
                or (
                    len(var["my_data"]["weapons"]) > 1
                    and var["my_data"]["weapons"][1]["key"] == weapon
                )
                or (
                    len(var["my_data"]["weapons"]) > 2
                    and var["my_data"]["weapons"][2]["key"] == weapon
                )
                or var["my_data"]["weapons"][0]["name"][locale] == weapon
                or (
                    len(var["my_data"]["weapons"]) > 1
                    and var["my_data"]["weapons"][1]["name"][locale] == weapon
                )
                or (
                    len(var["my_data"]["weapons"]) > 2
                    and var["my_data"]["weapons"][2]["name"][locale] == weapon
                )
            )
        )
        outPath += weapon + (mode if mode is not None else "")
    if mode == "and":
        return filterJobsAnd(
            data,
            outPath,
            filterFunctions,
        )
    if mode == "or":
        return filterJobsOr(
            data,
            outPath,
            filterFunctions,
        )
    return filterJobs(data, outPath, filterFunctions[0])


def onStages(data: str, stages: List[str], mode: str = None) -> Tuple[str, str]:
    """
    Filter the data file to only jobs on the chosen stage(s).

    :param data: the file name of the data file
    :type data: str
    :param stage: the name(s) or ID(s) of the chosen stage(s)
    :type stage: str
    :return: the full names of the paired filtered files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> core.onStage("data/", "salmonAll.jl.gz", "Ruins of Ark Polaris")
    (
        'data/salmonAll/stages/Ruins of Ark Polaris.jl.gz',
        'data/salmonAll/notstages/Ruins of Ark Polaris.jl.gz'
    )

    """
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
            lambda var, stage=stage: var["stage"] is not None
            and stage
            in (
                var["stage"]["key"],
                var["stage"]["name"][locale],
            )
        )
        outPath += stage + (mode if mode is not None else "")
    if mode == "or":
        return filterJobsOr(
            data,
            outPath,
            filterFunctions,
        )
    return filterJobs(data, outPath, filterFunctions[0])


def withSpecial(data: str, special: str) -> Tuple[str, str]:
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
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> core.withSpecial("data/salmonAll.jl.gz", "Splashdown")
    (
        'data/salmonAll/special/Splashdown.jl.gz',
        'data/salmonAll/notspecial/Splashdown.jl.gz'
    )

    """
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
        data,
        "special/" + special,
        lambda var: special
        in (
            var["my_data"]["special"]["key"],
            var["my_data"]["special"]["name"][locale],
        ),
    )


def failReasons(data: str, reasons: List[str], mode: str = None) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the fail reason was the chosen reason.

    :param data: the file name of the data file
    :type data: str
    :param reason: the chosen reason
    :type reason: str
    :return: the path and filename of the output data file
    :rtype: Tuple[Tuple[str, str], Tuple[str, str]]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> core.failReason("data/", "salmonAll.jl.gz", ["None"])
    (
        'data/salmonAll/failReasons/None.jl.gz',
        'data/salmonAll/notfailReasons/None.jl.gz'
    )

    """
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
        filterFunctions.append(lambda var, reason=reason: var["fail_reason"] == reason)
        outPath += reason + (mode if mode is not None else "")
    if mode == "or":
        return filterJobsOr(
            data,
            outPath,
            filterFunctions,
        )
    return filterJobs(data, outPath, filterFunctions[0])


def duringRotationInts(
    data: str, rotations: List[int], mode: str = None
) -> Tuple[str, str]:
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
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    >>> import core
    >>> core.duringRotationInt("data/salmonAll.jl.gz", [1607752800])
    (
        'data/salmonAll/rotations/1607752800.jl.gz',
        'data/salmonAll/notRotations/1607752800.jl.gz'
    )

    """
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
            lambda var, rotation=rotation: var["shift_start_at"]["time"] == rotation
        )
        outPath += str(rotation) + (mode if mode is not None else "")
    if mode == "or":
        return filterJobsOr(
            data,
            outPath,
            filterFunctions,
        )
    return filterJobs(data, outPath, filterFunctions[0])


def clearWave(data: str, wave: int, comparison: str = "=") -> Tuple[str, str]:
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
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> core.clearWave("data/salmonAll.jl.gz", 3)
    (
        ('data/salmonAll/clearWaves/equal/3.jl.gz'),
        ('data/salmonAll/clearWaves/notEqual/3.jl.gz')
    )

    """
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
        return filterJobs(data, outPath, lambda job: job["clear_waves"] > wave)
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
        return filterJobs(data, outPath, lambda job: job["clear_waves"] < wave)
    outPath += "equal" + str(wave)
    try:
        os.mkdir(data[0:-6] + "/clearWaves/equal/")
    except FileExistsError:
        pass
    try:
        os.mkdir(data[0:-6] + "/clearWaves/notequal/")
    except FileExistsError:
        pass
    return filterJobs(data, outPath, lambda job: job["clear_waves"] == wave)


def dangerRate(data: str, rate: str, comparison: str = "=") -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the danger rate was the chosen danger rate.

    :param data: the full name of the data file
    :type data: str
    :param rate: the chosen danger rate
    :type rate: int
    :return: the full names of the paired filtered files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> core.dangerRate("data/salmonAll.jl.gz", "200.0")
    (
        'data/salmonAll/dangerRate/equal/200.0.jl.gz',
        'data/salmonAll/dangerRate/notEqual/200.0.jl.gz'
    )

    """
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
        outPath += "greaterThan" + rate
        try:
            os.mkdir(data[0:-6] + "/dangerRate/greaterThan/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/dangerRate/notgreaterThan/")
        except FileExistsError:
            pass
        return filterJobs(data, outPath, lambda job: job["danger_rate"] > rate)
    if comparison == "<":
        outPath += "lessThan" + rate
        try:
            os.mkdir(data[0:-6] + "/dangerRate/lessThan/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/dangerRate/notlessThan/")
        except FileExistsError:
            pass
        return filterJobs(data, outPath, lambda job: job["danger_rate"] < rate)
    outPath += "equal" + rate
    try:
        os.mkdir(data[0:-6] + "/dangerRate/equal/")
    except FileExistsError:
        pass
    try:
        os.mkdir(data[0:-6] + "/dangerRate/notequal/")
    except FileExistsError:
        pass
    return filterJobs(data, outPath, lambda job: job["danger_rate"] == rate)


def hasTides(data: str, tides: List[str], mode: str = None) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the tide of at least one wave is the chosen tide.

    :param data: the full name of the data file
    :type data: str
    :param rotation: the chosen tide (as either "normal", "low", or "high")
    :type rotation: int
    :return: the full name of the output data files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    >>> import core
    >>> core.hasTides("data/salmonAll.jl.gz", ["high"])
    (
        "data/salmonAll/tides/high.jl.gz",
        "data/salmonAll/nottides/high.jl.gz"
    )

    """
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
                var["waves"][0]["water_level"] == tide
                or (len(var["waves"]) > 1 and var["waves"][1]["water_level"] == tide)
                or (len(var["waves"]) > 2 and var["waves"][2]["water_level"] == tide)
            )
        )
        outPath += tide + (mode if mode is not None else "")
    if mode == "and":
        return filterJobsAnd(
            data,
            outPath,
            filterFunctions,
        )
    if mode == "or":
        return filterJobsOr(
            data,
            outPath,
            filterFunctions,
        )
    return filterJobs(data, outPath, filterFunctions[0])


def hasEvents(data: str, events: List[str], mode: str = None) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the event of at least one wave is the chosen event.

    :param data: the full name of the data file
    :type data: str
    :param rotation: the chosen event (None, "mothership", "fog", "rush", "cohock_charge", "griller", "goldie_seeking")
    :type rotation: int
    :return: the full name of the output data files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    >>> import core
    >>> core.hasEvents("data/salmonAll.jl.gz", ["fog"])
    (
        "data/salmonAll/tides/fog.jl.gz",
        "data/salmonAll/nottides/fog.jl.gz"
    )

    """
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
            lambda var, tide=event: (
                var["waves"][0]["water_level"] == tide
                or (len(var["waves"]) > 1 and var["waves"][1]["water_level"] == tide)
                or (len(var["waves"]) > 2 and var["waves"][2]["water_level"] == tide)
            )
        )
        outPath += event + (mode if mode is not None else "")
    if mode == "and":
        return filterJobsAnd(
            data,
            outPath,
            filterFunctions,
        )
    if mode == "or":
        return filterJobsOr(
            data,
            outPath,
            filterFunctions,
        )
    return filterJobs(data, outPath, filterFunctions[0])
