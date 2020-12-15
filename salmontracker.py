import os.path
import json
import numpy as np
import requests
import jsonlines
import sys
from typing import Tuple, List, Union

locale = "en_US"

grizzcoWeapons = (
    ("Grizzco Charger", "kuma_charger"),
    ("Grizzco Brella", "kuma_brella"),
    ("Grizzco Blaster", "kuma_blaster"),
    ("Grizzco Slosher", "kuma_slosher"),
)


def fetchAllUser(api_key: str) -> None:
    """Fetch all Salmon Run results for the authenticated user and store it in the "data/salmon.jsonl" file.

    :param api_key: str: the stat.ink API key for the user

    """
    headers = {"Authorization": "Bearer {}".format(api_key)}
    lastId = 0
    prevLastId = 0
    params = {"order": "asc"}
    temp = requests.get(
        "http://stat.ink/api/v2/user-salmon", headers=headers, params=params
    ).json()
    lastId = temp[-1]["id"]
    print(lastId)
    with jsonlines.open("data/salmon.jsonl", mode="w") as writer:
        while lastId != prevLastId:
            writer.write_all(temp)
            params["newer_than"] = str(lastId)
            result = requests.get(
                "http://stat.ink/api/v2/user-salmon", headers=headers, params=params
            )
            print(result.url)
            print(result)
            temp = result.json()
            prevLastId = lastId
            if len(temp) > 0:
                lastId = temp[-1]["id"]
            print(lastId)


def fetchAll() -> None:
    """Fetch all Salmon Run results for all users and store it in the "data/salmonAll.jsonl" file."""
    lastId = 0
    prevLastId = 0
    params = {"order": "asc"}
    temp = requests.get("http://stat.ink/api/v2/salmon", params=params).json()
    lastId = temp[-1]["id"]
    print(lastId)
    with jsonlines.open("data/salmonAll.jsonl", mode="w") as writer:
        while lastId != prevLastId:
            writer.write_all(temp)
            print(os.path.getsize("data/salmonAll.jsonl"))
            params["newer_than"] = str(lastId)
            result = requests.get("http://stat.ink/api/v2/salmon", params=params)
            print(result.url)
            print(result)
            temp = result.json()
            prevLastId = lastId
            if len(temp) > 0:
                lastId = temp[-1]["id"]
            print(lastId)


def fetchNewUser(api_key: str, recentId: int) -> None:
    """
    Fetch new Salmon Run results for authenticated user and store it in the "data/salmon.jsonl" file.

    :param api_key: str: the stat.ink API key for the user
    :param recentId: int: the ID of the most recently retrieved job

    """
    headers = {"Authorization": "Bearer {}".format(api_key)}
    lastId = 0
    prevLastId = 0
    params = {"order": "asc"}
    params["newer_than"] = str(recentId)
    temp = requests.get(
        "http://stat.ink/api/v2/user-salmon", headers=headers, params=params
    ).json()
    if len(temp) > 0:
        lastId = temp[-1]["id"]
        print(lastId)
        with jsonlines.open("data/salmon.jsonl", mode="a") as writer:
            while lastId != prevLastId:
                writer.write_all(temp)
                params["newer_than"] = str(lastId)
                result = requests.get(
                    "http://stat.ink/api/v2/user-salmon", headers=headers, params=params
                )
                print(result.url)
                print(result)
                temp = result.json()
                prevLastId = lastId
                if len(temp) > 0:
                    lastId = temp[-1]["id"]
                print(lastId)


def fetchNewAll(recentId: int) -> None:
    """
    Fetch new Salmon Run results for all users and store it in the "data/salmonAll.jsonl" file.

    :param recentId: int: the ID of the most recently retrieved jobs

    """
    lastId = 0
    prevLastId = 0
    params = {"order": "asc"}
    params["newer_than"] = str(recentId)
    temp = requests.get("http://stat.ink/api/v2/salmon", params=params).json()
    if len(temp) > 0:
        lastId = temp[-1]["id"]
        print(lastId)
        with jsonlines.open("data/salmonAll.jsonl", mode="a") as writer:
            while lastId != prevLastId:
                writer.write_all(temp)
                print(os.path.getsize("data/salmonAll.jsonl"))
                params["newer_than"] = str(lastId)
                result = requests.get("http://stat.ink/api/v2/salmon", params=params)
                print(result.url)
                print(result)
                temp = result.json()
                prevLastId = lastId
                if len(temp) > 0:
                    lastId = temp[-1]["id"]
                print(lastId)


