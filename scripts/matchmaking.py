from objects import Job
import numpy as np
import core
from typing import List, Union, Tuple, Dict, cast
import ujson
import gzip
import jsonlines


class PlayerData:
    __slots__ = ["id", "hazard_level_vals", "std", "count"]

    def __init__(self, id):
        self.id = id
        self.hazard_level_vals = []
        self.std = 0.0
        self.count = 0.0


# to solve the question, "is matchmaking based on rank?"
dataFile: str = core.init("All", "data/")
playersData: Dict[str, PlayerData] = {}
dangerRates: List[float] = []
with gzip.open(dataFile) as reader:
    for line in reader:
        job = Job(**ujson.loads(line))
        userId = job.my_data.splatnet_id
        dangerRates.append(float(job.danger_rate))
        if userId not in playersData:
            playersData[userId] = PlayerData(id)
        playersData[userId].hazard_level_vals.append(float(job.danger_rate))
        playersData[userId].count += 1
dangerRateStd: float = np.std(dangerRates)
playersDataList: List[PlayerData] = list(playersData.values())
with open("reports/player_hazard_level_standard_deviations.txt", "w") as writer:
    for player in playersDataList:
        player.std = np.std(player.hazard_level_vals)
    for player in sorted(playersDataList, key=lambda val: cast(float, val.std)):
        writer.write("ID: " + player.id + "\n")
        writer.write("Standard Deviation: " + str(player.std) + "\n")
        writer.write("Count:" + str(player.count) + "\n")
        writer.write("\n")
    writer.write(str(dangerRateStd) + "\n")
