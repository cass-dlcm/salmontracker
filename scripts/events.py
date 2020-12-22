import sys

sys.path.insert(0, ".")
import core
import jsonlines
import ujson
import gzip
from typing import Dict

if __name__ == "__main__":
    data = "data/salmonAll.jl.gz"   # core.init("All")
    eventDict: Dict[str, dict] = {
        "None": {"key": "none", "count": 0.0},
        "mothership": {"key": "mothership", "count": 0.0},
        "fog": {"key": "fog", "count": 0.0},
        "rush": {"key": "rush", "count": 0.0},
        "cohock_charge": {"key": "cohock_charge", "count": 0.0},
        "griller": {"key": "griller", "count": 0.0},
        "goldie_seeking": {"key": "goldie_seeking", "count": 0.0},
    }
    total = 0.0
    with gzip.open(data) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            for wave in job["waves"]:
                total += 1.0
                if wave["known_occurrence"] is not None:
                    eventDict[wave["known_occurrence"]["key"]]["count"] += 1.0
                else:
                    eventDict["None"]["count"] += 1.0
    for event in eventDict.values():
        print(event["key"] + ": " + str(event["count"] / total))