def hasJobs(path: str, data: str) -> bool:
    """
    Check if a given data file has data.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file

    """
    with jsonlines.open(path + data, "r") as reader:
        try:
            reader.read()
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
    try:
        os.mkdir(path + data[0:-6] + "/")
    except FileExistsError:
        pass
    try:
        os.mkdir(path + data[0:-6] + "/playerId/")
    except FileExistsError:
        pass
    with jsonlines.open(path + data, "r") as reader:
        if hasJobs(path, data):
            with jsonlines.open(
                path + data[0:-6] + "/playerId/" + player + ".jsonl", "w"
            ) as writer:
                for var in reader:
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
                        writer.write(var)
        return (path + data[0:-6] + "/playerId/", player + ".jsonl")


def withoutPlayer(path: str, data: str, player: str) -> Tuple[str, str]:
    """
    Filter the jobs in the given data file to only jobs that do not contain the chosen player.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param player: str: the Splatnet ID of the chosen player

    """
    try:
        os.mkdir(path + data[0:-6] + "/")
    except FileExistsError:
        pass
    try:
        os.mkdir(path + data[0:-6] + "/notPlayerId/")
    except FileExistsError:
        pass
    with jsonlines.open(path + data, "r") as reader:
        if hasJobs(path, data):
            with jsonlines.open(
                path + data[0:-6] + "/notPlayerId/" + player + ".jsonl", "w"
            ) as writer:
                for var in reader:
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
                        writer.write(var)
        return (path + data[0:-6] + "/notPlayerId/", player + ".jsonl")


def hasPlayerByName(path: str, data: str, player: str) -> Tuple[str, str]:
    """
    Filter the jobs in the given data file to only jobs that contain the chosen player.

    :param path: str: the directory path of the data file
    :param data: str: the file name of the data file
    :param player: str: the name of the chosen player

    """
    try:
        os.mkdir(path + data[0:-6] + "/")
    except FileExistsError:
        pass
    try:
        os.mkdir(path + data[0:-6] + "/player/")
    except FileExistsError:
        pass
    with jsonlines.open(path + data, "r") as reader:
        if hasJobs(path, data):
            with jsonlines.open(
                path + data[0:-6] + "/player/" + player + ".jsonl", "w"
            ) as writer:
                for var in reader:
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
                        writer.write(var)
        return (path + data[0:-6] + "/player/", player + ".jsonl")


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
    foundRotations = []
    with jsonlines.open(data, mode="r") as reader:
        for job in reader:
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


def hasWeapon(path: str, data: str, weapon: str) -> Tuple[str, str]:
    """

    :param path: str:
    :param data: str:
    :param weapon: str:

    """
    try:
        os.mkdir(path + data[0:-6] + "/")
    except FileExistsError:
        pass
    try:
        os.mkdir(path + data[0:-6] + "/weapon/")
    except FileExistsError:
        pass
    with jsonlines.open(path + data, "r") as reader:
        with jsonlines.open(
            path + data[0:-6] + "/weapon/" + weapon + ".jsonl", "w"
        ) as writer:
            for var in reader:
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
                        len(var["teammates"]) > 0
                        and var["teammates"][0]["weapons"] is not None
                        and (
                            var["teammates"][0]["weapons"][0]["key"] == weapon
                            or (
                                len(var["teammates"][0]["weapons"]) > 1
                                and var["teammates"][0]["weapons"][1]["key"] == weapon
                            )
                            or (
                                len(var["teammates"][0]["weapons"]) > 2
                                and var["teammates"][0]["weapons"][2]["key"] == weapon
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
                                and var["teammates"][1]["weapons"][1]["key"] == weapon
                            )
                            or (
                                len(var["teammates"][1]["weapons"]) > 2
                                and var["teammates"][1]["weapons"][2]["key"] == weapon
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
                                and var["teammates"][2]["weapons"][1]["key"] == weapon
                            )
                            or (
                                len(var["teammates"][2]["weapons"]) > 2
                                and var["teammates"][2]["weapons"][2]["key"] == weapon
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
                        len(var["teammates"]) > 0
                        and var["teammates"][0]["weapons"] is not None
                        and (
                            var["teammates"][0]["weapons"][0]["name"][locale] == weapon
                            or (
                                len(var["teammates"][0]["weapons"]) > 1
                                and var["teammates"][0]["weapons"][1]["name"][locale]
                                == weapon
                            )
                            or (
                                len(var["teammates"][0]["weapons"]) > 2
                                and var["teammates"][0]["weapons"][2]["name"][locale]
                                == weapon
                            )
                        )
                    )
                    or (
                        len(var["teammates"]) > 1
                        and var["teammates"][1]["weapons"] is not None
                        and (
                            var["teammates"][1]["weapons"][0]["name"][locale] == weapon
                            or (
                                len(var["teammates"][1]["weapons"]) > 1
                                and var["teammates"][1]["weapons"][1]["name"][locale]
                                == weapon
                            )
                            or (
                                len(var["teammates"][1]["weapons"]) > 2
                                and var["teammates"][1]["weapons"][2]["name"][locale]
                                == weapon
                            )
                        )
                    )
                    or (
                        len(var["teammates"]) > 2
                        and var["teammates"][2]["weapons"] is not None
                        and (
                            var["teammates"][2]["weapons"][0]["name"][locale] == weapon
                            or (
                                len(var["teammates"][2]["weapons"]) > 1
                                and var["teammates"][2]["weapons"][1]["name"][locale]
                                == weapon
                            )
                            or (
                                len(var["teammates"][2]["weapons"]) > 2
                                and var["teammates"][2]["weapons"][2]["name"][locale]
                                == weapon
                            )
                        )
                    )
                ):
                    writer.write(var)
    return (path + data[0:-6] + "/weapon/", weapon + ".jsonl")


