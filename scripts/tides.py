import sys

sys.path.insert(0, ".")
import core
from objects import Job
import jsonlines
import ujson
import gzip
from typing import Dict

if __name__ == "__main__":
    data = "data/salmonAll.jl.gz"  # core.init("All")
    tideDict: Dict[str, dict] = {
        "high": {"key": "high", "count": 0.0},
        "normal": {"key": "normal", "count": 0.0},
        "low": {"key": "low", "count": 0.0},
    }
    total = 0.0
    with gzip.open(data) as reader:
        for line in reader:
            job = Job(**ujson.loads(line))
            for wave in job.waves:
                total += 1.0
                tideDict[wave.water_level.key]["count"] += 1.0
    for tide in tideDict.values():
        print(tide["key"] + ": " + str(tide["count"] / total))
