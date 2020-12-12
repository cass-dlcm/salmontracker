import requests

grizzcoWeapons = (("Grizzco Charger", "kuma_charger"),
    ("Grizzco Brella", "kuma_brella"),
    ("Grizzco Blaster", "kuma_blaster"),
    ("Grizzco Slosher", "kuma_slosher"))

def weaponNameToKey(weaponName: str, locale: str) -> str:
    for weapon in grizzcoWeapons:
        if weapon[0] == weaponName:
            return weapon[1]
    weaponsList = requests.get("https://stat.ink/api/v2/weapon").json()
    for weapon in weaponsList:
        if weapon["name"][locale] == weaponName:
            return weapon["key"]
    return ""