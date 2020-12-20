import sys

sys.path.insert(0, ".")
import numpy as np
import core
from typing import List, Union, Tuple, Dict
import ujson
import gzip
import jsonlines

# to solve the question, "is matchmaking based on rank?"
if __name__ == "__main__":
    dataFile: str = core.init("All")
    playersData: Dict[str, dict] = {}
    with gzip.open(dataFile) as reader:
        for job in jsonlines.Reader(reader, ujson.loads):
            userId = job["my_data"]["splatnet_id"]
            if userId not in playersData:
                playersData[userId] = {"id": userId, "hazard_level": {"vals": []}}
            playersData[userId]["hazard_level"]["vals"].append(
                float(job["danger_rate"])
            )
    playersDataList: List[dict] = list(playersData.values())
    with open("reports/player_hazard_level_standard_deviations.txt", "w") as writer:
        for player in playersDataList:
            writer.write(str(np.std(player["hazard_level"]["vals"])) + "\n")
