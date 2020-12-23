import sys

sys.path.insert(0, ".")
import core
import jsonlines
import ujson
import gzip
from typing import Dict

if __name__ == "__main__":
    data = core.init("All")
    tideDict: Dict[str, dict] = {
        "high": {
            "None": {"key": "none", "count": 0.0, "clear_count": 0.0},
            "mothership": {"key": "mothership", "count": 0.0, "clear_count": 0.0},
            "fog": {"key": "fog", "count": 0.0, "clear_count": 0.0},
            "rush": {"key": "rush", "count": 0.0, "clear_count": 0.0},
            "cohock_charge": {"key": "cohock_charge", "count": 0.0, "clear_count": 0.0},
            "griller": {"key": "griller", "count": 0.0, "clear_count": 0.0},
            "goldie_seeking": {
                "key": "goldie_seeking",
                "count": 0.0,
                "clear_count": 0.0,
            },
        },
        "normal": {
            "None": {"key": "none", "count": 0.0, "clear_count": 0.0},
            "mothership": {"key": "mothership", "count": 0.0, "clear_count": 0.0},
            "fog": {"key": "fog", "count": 0.0, "clear_count": 0.0},
            "rush": {"key": "rush", "count": 0.0, "clear_count": 0.0},
            "cohock_charge": {"key": "cohock_charge", "count": 0.0, "clear_count": 0.0},
            "griller": {"key": "griller", "count": 0.0, "clear_count": 0.0},
            "goldie_seeking": {
                "key": "goldie_seeking",
                "count": 0.0,
                "clear_count": 0.0,
            },
        },
        "low": {
            "None": {"key": "none", "count": 0.0, "clear_count": 0.0},
            "mothership": {"key": "mothership", "count": 0.0, "clear_count": 0.0},
            "fog": {"key": "fog", "count": 0.0, "clear_count": 0.0},
            "rush": {"key": "rush", "count": 0.0, "clear_count": 0.0},
            "cohock_charge": {"key": "cohock_charge", "count": 0.0, "clear_count": 0.0},
            "griller": {"key": "griller", "count": 0.0, "clear_count": 0.0},
            "goldie_seeking": {
                "key": "goldie_seeking",
                "count": 0.0,
                "clear_count": 0.0,
            },
        },
    }
    total = 0.0
    with gzip.open(data) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            waveCount = 0
            for wave in job["waves"]:
                total += 1.0
                if wave["known_occurrence"] is not None:
                    tideDict[wave["water_level"]["key"]][
                        wave["known_occurrence"]["key"]
                    ]["count"] += 1.0
                    if job["clear_waves"] > waveCount:
                        tideDict[wave["water_level"]["key"]][
                            wave["known_occurrence"]["key"]
                        ]["clear_count"] += 1.0
                else:
                    tideDict[wave["water_level"]["key"]]["None"]["count"] += 1.0
                    if job["clear_waves"] > waveCount:
                        tideDict[wave["water_level"]["key"]]["None"][
                            "clear_count"
                        ] += 1.0
                waveCount += 1
    for tide in tideDict.values():
        for event in tide.values():
            print(
                event["key"]
                + ": "
                + str(100.0 * event["count"] / total)
                + "%% occurance; "
                + str(
                    100.0
                    * event["clear_count"]
                    / (event["count"] if event["count"] > 0.0 else 1.0)
                )
                + " %% wave cleared"
            )
