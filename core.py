import os.path
import ujson
import numpy as np
import requests
import jsonlines
import sys
from typing import Tuple, List, Union, Dict, cast, Optional, Any
import gzip
import shutil

locale = "en_US"

grizzcoWeapons = (
    ("Grizzco Charger", "kuma_charger"),
    ("Grizzco Brella", "kuma_brella"),
    ("Grizzco Blaster", "kuma_blaster"),
    ("Grizzco Slosher", "kuma_slosher"),
)

jobType = Dict[
    str,
    Union[
        int,
        str,
        bool,
        Dict[
            str,
            Union[
                int,
                str,
                Dict[str, Union[int, str, Dict[str, Union[int, str]]]],
                List[
                    Union[
                        int,
                        Dict[
                            str,
                            Union[int, str, Dict[str, Union[int, str, Dict[str, str]]]],
                        ],
                    ]
                ],
            ],
        ],
        List[
            Union[
                int,
                Dict[
                    str,
                    Union[
                        str,
                        int,
                        Dict[str, Union[int, str, Dict[str, str]]],
                        List[
                            Union[
                                int,
                                Dict[
                                    str,
                                    Union[
                                        int, str, Dict[str, Union[str, Dict[str, str]]]
                                    ],
                                ],
                            ]
                        ],
                    ],
                ],
            ]
        ],
    ],
]


def hasJobs(data: str) -> bool:
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


def hasPlayer(data: str, player: str) -> Tuple[str, str]:
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
    >>> core.hasPlayer("data/salmonAll.jl.gz", "aeda69d2070fafb6")
    (
        ('data/salmonAll/playerId/', 'aeda69d2070fafb6.jl.gz'),
        ('data/salmonAll/notPlayerId/', 'aeda69d2070fafb6.jl.gz')
    )

    """
    if not (
        os.path.exists(data[0:-6] + "/playerId/" + player + ".jl.gz")
        and os.path.exists(data[0:-6] + "/notPlayerId/" + player + ".jl.gz")
    ):
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/playerId/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/notPlayerId/")
        except FileExistsError:
            pass
        with gzip.open(data) as reader:
            if hasJobs(data):
                with gzip.open(
                    data[0:-6] + "/playerId/" + player + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writerA:
                    with gzip.open(
                        data[0:-6] + "/notPlayerId/" + player + ".jl.gz",
                        "at",
                        encoding="utf8",
                    ) as writerB:
                        for var in jsonlines.Reader(reader, ujson.loads):
                            if var["my_data"]["splatnet_id"] == player or (
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
                            ):
                                ujson.dump(var, writerA)
                                writerA.write("\n")
                            else:
                                ujson.dump(var, writerB)
                                writerB.write("\n")
    return (
        data[0:-6] + "/playerId/" + player + ".jl.gz",
        data[0:-6] + "/notPlayerId/" + player + ".jl.gz",
    )


def findRotationByWeaponsAndStage(
    data: str, weapons: Union[Tuple[str, str, str, str], List[str]], stage: str
) -> List[int]:
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
        for job in jsonlines.Reader(reader, ujson.loads):
            found = job["stage"] is not None and stage in (
                job["stage"]["key"],
                job["stage"]["name"][locale],
            )
            for weapon in weapons:
                found = found and (
                    job["my_data"]["weapons"][0]["key"] == weapon
                    or (
                        len(job["my_data"]["weapons"]) > 1
                        and job["my_data"]["weapons"][1]["key"] == weapon
                    )
                    or (
                        len(job["my_data"]["weapons"]) > 2
                        and job["my_data"]["weapons"][2]["key"] == weapon
                    )
                    or (
                        job["teammates"] is not None
                        and (
                            (
                                len(job["teammates"]) > 0
                                and job["teammates"][0]["weapons"] is not None
                                and (
                                    job["teammates"][0]["weapons"][0]["key"] == weapon
                                    or (
                                        len(job["teammates"][0]["weapons"]) > 1
                                        and job["teammates"][0]["weapons"][1]["key"]
                                        == weapon
                                    )
                                    or (
                                        len(job["teammates"][0]["weapons"]) > 2
                                        and job["teammates"][0]["weapons"][2]["key"]
                                        == weapon
                                    )
                                )
                            )
                            or (
                                len(job["teammates"]) > 1
                                and job["teammates"][1]["weapons"] is not None
                                and (
                                    job["teammates"][1]["weapons"][0]["key"] == weapon
                                    or (
                                        len(job["teammates"][1]["weapons"]) > 1
                                        and job["teammates"][1]["weapons"][1]["key"]
                                        == weapon
                                    )
                                    or (
                                        len(job["teammates"][1]["weapons"]) > 2
                                        and job["teammates"][1]["weapons"][2]["key"]
                                        == weapon
                                    )
                                )
                            )
                            or (
                                len(job["teammates"]) > 2
                                and job["teammates"][2]["weapons"] is not None
                                and (
                                    job["teammates"][2]["weapons"][0]["key"] == weapon
                                    or (
                                        len(job["teammates"][2]["weapons"]) > 1
                                        and job["teammates"][2]["weapons"][1]["key"]
                                        == weapon
                                    )
                                    or (
                                        len(job["teammates"][2]["weapons"]) > 2
                                        and job["teammates"][2]["weapons"][2]["key"]
                                        == weapon
                                    )
                                )
                            )
                        )
                    )
                    or job["my_data"]["weapons"][0]["name"][locale] == weapon
                    or (
                        len(job["my_data"]["weapons"]) > 1
                        and job["my_data"]["weapons"][1]["name"][locale] == weapon
                    )
                    or (
                        len(job["my_data"]["weapons"]) > 2
                        and job["my_data"]["weapons"][2]["name"][locale] == weapon
                    )
                    or (
                        job["teammates"] is not None
                        and (
                            (
                                len(job["teammates"]) > 0
                                and job["teammates"][0]["weapons"] is not None
                                and (
                                    job["teammates"][0]["weapons"][0]["name"][locale]
                                    == weapon
                                    or (
                                        len(job["teammates"][0]["weapons"]) > 1
                                        and job["teammates"][0]["weapons"][1]["name"][
                                            locale
                                        ]
                                        == weapon
                                    )
                                    or (
                                        len(job["teammates"][0]["weapons"]) > 2
                                        and job["teammates"][0]["weapons"][2]["name"][
                                            locale
                                        ]
                                        == weapon
                                    )
                                )
                            )
                            or (
                                len(job["teammates"]) > 1
                                and job["teammates"][1]["weapons"] is not None
                                and (
                                    job["teammates"][1]["weapons"][0]["name"][locale]
                                    == weapon
                                    or (
                                        len(job["teammates"][1]["weapons"]) > 1
                                        and job["teammates"][1]["weapons"][1]["name"][
                                            locale
                                        ]
                                        == weapon
                                    )
                                    or (
                                        len(job["teammates"][1]["weapons"]) > 2
                                        and job["teammates"][1]["weapons"][2]["name"][
                                            locale
                                        ]
                                        == weapon
                                    )
                                )
                            )
                            or (
                                len(job["teammates"]) > 2
                                and job["teammates"][2]["weapons"] is not None
                                and (
                                    job["teammates"][2]["weapons"][0]["name"][locale]
                                    == weapon
                                    or (
                                        len(job["teammates"][2]["weapons"]) > 1
                                        and job["teammates"][2]["weapons"][1]["name"][
                                            locale
                                        ]
                                        == weapon
                                    )
                                    or (
                                        len(job["teammates"][2]["weapons"]) > 2
                                        and job["teammates"][2]["weapons"][2]["name"][
                                            locale
                                        ]
                                        == weapon
                                    )
                                )
                            )
                        )
                    )
                )
            if found and job["shift_start_at"]["time"] not in foundRotations:
                foundRotations.append(job["shift_start_at"]["time"])
    return foundRotations


def findWeaponsAndStageByRotation(
    data: str, rotation: int
) -> Dict[str, Union[str, List[str]]]:
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
        for job in jsonlines.Reader(reader, ujson.loads):
            if job["shift_start_at"]["time"] == rotation:
                result["stage"] = job["stage"]["name"][locale]
                result["weapons"] = []
                if job["my_data"]["weapons"] is not None:
                    for i in range(0, len(job["my_data"]["weapons"])):
                        if (
                            job["my_data"]["weapons"][i]["name"][locale]
                            not in result["weapons"]
                        ):
                            cast(Dict[str, List[str]], result)["weapons"].append(
                                job["my_data"]["weapons"][i]["name"][locale]
                            )
                for i in range(0, len(job["teammates"])):
                    if job["teammates"][i]["weapons"] is not None:
                        for j in range(0, len(job["teammates"][i]["weapons"])):
                            if (
                                job["teammates"][i]["weapons"][j]["name"][locale]
                                not in result["weapons"]
                            ):
                                cast(Dict[str, List[str]], result)["weapons"].append(
                                    job["teammates"][i]["weapons"][j]["name"][locale]
                                )
    return result


def hasWeapon(data: str, weapon: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs that contain the chosen weapon.

    :param data: the full name of the data file
    :type data: str
    :param weapon: the name or ID of the chosen weapon
    :type weapon: str
    :return: the full names of the paired filtered files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> core.hasWeapon("data/salmonAll.jl.gz", "Grizzco Charger")
    (
        'data/salmonAll/weapon/Grizzco Charger.jl.gz',
        'data/salmonAll/notWeapon/Grizzco Charger.jl.gz'
    )

    """
    if not (
        os.path.exists(data[0:-6] + "/weapon/" + weapon + ".jl.gz")
        and os.path.exists(data[0:-6] + "/notWeapon/" + weapon + ".jl.gz")
    ):
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/weapon/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/notWeapon/")
        except FileExistsError:
            pass
        with gzip.open(data) as reader:
            with gzip.open(
                data[0:-6] + "/weapon/" + weapon + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writerA:
                with gzip.open(
                    data[0:-6] + "/notWeapon/" + weapon + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writerB:
                    for var in jsonlines.Reader(reader, ujson.loads):
                        if (
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
                                            var["teammates"][0]["weapons"][0]["key"]
                                            == weapon
                                            or (
                                                len(var["teammates"][0]["weapons"]) > 1
                                                and var["teammates"][0]["weapons"][1][
                                                    "key"
                                                ]
                                                == weapon
                                            )
                                            or (
                                                len(var["teammates"][0]["weapons"]) > 2
                                                and var["teammates"][0]["weapons"][2][
                                                    "key"
                                                ]
                                                == weapon
                                            )
                                        )
                                    )
                                    or (
                                        len(var["teammates"]) > 1
                                        and var["teammates"][1]["weapons"] is not None
                                        and (
                                            var["teammates"][1]["weapons"][0]["key"]
                                            == weapon
                                            or (
                                                len(var["teammates"][1]["weapons"]) > 1
                                                and var["teammates"][1]["weapons"][1][
                                                    "key"
                                                ]
                                                == weapon
                                            )
                                            or (
                                                len(var["teammates"][1]["weapons"]) > 2
                                                and var["teammates"][1]["weapons"][2][
                                                    "key"
                                                ]
                                                == weapon
                                            )
                                        )
                                    )
                                    or (
                                        len(var["teammates"]) > 2
                                        and var["teammates"][2]["weapons"] is not None
                                        and (
                                            var["teammates"][2]["weapons"][0]["key"]
                                            == weapon
                                            or (
                                                len(var["teammates"][2]["weapons"]) > 1
                                                and var["teammates"][2]["weapons"][1][
                                                    "key"
                                                ]
                                                == weapon
                                            )
                                            or (
                                                len(var["teammates"][2]["weapons"]) > 2
                                                and var["teammates"][2]["weapons"][2][
                                                    "key"
                                                ]
                                                == weapon
                                            )
                                        )
                                    )
                                )
                            )
                            or (var["my_data"]["weapons"][0]["name"][locale] == weapon)
                            or (
                                len(var["my_data"]["weapons"]) > 1
                                and var["my_data"]["weapons"][1]["name"][locale]
                                == weapon
                            )
                            or (
                                len(var["my_data"]["weapons"]) > 2
                                and var["my_data"]["weapons"][2]["name"][locale]
                                == weapon
                            )
                            or (
                                var["teammates"] is not None
                                and (
                                    (
                                        len(var["teammates"]) > 0
                                        and var["teammates"][0]["weapons"] is not None
                                        and (
                                            var["teammates"][0]["weapons"][0]["name"][
                                                locale
                                            ]
                                            == weapon
                                            or (
                                                len(var["teammates"][0]["weapons"]) > 1
                                                and var["teammates"][0]["weapons"][1][
                                                    "name"
                                                ][locale]
                                                == weapon
                                            )
                                            or (
                                                len(var["teammates"][0]["weapons"]) > 2
                                                and var["teammates"][0]["weapons"][2][
                                                    "name"
                                                ][locale]
                                                == weapon
                                            )
                                        )
                                    )
                                    or (
                                        len(var["teammates"]) > 1
                                        and var["teammates"][1]["weapons"] is not None
                                        and (
                                            var["teammates"][1]["weapons"][0]["name"][
                                                locale
                                            ]
                                            == weapon
                                            or (
                                                len(var["teammates"][1]["weapons"]) > 1
                                                and var["teammates"][1]["weapons"][1][
                                                    "name"
                                                ][locale]
                                                == weapon
                                            )
                                            or (
                                                len(var["teammates"][1]["weapons"]) > 2
                                                and var["teammates"][1]["weapons"][2][
                                                    "name"
                                                ][locale]
                                                == weapon
                                            )
                                        )
                                    )
                                    or (
                                        len(var["teammates"]) > 2
                                        and var["teammates"][2]["weapons"] is not None
                                        and (
                                            var["teammates"][2]["weapons"][0]["name"][
                                                locale
                                            ]
                                            == weapon
                                            or (
                                                len(var["teammates"][2]["weapons"]) > 1
                                                and var["teammates"][2]["weapons"][1][
                                                    "name"
                                                ][locale]
                                                == weapon
                                            )
                                            or (
                                                len(var["teammates"][2]["weapons"]) > 2
                                                and var["teammates"][2]["weapons"][2][
                                                    "name"
                                                ][locale]
                                                == weapon
                                            )
                                        )
                                    )
                                )
                            )
                        ):
                            ujson.dump(var, writerA)
                            writerA.write("\n")
                        else:
                            ujson.dump(var, writerB)
                            writerB.write("\n")
    return (
        data[0:-6] + "/weapon/" + weapon + ".jl.gz",
        data[0:-6] + "/notWeapon/" + weapon + ".jl.gz",
    )


