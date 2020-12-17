import os.path
import ujson
import numpy as np
import requests
import jsonlines
import sys
from typing import Tuple, List, Union, Dict, cast, Optional, Any
import gzip

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


def fetchAllUser(api_key: str) -> None:
    """Fetch all Salmon Run results for the authenticated user and store it in the "data/salmon.jl.gz" file.

    :param api_key: str: the stat.ink API key for the user

    """
    headers: Dict[str, str] = {"Authorization": "Bearer {}".format(api_key)}
    prevLastId: int = 0
    params: Dict[str, str] = {"order": "asc"}
    temp: List[jobType] = requests.get(
        "http://stat.ink/api/v2/user-salmon", headers=headers, params=params
    ).json()
    lastId: int = cast(List[Dict[str, int]], temp)[-1]["id"]
    print(lastId)
    with gzip.open("data/salmon.jl.gz", "at", encoding="utf8") as writer:
        while lastId != prevLastId:
            for job in temp:
                ujson.dump(job, writer)
                writer.write("\n")
            params["newer_than"] = str(lastId)
            result = requests.get(
                "http://stat.ink/api/v2/user-salmon", headers=headers, params=params
            )
            print(result.url)
            print(result)
            temp = result.json()
            prevLastId = lastId
            if len(temp) > 0:
                lastId = cast(List[Dict[str, int]], temp)[-1]["id"]
            print(lastId)


def fetchAll() -> None:
    """Fetch all Salmon Run results for all users and store it in the "data/salmonAll.jl.gz" file."""
    prevLastId: int = 0
    params: Dict[str, str] = {"order": "asc"}
    temp: List[jobType] = requests.get(
        "http://stat.ink/api/v2/salmon", params=params
    ).json()
    lastId: int = cast(List[Dict[str, int]], temp)[-1]["id"]
    print(lastId)
    with gzip.open("data/salmonAll.jl.gz", "at", encoding="utf8") as writer:
        while lastId != prevLastId:
            for job in temp:
                ujson.dump(job, writer)
                writer.write("\n")
            print(os.path.getsize("data/salmonAll.jl.gz"))
            params["newer_than"] = str(lastId)
            result = requests.get("http://stat.ink/api/v2/salmon", params=params)
            print(result.url)
            print(result)
            temp = result.json()
            prevLastId = lastId
            if len(temp) > 0:
                lastId = cast(List[Dict[str, int]], temp)[-1]["id"]
            print(lastId)


def fetchNewUser(api_key: str, recentId: int) -> None:
    """
    Fetch new Salmon Run results for authenticated user and store it in the "data/salmon.jl.gz" file.

    :param api_key: str: the stat.ink API key for the user
    :param recentId: int: the ID of the most recently retrieved job

    """
    headers: Dict[str, str] = {"Authorization": "Bearer {}".format(api_key)}
    prevLastId: int = 0
    params: Dict[str, str] = {"order": "asc", "newer_than": str(recentId)}
    temp: List[jobType] = requests.get(
        "http://stat.ink/api/v2/user-salmon", headers=headers, params=params
    ).json()
    if len(temp) > 0:
        lastId: int = cast(List[Dict[str, int]], temp)[-1]["id"]
        print(lastId)
        with gzip.open("data/salmon.jl.gz", "at", encoding="utf8") as writer:
            while lastId != prevLastId:
                for job in temp:
                    ujson.dump(job, writer)
                    writer.write("\n")
                params["newer_than"] = str(lastId)
                result = requests.get(
                    "http://stat.ink/api/v2/user-salmon", headers=headers, params=params
                )
                print(result.url)
                print(result)
                temp = result.json()
                prevLastId = lastId
                if len(temp) > 0:
                    lastId = cast(List[Dict[str, int]], temp)[-1]["id"]
                print(lastId)