def doesntHaveWeapon(path: str, data: str, weapon: str) -> Tuple[str, str]:
    """

    :param path: str:
    :param data: str:
    :param weapon: str:

    """
    try:
        os.mkdir(path + data[0:-6] + "/")
    except FileExistsError:
        pass
    try:
        os.mkdir(path + data[0:-6] + "/notWeapon/")
    except FileExistsError:
        pass
    with jsonlines.open(path + data, "r") as reader:
        with jsonlines.open(
            path + data[0:-6] + "/notWeapon/" + weapon + ".jsonl", "w"
        ) as writer:
            for var in reader:
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
                        len(var["teammates"]) > 0
                        and var["teammates"][0]["weapons"] is not None
                        and (
                            var["teammates"][0]["weapons"][0]["key"] == weapon
                            or (
                                len(var["teammates"][0]["weapons"]) > 1
                                and var["teammates"][0]["weapons"][1]["key"] == weapon
                            )
                            or (
                                len(var["teammates"][0]["weapons"]) > 2
                                and var["teammates"][0]["weapons"][2]["key"] == weapon
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
                                and var["teammates"][1]["weapons"][1]["key"] == weapon
                            )
                            or (
                                len(var["teammates"][1]["weapons"]) > 2
                                and var["teammates"][1]["weapons"][2]["key"] == weapon
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
                                and var["teammates"][2]["weapons"][1]["key"] == weapon
                            )
                            or (
                                len(var["teammates"][2]["weapons"]) > 2
                                and var["teammates"][2]["weapons"][2]["key"] == weapon
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
                        len(var["teammates"]) > 0
                        and var["teammates"][0]["weapons"] is not None
                        and (
                            var["teammates"][0]["weapons"][0]["name"][locale] == weapon
                            or (
                                len(var["teammates"][0]["weapons"]) > 1
                                and var["teammates"][0]["weapons"][1]["name"][locale]
                                == weapon
                            )
                            or (
                                len(var["teammates"][0]["weapons"]) > 2
                                and var["teammates"][0]["weapons"][2]["name"][locale]
                                == weapon
                            )
                        )
                    )
                    or (
                        len(var["teammates"]) > 1
                        and var["teammates"][1]["weapons"] is not None
                        and (
                            var["teammates"][1]["weapons"][0]["name"][locale] == weapon
                            or (
                                len(var["teammates"][1]["weapons"]) > 1
                                and var["teammates"][1]["weapons"][1]["name"][locale]
                                == weapon
                            )
                            or (
                                len(var["teammates"][1]["weapons"]) > 2
                                and var["teammates"][1]["weapons"][2]["name"][locale]
                                == weapon
                            )
                        )
                    )
                    or (
                        len(var["teammates"]) > 2
                        and var["teammates"][2]["weapons"] is not None
                        and (
                            var["teammates"][2]["weapons"][0]["name"][locale] == weapon
                            or (
                                len(var["teammates"][2]["weapons"]) > 1
                                and var["teammates"][2]["weapons"][1]["name"][locale]
                                == weapon
                            )
                            or (
                                len(var["teammates"][2]["weapons"]) > 2
                                and var["teammates"][2]["weapons"][2]["name"][locale]
                                == weapon
                            )
                        )
                    )
                ):
                    writer.write(var)
    return (path + data[0:-6] + "/notWeapon/", weapon + ".jsonl")


