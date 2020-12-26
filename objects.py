import time
import ujson
from typing import List
import gzip


class Time(object):
    __slots__ = ["time", "iso8601"]

    def __init__(self, time, iso8601):
        self.time = time
        self.iso8601 = iso8601


class Name(object):
    __slots__ = [
        "de_DE",
        "en_GB",
        "en_US",
        "es_ES",
        "es_MX",
        "fr_CA",
        "fr_FR",
        "it_IT",
        "ja_JP",
        "nl_NL",
        "ru_RU",
        "zh_CN",
        "zh_TW",
    ]

    def __init__(
        self,
        de_DE,
        en_GB,
        en_US,
        es_ES,
        es_MX,
        fr_CA,
        fr_FR,
        it_IT,
        ja_JP,
        nl_NL,
        ru_RU,
        zh_CN,
        zh_TW,
    ):
        self.de_DE = de_DE
        self.en_GB = en_GB
        self.en_US = en_US
        self.es_ES = es_ES
        self.es_MX = es_MX
        self.fr_CA = fr_CA
        self.fr_FR = fr_FR
        self.it_IT = it_IT
        self.ja_JP = ja_JP
        self.nl_NL = nl_NL
        self.ru_RU = ru_RU
        self.zh_CN = zh_CN
        self.zh_TW = zh_TW


class Boss(object):
    __slots__ = ["key", "splatnet", "splatnet_str", "name"]

    def __init__(self, key, splatnet, splatnet_str, name):
        self.key = key
        self.splatnet = splatnet
        self.splatnet_str = splatnet_str
        self.name = Name(**name)


class Boss_Appearance(object):
    __slots__ = ["boss", "count"]

    def __init__(self, boss, count):
        self.boss = Boss(**boss)
        self.count = count


class Title(object):
    __slots__ = ["key", "splatnet", "name", "generic_name"]

    def __init__(self, key, splatnet, name, generic_name):
        self.key = key
        self.splatnet = splatnet
        self.name = Name(**name)
        self.generic_name = Name(**generic_name)


class Stage__Water_Level__Special__Known_Occurrence__Weapon(object):
    __slots__ = ["key", "splatnet", "name"]

    def __init__(self, key, splatnet, name):
        self.key = key
        self.splatnet = splatnet
        self.name = Name(**name)


class Wave(object):
    __slots__ = [
        "known_occurrence",
        "water_level",
        "golden_egg_quota",
        "golden_egg_appearances",
        "golden_egg_delivered",
        "power_egg_collected",
    ]

    def __init__(
        self,
        known_occurrence,
        water_level,
        golden_egg_quota,
        golden_egg_appearances,
        golden_egg_delivered,
        power_egg_collected,
    ):
        if known_occurrence is not None:
            self.known_occurrence = (
                Stage__Water_Level__Special__Known_Occurrence__Weapon(
                    **known_occurrence
                )
            )
        self.water_level = Stage__Water_Level__Special__Known_Occurrence__Weapon(
            **water_level
        )
        self.golden_egg_quota = golden_egg_quota
        self.golden_egg_appearances = golden_egg_appearances
        self.golden_egg_delivered = golden_egg_delivered
        self.power_egg_collected = power_egg_collected


class Gender(object):
    __slots__ = ["key", "iso5218", "name"]

    def __init__(self, key, iso5218, name):
        self.key = key
        self.iso5218 = iso5218
        self.name = Name(**name)


class Species(object):
    __slots__ = ["key", "name"]

    def __init__(self, key, name):
        self.key = key
        self.name = Name(**name)


class Agent(object):
    __slots__ = ["name", "version"]

    def __init__(self, name, version):
        self.name = name
        self.version = version


class My_Data_Teammate(object):
    __slots__ = [
        "splatnet_id",
        "name",
        "special",
        "rescue",
        "death",
        "golden_egg_delivered",
        "power_egg_collected",
        "species",
        "gender",
        "special_uses",
        "weapons",
        "boss_kills",
    ]

    def __init__(
        self,
        splatnet_id,
        name,
        special,
        rescue,
        death,
        golden_egg_delivered,
        power_egg_collected,
        species,
        gender,
        special_uses,
        weapons,
        boss_kills,
    ):
        self.splatnet_id = splatnet_id
        self.name = name
        self.special = Stage__Water_Level__Special__Known_Occurrence__Weapon(**special)
        self.rescue = rescue
        self.death = death
        self.golden_egg_delivered = golden_egg_delivered
        self.power_egg_collected = power_egg_collected
        if species is not None:
            self.species = Species(**species)
        if gender is not None:
            self.gender = Gender(**gender)
        self.special_uses = special_uses
        self.weapons = []
        if weapons is not None:
            for weapon in weapons:
                self.weapons.append(
                    Stage__Water_Level__Special__Known_Occurrence__Weapon(**weapon)
                )
        self.boss_kills = []
        if boss_kills is not None:
            for boss in boss_kills:
                self.boss_kills.append(Boss_Appearance(**boss))