def fetchNewAll(recentId: int) -> None:
    """
    Fetch new Salmon Run results for all users and store it in the "data/salmonAll.jl.gz" file.

    :param recentId: int: the ID of the most recently retrieved jobs

    """
    prevLastId: int = 0
    params: Dict[str, str] = {"order": "asc", "newer_than": str(recentId)}
    temp: List[jobType] = requests.get(
        "http://stat.ink/api/v2/salmon", params=params
    ).json()
    if len(temp) > 0:
        lastId: int = cast(List[Dict[str, int]], temp)[-1]["id"]
        print(lastId)
        with gzip.open("data/salmonAll.jl.gz", "at", encoding="utf8") as writer:
            while lastId != prevLastId:
                for job in temp:
                    ujson.dump(job, writer)
                    writer.write("\n")
                print(os.path.getsize("data/salmonAll.jl.gz"))
                params["newer_than"] = str(lastId)
                result = requests.get("http://stat.ink/api/v2/salmon", params=params)
                print(result.url)
                print(result)
                temp = result.json()
                prevLastId = lastId
                if len(temp) > 0:
                    lastId = cast(List[Dict[str, int]], temp)[-1]["id"]
                print(lastId)


def hasJobs(path: str, data: str) -> bool:
    """
    Check if a given data file has data.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file

    """
    with gzip.open(path + data) as reader:
        try:
            jsonlines.Reader(reader, ujson.loads).read()
            return True
        except EOFError:
            return False


