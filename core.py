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


def hasJobs(path: str, data: str) -> bool:
    """
    Check if a given data file has data.

    :param path: the directory path of the data file
    :type path: str
    :param data: the file name of the data file
    :type data: str
    :return: whether the file has jobs or not
    :rtype: bool

    """
    with gzip.open(path + data) as reader:
        try:
            jsonlines.Reader(reader, ujson.loads).read()
            return True
        except EOFError:
            return False


def hasPlayer(
    path: str, data: str, player: str
) -> Tuple[Tuple[str, str], Tuple[str, str]]:
    """
    Filter the jobs in the given data file to jobs that contain the chosen player and jobs that don't.

    :param path: the directory path of the data file
    :type path: str
    :param data: the file name of the data file
    :type data: str
    :param player: the Splatnet ID of the chosen player
    :type player: str
    :return: the path and file name of the paired filtered files
    :rtype: Tuple[Tuple[str, str], Tuple[str, str]]

    """
    if not (
        os.path.exists(path + data[0:-6] + "/playerId/" + player + ".jl.gz")
        and os.path.exists(path + data[0:-6] + "/notPlayerId/" + player + ".jl.gz")
    ):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/playerId/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/notPlayerId/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            if hasJobs(path, data):
                with gzip.open(
                    path + data[0:-6] + "/playerId/" + player + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writerA:
                    with gzip.open(
                        path + data[0:-6] + "/notPlayerId/" + player + ".jl.gz",
                        "at",
                        encoding="utf8",
                    ) as writerB:
                        for var in jsonlines.Reader(reader, ujson.loads):
                            if (
                                var["teammates"][0]["splatnet_id"] == player
                                or (
                                    len(var["teammates"]) > 1
                                    and var["teammates"][1]["splatnet_id"] == player
                                )
                                or (
                                    len(var["teammates"]) > 2
                                    and var["teammates"][2]["splatnet_id"] == player
                                )
                            ):
                                ujson.dump(var, writerA)
                                writerA.write("\n")
                            else:
                                ujson.dump(var, writerB)
                                writerB.write("\n")
    return (
        (path + data[0:-6] + "/playerId/", player + ".jl.gz"),
        (path + data[0:-6] + "/notPlayerId/", player + ".jl.gz"),
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

    """
    result: Dict[str, Union[str, List[str]]] = {}
    with gzip.open(data) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            if job["shift_start_at"]["time"] == rotation:
                result["stage"] = job["stage"]["name"][locale]
                result["weapons"] = []
                for i in range(0, len(job["my_data"]["weapons"])):
                    if (
                        job["my_data"]["weapons"][i]["name"][locale]
                        not in result["weapons"]
                    ):
                        cast(Dict[str, List[str]], result)["weapons"].append(
                            job["my_data"]["weapons"][i]["name"][locale]
                        )
                for i in range(0, len(job["teammates"])):
                    for j in range(0, len(job["teammates"][i]["weapons"])):
                        if (
                            job["teammates"][i]["weapons"][j]["name"][locale]
                            not in result["weapons"]
                        ):
                            cast(Dict[str, List[str]], result)["weapons"].append(
                                job["teammates"][i]["weapons"][j]["name"][locale]
                            )
    return result


def hasWeapon(
    path: str, data: str, weapon: str
) -> Tuple[Tuple[str, str], Tuple[str, str]]:
    """
    Filter the data file to only jobs that contain the chosen weapon and jobs that don't.

    :param path: the directory path of the data file
    :type path: str
    :param data: the file name of the data file
    :type data: str
    :param weapon: the name or ID of the chosen weapon
    :type weapon: str
    :return: the path and filename of the output data files
    :rtype: Tuple[Tuple[str, str], Tuple[str, str]]

    """
    if not (
        os.path.exists(path + data[0:-6] + "/weapon/" + weapon + ".jl.gz")
        and os.path.exists(path + data[0:-6] + "/notWeapon/" + weapon + ".jl.gz")
    ):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/weapon/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/notWeapon/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/weapon/" + weapon + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writerA:
                with gzip.open(
                    path + data[0:-6] + "/notWeapon/" + weapon + ".jl.gz",
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
        (path + data[0:-6] + "/weapon/", weapon + ".jl.gz"),
        (path + data[0:-6] + "/notWeapon/", weapon + ".jl.gz"),
    )


def usesWeapon(
    path: str, data: str, weapon: str
) -> Tuple[Tuple[str, str], Tuple[str, str]]:
    """
    Filter the data file to only jobs where the player uses the chosen weapon.

    :param path: the directory path of the data file
    :type path: str
    :param data: the file name of the data file
    :type data: str
    :param weapon: the name or ID of the chosen weapon
    :type weapon: str
    :return: the path and filename of the output data files
    :rtype: Tuple[Tuple[str, str], Tuple[str, str]]

    """
    if not (
        os.path.exists(path + data[0:-6] + "/usesWeapon/" + weapon + ".jl.gz")
        and os.path.exists(path + data[0:-6] + "/notUsesWeapon/" + weapon + ".jl.gz")
    ):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/usesWeapon/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/notUsesWeapon/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/usesWeapon/" + weapon + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writerA:
                with gzip.open(
                    path + data[0:-6] + "/usesWeapon/" + weapon + ".jl.gz",
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
        (path + data[0:-6] + "/usesWeapon/", weapon + ".jl.gz"),
        (path + data[0:-6] + "/notUsesWeapon/", weapon + ".jl.gz"),
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

    """
    foundIds: List[str] = []
    with gzip.open(data) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            for teammate in job["teammates"]:
                if (
                    teammate["name"] == player
                    and teammate["splatnet_id"] not in foundIds
                ):
                    foundIds.append(teammate["splatnet_id"])
    return foundIds


def onStage(
    path: str, data: str, stage: str
) -> Tuple[Tuple[str, str], Tuple[str, str]]:
    """
    Filter the data file to only jobs on the chosen stage.

    :param path: the directory path of the data file
    :type path: str
    :param data: the file name of the data file
    :type data: str
    :param stage: the name or ID of the chosen stage
    :type stage: str
    :return: the path and filename of the output data files
    :rtype: Tuple[Tuple[str, str], Tuple[str, str]]

    """
    if not (
        os.path.exists(path + data[0:-6] + "/stage/" + stage + ".jl.gz")
        and os.path.exists(path + data[0:-6] + "/notStage/" + stage + ".jl.gz")
    ):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/stage/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/notStage/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/stage/" + stage + ".jl.gz", "at", encoding="utf8"
            ) as writerA:
                with gzip.open(
                    path + data[0:-6] + "/notStage/" + stage + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writerB:
                    for var in jsonlines.Reader(reader, ujson.loads):
                        if stage in (var["stage"]["key"], var["stage"]["name"][locale]):
                            ujson.dump(var, writerA)
                            writerA.write("\n")
                        else:
                            ujson.dump(var, writerB)
                            writerB.write("\n")
    return (
        (path + data[0:-6] + "/stage/", stage + ".jl.gz"),
        (path + data[0:-6] + "/notStage/", stage + ".jl.gz"),
    )


def withSpecial(
    path: str, data: str, special: str
) -> Tuple[Tuple[str, str], Tuple[str, str]]:
    """
    Filter the data file to only jobs where the player had the chosen special.

    :param path: the directory path of the data file
    :type path: str
    :param data: the file name of the data file
    :type data: str
    :param special: the name or ID of the chosen special
    :type special: str
    :return: the path and filename of the output data file
    :rtype: Tuple[Tuple[str, str], Tuple[str, str]]

    """
    if not (
        os.path.exists(path + data[0:-6] + "/special/" + special + ".jl.gz")
        and os.path.exists(path + data[0:-6] + "/notSpecial/" + special + ".jl.gz")
    ):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/special/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/notSpecial/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/special/" + special + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writerA:
                with gzip.open(
                    path + data[0:-6] + "/notSpecial/" + special + ".jl.gz",
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
        (path + data[0:-6] + "/special/", special + ".jl.gz"),
        (path + data[0:-6] + "/notSpecial/", special + ".jl.gz"),
    )


def failReason(path: str, data: str, reason: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the fail reason was the chosen reason.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param reason: str: the chosen reason
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(path + data[0:-6] + "/failReason/" + reason + ".jl.gz"):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/failReason/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/failReason/" + reason + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for var in jsonlines.Reader(reader, ujson.loads):
                    if var["fail_reason"] == reason:
                        ujson.dump(var, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/failReason/", reason + ".jl.gz")


def notFailReason(path: str, data: str, reason: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the fail reason was not the chosen reason.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param reason: str: the chosen reason
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(path + data[0:-6] + "/notFailReason/" + reason + ".jl.gz"):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/notFailReason/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/notFailReason/" + reason + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for var in jsonlines.Reader(reader, ujson.loads):
                    if not var["fail_reason"] == reason:
                        ujson.dump(var, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/notFailReason/", reason + ".jl.gz")


def duringRotationInt(path: str, data: str, rotation: int) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the rotation was the chosen rotation.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param rotation: int: the ID of the chosen rotation
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(path + data[0:-6] + "/rotation/" + str(rotation) + ".jl.gz"):
        try:
            os.mkdir(path + data[0:-6])
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/rotation/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/rotation/" + str(rotation) + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for job in jsonlines.Reader(reader, ujson.loads):
                    if job["shift_start_at"]["time"] == rotation:
                        ujson.dump(job, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/rotation/", str(rotation) + ".jl.gz")


def notDuringRotationInt(path: str, data: str, rotation: int) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the rotation was not the chosen rotation.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param rotation: int: the ID of the chosen rotation
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(
        path + data[0:-6] + "/notRotation/" + str(rotation) + ".jl.gz"
    ):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/notRotation/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/notRotation/" + str(rotation) + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for job in jsonlines.Reader(reader, ujson.loads):
                    if not job["shift_start_at"]["time"] == rotation:
                        ujson.dump(job, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/notRotation/", str(rotation) + ".jl.gz")


def clearWave(path: str, data: str, wave: int) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the clear wave was the chosen clear wave.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param wave: int: the chosen clear wave
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(
        path + data[0:-6] + "/clearWaves/equal/" + str(wave) + ".jl.gz"
    ):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/clearWaves/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/clearWaves/equal/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/clearWaves/equal/" + str(wave) + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for job in jsonlines.Reader(reader, ujson.loads):
                    if job["clear_waves"] == wave:
                        ujson.dump(job, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/clearWaves/equal/", str(wave) + ".jl.gz")


def notClearWave(path: str, data: str, wave: int) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the clear wave was not the chosen clear wave.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param wave: int: the chosen clear wave
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(
        path + data[0:-6] + "/clearWaves/notEqual/" + str(wave) + ".jl.gz"
    ):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/clearWaves/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/clearWaves/notEqual/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/clearWaves/notEqual/" + str(wave) + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for job in jsonlines.Reader(reader, ujson.loads):
                    if job["clear_waves"] != wave:
                        ujson.dump(job, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/clearWaves/notEqual/", str(wave) + ".jl.gz")


def greaterThanClearWave(path: str, data: str, wave: int) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the clear wave was greater than the chosen clear wave.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param wave: int: the chosen clear wave
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(
        path + data[0:-6] + "/clearWaves/greaterThan/" + str(wave) + ".jl.gz"
    ):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/clearWaves/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/clearWaves/greaterThan/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/clearWaves/greaterThan/" + str(wave) + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for job in jsonlines.Reader(reader, ujson.loads):
                    if job["clear_waves"] > wave:
                        ujson.dump(job, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/clearWaves/greaterThan/", str(wave) + ".jl.gz")


def notGreaterThanClearWave(path: str, data: str, wave: int) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the clear wave was not greater than the chosen clear wave.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param wave: int: the chosen clear wave
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(
        path + data[0:-6] + "/clearWaves/notGreaterThan/" + str(wave) + ".jl.gz"
    ):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/clearWaves/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/clearWaves/notGreaterThan/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path
                + data[0:-6]
                + "/clearWaves/notGreaterThan/"
                + str(wave)
                + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for job in jsonlines.Reader(reader, ujson.loads):
                    if not job["clear_waves"] > wave:
                        ujson.dump(job, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/clearWaves/notGreaterThan/", str(wave) + ".jl.gz")


def lessThanClearWave(path: str, data: str, wave: int) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the clear wave was less than the chosen clear wave.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param wave: int: the chosen clear wave
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(
        path + data[0:-6] + "/clearWaves/lessThan/" + str(wave) + ".jl.gz"
    ):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/clearWaves/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/clearWaves/lessThan/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/clearWaves/lessThan/" + str(wave) + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for job in jsonlines.Reader(reader, ujson.loads):
                    if job["clear_waves"] < wave:
                        ujson.dump(job, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/clearWaves/lessThan/", str(wave) + ".jl.gz")


def notLessThanClearWave(path: str, data: str, wave: int) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the clear wave was not less than the chosen clear wave.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param wave: int: the chosen clear wave
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(
        path + data[0:-6] + "/clearWaves/notLessThan/" + str(wave) + ".jl.gz"
    ):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/clearWaves/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/clearWaves/notLessThan/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/clearWaves/notLessThan/" + str(wave) + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for job in jsonlines.Reader(reader, ujson.loads):
                    if not job["clear_waves"] < wave:
                        ujson.dump(job, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/clearWaves/notLessThan/", str(wave) + ".jl.gz")


def dangerRate(path: str, data: str, rate: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the danger rate was the chosen danger rate.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param rate: int: the chosen danger rate
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(path + data[0:-6] + "/dangerRate/equal/" + rate + ".jl.gz"):
        if not os.path.exists(path + data[0:-6]):
            os.mkdir(path + data[0:-6])
        if not os.path.exists(path + data[0:-6] + "/dangerRate/"):
            os.mkdir(path + data[0:-6] + "/dangerRate/")
        if not os.path.exists(path + data[0:-6] + "/dangerRate/equals/"):
            os.mkdir(path + data[0:-6] + "/dangerRate/equals/")
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/dangerRate/equals/" + rate + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for job in jsonlines.Reader(reader, ujson.loads):
                    if job["danger_rate"] == rate:
                        ujson.dump(job, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/dangerRate/equals/", rate + ".jl.gz")


def notDangerRate(path: str, data: str, rate: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the danger rate was not the chosen danger rate.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param rate: int: the chosen danger rate
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(
        path + data[0:-6] + "/dangerRate/notEqual/" + rate + ".jl.gz"
    ):
        if not os.path.exists(path + data[0:-6]):
            os.mkdir(path + data[0:-6])
        if not os.path.exists(path + data[0:-6] + "/dangerRate/"):
            os.mkdir(path + data[0:-6] + "/dangerRate/")
        if not os.path.exists(path + data[0:-6] + "/dangerRate/notEquals/"):
            os.mkdir(path + data[0:-6] + "/dangerRate/notEquals/")
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/dangerRate/notEquals/" + rate + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for job in jsonlines.Reader(reader, ujson.loads):
                    if not job["danger_rate"] == rate:
                        ujson.dump(job, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/dangerRate/notEquals/", rate + ".jl.gz")


def greaterThanDangerRate(path: str, data: str, rate: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the danger rate was greater than the chosen danger rate.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param rate: int: the chosen danger rate
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(
        path + data[0:-6] + "/dangerRate/greaterThan/" + rate + ".jl.gz"
    ):
        if not os.path.exists(path + data[0:-6]):
            os.mkdir(path + data[0:-6])
        if not os.path.exists(path + data[0:-6] + "/dangerRate/"):
            os.mkdir(path + data[0:-6] + "/dangerRate/")
        if not os.path.exists(path + data[0:-6] + "/dangerRate/greaterThan/"):
            os.mkdir(path + data[0:-6] + "/dangerRate/greaterThan/")
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/dangerRate/greaterThan/" + rate + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for job in jsonlines.Reader(reader, ujson.loads):
                    if float(job["danger_rate"]) > float(rate):
                        ujson.dump(job, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/dangerRate/greaterThan/", rate + ".jl.gz")


def notGreaterThanDangerRate(path: str, data: str, rate: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the danger rate was not greater than the chosen danger rate.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param rate: int: the chosen danger rate
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(
        path + data[0:-6] + "/dangerRate/notGreaterThan/" + rate + ".jl.gz"
    ):
        if not os.path.exists(path + data[0:-6]):
            os.mkdir(path + data[0:-6])
        if not os.path.exists(path + data[0:-6] + "/dangerRate/"):
            os.mkdir(path + data[0:-6] + "/dangerRate/")
        if not os.path.exists(path + data[0:-6] + "/dangerRate/notGreaterThan/"):
            os.mkdir(path + data[0:-6] + "/dangerRate/notGreaterThan/")
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/dangerRate/notGreaterThan/" + rate + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for job in jsonlines.Reader(reader, ujson.loads):
                    if float(job["danger_rate"]) <= float(rate):
                        ujson.dump(job, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/dangerRate/notGreaterThan/", rate + ".jl.gz")


def lessThanDangerRate(path: str, data: str, rate: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the danger rate was less than the chosen danger rate.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param rate: int: the chosen danger rate
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(
        path + data[0:-6] + "/dangerRate/notGreaterThan/" + rate + ".jl.gz"
    ):
        if not os.path.exists(path + data[0:-6]):
            os.mkdir(path + data[0:-6])
        if not os.path.exists(path + data[0:-6] + "/dangerRate/"):
            os.mkdir(path + data[0:-6] + "/dangerRate/")
        if not os.path.exists(path + data[0:-6] + "/dangerRate/lessThan/"):
            os.mkdir(path + data[0:-6] + "/dangerRate/lessThan/")
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/dangerRate/lessThan/" + rate + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for job in jsonlines.Reader(reader, ujson.loads):
                    if float(job["danger_rate"]) < float(rate):
                        ujson.dump(job, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/dangerRate/lessThan/", rate + ".jl.gz")


def notLessThanDangerRate(path: str, data: str, rate: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the danger rate was not less than the chosen danger rate.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param rate: int: the chosen danger rate
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(
        path + data[0:-6] + "/dangerRate/notLessThan/" + rate + ".jl.gz"
    ):
        if not os.path.exists(path + data[0:-6]):
            os.mkdir(path + data[0:-6])
        if not os.path.exists(path + data[0:-6] + "/dangerRate/"):
            os.mkdir(path + data[0:-6] + "/dangerRate/")
        if not os.path.exists(path + data[0:-6] + "/dangerRate/lessThan/"):
            os.mkdir(path + data[0:-6] + "/dangerRate/lessThan/")
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/dangerRate/notLessThan/" + rate + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for job in jsonlines.Reader(reader, ujson.loads):
                    if float(job["danger_rate"]) >= float(rate):
                        ujson.dump(job, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/dangerRate/lessThan/", rate + ".jl.gz")


def jobsCount(data: str) -> int:
    """
    Find the total number of jobs in a given data set.

    :param data: str: The full file path of the data file
    :returns int: The number of jobs in the file

    """
    with gzip.open(data) as reader:
        count: int = 0
        for _unused in jsonlines.Reader(reader, ujson.loads):
            count += 1
        return count


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
    if len(statArr) > 1:
        if isinstance(statArr[0], int):
            return getValMultiDimensional(cast(list, data)[statArr[0]], statArr[1:])
        return getValMultiDimensional(
            cast(Dict[str, Union[list, Dict[str, Any]]], data)[statArr[0]], statArr[1:]
        )
    if isinstance(statArr[0], int):
        return cast(List[str], data)[statArr[0]]
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


def wavePercentages(data: str) -> Tuple[float, float, float]:
    """

    :param data:
    :type data: str
    :return:
    :rtype: Tuple[float, float, float]

    """
    with gzip.open(data) as reader:
        clearCount: float = 0.0
        waveTwoCount: float = 0.0
        waveOneCount: float = 0.0
        count: float = 0.0
        for job in jsonlines.Reader(reader, ujson.loads):
            clearCount += int(job["clear_waves"] == 3)
            waveTwoCount += int(job["clear_waves"] >= 2)
            waveOneCount += int(job["clear_waves"] >= 1)
            count += 1.0
        return (clearCount / count, waveTwoCount / count, waveOneCount / count)


def sumStatWaves(data: jobType, stat: str) -> int:
    """

    :param data: dict:
    :param stat: str:
    :returns int:

    """
    sumVal: int = 0
    for w in cast(Dict[str, List[Dict[str, int]]], data)["waves"]:
        sumVal += w[stat]
    return sumVal


def getPlayersAttribute(data: jobType, attr: str) -> str:
    """

    :param data: dict:
    :param attr: str:
    :returns str:

    """
    attrsList: List[str] = attr.split()
    attrs: str = "{:<16}\t".format(
        getValMultiDimensional(
            cast(Dict[str, Union[list, Dict[str, Any]]], data)["my_data"],
            list(map(lambda ele: int(ele) if ele.isdigit() else ele, attrsList)),
        )
        or 0
    )
    for p in cast(Dict[str, List[Dict[str, Any]]], data)["teammates"]:
        attrs += "{:<16}\t".format(
            getValMultiDimensional(
                p, list(map(lambda ele: int(ele) if ele.isdigit() else ele, attrsList))
            )
            or 0
        )
    return attrs


def getWavesAttribute(data: jobType, attr: str) -> str:
    """

    :param data: dict:
    :param attr: str:
    :returns str:

    """
    attrs: str = ""
    attrsList: List[str] = attr.split()
    for i in range(0, 3):
        if i < len(cast(Dict[str, List[Dict[str, Any]]], data)["waves"]):
            attrs += "{:<16}\t".format(
                getValMultiDimensional(
                    cast(Dict[str, List[Dict[str, Any]]], data)["waves"],
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

    :param data: str:

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

    :param data: dict:

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

    :param data: dict:

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

    :param data: dict:

    """
    for i in range(
        0,
        len(cast(Dict[str, Dict[str, list]], data)["my_data"]["weapons"]),
    ):
        print(
            "{:16}\t{:}".format(
                "Wave {:1} Weapon".format(i + 1),
                getPlayersAttribute(data, "weapons " + str(i) + " name " + locale),
            )
        )


def printSpecials(data: jobType) -> None:
    """

    :param data: dict:

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

    :param data: dict:

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

    :param data: dict:
    :returns list:

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


def printBosses(data: jobType) -> None:
    """

    :param data: dict:

    """
    print(
        "{:16}\t{:16}\t{:}".format(
            "Boss Salmonid",
            "Appearances",
            getPlayersAttribute(
                data,
                "name",
            ),
        )
    )
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


def getArrayOfStat(data: str, stat: str) -> list:
    """

    :param data: str:
    :param stat: str:
    :returns list:

    """
    with gzip.open(data) as reader:
        results = []
        for job in jsonlines.Reader(reader, ujson.loads):
            results.append(
                float(
                    getValMultiDimensional(
                        job, cast(List[Union[str, int]], stat.split())
                    )
                )
            )
        return results


def init(mode: str, api_key: str = None) -> Tuple[str, str]:
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
            print(lastId)
            with gzip.open("data/salmon.jl.gz", "at", encoding="utf8") as writer:
                while lastId != prevLastId:
                    for job in temp:
                        ujson.dump(job, writer)
                        writer.write("\n")
                    params["newer_than"] = str(lastId)
                    result = requests.get(
                        "http://stat.ink/api/v2/user-salmon",
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
    return ("data/", fileName[5:])


if __name__ == "__main__":
    user_key: str = ujson.load(open("keys.json", "r"))["statink_key"]
    startFile = init("User", user_key)
    paths: List[str] = []
    dataFiles: List[str] = []
    rotations: List[int] = findRotationByWeaponsAndStage(
        startFile[0] + startFile[1],
        ("Grizzco Charger", "Grizzco Brella", "Grizzco Blaster", "Grizzco Slosher"),
        "Ruins of Ark Polaris",
    )
    print(rotations)
    jobs: Tuple[str, str] = duringRotationInt(startFile[0], startFile[1], rotations[1])
    paths.append(jobs[0])
    dataFiles.append(jobs[1])
    jobs = dangerRate(jobs[0], jobs[1], "200.0")
    paths.append(jobs[0])
    dataFiles.append(jobs[1])
    printOverview(jobs[0] + jobs[1])
    print()
    for a in range(0, len(paths)):
        os.remove(paths[a] + dataFiles[a])