class Stats(object):
    __slots__ = [
        "work_count",
        "total_golden_eggs",
        "total_eggs",
        "total_rescued",
        "total_point",
        "as_of",
        "registered_at",
    ]

    def __init__(
        self,
        work_count,
        total_golden_eggs,
        total_eggs,
        total_rescued,
        total_point,
        as_of,
        registered_at,
    ):
        self.work_count = work_count
        self.total_golden_eggs = total_golden_eggs
        self.total_eggs = total_eggs
        self.total_rescued = total_rescued
        self.total_point = total_point
        self.as_of = Time(**as_of)
        self.registered_at = Time(**registered_at)


class Profile(object):
    __slots__ = [
        "nnid",
        "friend_code",
        "twitter",
        "ikanakama",
        "ikanakama2",
        "environment",
    ]

    def __init__(self, nnid, friend_code, twitter, ikanakama, ikanakama2, environment):
        self.nnid = nnid
        self.friend_code = friend_code
        self.twitter = twitter
        self.ikanakama = ikanakama
        self.ikanakama2 = ikanakama2
        self.environment = environment


class User(object):
    __slots__ = [
        "id",
        "name",
        "screen_name",
        "url",
        "salmon_url",
        "battle_url",
        "join_at",
        "profile",
        "stats",
    ]

    def __init__(
        self,
        id,
        name,
        screen_name,
        url,
        salmon_url,
        battle_url,
        join_at,
        profile,
        stats,
    ):
        self.id = id
        self.name = name
        self.screen_name = screen_name
        self.url = url
        self.salmon_url = salmon_url
        self.battle_url = battle_url
        self.join_at = Time(**join_at)
        self.profile = Profile(**profile)
        self.stats = Stats(**stats)


class Job(object):
    __slots__ = [
        "id",
        "uuid",
        "splatnet_number",
        "url",
        "api_endpoint",
        "user",
        "stage",
        "is_cleared",
        "fail_reason",
        "clear_waves",
        "danger_rate",
        "quota",
        "title",
        "title_exp",
        "title_after",
        "title_exp_after",
        "boss_appearances",
        "waves",
        "my_data",
        "teammates",
        "agent",
        "automated",
        "note",
        "link_url",
        "shift_start_at",
        "start_at",
        "end_at",
        "register_at",
    ]

    def __init__(
        self,
        id,
        uuid,
        splatnet_number,
        url,
        api_endpoint,
        user,
        stage,
        is_cleared,
        fail_reason,
        clear_waves,
        danger_rate,
        quota,
        title,
        title_exp,
        title_after,
        title_exp_after,
        boss_appearances,
        waves,
        my_data,
        teammates,
        agent,
        automated,
        note,
        link_url,
        shift_start_at,
        start_at,
        end_at,
        register_at,
    ):
        self.id = id
        self.uuid = uuid
        self.splatnet_number = splatnet_number
        self.url = url
        self.api_endpoint = api_endpoint
        self.user = User(**user)
        if stage is not None:
            self.stage = Stage__Water_Level__Special__Known_Occurrence__Weapon(**stage)
        self.is_cleared = is_cleared
        self.fail_reason = fail_reason
        self.clear_waves = clear_waves
        self.danger_rate = danger_rate
        self.quota = quota
        if title is not None:
            self.title = Title(**title)
        else:
            self.title = None
        self.title_exp = title_exp
        self.title_after = Title(**title_after)
        self.title_exp_after = title_exp_after
        self.boss_appearances = []
        if boss_appearances is not None:
            for boss in boss_appearances:
                self.boss_appearances.append(Boss_Appearance(**boss))
        self.waves = []
        for wave in waves:
            self.waves.append(Wave(**wave))
        self.my_data = My_Data_Teammate(**my_data)
        self.teammates = []
        if teammates is not None:
            for teammate in teammates:
                self.teammates.append(My_Data_Teammate(**teammate))
        self.agent = Agent(**agent)
        self.automated = automated
        self.note = note
        self.link_url = link_url
        self.shift_start_at = Time(**shift_start_at)
        self.start_at = Time(**start_at)
        if end_at is not None:
            self.end_at = Time(**end_at)
        else:
            self.end_at = end_at
        self.register_at = Time(**register_at)

    def has_stage(self) -> bool:
        return self.stage is not None


if __name__ == "__main__":
    tic = time.perf_counter()
    jobs: List[Job] = []
    with gzip.open("data/salmonAll.jl.gz", "r") as reader:
        for line in reader:
            jobs.append(Job(**ujson.loads(line)))
    print("Time taken: {}".format(time.perf_counter() - tic))