def hasPlayer(path: str, data: str, player: str) -> Tuple[str, str]:
    """
    Filter the jobs in the given data file to only jobs that contain the chosen player.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param player: str: the Splatnet ID of the chosen player

    """
    if not os.path.exists(path + data[0:-6] + "/playerId/" + player + ".jl.gz"):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/playerId/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            if hasJobs(path, data):
                with gzip.open(
                    path + data[0:-6] + "/playerId/" + player + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writer:
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
                            ujson.dump(var, writer)
                            writer.write("\n")
    return (path + data[0:-6] + "/playerId/", player + ".jl.gz")


def withoutPlayer(path: str, data: str, player: str) -> Tuple[str, str]:
    """
    Filter the jobs in the given data file to only jobs that do not contain the chosen player.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param player: str: the Splatnet ID of the chosen player

    """
    if not os.path.exists(path + data[0:-6] + "/notPlayerId/" + player + ".jl.gz"):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/notPlayerId/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            if hasJobs(path, data):
                with gzip.open(
                    path + data[0:-6] + "/notPlayerId/" + player + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writer:
                    for var in jsonlines.Reader(reader, ujson.loads):
                        if not (
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
                            ujson.dump(var, writer)
                            writer.write("\n")
    return (path + data[0:-6] + "/notPlayerId/", player + ".jl.gz")


def hasPlayerByName(path: str, data: str, player: str) -> Tuple[str, str]:
    """
    Filter the jobs in the given data file to only jobs that contain the chosen player.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param player: str: the name of the chosen player

    """
    if not os.path.exists(path + data[0:-6] + "/player/" + player + ".jl.gz"):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/player/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            if hasJobs(path, data):
                with gzip.open(
                    path + data[0:-6] + "/player/" + player + ".jl.gz",
                    "at",
                    encoding="utf8",
                ) as writer:
                    for var in jsonlines.Reader(reader, ujson.loads):
                        if (
                            var["teammates"][0]["name"] == player
                            or (
                                len(var["teammates"]) > 1
                                and var["teammates"][1]["name"] == player
                            )
                            or (
                                len(var["teammates"]) > 2
                                and var["teammates"][2]["name"] == player
                            )
                        ):
                            ujson.dump(var, writer)
                            writer.write("\n")
    return (path + data[0:-6] + "/player/", player + ".jl.gz")


def findRotationByWeaponsAndStage(
    data: str, weapons: Union[Tuple[str, str, str, str], List[str]], stage: str
) -> List[int]:
    """
    Find the rotation IDs for a rotation of the given weapons and stage in the given data file.

    :param data: str: the full path of the data file
    :param weapons: Union[Tuple[str, str, str, str], List[str]: the chosen weapons
    :param stage: str: the chosen stage
    :returns: List[int]: a list of rotation IDs

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
) -> Optional[Dict[str, Union[str, List[str]]]]:
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
    return None


def hasWeapon(path: str, data: str, weapon: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs that contain the chosen weapon.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param weapon: str: The name or ID of the chosen weapon
    :returns Tuple[str, str]: The path and filename of the output data file

    """
    if not os.path.exists(path + data[0:-6] + "/weapon/" + weapon + ".jl.gz"):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/weapon/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/weapon/" + weapon + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
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
                                        var["teammates"][1]["weapons"][0]["key"]
                                        == weapon
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
                                        var["teammates"][2]["weapons"][0]["key"]
                                        == weapon
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
                        ujson.dump(var, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/weapon/", weapon + ".jl.gz")


def doesntHaveWeapon(path: str, data: str, weapon: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs that do not contain the chosen weapon.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param weapon: str: The name or ID of the chosen weapon
    :returns Tuple[str, str]: The path and filename of the output data file

    """
    if not os.path.exists(path + data[0:-6] + "/notWeapon/" + weapon + ".jl.gz"):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/notWeapon/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/notWeapon/" + weapon + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for var in jsonlines.Reader(reader, ujson.loads):
                    if not (
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
                                        var["teammates"][1]["weapons"][0]["key"]
                                        == weapon
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
                                        var["teammates"][2]["weapons"][0]["key"]
                                        == weapon
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
                        ujson.dump(var, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/notWeapon/", weapon + ".jl.gz")


def usesWeapon(path: str, data: str, weapon: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the player uses the chosen weapon.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param weapon: str: The name or ID of the chosen weapon
    :returns Tuple[str, str]: The path and filename of the output data file

    """
    if not os.path.exists(path + data[0:-6] + "/usesWeapon/" + weapon + ".jl.gz"):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/usesWeapon/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/usesWeapon/" + weapon + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
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
                            and var["my_data"]["weapons"][1]["name"][locale] == weapon
                        )
                        or (
                            len(var["my_data"]["weapons"]) > 2
                            and var["my_data"]["weapons"][2]["name"][locale] == weapon
                        )
                    ):
                        ujson.dump(var, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/usesWeapon/", weapon + ".jl.gz")


def doesntUseWeapon(path: str, data: str, weapon: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the player doesn't use the chosen weapon.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param weapon: str: The name or ID of the chosen weapon
    :returns Tuple[str, str]: The path and filename of the output data file

    """
    if not os.path.exists(path + data[0:-6] + "/notUsesWeapon/" + weapon + ".jl.gz"):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/notUsesWeapon/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/notUsesWeapon/" + weapon + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for var in jsonlines.Reader(reader, ujson.loads):
                    if not (
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
                    ):
                        ujson.dump(var, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/notUsesWeapon/", weapon + ".jl.gz")


def findPlayerIdByName(path: str, data: str, player: str) -> List[str]:
    """
    Find all the recorded player IDs for a given player name.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param player: str: the player name to find
    :returns List[str]: the list of found player IDs

    """
    foundIds: List[str] = []
    matches = hasPlayerByName(path, data, player)
    with gzip.open(matches[0] + matches[1]) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            for teammate in job["teammates"]:
                if (
                    teammate["name"] == player
                    and teammate["splatnet_id"] not in foundIds
                ):
                    foundIds.append(teammate["splatnet_id"])
    return foundIds


def onStage(path: str, data: str, stage: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs on the chosen stage.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param stage: str: the name or ID of the chosen stage
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(path + data[0:-6] + "/stage/" + stage + ".jl.gz"):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/stage/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/stage/" + stage + ".jl.gz", "at", encoding="utf8"
            ) as writer:
                for var in jsonlines.Reader(reader, ujson.loads):
                    if stage in (var["stage"]["key"], var["stage"]["name"][locale]):
                        ujson.dump(var, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/stage/", stage + ".jl.gz")


def notOnStage(path: str, data: str, stage: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs not on the chosen stage.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param stage: str: the name or ID of the chosen stage
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(path + data[0:-6] + "/notStage/" + stage + ".jl.gz"):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/notStage/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/notStage/" + stage + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for var in jsonlines.Reader(reader, ujson.loads):
                    if not (
                        stage in (var["stage"]["key"], var["stage"]["name"][locale])
                    ):
                        ujson.dump(var, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/notStage/", stage + ".jl.gz")


def withSpecial(path: str, data: str, special: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the player had the chosen special.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param special: str: the name or ID of the chosen special
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(path + data[0:-6] + "/special/" + special + ".jl.gz"):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/special/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/special/" + special + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for var in jsonlines.Reader(reader, ujson.loads):
                    if special in (
                        var["my_data"]["special"]["key"],
                        var["my_data"]["special"]["name"][locale],
                    ):
                        ujson.dump(var, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/special/", special + ".jl.gz")


def withoutSpecial(path: str, data: str, special: str) -> Tuple[str, str]:
    """
    Filter the data file to only jobs where the player didn't have the chosen special.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param special: str: the name or ID of the chosen special
    :returns Tuple[str, str]: the path and filename of the output data file

    """
    if not os.path.exists(path + data[0:-6] + "/notSpecial/" + special + ".jl.gz"):
        try:
            os.mkdir(path + data[0:-6] + "/")
        except FileExistsError:
            pass
        try:
            os.mkdir(path + data[0:-6] + "/notSpecial/")
        except FileExistsError:
            pass
        with gzip.open(path + data) as reader:
            with gzip.open(
                path + data[0:-6] + "/notSpecial/" + special + ".jl.gz",
                "at",
                encoding="utf8",
            ) as writer:
                for var in jsonlines.Reader(reader, ujson.loads):
                    if not (
                        special
                        in (
                            var["my_data"]["special"]["key"],
                            var["my_data"]["special"]["name"][locale],
                        )
                    ):
                        ujson.dump(var, writer)
                        writer.write("\n")
    return (path + data[0:-6] + "/notSpecial/", special + ".jl.gz")


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

    :param data: str:
    :returns int:

    """
    with gzip.open(data) as reader:
        count: int = 0
        for _unused in jsonlines.Reader(reader, ujson.loads):
            count += 1
        return count


def avgStat(data: str, stat: str) -> float:
    """

    :param data: str:
    :param stat: str:
    :returns float:

    """
    with gzip.open(data) as reader:
        sumVal: float = 0.0
        count: float = 0.0
        for job in jsonlines.Reader(reader, ujson.loads):
            sumVal += float(job[stat])
            count += 1.0
        return sumVal / count


def avgStat2D(data: str, firstD: str, secondD: str) -> float:
    """

    :param data: str:
    :param firstD: str:
    :param secondD: str:
    :returns float:

    """
    with gzip.open(data) as reader:
        sumVal: float = 0.0
        count: float = 0.0
        for job in jsonlines.Reader(reader, ujson.loads):
            sumVal += float(job[firstD][secondD])
            count += 1.0
        return sumVal / count


def maxStat(data: str, stat: str) -> float:
    """

    :param data: str:
    :param stat: str:
    :returns float:

    """
    maxVal: float = 0.0
    with gzip.open(data) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            if maxVal < float(job[stat]):
                maxVal = float(job[stat])
    return maxVal


def maxStat2D(data: str, firstD: str, secondD: str) -> float:
    """

    :param data: str:
    :param firstD: str:
    :param secondD: str:
    :returns float:

    """
    maxVal: float = 0.0
    with gzip.open(data) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            if maxVal < float(job[firstD][secondD]):
                maxVal = float(job[firstD][secondD])
    return maxVal


def minStat(data: str, stat: str) -> float:
    """

    :param data: str:
    :param stat: str:
    :returns float:

    """
    with gzip.open(data) as reader:
        minVal: float = sys.float_info.max
        for job in jsonlines.Reader(reader, ujson.loads):
            if minVal > float(job[stat]):
                minVal = float(job[stat])
    return minVal


def minStat2D(data: str, firstD: str, secondD: str) -> float:
    """

    :param data: str:
    :param firstD: str:
    :param secondD: str:
    :returns float:

    """
    with gzip.open(data) as reader:
        minVal: float = sys.float_info.max
        for job in jsonlines.Reader(reader, ujson.loads):
            if minVal > float(job[firstD][secondD]):
                minVal = float(job[firstD][secondD])
    return minVal


def medianStat(data: str, stat: str) -> float:
    """

    :param data: str:
    :param stat: str:
    :returns float:

    """
    vals: List[float] = []
    with gzip.open(data) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            vals.append(float(job[stat]))
    return np.median(vals)


def medianStat2D(data: str, firstD: str, secondD: str) -> float:
    """

    :param data: str:
    :param firstD: str:
    :param secondD: str:
    :returns float:

    """
    vals: List[float] = []
    with gzip.open(data) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            vals.append(job[firstD][secondD])
    return np.median(vals)


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


def clearPercentage(data: str) -> float:
    """

    :param data: str:
    :returns float:

    """
    with gzip.open(data) as reader:
        sumVal: float = 0.0
        count: float = 0.0
        for job in jsonlines.Reader(reader, ujson.loads):
            sumVal += int(job["clear_waves"] == 3)
            count += 1.0
        return sumVal / count


def waveTwoPercentage(data: str) -> float:
    """

    :param data: str:
    :returns float:

    """
    with gzip.open(data) as reader:
        sumVal: float = 0.0
        count: float = 0.0
        for job in jsonlines.Reader(reader, ujson.loads):
            sumVal += int(job["clear_waves"] >= 2)
            count += 1.0
        return sumVal / count


def waveOnePercentage(data: str) -> float:
    """

    :param data: str:
    :returns float:

    """
    with gzip.open(data) as reader:
        sumVal: float = 0.0
        count: float = 0.0
        for job in jsonlines.Reader(reader, ujson.loads):
            sumVal += int(job["clear_waves"] >= 1)
            count += 1.0
        return sumVal / count


def statSummary(data: str, stat: str) -> str:
    """

    :param data: str:
    :param stat: str:
    :returns str:

    """
    return (
        str(avgStat(data, stat))
        + " ("
        + str(minStat(data, stat))
        + ", "
        + str(medianStat(data, stat))
        + ", "
        + str(maxStat(data, stat))
        + ")"
    )


def statSummary2D(data: str, firstD: str, secondD: str) -> str:
    """

    :param data: str:
    :param firstD: str:
    :param secondD: str:
    :returns str:

    """
    return (
        str(avgStat2D(data, firstD, secondD))
        + " ("
        + str(minStat2D(data, firstD, secondD))
        + ", "
        + str(medianStat2D(data, firstD, secondD))
        + ", "
        + str(maxStat2D(data, firstD, secondD))
        + ")"
    )


def sumStatWaves(
    data: jobType,
    stat: str,
) -> int:
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
    attrs: str = "{:<16}\t".format(
        cast(Dict[str, Dict[str, Union[int, str]]], data)["my_data"][attr] or 0
    )
    for p in cast(Dict[str, List[Dict[str, Union[int, str]]]], data)["teammates"]:
        attrs += "{:<16}\t".format(p[attr] or 0)
    return attrs


def getPlayersAttribute2D(data: jobType, firstD: str, secondD: Union[int, str]) -> str:
    """

    :param data: dict:
    :param firstD: str:
    :param secondD: Union[int, str]:
    :returns str:

    """
    attrs: str = "{:<16}\t".format(
        cast(Dict[str, Dict[str, Any]], data)["my_data"][firstD][secondD] or 0
    )
    for p in cast(Dict[str, List[Dict[str, Any]]], data)["teammates"]:
        attrs += "{:<16}\t".format(p[firstD][secondD] or 0)
    return attrs


def getPlayersAttribute3D(
    data: jobType,
    firstD: str,
    secondD: str,
    thirdD: str,
) -> str:
    """

    :param data: dict:
    :param firstD: str:
    :param secondD: str:
    :param thirdD: str:
    :returns str:

    """
    attrs: str = "{:<16}\t".format(
        cast(Dict[str, Dict[str, Dict[str, Dict[str, Union[int, str]]]]], data)[
            "my_data"
        ][firstD][secondD][thirdD]
        or 0
    )
    for p in cast(
        Dict[str, List[Dict[str, Dict[str, Dict[str, Union[int, str]]]]]], data
    )["teammates"]:
        attrs += "{:<16}\t".format(p[firstD][secondD][thirdD] or 0)
    return attrs


def getPlayersAttribute4D(
    data: jobType,
    firstD: str,
    secondD: int,
    thirdD: str,
    fourthD: str,
) -> str:
    """

    :param data: dict:
    :param firstD: str:
    :param secondD: int:
    :param thirdD: str:
    :param fourthD: str:
    :returns str:

    """
    attrs: str = "{:<16}\t".format(
        cast(Dict[str, List[Dict[str, Dict[str, Union[int, str]]]]], data["my_data"])[
            firstD
        ][secondD][thirdD][fourthD]
        or 0
    )
    for p in cast(
        List[Dict[str, List[Dict[str, Dict[str, Union[int, str]]]]]], data["teammates"]
    ):
        if cast(Dict[str, List[Dict[str, Dict[str, Union[int, str]]]]], p)[
            firstD
        ] is not None and secondD < len(
            cast(Dict[str, List[Dict[str, Dict[str, Union[int, str]]]]], p)[firstD]
        ):
            attrs += "{:<16}\t".format(
                cast(Dict[str, List[Dict[str, Dict[str, Union[int, str]]]]], p)[firstD][
                    secondD
                ][thirdD][fourthD]
                or 0
            )
        else:
            attrs += "{:<16}\t".format("")
    return attrs


def getWavesAttribute(
    data: jobType,
    attr: str,
) -> str:
    """

    :param data: dict:
    :param attr: str:
    :returns str:

    """
    attrs: str = ""
    for i in range(0, 3):
        if i < len(cast(Dict[str, List[Dict[str, Union[int, str]]]], data)["waves"]):
            attrs += "{:<16}\t".format(
                cast(Dict[str, List[Dict[str, Union[int, str]]]], data)["waves"][i][
                    attr
                ]
            )
        else:
            attrs += "{:<16}\t".format("")
    return attrs


def getWavesAttribute3D(
    data: jobType,
    firstD: str,
    secondD: str,
    thirdD: str,
) -> str:
    """

    :param data: dict:
    :param firstD: str:
    :param secondD: str:
    :param thirdD: str:
    :returns str:

    """
    attrs: str = ""
    for i in range(0, 3):
        if (
            i
            < len(
                cast(Dict[str, List[Dict[str, Dict[str, Dict[str, str]]]]], data)[
                    "waves"
                ]
            )
            and cast(Dict[str, List[Dict[str, Dict[str, Dict[str, str]]]]], data)[
                "waves"
            ][i][firstD]
        ):
            attrs += "{:<16}\t".format(
                cast(Dict[str, List[Dict[str, Dict[str, Dict[str, str]]]]], data)[
                    "waves"
                ][i][firstD][secondD][thirdD]
            )
        else:
            attrs += "{:<16}\t".format("")
    return attrs


def printOverview(path: str, data: str) -> None:
    """

    :param path: str:
    :param data: str:

    """
    print("Jobs: " + str(jobsCount(path + data)))
    print("Average Waves: " + str(avgStat(path + data, "clear_waves")))
    print("Clear %: " + str(clearPercentage(path + data)))
    print("Wave 2 %: " + str(waveTwoPercentage(path + data)))
    print("Wave 1 %: " + str(waveOnePercentage(path + data)))
    print("Golden: " + statSummary2D(path + data, "my_data", "golden_egg_delivered"))
    print("Power Eggs: " + statSummary2D(path + data, "my_data", "power_egg_collected"))
    print("Rescued: " + statSummary2D(path + data, "my_data", "rescue"))
    print("Deaths: " + statSummary2D(path + data, "my_data", "death"))
    print("Hazard Level: " + statSummary(path + data, "danger_rate"))


def printGeneral(data: jobType) -> None:
    """

    :param data: dict:

    """
    print("Stat.ink Link: " + cast(Dict[str, str], data)["url"])
    print("Splatnet #: {:<}".format(data["splatnet_number"]))
    print(
        "Stage: {:}".format(
            cast(Dict[str, Dict[str, Dict[str, str]]], data)["stage"]["name"][locale]
        )
    )
    print(
        "Rotation Start Date: "
        + cast(Dict[str, Dict[str, str]], data)["shift_start_at"]["iso8601"]
    )
    print("Start Date: " + cast(Dict[str, Dict[str, str]], data)["start_at"]["iso8601"])
    print("Result: {:}".format("Cleared" if data["clear_waves"] == 3 else "Failed"))
    print(
        "Title: {:} {:<3} -> {:} {:<3}".format(
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
            "Event", getWavesAttribute3D(data, "known_occurrence", "name", locale)
        )
    )
    print(
        "{:16}\t{:<}".format(
            "Water Level", getWavesAttribute3D(data, "water_level", "name", locale)
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
                getPlayersAttribute4D(data, "weapons", i, "name", locale),
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
                getPlayersAttribute2D(data, "special_uses", i),
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
            getPlayersAttribute3D(
                data,
                "special",
                "name",
                locale,
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
            results.append(float(job[stat]))
        return results


def getArrayOfStat2D(data: str, firstD: str, secondD: Union[str, int]) -> list:
    """

    :param data: str:
    :param firstD: str:
    :param secondD: Union[str, int]:
    :returns ;ost:

    """
    with gzip.open(data) as reader:
        results = []
        for job in jsonlines.Reader(reader, ujson.loads):
            results.append(float(job[firstD][secondD]))
        return results


def initAll() -> Tuple[str, str]:
    """

    :returns Tuple[str, str]:

    """
    if os.path.exists("data/salmonAll.jl.gz"):
        recentId = 0
        try:
            with gzip.open("data/salmonAll.jl.gz") as reader:
                with gzip.open(
                    "data/salmonAllTemp.jl.gz", "at", encoding="utf8"
                ) as writer:
                    for line in jsonlines.Reader(reader, ujson.loads):
                        ujson.dump(line, writer)
                        writer.write("\n")
                        recentId = line["id"]
                os.remove("data/salmonAllTemp.jl.gz")
        except jsonlines.jsonlines.InvalidLineError:
            os.replace(r"data/salmonAllTemp.jl.gz", r"data/salmonAll.jl.gz")
        fetchNewAll(recentId)
    else:
        fetchAll()
    return ("data/", "salmonAll.jl.gz")


def initUser(api_key: str) -> Tuple[str, str]:
    """

    :param api_key: str:
    :returns Tuple[str, str]:

    """
    if os.path.exists("data/salmon.jl.gz"):
        recentId = 0
        try:
            with gzip.open("data/salmon.jl.gz") as reader:
                with gzip.open(
                    "data/salmonTemp.jl.gz", "at", encoding="utf8"
                ) as writer:
                    for line in jsonlines.Reader(reader, ujson.loads):
                        ujson.dump(line, writer)
                        writer.write("\n")
                        recentId = line["id"]
            os.remove("data/salmonTemp.jl.gz")
        except jsonlines.jsonlines.InvalidLineError:
            os.replace(r"data/salmonTemp.jl.gz", r"data/salmon.jl.gz")
        fetchNewUser(api_key, recentId)
    else:
        fetchAllUser(api_key)
    return ("data/", "salmon.jl.gz")


if __name__ == "__main__":
    user_key: str = ujson.load(open("keys.json", "r"))["statink_key"]
    initAll()
    paths: List[str] = []
    dataFiles: List[str] = []
    dataFile: str = "salmonAll.jl.gz"
    rotations: List[int] = findRotationByWeaponsAndStage(
        "data/" + dataFile,
        ("Grizzco Charger", "Grizzco Brella", "Grizzco Blaster", "Grizzco Slosher"),
        "Ruins of Ark Polaris",
    )
    print(rotations)
    jobs: Tuple[str, str] = duringRotationInt("data/", dataFile, rotations[1])
    paths.append(jobs[0])
    dataFiles.append(jobs[1])
    jobs = dangerRate(jobs[0], jobs[1], "200.0")
    paths.append(jobs[0])
    dataFiles.append(jobs[1])
    printOverview(jobs[0], jobs[1])
    print()
    for a in range(0, len(paths)):
        os.remove(paths[a] + dataFiles[a])
        # with gzip.open(jobs[0] + jobs[1]) as readerFile:
        """for job in jsonlines.Reader(reader, ujson.loads):
        printGeneral(job)
        print()
        printWaves(job)
        print()
        printPlayers(job)
        print()
        printBosses(job)
        print()
        print()"""
