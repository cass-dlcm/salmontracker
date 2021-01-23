import core
from objects import Job
import ujson
import gzip
from typing import Dict, List, Union, cast

data = core.init("All", "data/")
tideList: List[str] = ["high", "normal", "low"]
eventList: List[str] = [
    "None",
    "mothership",
    "fog",
    "rush",
    "cohock_charge",
    "griller",
    "goldie_seeking",
]
tideDict: Dict[str, Dict[str, Dict[str, Union[str, float]]]] = {}
for tideStr in tideList:
    eventDict: Dict[str, Dict[str, Union[str, float]]] = {}
    for eventStr in eventList:
        eventDict[eventStr] = {"key": eventStr, "count": 0.0, "clear_count": 0.0}
    tideDict[tideStr] = eventDict
total = 0.0
with gzip.open(data) as reader:
    for line in reader:
        job = Job(**ujson.loads(line))
        waveCount: int = 0
        for wave in job.waves:
            total += 1.0
            if wave.known_occurrence is not None:
                cast(
                    Dict[str, float],
                    tideDict[wave.water_level.key][wave.known_occurrence.key],
                )["count"] += 1.0
                if job.clear_waves > waveCount:
                    cast(
                        Dict[str, float],
                        tideDict[wave.water_level.key][wave.known_occurrence.key],
                    )["clear_count"] += 1.0
            else:
                cast(Dict[str, float], tideDict[wave.water_level.key]["None"])[
                    "count"
                ] += 1.0
                if job.clear_waves > waveCount:
                    cast(
                        Dict[str, float],
                        tideDict[wave.water_level.key]["None"],
                    )["clear_count"] += 1.0
            waveCount += 1
for tide in tideDict.values():
    for event in tide.values():
        print(
            cast(str, event["key"])
            + ": "
            + str(100.0 * cast(float, event["count"]) / total)
            + "% occurance; "
            + str(
                100.0
                * cast(float, event["clear_count"])
                / (
                    cast(float, event["count"])
                    if cast(float, event["count"]) > 0.0
                    else 1.0
                )
            )
            + " % wave cleared"
        )
