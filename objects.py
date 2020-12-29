from typing import List, Dict, Union, Optional


class Time:
    __slots__ = ["time", "iso8601"]

    def __init__(self, time: int, iso8601: str):
        self.time: int = time
        self.iso8601: str = iso8601


class Name:
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
        de_DE: str,
        en_GB: str,
        en_US: str,
        es_ES: str,
        es_MX: str,
        fr_CA: str,
        fr_FR: str,
        it_IT: str,
        ja_JP: str,
        nl_NL: str,
        ru_RU: str,
        zh_CN: str,
        zh_TW: str,
    ):
        self.de_DE: str = de_DE
        self.en_GB: str = en_GB
        self.en_US: str = en_US
        self.es_ES: str = es_ES
        self.es_MX: str = es_MX
        self.fr_CA: str = fr_CA
        self.fr_FR: str = fr_FR
        self.it_IT: str = it_IT
        self.ja_JP: str = ja_JP
        self.nl_NL: str = nl_NL
        self.ru_RU: str = ru_RU
        self.zh_CN: str = zh_CN
        self.zh_TW: str = zh_TW


class Boss:
    __slots__ = ["key", "splatnet", "splatnet_str", "name"]

    def __init__(
        self, key: str, splatnet: int, splatnet_str: str, name: Dict[str, str]
    ):
        self.key: str = key
        self.splatnet: int = splatnet
        self.splatnet_str: str = splatnet_str
        self.name: Name = Name(**name)


class Boss_Appearance:
    __slots__ = ["boss", "count"]

    def __init__(self, boss: dict, count: int):
        self.boss: Boss = Boss(**boss)
        self.count: int = count


class Title:
    __slots__ = ["key", "splatnet", "name", "generic_name"]

    def __init__(
        self,
        key: str,
        splatnet: int,
        name: Dict[str, str],
        generic_name: Dict[str, str],
    ):
        self.key: str = key
        self.splatnet: int = splatnet
        self.name: Name = Name(**name)
        self.generic_name: Name = Name(**generic_name)


class Special_Weapon:
    __slots__ = ["key", "splatnet", "name"]

    def __init__(self, key: str, splatnet, name: Dict[str, str]):
        self.key: str = key
        self.splatnet: int = splatnet
        self.name: Name = Name(**name)


class Stage_WaterLevel_KnownOccurrence:
    __slots__ = ["key", "splatnet", "name"]

    def __init__(self, key: str, splatnet, name: Dict[str, str]):
        self.key: str = key
        self.splatnet: str = splatnet
        self.name: Name = Name(**name)


class Wave:
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
        known_occurrence: dict,
        water_level: dict,
        golden_egg_quota: int,
        golden_egg_appearances: int,
        golden_egg_delivered: int,
        power_egg_collected: int,
    ):
        if known_occurrence is not None:
            self.known_occurrence: Stage_WaterLevel_KnownOccurrence = (
                Stage_WaterLevel_KnownOccurrence(**known_occurrence)
            )
        else:
            known_occurrence = None
        self.water_level: Stage_WaterLevel_KnownOccurrence = (
            Stage_WaterLevel_KnownOccurrence(**water_level)
        )
        self.golden_egg_quota: int = golden_egg_quota
        self.golden_egg_appearances: int = golden_egg_appearances
        self.golden_egg_delivered: int = golden_egg_delivered
        self.power_egg_collected: int = power_egg_collected


class Gender:
    __slots__ = ["key", "iso5218", "name"]

    def __init__(self, key: str, iso5218: int, name: Dict[str, str]):
        self.key: str = key
        self.iso5218: int = iso5218
        self.name: Name = Name(**name)


class Species_FailReason:
    __slots__ = ["key", "name"]

    def __init__(self, key, name):
        self.key: str = key
        self.name: Name = Name(**name)


class Agent:
    __slots__ = ["name", "version"]

    def __init__(self, name: str, version: str):
        self.name: str = name
        self.version: str = version


class My_Data_Teammate:
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
        splatnet_id: str,
        name: str,
        special: dict,
        rescue: int,
        death: int,
        golden_egg_delivered: int,
        power_egg_collected: int,
        species: Dict[str, Union[str, Dict[str, str]]],
        gender: dict,
        special_uses: List[int],
        weapons: List[dict],
        boss_kills: List[dict],
    ):
        self.splatnet_id: str = splatnet_id
        self.name: str = name
        self.special: Special_Weapon = Special_Weapon(**special)
        self.rescue: int = rescue
        self.death: int = death
        self.golden_egg_delivered: int = golden_egg_delivered
        self.power_egg_collected: int = power_egg_collected
        if species is not None:
            self.species: Species_FailReason = Species_FailReason(**species)
        else:
            self.species = None
        if gender is not None:
            self.gender = Gender(**gender)
        else:
            self.gender = None
        self.special_uses: List[int] = special_uses
        self.weapons: List[Special_Weapon] = []
        if weapons is not None:
            for weapon in weapons:
                self.weapons.append(Special_Weapon(**weapon))
        else:
            self.weapons = None
        self.boss_kills: List[Boss_Appearance] = []
        if boss_kills is not None:
            for boss in boss_kills:
                self.boss_kills.append(Boss_Appearance(**boss))
        else:
            self.boss_kills = None


