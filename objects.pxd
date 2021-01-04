import cython

cdef class Time:
    cdef public int time
    cdef public str iso8601

cdef class Name:
    cdef public str de_DE, en_GB, en_US, es_ES, es_MX, fr_CA, fr_FR, it_IT, ja_JP, nl_NL, ru_RU, zh_CN, zh_TW

cdef class Boss:
    cdef public int splatnet
    cdef public str key, splatnet_str
    cdef public Name name

cdef class Boss_Appearance:
    cdef public int count
    cdef public Boss boss

cdef class Title:
    cdef public int splatnet
    cdef public str key
    cdef public Name name, generic_name

cdef class Special_Weapon:
    cdef public str key
    cdef public Name name
    cdef public int splatnet

cdef class Stage_WaterLevel_KnownOccurrence:
    cdef public str key, splatnet
    cdef public Name name

cdef class Wave:
    cdef public int golden_egg_quota, golden_egg_appearances, golden_egg_delivered, power_egg_collected
    cdef public Stage_WaterLevel_KnownOccurrence known_occurrence, water_level

cdef class Gender:
    cdef public int iso5218
    cdef public str key
    cdef public Name name

cdef class Species_FailReason:
    cdef public str key
    cdef public Name name

cdef class Agent:
    cdef public str name, version

cdef class My_Data_Teammate:
    cdef public int rescue, death, golden_egg_delivered, power_egg_collected
    cdef public str splatnet_id, name
    cdef public Special_Weapon special
    cdef public Gender gender
    cdef public Species_FailReason species
    cdef public list weapons, boss_kills, special_uses

cdef class Stats:
    cdef public int work_count, total_golden_eggs, total_eggs, total_rescued, total_point
    cdef public Time as_of, registered_at

cdef class Profile:
    cdef public str nnid, friend_code, twitter, ikanakama, ikanakama2, environment

cdef class User:
    cdef public int id
    cdef public str name, screen_name, url, salmon_url, battle_url
    cdef public Time join_at
    cdef public Profile profile
    cdef public Stats stats

cdef class Job:
    cdef public int id, splatnet_number, clear_waves, title_exp, title_exp_after
    cdef public short is_cleared, automated
    cdef public str uuid, url, api_endpoint, danger_rate, note, link_url
    cdef public Stage_WaterLevel_KnownOccurrence stage
    cdef public Species_FailReason fail_reason
    cdef public My_Data_Teammate my_data
    cdef public Agent agent
    cdef public Time shift_start_at, start_at, end_at, register_at
    cdef public User user
    cdef public Title title, title_after
    cdef public list boss_appearances, waves, teammates, quota