import sys

sys.path.insert(0, ".")
from objects import Job
import numpy as np
import core
from typing import List, Union, Tuple, Dict, cast
import ujson
import gzip
import jsonlines

# to solve the question, "is matchmaking based on rank?"
if __name__ == "__main__":
    dataFile: str = "data/salmonAll.jl.gz"  # core.init("All")
    playersData: Dict[str, dict] = {}
    dangerRates: List[float] = []
    with gzip.open(dataFile) as reader:
        for line in reader:
            job = Job(**ujson.loads(line))
            userId = job.my_data.splatnet_id
            dangerRates.append(float(job.danger_rate))
            if userId not in playersData:
                playersData[userId] = {
                    "id": userId,
                    "hazard_level": {"vals": []},
                    "std": 0.0,
                    "count": 0.0,
                }
            playersData[userId]["hazard_level"]["vals"].append(float(job.danger_rate))
            playersData[userId]["count"] += 1
    dangerRateStd: float = np.std(dangerRates)
    playersDataList: List[dict] = list(playersData.values())
    with open("reports/player_hazard_level_standard_deviations.txt", "w") as writer:
        for player in playersDataList:
            player["std"] = np.std(player["hazard_level"]["vals"])
        for player in sorted(playersDataList, key=lambda val: cast(float, val["std"])):
            writer.write("ID: " + player["id"] + "\n")
            writer.write("Standard Deviation: " + str(player["std"]) + "\n")
            writer.write("Count:" + str(player["count"]) + "\n")
            writer.write("\n")
        writer.write(str(dangerRateStd) + "\n")