class Stats:
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
        work_count: int,
        total_golden_eggs: int,
        total_eggs: int,
        total_rescued: int,
        total_point: int,
        as_of: dict,
        registered_at: dict,
    ):
        self.work_count: int = work_count
        self.total_golden_eggs: int = total_golden_eggs
        self.total_eggs: int = total_eggs
        self.total_rescued: int = total_rescued
        self.total_point: int = total_point
        self.as_of: Time = Time(**as_of)
        self.registered_at: Time = Time(**registered_at)


class Profile:
    __slots__ = [
        "nnid",
        "friend_code",
        "twitter",
        "ikanakama",
        "ikanakama2",
        "environment",
    ]

    def __init__(
        self,
        nnid: str,
        friend_code: str,
        twitter: str,
        ikanakama: str,
        ikanakama2: str,
        environment: str,
    ):
        self.nnid: str = nnid
        self.friend_code: str = friend_code
        self.twitter: str = twitter
        self.ikanakama: str = ikanakama
        self.ikanakama2: str = ikanakama2
        self.environment: str = environment


class User:
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
        id: int,
        name: str,
        screen_name: str,
        url: str,
        salmon_url: str,
        battle_url: str,
        join_at: dict,
        profile: Dict[str, str],
        stats: dict,
    ):
        self.id: int = id
        self.name: str = name
        self.screen_name: str = screen_name
        self.url: str = url
        self.salmon_url: str = salmon_url
        self.battle_url: str = battle_url
        self.join_at: Time = Time(**join_at)
        self.profile: Profile = Profile(**profile)
        self.stats: Stats = Stats(**stats)


class Job:
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
        id: int,
        uuid: str,
        splatnet_number: int,
        url: str,
        api_endpoint: str,
        user: dict,
        stage: dict,
        is_cleared: bool,
        fail_reason: dict,
        clear_waves: int,
        danger_rate: str,
        quota: List[int],
        title: dict,
        title_exp: int,
        title_after: dict,
        title_exp_after: int,
        boss_appearances: List[dict],
        waves: List[dict],
        my_data: dict,
        teammates: List[dict],
        agent: Dict[str, str],
        automated: bool,
        note: str,
        link_url: str,
        shift_start_at: dict,
        start_at: dict,
        end_at: Optional[dict],
        register_at: dict,
    ):
        self.id: int = id
        self.uuid: str = uuid
        self.splatnet_number: int = splatnet_number
        self.url: str = url
        self.api_endpoint: str = api_endpoint
        self.user: User = User(**user)
        if stage is not None:
            self.stage: Optional[
                Stage_WaterLevel_KnownOccurrence
            ] = Stage_WaterLevel_KnownOccurrence(**stage)
        else:
            self.stage = None
        self.is_cleared: bool = is_cleared
        if fail_reason is not None and fail_reason != "None":
            self.fail_reason: Optional[Species_FailReason] = Species_FailReason(
                **fail_reason
            )
        else:
            self.fail_reason = None
        self.clear_waves: int = clear_waves
        self.danger_rate: str = danger_rate
        self.quota: List[int] = quota
        if title is not None:
            self.title: Optional[Title] = Title(**title)
        else:
            self.title = None
        if title_exp is not None:
            self.title_exp: int = title_exp
        else:
            self.title_exp = None
        self.title_after: Title = Title(**title_after)
        self.title_exp_after: int = title_exp_after
        self.boss_appearances: List[Boss_Appearance] = []
        if boss_appearances is not None:
            for boss in boss_appearances:
                self.boss_appearances.append(Boss_Appearance(**boss))
        self.waves: List[Wave] = []
        for wave in waves:
            self.waves.append(Wave(**wave))
        self.my_data: My_Data_Teammate = My_Data_Teammate(**my_data)
        self.teammates: List[My_Data_Teammate] = []
        if teammates is not None:
            for teammate in teammates:
                self.teammates.append(My_Data_Teammate(**teammate))
        else:
            self.teammates = None
        self.agent: Agent = Agent(**agent)
        self.automated: bool = automated
        self.note: str = note
        self.link_url: str = link_url
        self.shift_start_at: Time = Time(**shift_start_at)
        self.start_at: Time = Time(**start_at)
        if end_at is not None:
            self.end_at: Optional[Time] = Time(**end_at)
        else:
            self.end_at = None
        self.register_at: Time = Time(**register_at)

    def has_stage(self) -> bool:
        return self.stage is not None