def usesWeapon(weapon: str) -> bool:
    """

    :param weapon: str:

    """
    return lambda var: (
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


def doesntUseWeapon(weapon: str) -> bool:
    """

    :param weapon: str:

    """
    return lambda var: not (
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


def findPlayerIdByName(path: str, data: str, player: str) -> List[str]:
    """

    :param path: str:
    :param data: str:
    :param player: str:

    """
    foundIds: List[str] = []
    matches = hasPlayerByName(path, data, player)
    with jsonlines.open(matches[0] + matches[1], "r") as reader:
        for job in reader:
            for teammate in job["teammates"]:
                if (
                    teammate["name"] == player
                    and teammate["splatnet_id"] not in foundIds
                ):
                    foundIds.append(teammate["splatnet_id"])
        return foundIds


def onStage(path: str, data: str, stage: str) -> Tuple[str, str]:
    """

    :param path: str:
    :param data: str:
    :param stage: str:

    """
    try:
        os.mkdir(path + data[0:-6] + "/")
    except FileExistsError:
        pass
    try:
        os.mkdir(path + data[0:-6] + "/stage/")
    except FileExistsError:
        pass
    with jsonlines.open(path + data, "r") as reader:
        with jsonlines.open(
            path + data[0:-6] + "/stage/" + stage + ".jsonl", "w"
        ) as writer:
            for var in reader:
                if stage in (var["stage"]["key"], var["stage"]["name"][locale]):
                    writer.write(var)
    return (path + data[0:-6] + "/stage/", stage + ".jsonl")


def notOnStage(path: str, data: str, stage: str) -> Tuple[str, str]:
    """

    :param path: str:
    :param data: str:
    :param stage: str:

    """
    try:
        os.mkdir(path + data[0:-6] + "/")
    except FileExistsError:
        pass
    try:
        os.mkdir(path + data[0:-6] + "/notStage/")
    except FileExistsError:
        pass
    with jsonlines.open(path + data, "r") as reader:
        with jsonlines.open(
            path + data[0:-6] + "/notStage/" + stage + ".jsonl", "w"
        ) as writer:
            for var in reader:
                if not (stage in (var["stage"]["key"], var["stage"]["name"][locale])):
                    writer.write(var)
    return (path + data[0:-6] + "/notStage/", stage + ".jsonl")


def withSpecial(path: str, data: str, special: str) -> Tuple[str, str]:
    """

    :param path: str:
    :param data: str:
    :param special: str:

    """
    try:
        os.mkdir(path + data[0:-6] + "/")
    except FileExistsError:
        pass
    try:
        os.mkdir(path + data[0:-6] + "/special/")
    except FileExistsError:
        pass
    with jsonlines.open(path + data, "r") as reader:
        with jsonlines.open(
            path + data[0:-6] + "/special/" + special + ".jsonl", "w"
        ) as writer:
            for var in reader:
                if special in (
                    var["my_data"]["special"]["key"],
                    var["my_data"]["special"]["name"][locale],
                ):
                    writer.write(var)
    return (path + data[0:-6] + "/special/", special + ".jsonl")


def withoutSpecial(path: str, data: str, special: str) -> Tuple[str, str]:
    """

    :param path: str:
    :param data: str:
    :param special: str:

    """
    try:
        os.mkdir(path + data[0:-6] + "/")
    except FileExistsError:
        pass
    try:
        os.mkdir(path + data[0:-6] + "/notSpecial/")
    except FileExistsError:
        pass
    with jsonlines.open(path + data, "r") as reader:
        with jsonlines.open(
            path + data[0:-6] + "/notSpecial/" + special + ".jsonl", "w"
        ) as writer:
            for var in reader:
                if not (
                    special
                    in (
                        var["my_data"]["special"]["key"],
                        var["my_data"]["special"]["name"][locale],
                    )
                ):
                    writer.write(var)
    return (path + data[0:-6] + "/notSpecial/", special + ".jsonl")


def failReason(reason: str) -> bool:
    """

    :param reason: str:

    """
    return lambda var: var["fail_reason"] == reason


def notFailReason(reason: str) -> bool:
    """

    :param reason: str:

    """
    return lambda var: not (var["fail_reason"] == reason)


def duringRotationInt(path: str, data: str, rotation: int) -> Tuple[str, str]:
    """

    :param path: str:
    :param data: str:
    :param rotation: int:

    """
    try:
        os.mkdir(path + data[0:-6])
    except FileExistsError:
        pass
    try:
        os.mkdir(path + data[0:-6] + "/rotation/")
    except FileExistsError:
        pass
    with jsonlines.open(path + data, mode="r") as reader:
        with jsonlines.open(
            path + data[0:-6] + "/rotation/" + str(rotation) + ".jsonl", "w"
        ) as writer:
            for job in reader:
                if job["shift_start_at"]["time"] == rotation:
                    writer.write(job)
    return (path + data[0:-6] + "/rotation/", str(rotation) + ".jsonl")


def duringRotationStr(rotation: str) -> bool:
    """

    :param rotation: str:

    """
    return lambda var: var["shift_start_at"]["iso8601"] == rotation


def notDuringRotationInt(path: str, data: str, rotation: int) -> Tuple[str, str]:
    """

    :param path: str:
    :param data: str:
    :param rotation: int:

    """
    try:
        os.mkdir(path + data[0:-6])
    except FileExistsError:
        pass
    try:
        os.mkdir(path + data[0:-6] + "/notRotations/")
    except FileExistsError:
        pass
    with jsonlines.open(path + data, mode="r") as reader:
        with jsonlines.open(
            path + data[0:-6] + "/notRotations/" + str(rotation) + ".jsonl", "w"
        ) as writer:
            for job in reader:
                if not job["shift_start_at"]["time"] == rotation:
                    writer.write(job)
    return (path + data[0:-6] + "/notRotations/", str(rotation) + ".jsonl")


def notDuringRotationStr(rotation: str) -> bool:
    """

    :param rotation: str:

    """
    return lambda var: not (var["shift_start_at"]["iso8601"] == rotation)


def clearWave(wave: int) -> bool:
    """

    :param wave: int:

    """
    return lambda var: var["clear_waves"] == wave


def notClearWave(wave: int) -> bool:
    """

    :param wave: int:

    """
    return lambda var: not (var["clear_waves"] == wave)


def greaterThanClearWave(wave: int) -> bool:
    """

    :param wave: int:

    """
    return lambda var: var["clear_waves"] > wave


def notGreaterThanClearWave(wave: int) -> bool:
    """

    :param wave: int:

    """
    return lambda var: not (var["clear_waves"] > wave)


def lessThanClearWave(wave: int) -> bool:
    """

    :param wave: int:

    """
    return lambda var: var["clear_waves"] < wave


def notLessThanClearWave(wave: int) -> bool:
    """

    :param wave: int:

    """
    return lambda var: not (var["clear_waves"] < wave)


def dangerRate(path: str, data: str, rate: str) -> Tuple[str, str]:
    """

    :param path: str:
    :param data: str:
    :param rate: str:

    """
    if not os.path.exists(path + data[0:-6]):
        os.mkdir(path + data[0:-6])
    if not os.path.exists(path + data[0:-6] + "/dangerRate/"):
        os.mkdir(path + data[0:-6] + "/dangerRate/")
    with jsonlines.open(path + data, mode="r") as reader:
        with jsonlines.open(
            path + data[0:-6] + "/dangerRate/" + rate + ".jsonl", "w"
        ) as writer:
            for job in reader:
                if job["danger_rate"] == rate:
                    writer.write(job)
    return path + data[0:-6] + "/dangerRate/", rate + ".jsonl"


def notDangerRate(rate: int) -> bool:
    """

    :param rate: int:

    """
    return lambda var: not (var["danger_rate"] == rate)


def greaterThanDangerRate(rate: int) -> bool:
    """

    :param rate: int:

    """
    return lambda var: var["danger_rate"] > rate


def notGreaterThanDangerRate(rate: int) -> bool:
    """

    :param rate: int:

    """
    return lambda var: not (var["danger_rate"] > rate)


def lessThanDangerRate(rate: int) -> bool:
    """

    :param rate: int:

    """
    return lambda var: var["danger_rate"] < rate


def notLessThandDangerRate(rate: int) -> bool:
    """

    :param rate: int:

    """
    return lambda var: not (var["danger_rate"] < rate)


def splatnet_number(num: int) -> bool:
    """

    :param num: int:

    """
    return lambda var: var["splatnet_number"] == num


def jobsCount(data: str) -> int:
    """

    :param data: str:

    """
    with jsonlines.open(data, mode="r") as reader:
        count = 0
        for _unused in reader:
            count += 1
        return count


def avgStat(data: str, stat: str) -> float:
    """

    :param data: str:
    :param stat: str:

    """
    with jsonlines.open(data, mode="r") as reader:
        sumVal = 0.0
        count = 0.0
        for job in reader:
            sumVal += float(job[stat])
            count += 1.0
        return sumVal / count


def avgStat2D(data: str, firstD: str, secondD: str) -> float:
    """

    :param data: str:
    :param firstD: str:
    :param secondD: str:

    """
    with jsonlines.open(data, mode="r") as reader:
        sumVal = 0.0
        count = 0.0
        for job in reader:
            sumVal += float(job[firstD][secondD])
            count += 1.0
        return sumVal / count


def maxStat(data: str, stat: str) -> float:
    """

    :param data: str:
    :param stat: str:

    """
    maxVal = 0.0
    with jsonlines.open(data, "r") as reader:
        for job in reader:
            if maxVal < float(job[stat]):
                maxVal = float(job[stat])
    return maxVal


def maxStat2D(data: str, firstD: str, secondD: str) -> float:
    """

    :param data: str:
    :param firstD: str:
    :param secondD: str:

    """
    maxVal = 0.0
    with jsonlines.open(data, "r") as reader:
        for job in reader:
            if maxVal < float(job[firstD][secondD]):
                maxVal = float(job[firstD][secondD])
    return maxVal


def minStat(data: str, stat: str) -> float:
    """

    :param data: str:
    :param stat: str:

    """
    with jsonlines.open(data, "r") as reader:
        minVal: float = sys.float_info.max
        for job in reader:
            if minVal > float(job[stat]):
                minVal = float(job[stat])
    return minVal


def minStat2D(data: str, firstD: str, secondD: str) -> float:
    """

    :param data: str:
    :param firstD: str:
    :param secondD: str:

    """
    with jsonlines.open(data, "r") as reader:
        minVal: float = sys.float_info.max
        for job in reader:
            if minVal > float(job[firstD][secondD]):
                minVal = float(job[firstD][secondD])
    return minVal


def medianStat(data: str, stat: str) -> float:
    """

    :param data: str:
    :param stat: str:

    """
    vals = []
    with jsonlines.open(data, "r") as reader:
        for job in reader:
            vals.append(float(job[stat]))
    return np.median(vals)


def medianStat2D(data: str, firstD: str, secondD: str) -> float:
    """

    :param data: str:
    :param firstD: str:
    :param secondD: str:

    """
    vals = []
    with jsonlines.open(data, "r") as reader:
        for job in reader:
            vals.append(job[firstD][secondD])
    return np.median(vals)


def clearPercentage(data: str) -> float:
    """

    :param data: str:

    """
    with jsonlines.open(data, mode="r") as reader:
        sumVal = 0.0
        count = 0.0
        for job in reader:
            sumVal += int(job["clear_waves"] == 3)
            count += 1.0
        return sumVal / count


def waveTwoPercentage(data: str) -> float:
    """

    :param data: str:

    """
    with jsonlines.open(data, mode="r") as reader:
        sumVal = 0.0
        count = 0.0
        for job in reader:
            sumVal += int(job["clear_waves"] >= 2)
            count += 1.0
        return sumVal / count


def waveOnePercentage(data: str) -> float:
    """

    :param data: str:

    """
    with jsonlines.open(data, mode="r") as reader:
        sumVal = 0.0
        count = 0.0
        for job in reader:
            sumVal += int(job["clear_waves"] >= 1)
            count += 1.0
        return sumVal / count


def statSummary(data: str, stat: str) -> str:
    """

    :param data: str:
    :param stat: str:

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


def sumStatWaves(data: dict, stat: str) -> int:
    """

    :param data: dict:
    :param stat: str:

    """
    sumVal = 0
    for w in data["waves"]:
        sumVal += w[stat]
    return sumVal


def getPlayersAttribute(data: dict, attr: str) -> str:
    """

    :param data: dict:
    :param attr: str:

    """
    attrs = "{:<16}\t".format(data["my_data"][attr] or 0)
    for p in data["teammates"]:
        attrs += "{:<16}\t".format(p[attr] or 0)
    return attrs


def getPlayersAttribute2D(data: dict, firstD: str, secondD: Union[int, str]) -> str:
    """
    s
        :param data: dict:
        :param firstD: str:
        :param secondD: Union[int, str]:

    """
    attrs = "{:<16}\t".format(data["my_data"][firstD][secondD] or 0)
    for p in data["teammates"]:
        attrs += "{:<16}\t".format(p[firstD][secondD] or 0)
    return attrs


def getPlayersAttribute3D(data: dict, firstD: str, secondD: str, thirdD: str) -> str:
    """

    :param data: dict:
    :param firstD: str:
    :param secondD: str:
    :param thirdD: str:

    """
    attrs = "{:<16}\t".format(data["my_data"][firstD][secondD][thirdD] or 0)
    for p in data["teammates"]:
        attrs += "{:<16}\t".format(p[firstD][secondD][thirdD] or 0)
    return attrs


def getPlayersAttribute4D(
    data: dict, firstD: str, secondD: int, thirdD: str, fourthD: str
) -> str:
    """

    :param data: dict:
    :param firstD: str:
    :param secondD: int:
    :param thirdD: str:
    :param fourthD: str:

    """
    attrs = "{:<16}\t".format(data["my_data"][firstD][secondD][thirdD][fourthD] or 0)
    for p in data["teammates"]:
        if secondD < len(p[firstD]):
            attrs += "{:<16}\t".format(p[firstD][secondD][thirdD][fourthD] or 0)
        else:
            attrs += "{:<16}\t".format("")
    return attrs


def getWavesAttribute(data: dict, attr: str) -> str:
    """

    :param data: dict:
    :param attr: str:

    """
    attrs = ""
    for i in range(0, 3):
        if i < len(data["waves"]):
            attrs += "{:<16}\t".format(data["waves"][i][attr])
        else:
            attrs += "{:<16}\t".format("")
    return attrs


def getWavesAttribute3D(data: dict, firstD: str, secondD: str, thirdD: str) -> str:
    """

    :param data: dict:
    :param firstD: str:
    :param secondD: str:
    :param thirdD: str:

    """
    attrs = ""
    for i in range(0, 3):
        if i < len(data["waves"]) and data["waves"][i][firstD]:
            attrs += "{:<16}\t".format(data["waves"][i][firstD][secondD][thirdD])
        else:
            attrs += "{:<16}\t".format("")
    return attrs


def getBossDataStr(data: dict, boss: str) -> str:
    """

    :param data: dict:
    :param boss: str:

    """
    return "{:<16}\t{:}".format(
        data[boss + "_appearances"] or 0,
        getPlayersAttribute2D(data, "kills", boss + "_"),
    )


def getTotalBosses(data: list, bosses: list, player: str) -> int:
    """

    :param data: list:
    :param bosses: list:
    :param player: str:

    """
    return sum(
        int(data[boss.replace(" ", "_").lower() + "_" + player] or 0) for boss in bosses
    )


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


def printGeneral(data: dict) -> None:
    """

    :param data: dict:

    """
    print("Stat.ink Link: " + data["url"])
    print("Splatnet #: {:<}".format(data["splatnet_number"]))
    print("Stage: {:}".format(data["stage"]["name"][locale]))
    print("Rotation Start Date: " + str(data["shift_start_at"]["iso8601"]))
    print("Start Date: " + data["start_at"]["iso8601"])
    print("Result: {:}".format("Cleared" if data["clear_waves"] == 3 else "Failed"))
    print(
        "Title: {:} {:<3} -> {:} {:<3}".format(
            data["title"]["name"][locale] if data["title"] else "",
            data["title_exp"],
            data["title_after"]["name"][locale] if data["title_after"] else "",
            data["title_exp_after"],
        )
    )


def printWaves(data: dict) -> None:
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


def printWeapons(data: dict) -> None:
    """

    :param data: dict:

    """
    for i in range(0, len(data["my_data"]["weapons"])):
        print(
            "{:16}\t{:}".format(
                "Wave {:1} Weapon".format(i + 1),
                getPlayersAttribute4D(data, "weapons", i, "name", locale),
            )
        )


def printSpecials(data: dict) -> None:
    """

    :param data: dict:

    """
    for i in range(0, len(data["my_data"]["special_uses"])):
        print(
            "{:16}\t{:}".format(
                "Wave {:1} Special Use".format(i + 1),
                getPlayersAttribute2D(data, "special_uses", i),
            )
        )


def printPlayers(data: dict) -> None:
    """

    :param data: dict:

    """
    print("{:16}\t{:}".format("ID", getPlayersAttribute(data, "splatnet_id")))
    print("{:16}\t{:}".format("Name", getPlayersAttribute(data, "name")))
    printWeapons(data)
    print(
        "{:16}\t{:}".format(
            "Special", getPlayersAttribute3D(data, "special", "name", locale)
        )
    )
    printSpecials(data)
    print("{:16}\t{:}".format("Rescues", getPlayersAttribute(data, "rescue")))
    print("{:16}\t{:}".format("Deaths", getPlayersAttribute(data, "death")))
    print(
        "{:16}\t{:}".format(
            "Golden Eggs", getPlayersAttribute(data, "golden_egg_delivered")
        )
    )
    print(
        "{:16}\t{:}".format(
            "Power Eggs", getPlayersAttribute(data, "power_egg_collected")
        )
    )


def getBosses(data: dict) -> list:
    """

    :param data: dict:

    """
    results = []
    names = {}
    appearances = {"": 0}
    for boss in range(0, len(data["boss_appearances"])):
        names[data["boss_appearances"][boss]["boss"]["name"][locale]] = data[
            "boss_appearances"
        ][boss]["boss"]["name"][locale]
        appearances[data["boss_appearances"][boss]["boss"]["name"][locale]] = data[
            "boss_appearances"
        ][boss]["count"]
    results.append(names)
    results.append(appearances)
    my_data = {"": 0}
    if data["my_data"]["boss_kills"] is not None:
        for boss in range(0, len(data["my_data"]["boss_kills"])):
            my_data[data["my_data"]["boss_kills"][boss]["boss"]["name"][locale]] = data[
                "my_data"
            ]["boss_kills"][boss]["count"]
    results.append(my_data)
    for teammate in range(0, len(data["teammates"])):
        teammate_data = {"": 0}
        if data["teammates"][teammate]["boss_kills"] is not None:
            for boss in range(0, len(data["teammates"][teammate]["boss_kills"])):
                my_data[
                    data["teammates"][teammate]["boss_kills"][boss]["boss"]["name"][
                        locale
                    ]
                ] = data["teammates"][teammate]["boss_kills"][boss]["count"]
        results.append(teammate_data)
    return results


def printBosses(data: dict) -> None:
    """

    :param data: dict:

    """
    print(
        "{:16}\t{:16}\t{:}".format(
            "Boss Salmonid", "Appearances", getPlayersAttribute(data, "name")
        )
    )
    bosses = getBosses(data)
    listBosses = list(bosses[0])
    for boss in range(0, len(bosses[0])):
        print(
            "{:16}\t{:<16}\t{:<16}\t{:<16}\t{:<16}\t{:<16}".format(
                bosses[0][listBosses[boss]],
                bosses[1][listBosses[boss] if listBosses[boss] in bosses[1] else ""],
                bosses[2][listBosses[boss] if listBosses[boss] in bosses[2] else ""],
                bosses[3][listBosses[boss] if listBosses[boss] in bosses[3] else ""],
                bosses[4][listBosses[boss] if listBosses[boss] in bosses[4] else ""],
                bosses[5][listBosses[boss] if listBosses[boss] in bosses[5] else ""],
            )
        )
    getBosses(data)


def getArrayOfStat(data: str, stat: str) -> list:
    """

    :param data: str:
    :param stat: str:

    """
    with jsonlines.open(data, "r") as reader:
        results = []
        for job in reader:
            results.append(float(job[stat]))
        return results


def getArrayOfStat2D(data: str, firstD: str, secondD: Union[str, int]) -> list:
    """

    :param data: str:
    :param firstD: str:
    :param secondD: Union[str, int]:

    """
    with jsonlines.open(data, "r") as reader:
        results = []
        for job in reader:
            results.append(float(job[firstD][secondD]))
        return results


def initAll() -> None:
    """ """
    if os.path.exists("data/salmonAll.jsonl"):
        recentId = 0
        try:
            with jsonlines.open("data/salmonAll.jsonl", mode="r") as reader:
                with jsonlines.open("data/salmonAllTemp.jsonl", mode="w") as writer:
                    for line in reader:
                        writer.write(line)
                        recentId = line["id"]
                os.remove("data/salmonAllTemp.jsonl")
        except jsonlines.jsonlines.InvalidLineError:
            os.replace(r"data/salmonAllTemp.jsonl", r"data/salmonAll.jsonl")
        fetchNewAll(recentId)
    else:
        fetchAll()


def initUser(api_key: str) -> None:
    """

    :param api_key: str:

    """
    if os.path.exists("data/salmon.jsonl"):
        recentId = 0
        with jsonlines.open("data/salmon.jsonl", mode="r") as reader:
            for line in reader:
                recentId = line["id"]
        fetchNewUser(api_key, recentId)
    else:
        fetchAllUser(api_key)


if __name__ == "__main__":
    user_key: str = json.load(open("keys.json", "r"))["statink_key"]
    initAll()
    dataFile: str = "salmonAll.jsonl"
    rotations: List[int] = findRotationByWeaponsAndStage(
        "data/" + dataFile,
        ("Grizzco Charger", "Grizzco Brella", "Grizzco Blaster", "Grizzco Slosher"),
        "Ruins of Ark Polaris",
    )
    print(rotations)
    jobs = duringRotationInt("data/", dataFile, rotations[1])
    jobs = dangerRate(jobs[0], jobs[1], "200.0")
    printOverview(jobs[0], jobs[1])
    print()
    with jsonlines.open(jobs[0] + jobs[1], "r") as readerFile:
        """for job in reader:
        printGeneral(job)
        print()
        printWaves(job)
        print()
        printPlayers(job)
        print()
        printBosses(job)
        print()
        print()"""
