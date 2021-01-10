import core
from objects import Job
import ujson
import gzip

data = core.init("User", "data/", ujson.load(open("keys.json"))["statink_key"])
scoresDict: dict = {
    "All": None,
    "Princess": None,
    "None": {"low": None, "normal": None, "high": None},
    "mothership": {"low": None, "normal": None, "high": None},
    "fog": {"low": None, "normal": None, "high": None},
    "rush": {"low": None, "normal": None, "high": None},
    "cohock_charge": {"low": None, "normal": None, "high": None},
    "griller": {"low": None, "normal": None, "high": None},
    "goldie_seeking": {"low": None, "normal": None, "high": None},
}
for keyA in scoresDict:
    if isinstance(scoresDict[keyA], dict):
        for keyB in scoresDict[keyA]:
            scoresDict[keyA][keyB] = {
                "dam": {
                    "total": 0,
                    "url": None,
                },
                "shaketoba": {
                    "total": 0,
                    "url": None,
                },
                "tokishirazu": {
                    "total": 0,
                    "url": None,
                },
                "donburako": {
                    "total": 0,
                    "url": None,
                },
                "polaris": {
                    "total": 0,
                    "url": None,
                },
            }
    else:
        scoresDict[keyA] = {
            "dam": {
                "total": 0,
                "url": None,
            },
            "shaketoba": {
                "total": 0,
                "url": None,
            },
            "tokishirazu": {
                "total": 0,
                "url": None,
            },
            "donburako": {
                "total": 0,
                "url": None,
            },
            "polaris": {
                "total": 0,
                "url": None,
            },
        }
with gzip.open(data) as reader:
    for line in reader:
        job = Job(**ujson.loads(line))
        totalEggs = 0
        if job is not None and job.stage is not None and job.waves is not None:
            for wave in job.waves:
                totalEggs += wave.golden_egg_delivered
                if hasattr(wave, "known_occurrence"):
                    if (
                        wave.golden_egg_delivered
                        > scoresDict[wave.known_occurrence.key][wave.water_level.key][
                            job.stage.key
                        ]["total"]
                    ):
                        scoresDict[wave.known_occurrence.key][wave.water_level.key][
                            job.stage.key
                        ]["url"] = job.url
                        scoresDict[wave.known_occurrence.key][wave.water_level.key][
                            job.stage.key
                        ]["total"] = wave.golden_egg_delivered
                else:
                    if (
                        wave.golden_egg_delivered
                        > scoresDict["None"][wave.water_level.key][job.stage.key][
                            "total"
                        ]
                    ):
                        scoresDict["None"][wave.water_level.key][job.stage.key][
                            "url"
                        ] = job.url
                        scoresDict["None"][wave.water_level.key][job.stage.key][
                            "total"
                        ] = wave.golden_egg_delivered
            if totalEggs > scoresDict["All"][job.stage.key]["total"]:
                scoresDict["All"][job.stage.key]["total"] = totalEggs
                scoresDict["All"][job.stage.key]["url"] = job.url
            if job.my_data is not None and (
                job.my_data.golden_egg_delivered
                > scoresDict["Princess"][job.stage.key]["total"]
            ):
                scoresDict["Princess"][job.stage.key][
                    "total"
                ] = job.my_data.golden_egg_delivered
                scoresDict["Princess"][job.stage.key]["url"] = job.url
print(scoresDict)