def usesWeapon(data: str, weapon: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the player uses the chosen weapon.

    :param data: the file name of the data file
    :type data: str
    :param weapon: the name or ID of the chosen weapon
    :type weapon: str
    :return: the full names of the paired filtered files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> usesWeapon("data/", "salmonAll.jl.gz", "Grizzco Charger")
    (
        'data/salmonAll/usesWeapon/Grizzco Charger.jl.gz',
        'data/salmonAll/notUsesWeapon/Grizzco Charger.jl.gz'
    )

    """
    if not (
        os.path.exists(data[0:-6] + "/usesWeapon/" + weapon + ".jl.gz")
        and os.path.exists(data[0:-6] + "/notUsesWeapon/" + weapon + ".jl.gz")
    ):
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/usesWeapon/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/notUsesWeapon/")
        except FileExistsError:
            pass
        with gzip.open(data) as reader:
            with gzip.open(
                data[0:-6] + "/usesWeapon/" + weapon + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writerA:
                with gzip.open(
                    data[0:-6] + "/usesWeapon/" + weapon + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writerB:
                    for var in jsonlines.Reader(reader, ujson.loads):
                        if (
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
                                and var["my_data"]["weapons"][1]["name"][locale]
                                == weapon
                            )
                            or (
                                len(var["my_data"]["weapons"]) > 2
                                and var["my_data"]["weapons"][2]["name"][locale]
                                == weapon
                            )
                        ):
                            ujson.dump(var, writerA)
                            writerA.write("\n")
                        else:
                            ujson.dump(var, writerB)
                            writerB.write("\n")
    return (
        data[0:-6] + "/usesWeapon/" + weapon + ".jl.gz",
        data[0:-6] + "/notUsesWeapon/" + weapon + ".jl.gz",
    )


def findPlayerIdByName(data: str, player: str) -> List[str]:
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
        for job in jsonlines.Reader(reader, ujson.loads):
            if (
                job["my_data"]["name"] == player
                and job["my_data"]["splatnet_id"] not in foundIds
            ):
                foundIds.append(job["my_data"]["splatnet_id"])
            if job["teammates"] is not None:
                for teammate in job["teammates"]:
                    if (
                        teammate["name"] == player
                        and teammate["splatnet_id"] not in foundIds
                    ):
                        foundIds.append(teammate["splatnet_id"])
    return foundIds


def onStage(data: str, stage: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs on the chosen stage.

    :param data: the file name of the data file
    :type data: str
    :param stage: the name or ID of the chosen stage
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
        'data/salmonAll/stage/Ruins of Ark Polaris.jl.gz',
        'data/salmonAll/notStage/Ruins of Ark Polaris.jl.gz'
    )

    """
    if not (
        os.path.exists(data[0:-6] + "/stage/" + stage + ".jl.gz")
        and os.path.exists(data[0:-6] + "/notStage/" + stage + ".jl.gz")
    ):
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/stage/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/notStage/")
        except FileExistsError:
            pass
        with gzip.open(data) as reader:
            with gzip.open(
                data[0:-6] + "/stage/" + stage + ".jl.gz", "at", encoding="utf8"
            ) as writerA:
                with gzip.open(
                    data[0:-6] + "/notStage/" + stage + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writerB:
                    for var in jsonlines.Reader(reader, ujson.loads):
                        if var["stage"] is not None and stage in (
                            var["stage"]["key"],
                            var["stage"]["name"][locale],
                        ):
                            ujson.dump(var, writerA)
                            writerA.write("\n")
                        else:
                            ujson.dump(var, writerB)
                            writerB.write("\n")
    return (
        data[0:-6] + "/stage/" + stage + ".jl.gz",
        data[0:-6] + "/notStage/" + stage + ".jl.gz",
    )


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
        'data/salmonAll/notSpecial/Splashdown.jl.gz'
    )

    """
    if not (
        os.path.exists(data[0:-6] + "/special/" + special + ".jl.gz")
        and os.path.exists(data[0:-6] + "/notSpecial/" + special + ".jl.gz")
    ):
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/special/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/notSpecial/")
        except FileExistsError:
            pass
        with gzip.open(data) as reader:
            with gzip.open(
                data[0:-6] + "/special/" + special + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writerA:
                with gzip.open(
                    data[0:-6] + "/notSpecial/" + special + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writerB:
                    for var in jsonlines.Reader(reader, ujson.loads):
                        if special in (
                            var["my_data"]["special"]["key"],
                            var["my_data"]["special"]["name"][locale],
                        ):
                            ujson.dump(var, writerA)
                            writerA.write("\n")
                        else:
                            ujson.dump(var, writerB)
                            writerB.write("\n")
    return (
        data[0:-6] + "/special/" + special + ".jl.gz",
        data[0:-6] + "/notSpecial/" + special + ".jl.gz",
    )


def failReason(
    path: str, data: str, reason: str
) -> Tuple[Tuple[str, str], Tuple[str, str]]:
    """
    Filter the data file to only jobs where the fail reason was the chosen reason.

    :param path: the directory path of the data file
    :type path: str
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
    >>> core.failReason("data/", "salmonAll.jl.gz", "None")
    (
        ('data/salmonAll/failReason/', 'None.jl.gz'),
        ('data/salmonAll/notFailReason/', 'None.jl.gz')
    )

    """
    if not (
        os.path.exists(path + data[0:-6] + "/failReason/" + reason + ".jl.gz")
        and os.path.exists(path + data[0:-6] + "/notFailReason/" + reason + ".jl.gz")
    ):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/failReason/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/notFailReason/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/failReason/" + reason + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writerA:
                with gzip.open(
                    path + data[0:-6] + "/notFailReason/" + reason + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writerB:
                    for var in jsonlines.Reader(reader, ujson.loads):
                        if var["fail_reason"] == reason:
                            ujson.dump(var, writerA)
                            writerA.write("\n")
                        else:
                            ujson.dump(var, writerB)
                            writerB.write("\n")
    return (
        (path + data[0:-6] + "/failReason/", reason + ".jl.gz"),
        (path + data[0:-6] + "/notFailReason/", reason + ".jl.gz"),
    )


def duringRotationInt(data: str, rotation: int) -> Tuple[str, str]:
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
    >>> core.duringRotationInt("data/salmonAll.jl.gz", 1607752800)
    (
        'data/salmonAll/rotation/1607752800.jl.gz',
        'data/salmonAll/notRotation/1607752800.jl.gz'
    )

    """
    if not (
        os.path.exists(data[0:-6] + "/rotation/" + str(rotation) + ".jl.gz")
        and os.path.exists(data[0:-6] + "/notRotation/" + str(rotation) + ".jl.gz")
    ):
        try:
            os.mkdir(data[0:-6])
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/rotation/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/notRotation/")
        except FileExistsError:
            pass
        with gzip.open(data) as reader:
            with gzip.open(
                data[0:-6] + "/rotation/" + str(rotation) + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writerA:
                with gzip.open(
                    data[0:-6] + "/notRotation/" + str(rotation) + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writerB:
                    for job in jsonlines.Reader(reader, ujson.loads):
                        if job["shift_start_at"]["time"] == rotation:
                            ujson.dump(job, writerA)
                            writerA.write("\n")
                        else:
                            ujson.dump(job, writerB)
                            writerB.write("\n")
    return (
        data[0:-6] + "/rotation/" + str(rotation) + ".jl.gz",
        data[0:-6] + "/notRotation/" + str(rotation) + ".jl.gz",
    )


def clearWave(data: str, wave: int) -> Tuple[str, str]:
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
    if not os.path.exists(
        (data[0:-6] + "/clearWaves/equal/" + str(wave) + ".jl.gz")
        and (data[0:-6] + "/clearWaves/notEqual/" + str(wave) + ".jl.gz")
    ):
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/clearWaves/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/clearWaves/equal/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/clearWaves/notEqual/")
        except FileExistsError:
            pass
        with gzip.open(data) as reader:
            with gzip.open(
                data[0:-6] + "/clearWaves/equal/" + str(wave) + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writerA:
                with gzip.open(
                    data[0:-6] + "/clearWaves/notEqual/" + str(wave) + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writerB:
                    for job in jsonlines.Reader(reader, ujson.loads):
                        if job["clear_waves"] == wave:
                            ujson.dump(job, writerA)
                            writerA.write("\n")
                        else:
                            ujson.dump(job, writerB)
                            writerB.write("\n")
    return (
        data[0:-6] + "/clearWaves/equal/" + str(wave) + ".jl.gz",
        data[0:-6] + "/clearWaves/notEqual/" + str(wave) + ".jl.gz",
    )


def greaterThanClearWave(data: str, wave: int) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the clear wave was greater than the chosen clear wave.

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
    >>> core.greaterThanClearWave("data/salmonAll.jl.gz", 2)
    (
        ('data/salmonAll/clearWaves/greaterThan/2.jl.gz'),
        ('data/salmonAll/clearWaves/notGreaterThan/2.jl.gz')
    )

    """
    if not os.path.exists(
        (data[0:-6] + "/clearWaves/greaterThan/" + str(wave) + ".jl.gz")
        and (data[0:-6] + "/clearWaves/notGreaterThan/" + str(wave) + ".jl.gz")
    ):
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/clearWaves/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/clearWaves/greaterThan/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/clearWaves/notGreaterThan/")
        except FileExistsError:
            pass
        with gzip.open(data) as reader:
            with gzip.open(
                data[0:-6] + "/clearWaves/greaterThan/" + str(wave) + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writerA:
                with gzip.open(
                    data[0:-6] + "/clearWaves/notGreaterThan/" + str(wave) + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writerB:
                    for job in jsonlines.Reader(reader, ujson.loads):
                        if job["clear_waves"] > wave:
                            ujson.dump(job, writerA)
                            writerA.write("\n")
                        else:
                            ujson.dump(job, writerB)
                            writerB.write("\n")
    return (
        data[0:-6] + "/clearWaves/greaterThan/" + str(wave) + ".jl.gz",
        data[0:-6] + "/clearWaves/notGreaterThan/" + str(wave) + ".jl.gz",
    )


def lessThanClearWave(data: str, wave: int) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the clear wave was less than the chosen clear wave.

    :param data: the full name name of the data file
    :type data: str
    :param wave: the chosen clear wave
    :type wave: int
    :return: the full names of the paired filtered files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> core.lessThanClearWave("data/salmonAll.jl.gz", 1)
    (
        'data/salmonAll/clearWaves/lessThan/1.jl.gz',
        'data/salmonAll/clearWaves/notLessThan/1.jl.gz'
    )

    """
    if not (
        os.path.exists(data[0:-6] + "/clearWaves/lessThan/" + str(wave) + ".jl.gz")
        and os.path.exists(
            data[0:-6] + "/clearWaves/notLessThan/" + str(wave) + ".jl.gz"
        )
    ):
        try:
            os.mkdir(data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/clearWaves/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/clearWaves/lessThan/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/clearWaves/notLessThan/")
        except FileExistsError:
            pass
        with gzip.open(data) as reader:
            with gzip.open(
                data[0:-6] + "/clearWaves/lessThan/" + str(wave) + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writerA:
                with gzip.open(
                    data[0:-6] + "/clearWaves/notLessThan/" + str(wave) + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writerB:
                    for job in jsonlines.Reader(reader, ujson.loads):
                        if job["clear_waves"] < wave:
                            ujson.dump(job, writerA)
                            writerA.write("\n")
                        else:
                            ujson.dump(job, writerB)
                            writerB.write("\n")
    return (
        data[0:-6] + "/clearWaves/lessThan/" + str(wave) + ".jl.gz",
        data[0:-6] + "/clearWaves/notLessThan/" + str(wave) + ".jl.gz",
    )


def dangerRate(data: str, rate: str) -> Tuple[str, str]:
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
    if not (
        os.path.exists(data[0:-6] + "/dangerRate/equal/" + rate + ".jl.gz")
        and os.path.exists(data[0:-6] + "/dangerRate/notEqual/" + rate + ".jl.gz")
    ):
        try:
            os.mkdir(data[0:-6])
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/dangerRate/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/dangerRate/equal/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/dangerRate/notEqual/")
        except FileExistsError:
            pass
        with gzip.open(data) as reader:
            with gzip.open(
                data[0:-6] + "/dangerRate/equal/" + rate + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writerA:
                with gzip.open(
                    data[0:-6] + "/dangerRate/notEqual/" + rate + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writerB:
                    for job in jsonlines.Reader(reader, ujson.loads):
                        if job["danger_rate"] == rate:
                            ujson.dump(job, writerA)
                            writerA.write("\n")
                        else:
                            ujson.dump(job, writerB)
                            writerB.write("\n")
    return (
        data[0:-6] + "/dangerRate/equal/" + rate + ".jl.gz",
        data[0:-6] + "/dangerRate/notEqual/" + rate + ".jl.gz",
    )


def greaterThanDangerRate(data: str, rate: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the danger rate was greater than the chosen danger rate.

    :param data: the full name of the data file
    :type data: str
    :param rate: the chosen danger rate
    :type rate: str
    :return: the full names of the paired filtered files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> core.greaterThanDangerRate("data/salmonAll.jl.gz", "100.0")
    (
        'data/salmonAll/dangerRate/greaterThan/100.0.jl.gz',
        'data/salmonAll/dangerRate/notGreaterThan/100.0.jl.gz'
    )

    """
    if not (
        os.path.exists(data[0:-6] + "/dangerRate/greaterThan/" + rate + ".jl.gz")
        and os.path.exists(data[0:-6] + "/dangerRate/notGreaterThan/" + rate + ".jl.gz")
    ):
        try:
            os.mkdir(data[0:-6])
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/dangerRate/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/dangerRate/greaterThan/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/dangerRate/notGreaterThan/")
        except FileExistsError:
            pass
        with gzip.open(data) as reader:
            with gzip.open(
                data[0:-6] + "/dangerRate/greaterThan/" + rate + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writerA:
                with gzip.open(
                    data[0:-6] + "/dangerRate/notGreaterThan/" + rate + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writerB:
                    for job in jsonlines.Reader(reader, ujson.loads):
                        if float(job["danger_rate"]) > float(rate):
                            ujson.dump(job, writerA)
                            writerA.write("\n")
                        else:
                            ujson.dump(job, writerB)
                            writerB.write("\n")
    return (
        data[0:-6] + "/dangerRate/greaterThan/" + rate + ".jl.gz",
        data[0:-6] + "/dangerRate/notGreaterThan/" + rate + ".jl.gz",
    )


def lessThanDangerRate(data: str, rate: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the danger rate was less than the chosen danger rate.

    :param data: the full name of the data file
    :type data: str
    :param rate: the chosen danger rate
    :type rate: str
    :return: the full names of the paired filtered files
    :rtype: Tuple[str, str]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> core.lessThanDangerRate("data/salmonAll.jl.gz", "100.0")
    (
        'data/salmonAll/dangerRate/lessThan/100.0.jl.gz',
        'data/salmonAll/dangerRate/notLessThan/100.0.jl.gz'
    )

    """
    if not (
        os.path.exists(data[0:-6] + "/dangerRate/lessThan/" + rate + ".jl.gz")
        and os.path.exists(data[0:-6] + "/dangerRate/notLessThan/" + rate + ".jl.gz")
    ):
        try:
            os.mkdir(data[0:-6])
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/dangerRate/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/dangerRate/lessThan/")
        except FileExistsError:
            pass
        try:
            os.mkdir(data[0:-6] + "/dangerRate/notLessThan/")
        except FileExistsError:
            pass
        with gzip.open(data) as reader:
            with gzip.open(
                data[0:-6] + "/dangerRate/lessThan/" + rate + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writerA:
                with gzip.open(
                    data[0:-6] + "/dangerRate/notLessThan/" + rate + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writerB:
                    for job in jsonlines.Reader(reader, ujson.loads):
                        if float(job["danger_rate"]) < float(rate):
                            ujson.dump(job, writerA)
                            writerA.write("\n")
                        else:
                            ujson.dump(job, writerB)
                            writerB.write("\n")
    return (
        data[0:-6] + "/dangerRate/lessThan/" + rate + ".jl.gz",
        data[0:-6] + "/dangerRate/notLessThan/" + rate + ".jl.gz",
    )


def getValMultiDimensional(
    data: Union[list, Dict[str, Any]], statArr: List[Union[str, int]]
) -> str:
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
                return getValMultiDimensional(cast(list, data)[statArr[0]], statArr[1:])
            return ""
        return getValMultiDimensional(
            cast(Dict[str, Union[list, Dict[str, Any]]], data)[statArr[0]], statArr[1:]
        )
    if isinstance(statArr[0], int):
        if len(data) > statArr[0]:
            return cast(List[str], data)[statArr[0]]
        return ""
    return cast(Dict[str, str], data)[statArr[0]]


def statSummary(data: str, stat: str) -> Tuple[float, float, float, float]:
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


def waveClearPercentageWithWeapon(data: str, weapon: str) -> float:
    """

    :param data: str:
    :param weapon: str:
    :returns float:

    """
    with gzip.open(data) as reader:
        sumVal: float = 0.0
        count: float = 0.0
        for job in jsonlines.Reader(reader, ujson.loads):
            sumVal += int(
                (
                    weapon
                    in (
                        job["my_data"]["weapons"][0]["key"],
                        job["my_data"]["weapons"][0]["name"][locale],
                    )
                    and job["clear_waves"] > 0
                )
                or (
                    len(job["my_data"]["weapons"]) > 1
                    and weapon
                    in (
                        job["my_data"]["weapons"][1]["key"],
                        job["my_data"]["weapons"][1]["name"][locale],
                    )
                    and job["clear_waves"] > 1
                )
                or (
                    len(job["my_data"]["weapons"]) > 2
                    and weapon
                    in (
                        job["my_data"]["weapons"][2]["key"],
                        job["my_data"]["weapons"][2]["name"][locale],
                    )
                    and job["clear_waves"] > 2
                )
            )
            count += int(
                weapon
                in (
                    job["my_data"]["weapons"][0]["key"],
                    job["my_data"]["weapons"][0]["name"][locale],
                )
                or (
                    len(job["my_data"]["weapons"]) > 1
                    and weapon
                    in (
                        job["my_data"]["weapons"][1]["key"],
                        job["my_data"]["weapons"][1]["name"][locale],
                    )
                )
                or (
                    len(job["my_data"]["weapons"]) > 2
                    and weapon
                    in (
                        job["my_data"]["weapons"][2]["key"],
                        job["my_data"]["weapons"][2]["name"][locale],
                    )
                )
            )
        return sumVal / count


def sumStatWaves(data: jobType, stat: str) -> int:
    """

    :param data:
    :type data: jobType
    :param stat:
    :type stat: str
    :return:
    :rtype: int

    """
    sumVal: int = 0
    for w in cast(Dict[str, List[Dict[str, int]]], data)["waves"]:
        sumVal += w[stat]
    return sumVal


def getPlayersAttribute(data: jobType, attr: str) -> List[str]:
    """

    :param data:
    :type data: jobType
    :param attr:
    :type attr: str
    :return:
    :rtype: List[float]

    """
    attrsList: List[str] = attr.split()
    attrs: List[str] = [
        getValMultiDimensional(
            cast(Dict[str, Union[list, Dict[str, Any]]], data)["my_data"],
            list(map(lambda ele: int(ele) if ele.isdigit() else ele, attrsList)),
        )
    ]
    for p in cast(Dict[str, List[Dict[str, Any]]], data)["teammates"]:
        attrs.append(
            getValMultiDimensional(
                p, list(map(lambda ele: int(ele) if ele.isdigit() else ele, attrsList))
            )
        )
    return attrs


def getWavesAttribute(data: jobType, attr: str) -> str:
    """

    :param data:
    :type data: jobType
    :param attr:
    :type attr: str
    :return:
    :rtype: str

    """
    attrs: str = ""
    attrsList: List[str] = attr.split()
    for i in range(0, 3):
        if i < len(cast(Dict[str, List[Dict[str, Any]]], data)["waves"]):
            attrs += "{:<16}\t".format(
                getValMultiDimensional(
                    cast(Dict[str, List[Dict[str, Any]]], data)["waves"][i],
                    list(
                        map(lambda ele: int(ele) if ele.isdigit() else ele, attrsList)
                    ),
                )
                or 0
            )
        else:
            attrs += "{:<16}\t".format("")
    return attrs


def printOverview(data: str) -> None:
    """

    :param data:
    :type data: str

    """
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
        for job in jsonlines.Reader(reader, ujson.loads):
            count += 1
            clearCount += float(job["clear_waves"] == 3)
            waveTwoCount += float(job["clear_waves"] >= 2)
            waveOneCount += float(job["clear_waves"] >= 1)
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
    print("Jobs: " + str(count))
    print("Average Waves: " + str(sumVal[0] / count))
    print("Clear %: " + str(clearCount / count))
    print("Wave 2 %: " + str(waveTwoCount / count))
    print("Wave 1 %: " + str(waveOneCount / count))
    print(
        "Golden: {} ({}, {}, {}".format(
            sumVal[1] / count, minVal[1], np.median(vals[1]), maxVal[1]
        )
    )
    print(
        "Power Eggs: {} ({}, {}, {})".format(
            sumVal[2] / count, minVal[2], np.median(vals[2]), maxVal[2]
        )
    )
    print(
        "Rescued: {} ({}, {}, {})".format(
            sumVal[3] / count, minVal[3], np.median(vals[3]), maxVal[3]
        )
    )
    print(
        "Deaths: {} ({}, {}, {})".format(
            sumVal[4] / count, minVal[4], np.median(vals[4]), maxVal[4]
        )
    )
    print(
        "Hazard Level: {} ({}, {}, {})".format(
            sumVal[5] / count, minVal[5], np.median(vals[5]), maxVal[5]
        )
    )


def printGeneral(data: jobType) -> None:
    """

    :param data:
    :type data: jobType

    """
    print("Stat.ink Link: {}".format(data["url"]))
    print("Splatnet #: {}".format(data["splatnet_number"]))
    print(
        "Stage: {}".format(
            cast(Dict[str, Dict[str, Dict[str, str]]], data)["stage"]["name"][locale]
        )
    )
    print(
        "Rotation Start Date: {}".format(
            cast(Dict[str, Dict[str, str]], data)["shift_start_at"]["iso8601"]
        )
    )
    print(
        "Start Date: {}".format(
            cast(Dict[str, Dict[str, str]], data)["start_at"]["iso8601"]
        )
    )
    print("Result: {}".format("Cleared" if data["clear_waves"] == 3 else "Failed"))
    print(
        "Title: {} {:<3} -> {} {:<3}".format(
            cast(Dict[str, Dict[str, Dict[str, str]]], data)["title"]["name"][locale]
            if data["title"]
            else "",
            data["title_exp"],
            cast(Dict[str, Dict[str, Dict[str, str]]], data)["title_after"]["name"][
                locale
            ]
            if data["title_after"]
            else "",
            data["title_exp_after"],
        )
    )


def printWaves(data: jobType) -> None:
    """

    :param data:
    :type data: jobType

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


def printWeapons(data: jobType) -> None:
    """

    :param data:
    :type data: jobType

    """
    for i in range(
        0,
        len(cast(Dict[str, Dict[str, list]], data)["my_data"]["weapons"]),
    ):
        weapons = getPlayersAttribute(data, "weapons " + str(i) + " name " + locale)
        print(
            "{:16}".format(
                "Wave {:1} Weapon".format(i + 1),
            )
        )
        for player in weapons:
            print("\t{:16}".format(player))


def printSpecials(data: jobType) -> None:
    """

    :param data:
    :type data: jobType

    """
    for i in range(
        0, len(cast(Dict[str, Dict[str, List[int]]], data)["my_data"]["special_uses"])
    ):
        print(
            "{:16}\t{:}".format(
                "Wave {:1} Special Use".format(i + 1),
                getPlayersAttribute(data, "special_uses " + str(i)),
            )
        )


def printPlayers(data: jobType) -> None:
    """

    :param data:
    :type data: jobType

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


def getBosses(data: jobType) -> List[Union[Dict[str, str], Dict[str, int]]]:
    """

    :param data:
    :type data: jobType
    :return:
    :rtype: List[Union[Dict[str, str], Dict[str, int]]]

    """
    results: List[Union[Dict[str, str], Dict[str, int]]] = []
    names: Dict[str, str] = {}
    appearances: Dict[str, int] = {"": 0}
    if data["boss_appearances"] is None:
        return results
    for boss in range(0, len(cast(Dict[str, list], data)["boss_appearances"])):
        names[
            cast(Dict[str, List[Dict[str, Dict[str, Dict[str, str]]]]], data)[
                "boss_appearances"
            ][boss]["boss"]["name"][locale]
        ] = cast(Dict[str, List[Dict[str, Dict[str, Dict[str, str]]]]], data)[
            "boss_appearances"
        ][
            boss
        ][
            "boss"
        ][
            "name"
        ][
            locale
        ]
        appearances[
            cast(Dict[str, List[Dict[str, Dict[str, Dict[str, str]]]]], data)[
                "boss_appearances"
            ][boss]["boss"]["name"][locale]
        ] = cast(Dict[str, List[Dict[str, int]]], data)["boss_appearances"][boss][
            "count"
        ]
    results.append(names)
    results.append(appearances)
    my_data: Dict[str, int] = {"": 0}
    if cast(Dict[str, Dict[str, list]], data)["my_data"]["boss_kills"] is not None:
        for boss in range(
            0, len(cast(Dict[str, Dict[str, list]], data)["my_data"]["boss_kills"])
        ):
            my_data[
                cast(
                    Dict[str, Dict[str, List[Dict[str, Dict[str, Dict[str, str]]]]]],
                    data,
                )["my_data"]["boss_kills"][boss]["boss"]["name"][locale]
            ] = cast(Dict[str, Dict[str, List[Dict[str, int]]]], data)["my_data"][
                "boss_kills"
            ][
                boss
            ][
                "count"
            ]
    results.append(my_data)
    for teammate in range(0, len(cast(Dict[str, list], data)["teammates"])):
        teammate_data: Dict[str, int] = {"": 0}
        if (
            cast(Dict[str, List[Dict[str, list]]], data)["teammates"][teammate][
                "boss_kills"
            ]
            is not None
        ):
            for boss in range(
                0,
                len(
                    cast(Dict[str, List[Dict[str, list]]], data)["teammates"][teammate][
                        "boss_kills"
                    ]
                ),
            ):
                my_data[
                    cast(
                        Dict[
                            str,
                            List[Dict[str, List[Dict[str, Dict[str, Dict[str, str]]]]]],
                        ],
                        data,
                    )["teammates"][teammate]["boss_kills"][boss]["boss"]["name"][locale]
                ] = cast(Dict[str, List[Dict[str, List[Dict[str, int]]]]], data)[
                    "teammates"
                ][
                    teammate
                ][
                    "boss_kills"
                ][
                    boss
                ][
                    "count"
                ]
        results.append(teammate_data)
    return results


def getSingleJob(data: str, index: int) -> Optional[jobType]:
    """

    :param data: the full name of the data file
    :type data: str
    :param index: the index in the list of the job to find
    :type index: int
    :return: either the found job or None if there isn't a job at that index
    :rtype: Optional[jobType]
    :raises gzip.BadGzipFile: if the file exists but isn't a gzip file
    :raises FileNotFoundError: if the file doesn't exist
    :raises jsonlines.InvalidLineError: if the file is a gzip file of something else

    :Example:

    >>> import core
    >>> core.getSingleJob("data/salmonAll.jl.gz", 0)
    {'id': 2, 'uuid': 'e366bc7e-89a9-5473-a5f4-bc9371fd798a', 'splatnet_number': 475, 'url': 'https://stat.ink/@frozenpandaman/salmon/2', 'api_endpoint': 'https://stat.ink/api/v2/salmon/2', 'user': {'id': 1419, 'name': 'eli', 'screen_name': 'frozenpandaman', 'url': 'https://stat.ink/@frozenpandaman', 'salmon_url': 'https://stat.ink/@frozenpandaman/salmon', 'battle_url': 'https://stat.ink/@frozenpandaman/spl2', 'join_at': {'time': 1451816783, 'iso8601': '2016-01-03T10:26:23+00:00'}, 'profile': {'nnid': 'frozenpandaman', 'friend_code': 'SW-1382-5495-2712', 'twitter': 'frozenpandaman', 'ikanakama': None, 'ikanakama2': 'https://ikanakama.ink/users/62097', 'environment': 'Splatoon: Blackmagic UltraStudio Mini Recorder, Sewell Direct 1x2 HDMI Splitter, HDMI & Thunderbolt cables,
    Mac OS X 10.11 Splatoon 2: splatnet2statink dev :)'}, 'stats': {'work_count': 511, 'total_golden_eggs': 5795, 'total_eggs': 243863, 'total_rescued': 967, 'total_point': 63173, 'as_of': {'time':
    1593685017, 'iso8601': '2020-07-02T10:16:57+00:00'}, 'registered_at': {'time': 1593685018, 'iso8601': '2020-07-02T10:16:58+00:00'}}}, 'stage': {'key': 'shaketoba', 'splatnet': '/images/coop_stage/6d68f5baa75f3a94e5e9bfb89b82e7377e3ecd2c.png', 'name': {'de_DE': 'Siedlungsruine', 'en_GB': 'Lost Outpost', 'en_US': 'Lost Outpost', 'es_ES': 'Caserón Salitre', 'es_MX': 'Caserón Salitre', 'fr_CA': 'Baraque barracuda', 'fr_FR': 'Baraque barracuda', 'it_IT': 'Barricata Barracuda', 'ja_JP': '海上集落シャケト場', 'nl_NL': 'Barracudabarak', 'ru_RU': 'Воблов Отшиб', 'zh_CN': '废弃前哨站', 'zh_TW': '廢棄前哨站'}}, 'is_cleared': False, 'fail_reason': None, 'clear_waves': 2, 'danger_rate': '140.2', 'quota': [16, 17, 19], 'title': None, 'title_exp': 40, 'title_after': {'key': 'profreshional', 'splatnet': 5, 'name': {'de_DE': 'Boss', 'en_GB': 'Profreshional', 'en_US': 'Profreshional', 'es_ES': 'Jefa', 'es_MX': 'Jefa', 'fr_CA': 'Prodige', 'fr_FR': 'Prodige', 'it_IT': 'Ragazza professionista', 'ja_JP': 'たつじん', 'nl_NL': 'Baas', 'ru_RU': 'Начальник', 'zh_CN': '专业人士', 'zh_TW': '專業人士'}, 'generic_name': {'de_DE': 'Boss', 'en_GB': 'Profreshional', 'en_US': 'Profreshional', 'es_ES': 'Jefe/Jefa', 'es_MX': 'Jefe/Jefa', 'fr_CA': 'Prodige', 'fr_FR': 'Prodige', 'it_IT': 'Professionista', 'ja_JP': 'たつじん', 'nl_NL': 'Baas', 'ru_RU': 'Начальник', 'zh_CN': '专业人
    士', 'zh_TW': '專業人士'}}, 'title_exp_after': 40, 'boss_appearances': [{'boss': {'key': 'goldie', 'splatnet': 3, 'splatnet_str': 'sakelien-golden', 'name': {'de_DE': 'Goldie', 'en_GB': 'Goldie', 'en_US': 'Goldie', 'es_ES': 'Salmóreo', 'es_MX': 'Orónido', 'fr_CA': 'Dorax', 'fr_FR': 'Dorax', 'it_IT': "Pinna d'Oro", 'ja_JP': 'キンシャケ', 'nl_NL': 'Goldie', 'ru_RU': "Великий Сам О'Нид", 'zh_CN': '金鱼', 'zh_TW': '金魚'}}, 'count': 3}, {'boss': {'key': 'steelhead', 'splatnet': 6, 'splatnet_str': 'sakelien-bomber', 'name': {'de_DE': 'Bäm', 'en_GB': 'Steelhead', 'en_US': 'Steelhead', 'es_ES': 'Ferroz', 'es_MX': 'Ferroz', 'fr_CA': 'Tête-de-pneu', 'fr_FR': 'Tête-de-pneu', 'it_IT': 'Bomber', 'ja_JP': 'バクダン', 'nl_NL': 'Staalkop', 'ru_RU': 'Дядя Семг', 'zh_CN': '绿帽怪', 'zh_TW': '綠帽怪'}}, 'count': 10}, {'boss': {'key': 'flyfish', 'splatnet': 9, 'splatnet_str': 'sakelien-cup-twins', 'name': {'de_DE': 'Rakzak', 'en_GB': 'Flyfish', 'en_US': 'Flyfish', 'es_ES': 'Drónido', 'es_MX': 'Drónido', 'fr_CA': 'Aéro Ben', 'fr_FR': 'Aéro Ben', 'it_IT': 'Salmodrone', 'ja_JP': 'カタパッド', 'nl_NL': 'Salmodrone', 'ru_RU': 'Некретчик', 'zh_CN': '垃圾桶', 'zh_TW': '垃圾桶'}}, 'count': 4}, {'boss': {'key': 'scrapper', 'splatnet': 12, 'splatnet_str': 'sakelien-shield', 'name': {'de_DE': 'Pfanndit', 'en_GB': 'Scrapper', 'en_US': 'Scrapper', 'es_ES': 'Chatarrónido', 'es_MX': 'Parrillero', 'fr_CA': 'Bricabrute', 'fr_FR': 'Bricabrute', 'it_IT': 'Bindomito', 'ja_JP': 'テッパン', 'nl_NL': 'Jutter', 'ru_RU': 'Кетанкист', 'zh_CN': '铁车', 'zh_TW': '鐵車'}}, 'count': 8}, {'boss': {'key': 'steel_eel', 'splatnet': 13, 'splatnet_str': 'sakelien-snake', 'name': {'de_DE': 'Staal', 'en_GB': 'Steel Eel', 'en_US': 'Steel Eel', 'es_ES': 'Raspoide', 'es_MX': 'Anguiladera', 'fr_CA': 'Carnacier', 'fr_FR': 'Carnacier', 'it_IT': 'Anguilmone', 'ja_JP': 'ヘビ', 'nl_NL': 'Staal', 'ru_RU': 'Громыхариус', 'zh_CN': '长龙铁鳗', 'zh_TW': '長龍鐵鰻'}}, 'count': 6}, {'boss': {'key': 'stinger', 'splatnet': 14, 'splatnet_str': 'sakelien-tower', 'name': {'de_DE': 'Stapla', 'en_GB': 'Stinger', 'en_US': 'Stinger', 'es_ES': 'Pilónido', 'es_MX': 'Fregatorre', 'fr_CA': 'Marmirador', 'fr_FR': 'Marmirador', 'it_IT': 'Pentolaio', 'ja_JP': 'タワー', 'nl_NL': 'Staaplo', 'ru_RU': 'Котельный Сиг', 'zh_CN': '塔怪', 'zh_TW': '塔怪'}}, 'count': 7}, {'boss': {'key': 'maws', 'splatnet': 15, 'splatnet_str': 'sakediver', 'name': {'de_DE': 'Grablax', 'en_GB': 'Maws', 'en_US': 'Maws', 'es_ES': 'Fáucex', 'es_MX': 'Mandíburo', 'fr_CA': 'Gobb', 'fr_FR': 'Gobb', 'it_IT': 'Boccalone', 'ja_JP': 'モグラ', 'nl_NL': 'Snaai', 'ru_RU': 'Жуй-Горбуш', 'zh_CN': '遁地鲨', 'zh_TW': '遁地鯊'}}, 'count': 5}, {'boss': {'key': 'drizzler', 'splatnet': 21, 'splatnet_str': 'sakerocket', 'name': {'de_DE': 'Regnar', 'en_GB': 'Drizzler', 'en_US': 'Drizzler', 'es_ES': 'Barreno', 'es_MX': 'Paragüistas', 'fr_CA': 'Crachin', 'fr_FR': 'Crachin', 'it_IT': 'Piovasco', 'ja_JP': 'コウモ
    リ', 'nl_NL': 'Miezer', 'ru_RU': 'Метеоголец', 'zh_CN': '雨怪', 'zh_TW': '雨怪'}}, 'count': 5}], 'waves': [{'known_occurrence': None, 'water_level': {'key': 'normal', 'splatnet': 'normal', 'name': {'de_DE': 'Mid Tide', 'en_GB': 'Mid Tide', 'en_US': 'Mid Tide', 'es_ES': 'Mid Tide', 'es_MX': 'Mid Tide', 'fr_CA': 'Mid Tide', 'fr_FR': 'Mid Tide', 'it_IT': 'Mid Tide', 'ja_JP': '普通', 'nl_NL': 'Mid Tide', 'ru_RU': 'Mid Tide', 'zh_CN': '普通', 'zh_TW': '普通'}}, 'golden_egg_quota': 16, 'golden_egg_appearances': 39, 'golden_egg_delivered': 22, 'power_egg_collected': 795}, {'known_occurrence': {'key': 'fog', 'splatnet': 'fog', 'name': {'de_DE': 'Nebel', 'en_GB': 'Fog', 'en_US': 'Fog', 'es_ES': 'Niebla', 'es_MX': 'Niebla', 'fr_CA': 'Brouillard', 'fr_FR': 'Brouillard', 'it_IT': 'Nebbia', 'ja_JP': '霧', 'nl_NL': 'Mist', 'ru_RU': 'Туман', 'zh_CN': '大雾', 'zh_TW': '大霧'}}, 'water_level': {'key': 'high', 'splatnet': 'high', 'name': {'de_DE': 'High Tide', 'en_GB': 'High Tide', 'en_US': 'High Tide', 'es_ES': 'High Tide', 'es_MX': 'High Tide', 'fr_CA': 'High Tide', 'fr_FR': 'High Tide', 'it_IT': 'High Tide', 'ja_JP': '満潮', 'nl_NL': 'High Tide', 'ru_RU': 'High Tide', 'zh_CN': '涨潮', 'zh_TW': '漲潮'}}, 'golden_egg_quota': 17, 'golden_egg_appearances': 39, 'golden_egg_delivered': 18, 'power_egg_collected': 832}, {'known_occurrence': None, 'water_level': {'key': 'high', 'splatnet': 'high', 'name': {'de_DE': 'High Tide', 'en_GB': 'High Tide', 'en_US': 'High Tide', 'es_ES': 'High Tide', 'es_MX': 'High Tide', 'fr_CA': 'High Tide', 'fr_FR': 'High Tide',
    'it_IT': 'High Tide', 'ja_JP': '満潮', 'nl_NL': 'High Tide', 'ru_RU': 'High Tide', 'zh_CN': '涨潮', 'zh_TW': '漲潮'}}, 'golden_egg_quota': 19, 'golden_egg_appearances': 30, 'golden_egg_delivered': 18, 'power_egg_collected': 778}], 'my_data': {'splatnet_id': 'cea66b072367d7a3', 'name': 'eli', 'special': {'key': 'presser', 'splatnet': 7, 'name': {'de_DE': 'Hochdruckverunreiniger', 'en_GB': 'Sting Ray', 'en_US': 'Sting Ray', 'es_ES': 'Rayo tintódico', 'es_MX': 'Rayo tintódico', 'fr_CA': 'Pigmalance', 'fr_FR': 'Pigmalance', 'it_IT': 'Baccalaser', 'ja_JP': 'ハイパープレッサー', 'nl_NL': 'Magistraal', 'ru_RU': 'Струятор', 'zh_CN': '水枪', 'zh_TW': '水槍'}}, 'rescue': 5, 'death': 6, 'golden_egg_delivered': 8, 'power_egg_collected': 530, 'species': {'key': 'inkling', 'name': {'de_DE': 'Inkling', 'en_GB': 'Inkling', 'en_US': 'Inkling', 'es_ES': 'Inkling', 'es_MX': 'Inkling', 'fr_CA': 'Inkling', 'fr_FR': 'Inkling', 'it_IT': 'Inkling', 'ja_JP': 'イカ', 'nl_NL': 'Inkling', 'ru_RU': 'Inkling', 'zh_CN': '鱿鱼形态', 'zh_TW': '魷魚形態'}}, 'gender': {'key': 'girl', 'iso5218': 2, 'name': {'de_DE': 'Girl', 'en_GB': 'Girl', 'en_US': 'Girl', 'es_ES': 'Chica', 'es_MX': 'Chica', 'fr_CA': 'Girl', 'fr_FR': 'Girl', 'it_IT': 'Girl', 'ja_JP': 'ガール', 'nl_NL': 'Girl', 'ru_RU': 'Girl', 'zh_CN': '女生', 'zh_TW': '女生'}}, 'special_uses': [0, 1, 0], 'weapons': [{'key': 'campingshelter', 'splatnet': 6010, 'name': {'de_DE': 'Camp-Pluviator', 'en_GB': 'Tenta Brella', 'en_US': 'Tenta Brella', 'es_ES': 'Paratintas maxi', 'es_MX': 'Paratintas forestal', 'fr_CA': 'Méga
    para-encre', 'fr_FR': 'Para-encre XL', 'it_IT': 'Sparatenda', 'ja_JP': 'キャンピングシェルター', 'nl_NL': 'Kampeerplenzer', 'ru_RU': 'Зонтент', 'zh_CN': '野营伞', 'zh_TW': '野營傘'}}, {'key': 'nautilus47', 'splatnet': 4040, 'name': {'de_DE': 'Nautilus 47', 'en_GB': 'Nautilus 47', 'en_US': 'Nautilus 47', 'es_ES': 'Subtralladora 47', 'es_MX': 'Nautilo 47', 'fr_CA': 'Nautilus 47', 'fr_FR':
    'Nautilus 47', 'it_IT': 'Nautilus 47', 'ja_JP': 'ノーチラス47', 'nl_NL': 'Nautilus 47', 'ru_RU': 'Наутилус-47', 'zh_CN': '47式鹦鹉螺', 'zh_TW': '47式鸚鵡螺'}}, {'key': 'sharp', 'splatnet': 20, 'name': {'de_DE': 'Fein-Disperser', 'en_GB': 'Splash-o-matic', 'en_US': 'Splash-o-matic', 'es_ES': 'Marcador fino', 'es_MX': 'Plumón', 'fr_CA': 'Marqueur léger', 'fr_FR': 'Marqueur léger', 'it_IT': "Marker d'assalto", 'ja_JP': 'シャープマーカー', 'nl_NL': 'Spetterspuit', 'ru_RU': 'Плюхомет', 'zh_CN': '针管枪', 'zh_TW': '針管槍'}}], 'boss_kills': [{'boss': {'key': 'scrapper', 'splatnet': 12, 'splatnet_str': 'sakelien-shield', 'name': {'de_DE': 'Pfanndit', 'en_GB': 'Scrapper', 'en_US': 'Scrapper', 'es_ES': 'Chatarrónido', 'es_MX': 'Parrillero', 'fr_CA': 'Bricabrute', 'fr_FR': 'Bricabrute', 'it_IT': 'Bindomito', 'ja_JP': 'テッパン', 'nl_NL': 'Jutter', 'ru_RU': 'Кетанкист', 'zh_CN': '铁车', 'zh_TW': '鐵車'}}, 'count': 3}, {'boss': {'key': 'steel_eel', 'splatnet': 13, 'splatnet_str': 'sakelien-snake', 'name': {'de_DE': 'Staal', 'en_GB': 'Steel Eel', 'en_US': 'Steel Eel', 'es_ES': 'Raspoide', 'es_MX': 'Anguiladera', 'fr_CA': 'Carnacier', 'fr_FR': 'Carnacier', 'it_IT':
    'Anguilmone', 'ja_JP': 'ヘビ', 'nl_NL': 'Staal', 'ru_RU': 'Громыхариус', 'zh_CN': '长龙铁鳗', 'zh_TW': '長龍鐵鰻'}}, 'count': 1}, {'boss': {'key': 'stinger', 'splatnet': 14, 'splatnet_str': 'sakelien-tower', 'name': {'de_DE': 'Stapla', 'en_GB': 'Stinger', 'en_US': 'Stinger', 'es_ES': 'Pilónido', 'es_MX': 'Fregatorre', 'fr_CA': 'Marmirador', 'fr_FR': 'Marmirador', 'it_IT': 'Pentolaio', 'ja_JP': 'タワー', 'nl_NL': 'Staaplo', 'ru_RU': 'Котельный Сиг', 'zh_CN': '塔怪', 'zh_TW': '塔怪'}}, 'count': 1}, {'boss': {'key': 'drizzler', 'splatnet': 21, 'splatnet_str': 'sakerocket', 'name':
    {'de_DE': 'Regnar', 'en_GB': 'Drizzler', 'en_US': 'Drizzler', 'es_ES': 'Barreno', 'es_MX': 'Paragüistas', 'fr_CA': 'Crachin', 'fr_FR': 'Crachin', 'it_IT': 'Piovasco', 'ja_JP': 'コウモリ', 'nl_NL': 'Miezer', 'ru_RU': 'Метеоголец', 'zh_CN': '雨怪', 'zh_TW': '雨怪'}}, 'count': 1}]}, 'teammates': [{'splatnet_id': '2203c2da08903d8b', 'name': 'Razzle', 'special': {'key': 'pitcher', 'splatnet': 2, 'name': {'de_DE': 'Klecks-Bomber', 'en_GB': 'Splat-Bomb Launcher', 'en_US': 'Splat-Bomb Launcher', 'es_ES': 'Ráfaga básica', 'es_MX': 'Plasbombardeo', 'fr_CA': 'Lance-bombes splash', 'fr_FR': 'Lance-bombes splash', 'it_IT': 'Lanciabombe splash', 'ja_JP': 'スプラッシュボムピッチャー', 'nl_NL': 'Klodderbomkanon', 'ru_RU': 'Бомбомет (брызгающие)', 'zh_CN': '三角雷发射器', 'zh_TW': '三角
    雷發射器'}}, 'rescue': 5, 'death': 6, 'golden_egg_delivered': 8, 'power_egg_collected': 700, 'species': None, 'gender': None, 'special_uses': [0, 1, 1], 'weapons': [{'key': 'nautilus47', 'splatnet': 4040, 'name': {'de_DE': 'Nautilus 47', 'en_GB': 'Nautilus 47', 'en_US': 'Nautilus 47', 'es_ES': 'Subtralladora 47', 'es_MX': 'Nautilo 47', 'fr_CA': 'Nautilus 47', 'fr_FR': 'Nautilus 47', 'it_IT': 'Nautilus 47', 'ja_JP': 'ノーチラス47', 'nl_NL': 'Nautilus 47', 'ru_RU': 'Наутилус-47', 'zh_CN': '47式鹦鹉螺', 'zh_TW': '47式鸚鵡螺'}}, {'key': 'sharp', 'splatnet': 20, 'name': {'de_DE': 'Fein-Disperser', 'en_GB': 'Splash-o-matic', 'en_US': 'Splash-o-matic', 'es_ES': 'Marcador fino', 'es_MX': 'Plumón', 'fr_CA': 'Marqueur léger', 'fr_FR': 'Marqueur léger', 'it_IT': "Marker d'assalto", 'ja_JP': 'シャープマーカー', 'nl_NL': 'Spetterspuit', 'ru_RU': 'Плюхомет', 'zh_CN': '针管枪', 'zh_TW': '針管槍'}}, {'key': 'maneuver', 'splatnet': 5010, 'name': {'de_DE': 'Klecks-Doppler', 'en_GB': 'Splat Dualies', 'en_US': 'Splat Dualies', 'es_ES': 'Difusor dual', 'es_MX': 'Difusor dual', 'fr_CA': 'Double encreur', 'fr_FR': 'Double encreur', 'it_IT': 'Repolper duplo', 'ja_JP': 'スプラ
    マニューバー', 'nl_NL': 'Dubbelknallers', 'ru_RU': 'Спуртометы', 'zh_CN': '绿色双枪', 'zh_TW': '綠色雙槍'}}], 'boss_kills': [{'boss': {'key': 'goldie', 'splatnet': 3, 'splatnet_str': 'sakelien-golden', 'name': {'de_DE': 'Goldie', 'en_GB': 'Goldie', 'en_US': 'Goldie', 'es_ES': 'Salmóreo', 'es_MX': 'Orónido', 'fr_CA': 'Dorax', 'fr_FR': 'Dorax', 'it_IT': "Pinna d'Oro", 'ja_JP': 'キンシャケ', 'nl_NL': 'Goldie', 'ru_RU': "Великий Сам О'Нид", 'zh_CN': '金鱼', 'zh_TW': '金魚'}}, 'count': 1}, {'boss': {'key': 'steelhead', 'splatnet': 6, 'splatnet_str': 'sakelien-bomber', 'name': {'de_DE': 'Bäm', 'en_GB': 'Steelhead', 'en_US': 'Steelhead', 'es_ES': 'Ferroz', 'es_MX': 'Ferroz', 'fr_CA': 'Tête-de-pneu', 'fr_FR': 'Tête-de-pneu', 'it_IT': 'Bomber', 'ja_JP': 'バクダン', 'nl_NL': 'Staalkop', 'ru_RU': 'Дядя Семг', 'zh_CN': '绿帽怪', 'zh_TW': '綠帽怪'}}, 'count': 4}, {'boss': {'key': 'scrapper', 'splatnet': 12, 'splatnet_str': 'sakelien-shield', 'name': {'de_DE': 'Pfanndit', 'en_GB': 'Scrapper', 'en_US': 'Scrapper', 'es_ES': 'Chatarrónido', 'es_MX': 'Parrillero', 'fr_CA': 'Bricabrute', 'fr_FR': 'Bricabrute', 'it_IT': 'Bindomito', 'ja_JP': 'テッパン', 'nl_NL': 'Jutter', 'ru_RU': 'Кетанкист', 'zh_CN': '铁车', 'zh_TW': '鐵車'}}, 'count': 1}, {'boss': {'key': 'steel_eel', 'splatnet': 13, 'splatnet_str': 'sakelien-snake', 'name': {'de_DE': 'Staal', 'en_GB': 'Steel
    Eel', 'en_US': 'Steel Eel', 'es_ES': 'Raspoide', 'es_MX': 'Anguiladera', 'fr_CA': 'Carnacier', 'fr_FR': 'Carnacier', 'it_IT': 'Anguilmone', 'ja_JP': 'ヘビ', 'nl_NL': 'Staal', 'ru_RU': 'Громыхариус', 'zh_CN': '长龙铁鳗', 'zh_TW': '長龍鐵鰻'}}, 'count': 1}, {'boss': {'key': 'stinger', 'splatnet': 14, 'splatnet_str': 'sakelien-tower', 'name': {'de_DE': 'Stapla', 'en_GB': 'Stinger', 'en_US': 'Stinger', 'es_ES': 'Pilónido', 'es_MX': 'Fregatorre', 'fr_CA': 'Marmirador', 'fr_FR': 'Marmirador', 'it_IT': 'Pentolaio', 'ja_JP': 'タワー', 'nl_NL': 'Staaplo', 'ru_RU': 'Котельный Сиг', 'zh_CN': '塔怪', 'zh_TW': '塔怪'}}, 'count': 1}, {'boss': {'key': 'maws', 'splatnet': 15, 'splatnet_str': 'sakediver', 'name': {'de_DE': 'Grablax', 'en_GB': 'Maws', 'en_US': 'Maws', 'es_ES': 'Fáucex',
    'es_MX': 'Mandíburo', 'fr_CA': 'Gobb', 'fr_FR': 'Gobb', 'it_IT': 'Boccalone', 'ja_JP': 'モグラ', 'nl_NL': 'Snaai', 'ru_RU': 'Жуй-Горбуш', 'zh_CN': '遁地鲨', 'zh_TW': '遁地鯊'}}, 'count': 1}]}, {'splatnet_id': '169d01a86d3a15cf', 'name': 'slum', 'special': {'key': 'jetpack', 'splatnet': 8, 'name': {'de_DE': 'Tintendüser', 'en_GB': 'Inkjet', 'en_US': 'Inkjet', 'es_ES': 'Propulsor', 'es_MX': 'Propulsor', 'fr_CA': 'Chromo-jet', 'fr_FR': 'Chromo-jet', 'it_IT': 'Jet splat', 'ja_JP': 'ジェットパック', 'nl_NL': 'Inktjet', 'ru_RU': 'Красколет', 'zh_CN': '喷墨背包', 'zh_TW': '噴墨揹包'}}, 'rescue': 8, 'death': 4, 'golden_egg_delivered': 25, 'power_egg_collected': 525, 'species': None, 'gender': None, 'special_uses': [0, 0, 0], 'weapons': [{'key': 'maneuver', 'splatnet': 5010, 'name': {'de_DE': 'Klecks-Doppler', 'en_GB': 'Splat Dualies', 'en_US': 'Splat Dualies', 'es_ES': 'Difusor dual', 'es_MX': 'Difusor dual', 'fr_CA': 'Double encreur', 'fr_FR': 'Double encreur', 'it_IT': 'Repolper duplo', 'ja_JP': 'スプラマニューバー', 'nl_NL': 'Dubbelknallers', 'ru_RU': 'Спуртометы', 'zh_CN': '绿色双枪', 'zh_TW': '綠色雙槍'}}, {'key': 'campingshelter', 'splatnet': 6010, 'name': {'de_DE': 'Camp-Pluviator', 'en_GB': 'Tenta Brella', 'en_US': 'Tenta Brella', 'es_ES': 'Paratintas maxi', 'es_MX': 'Paratintas forestal', 'fr_CA': 'Méga para-encre', 'fr_FR': 'Para-encre XL',
    'it_IT': 'Sparatenda', 'ja_JP': 'キャンピングシェルター', 'nl_NL': 'Kampeerplenzer', 'ru_RU': 'Зонтент', 'zh_CN': '野营伞', 'zh_TW': '野營傘'}}, {'key': 'nautilus47', 'splatnet': 4040, 'name': {'de_DE': 'Nautilus 47', 'en_GB': 'Nautilus 47', 'en_US': 'Nautilus 47', 'es_ES': 'Subtralladora 47', 'es_MX': 'Nautilo 47', 'fr_CA': 'Nautilus 47', 'fr_FR': 'Nautilus 47', 'it_IT': 'Nautilus 47',
    'ja_JP': 'ノーチラス47', 'nl_NL': 'Nautilus 47', 'ru_RU': 'Наутилус-47', 'zh_CN': '47式鹦鹉螺', 'zh_TW': '47式鸚鵡螺'}}], 'boss_kills': [{'boss': {'key': 'goldie', 'splatnet': 3, 'splatnet_str':
    'sakelien-golden', 'name': {'de_DE': 'Goldie', 'en_GB': 'Goldie', 'en_US': 'Goldie', 'es_ES': 'Salmóreo', 'es_MX': 'Orónido', 'fr_CA': 'Dorax', 'fr_FR': 'Dorax', 'it_IT': "Pinna d'Oro", 'ja_JP':
    'キンシャケ', 'nl_NL': 'Goldie', 'ru_RU': "Великий Сам О'Нид", 'zh_CN': '金鱼', 'zh_TW': '金魚'}}, 'count': 1}, {'boss': {'key': 'steelhead', 'splatnet': 6, 'splatnet_str': 'sakelien-bomber', 'name': {'de_DE': 'Bäm', 'en_GB': 'Steelhead', 'en_US': 'Steelhead', 'es_ES': 'Ferroz', 'es_MX': 'Ferroz', 'fr_CA': 'Tête-de-pneu', 'fr_FR': 'Tête-de-pneu', 'it_IT': 'Bomber', 'ja_JP': 'バクダン', 'nl_NL': 'Staalkop', 'ru_RU': 'Дядя Семг', 'zh_CN': '绿帽怪', 'zh_TW': '綠帽怪'}}, 'count': 4}, {'boss': {'key': 'flyfish', 'splatnet': 9, 'splatnet_str': 'sakelien-cup-twins', 'name': {'de_DE': 'Rakzak', 'en_GB': 'Flyfish', 'en_US': 'Flyfish', 'es_ES': 'Drónido', 'es_MX': 'Drónido', 'fr_CA': 'Aéro Ben', 'fr_FR': 'Aéro Ben', 'it_IT': 'Salmodrone', 'ja_JP': 'カタパッド', 'nl_NL': 'Salmodrone', 'ru_RU': 'Некретчик', 'zh_CN': '垃圾桶', 'zh_TW': '垃圾桶'}}, 'count': 1}, {'boss': {'key': 'scrapper', 'splatnet': 12, 'splatnet_str': 'sakelien-shield', 'name': {'de_DE': 'Pfanndit', 'en_GB': 'Scrapper', 'en_US': 'Scrapper', 'es_ES': 'Chatarrónido', 'es_MX': 'Parrillero', 'fr_CA': 'Bricabrute', 'fr_FR': 'Bricabrute', 'it_IT': 'Bindomito', 'ja_JP': 'テッパン', 'nl_NL': 'Jutter', 'ru_RU': 'Кетанкист', 'zh_CN': '铁车', 'zh_TW': '鐵車'}}, 'count': 1}, {'boss': {'key': 'steel_eel', 'splatnet': 13, 'splatnet_str': 'sakelien-snake', 'name': {'de_DE': 'Staal', 'en_GB': 'Steel Eel', 'en_US': 'Steel Eel', 'es_ES': 'Raspoide', 'es_MX': 'Anguiladera', 'fr_CA': 'Carnacier', 'fr_FR': 'Carnacier', 'it_IT': 'Anguilmone', 'ja_JP': 'ヘビ', 'nl_NL': 'Staal', 'ru_RU': 'Громыхариус', 'zh_CN': '长龙铁鳗', 'zh_TW': '長龍鐵鰻'}}, 'count': 1}, {'boss': {'key': 'stinger', 'splatnet': 14, 'splatnet_str': 'sakelien-tower', 'name': {'de_DE': 'Stapla', 'en_GB': 'Stinger', 'en_US': 'Stinger', 'es_ES': 'Pilónido', 'es_MX': 'Fregatorre', 'fr_CA': 'Marmirador', 'fr_FR': 'Marmirador', 'it_IT': 'Pentolaio', 'ja_JP': 'タワー', 'nl_NL': 'Staaplo', 'ru_RU': 'Котельный Сиг', 'zh_CN':
    '塔怪', 'zh_TW': '塔怪'}}, 'count': 3}, {'boss': {'key': 'maws', 'splatnet': 15, 'splatnet_str': 'sakediver', 'name': {'de_DE': 'Grablax', 'en_GB': 'Maws', 'en_US': 'Maws', 'es_ES': 'Fáucex', 'es_MX': 'Mandíburo', 'fr_CA': 'Gobb', 'fr_FR': 'Gobb', 'it_IT': 'Boccalone', 'ja_JP': 'モグラ', 'nl_NL': 'Snaai', 'ru_RU': 'Жуй-Горбуш', 'zh_CN': '遁地鲨', 'zh_TW': '遁地鯊'}}, 'count': 1}, {'boss': {'key': 'drizzler', 'splatnet': 21, 'splatnet_str': 'sakerocket', 'name': {'de_DE': 'Regnar', 'en_GB': 'Drizzler', 'en_US': 'Drizzler', 'es_ES': 'Barreno', 'es_MX': 'Paragüistas', 'fr_CA': 'Crachin', 'fr_FR': 'Crachin', 'it_IT': 'Piovasco', 'ja_JP': 'コウモリ', 'nl_NL': 'Miezer', 'ru_RU': 'Метеоголец', 'zh_CN': '雨怪', 'zh_TW': '雨怪'}}, 'count': 3}]}, {'splatnet_id': '9824a3d3df92a97e', 'name': 'Chito', 'special': {'key': 'chakuchi', 'splatnet': 9, 'name': {'de_DE': 'Tintenschock', 'en_GB': 'Splashdown', 'en_US': 'Splashdown', 'es_ES': 'Salto explosivo', 'es_MX': 'Clavado', 'fr_CA': 'Choc chromatique', 'fr_FR': 'Choc chromatique', 'it_IT': 'Vernischianto', 'ja_JP': 'スーパーチャクチ', 'nl_NL': 'Superlanding', 'ru_RU': 'Мегаплюх', 'zh_CN': '砸地', 'zh_TW': '砸地'}}, 'rescue': 3, 'death': 5, 'golden_egg_delivered': 17, 'power_egg_collected': 650, 'species': None, 'gender': None, 'special_uses': [0, 2, 0], 'weapons': [{'key': 'sharp', 'splatnet': 20, 'name': {'de_DE': 'Fein-Disperser', 'en_GB': 'Splash-o-matic', 'en_US': 'Splash-o-matic', 'es_ES': 'Marcador fino', 'es_MX': 'Plumón', 'fr_CA': 'Marqueur léger', 'fr_FR': 'Marqueur léger', 'it_IT': "Marker d'assalto", 'ja_JP': 'シャープマーカー', 'nl_NL': 'Spetterspuit', 'ru_RU': 'Плюхомет', 'zh_CN': '针管枪', 'zh_TW': '針管槍'}}, {'key': 'maneuver', 'splatnet': 5010, 'name': {'de_DE': 'Klecks-Doppler', 'en_GB': 'Splat Dualies', 'en_US': 'Splat Dualies', 'es_ES': 'Difusor dual', 'es_MX': 'Difusor dual', 'fr_CA': 'Double encreur', 'fr_FR': 'Double encreur', 'it_IT': 'Repolper duplo', 'ja_JP': 'スプラマニューバー', 'nl_NL': 'Dubbelknallers', 'ru_RU': 'Спуртометы', 'zh_CN': '绿色双枪', 'zh_TW': '綠色雙槍'}}, {'key': 'campingshelter', 'splatnet': 6010, 'name': {'de_DE': 'Camp-Pluviator', 'en_GB': 'Tenta Brella', 'en_US': 'Tenta Brella', 'es_ES': 'Paratintas maxi', 'es_MX': 'Paratintas forestal', 'fr_CA': 'Méga para-encre', 'fr_FR': 'Para-encre XL', 'it_IT': 'Sparatenda', 'ja_JP': 'キャンピングシェルター', 'nl_NL': 'Kampeerplenzer', 'ru_RU': 'Зонтент', 'zh_CN': '野营伞', 'zh_TW': '野營傘'}}], 'boss_kills': [{'boss': {'key': 'goldie', 'splatnet': 3, 'splatnet_str': 'sakelien-golden', 'name': {'de_DE': 'Goldie', 'en_GB': 'Goldie', 'en_US': 'Goldie', 'es_ES': 'Salmóreo', 'es_MX': 'Orónido', 'fr_CA': 'Dorax', 'fr_FR': 'Dorax', 'it_IT': "Pinna d'Oro", 'ja_JP': '
    キンシャケ', 'nl_NL': 'Goldie', 'ru_RU': "Великий Сам О'Нид", 'zh_CN': '金鱼', 'zh_TW': '金魚'}}, 'count': 1}, {'boss': {'key': 'steel_eel', 'splatnet': 13, 'splatnet_str': 'sakelien-snake', 'name': {'de_DE': 'Staal', 'en_GB': 'Steel Eel', 'en_US': 'Steel Eel', 'es_ES': 'Raspoide', 'es_MX': 'Anguiladera', 'fr_CA': 'Carnacier', 'fr_FR': 'Carnacier', 'it_IT': 'Anguilmone', 'ja_JP': 'ヘビ', 'nl_NL': 'Staal', 'ru_RU': 'Громыхариус', 'zh_CN': '长龙铁鳗', 'zh_TW': '長龍鐵鰻'}}, 'count': 3}, {'boss': {'key': 'maws', 'splatnet': 15, 'splatnet_str': 'sakediver', 'name': {'de_DE': 'Grablax', 'en_GB': 'Maws', 'en_US': 'Maws', 'es_ES': 'Fáucex', 'es_MX': 'Mandíburo', 'fr_CA': 'Gobb', 'fr_FR': 'Gobb', 'it_IT': 'Boccalone', 'ja_JP': 'モグラ', 'nl_NL': 'Snaai', 'ru_RU': 'Жуй-Горбуш',
    'zh_CN': '遁地鲨', 'zh_TW': '遁地鯊'}}, 'count': 2}]}], 'agent': {'name': 'splatnet2statink', 'version': '1.3.0'}, 'automated': True, 'note': None, 'link_url': None, 'shift_start_at': {'time': 1538460000, 'iso8601': '2018-10-02T06:00:00+00:00'}, 'start_at': {'time': 1538559569, 'iso8601': '2018-10-03T09:39:29+00:00'}, 'end_at': None, 'register_at': {'time': 1541143234, 'iso8601': '2018-11-02T07:20:34+00:00'}}

    """
    count = 0
    with gzip.open(data) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            if count == index:
                return job
            count += 1
    return None


def printBosses(data: jobType) -> None:
    """

    :param data: the job to print boss information for
    :type data: jobType

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


def getArrayOfStat(data: str, stat: str) -> List[float]:
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
        for job in jsonlines.Reader(reader, ujson.loads):
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


def init(mode: str, api_key: str = None) -> str:
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
        temp: List[jobType] = requests.get(url, headers=headers, params=params).json()
        if len(temp) > 0:
            try:
                shutil.rmtree(fileName[0:-6])
            except FileNotFoundError:
                pass
            lastId: int = cast(List[Dict[str, int]], temp)[-1]["id"]
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
                    temp = result.json()
                    prevLastId = lastId
                    if len(temp) > 0:
                        lastId = cast(List[Dict[str, int]], temp)[-1]["id"]
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


if __name__ == "__main__":
    user_key: str = ujson.load(open("keys.json", "r"))["statink_key"]
    startFile = init("User", user_key)
    dataFiles: List[str] = []
    rotations: List[int] = findRotationByWeaponsAndStage(
        startFile,
        ("Grizzco Charger", "Grizzco Brella", "Grizzco Blaster", "Grizzco Slosher"),
        "Ruins of Ark Polaris",
    )
    print(rotations)
    jobs: str = duringRotationInt(startFile, rotations[1])[0]
    dataFiles.append(jobs)
    jobs = dangerRate(jobs, "200.0")[0]
    dataFiles.append(jobs)
    printOverview(jobs)
    print()
    for a in range(0, len(dataFiles)):
        os.remove(dataFiles[a])
