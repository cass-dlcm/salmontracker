import sys
sys.path.insert(0,'.')
import core
from core import getValMultiDimensional
import gzip
import jsonlines
import os
import ujson
import sys
import numpy as np
from typing import List, Dict, Union, cast

"""
Get the overviews for the top 100 most prolific players and write it to reports/players.txt.

"""

if __name__ == "__main__":
    startFile: str = core.init("All")
    usersDetails = {}
    stats: list = [
        ["clear_waves"],
        ["my_data", "golden_egg_delivered"],
        ["my_data", "power_egg_collected"],
        ["my_data", "rescue"],
        ["my_data", "death"],
        ["danger_rate"],
    ]
    with gzip.open(startFile) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            userId = job["my_data"]["splatnet_id"]
            if userId not in usersDetails:
                usersDetails[userId] = {
                    "id": userId,
                    "count": 0.0,
                    "clear_count": 0.0,
                    "w2_count": 0.0,
                    "w1_count": 0.0,
                    "clear_waves": {
                        "sum": 0.0,
                        "max": 0.0,
                        "min": sys.float_info.max,
                        "vals": []
                    },
                    "golden_egg_delivered": {
                        "sum": 0.0,
                        "max": 0.0,
                        "min": sys.float_info.max,
                        "vals": []
                    },
                    "power_egg_collected": {
                        "sum": 0.0,
                        "max": 0.0,
                        "min": sys.float_info.max,
                        "vals": []
                    },
                    "rescue": {
                        "sum": 0.0,
                        "max": 0.0,
                        "min": sys.float_info.max,
                        "vals": []
                    },
                    "death": {
                        "sum": 0.0,
                        "max": 0.0,
                        "min": sys.float_info.max,
                        "vals": []
                    },
                    "danger_rate": {
                        "sum": 0.0,
                        "max": 0.0,
                        "min": sys.float_info.max,
                        "vals": []
                    }
                }
            usersDetails[userId]["count"] += 1
            usersDetails[userId]["clear_count"] += float(job["clear_waves"] == 3)
            usersDetails[userId]["w2_count"] += float(job["clear_waves"] >= 2)
            usersDetails[userId]["w1_count"] += float(job["clear_waves"] >= 1)
            for i in range(0, len(stats)):
                usersDetails[userId][stats[i][-1]]["sum"] += float(getValMultiDimensional(job, stats[i]))
                usersDetails[userId][stats[i][-1]]["max"] = (
                    float(getValMultiDimensional(job, stats[i]))
                    if float(getValMultiDimensional(job, stats[i])) > usersDetails[userId][stats[i][-1]]["max"]
                    else usersDetails[userId][stats[i][-1]]["max"]
                )
                usersDetails[userId][stats[i][-1]]["min"] = (
                    float(getValMultiDimensional(job, stats[i]))
                    if float(getValMultiDimensional(job, stats[i])) < usersDetails[userId][stats[i][-1]]["min"]
                    else usersDetails[userId][stats[i][-1]]["min"]
                )
                usersDetails[userId][stats[i][-1]]["vals"].append(float(getValMultiDimensional(job, stats[i])))

    usersDetailsList = sorted(usersDetails.values(),
        key=lambda val: val["count"],
        reverse=True,
    )
    try:
        os.mkdir("reports")
    except FileExistsError:
        pass
    with open("reports/players.txt", "w") as writer:
        for i in range(0, 100):
            user = usersDetailsList[i]
            result = user["id"] + "\n"
            result += "Jobs: " + str(user["count"]) + "\n"
            result += "Average Waves: " + str(user["clear_waves"]["sum"] / user["count"]) + "\n"
            result += "Clear %: " + str(user["clear_count"] / user["count"]) + "\n"
            result += "Wave 2 %: " + str(user["w2_count"] / user["count"]) + "\n"
            result += "Wave 1 %: " + str(user["w1_count"] / user["count"]) + "\n"
            result += "Golden: {} ({}, {}, {})\n".format(
                user["golden_egg_delivered"]["sum"] / user["count"], user["golden_egg_delivered"]["min"], np.median(user["golden_egg_delivered"]["vals"]), user["golden_egg_delivered"]["max"]
            )
            result += "Power Eggs: {} ({}, {}, {})\n".format(
                user["power_egg_collected"]["sum"] / user["count"], user["power_egg_collected"]["min"], np.median(user["power_egg_collected"]["vals"]), user["power_egg_collected"]["max"]
            )
            result += "Rescued: {} ({}, {}, {})\n".format(
                user["rescue"]["sum"] / user["count"], user["rescue"]["min"], np.median(user["rescue"]["vals"]), user["rescue"]["max"]
            )
            result += "Deaths: {} ({}, {}, {})\n".format(
                user["death"]["sum"] / user["count"], user["death"]["min"], np.median(user["death"]["vals"]), user["death"]["max"]
            )
            result += "Hazard Level: {} ({}, {}, {})\n".format(
                user["danger_rate"]["sum"] / user["count"], user["danger_rate"]["min"], np.median(user["danger_rate"]["vals"]), user["danger_rate"]["max"]
            )
            writer.write(result + "\n")
