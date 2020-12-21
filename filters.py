from core import hasJobs, locale
import os.path.exists
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
        ('data/salmonAll/playerId/', 'aeda69d2070fafb6.jl.gz'),
        ('data/salmonAll/notPlayerId/', 'aeda69d2070fafb6.jl.gz')
    )

    """
    try:
        os.mkdir(data[0:-6] + "/")
    except FileExistsError:
        pass
    try:
        os.mkdir(data[0:-6] + "/playerId/")
    except FileExistsError:
        pass
    try:
        os.mkdir(data[0:-6] + "/notplayerId")
    except FileExistsError:
        pass
    outPath = "playerId"
    filterFunctions: List[Callable] = []
    for player in players:
        filterFunctions.append(
            lambda var: var["my_data"]["splatnet_id"] == player
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
        'data/salmonAll/weapon/Grizzco Charger.jl.gz',
        'data/salmonAll/notWeapon/Grizzco Charger.jl.gz'
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
            lambda var: (
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
            lambda var: (
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
