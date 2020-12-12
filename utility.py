import requests

def weaponNameToKey(weaponName: str, locale: str) -> str:
    weaponsList = requests.get("https://stat.ink/api/v2/weapon").json()
    for weapon in weaponsList:
        if weapon["name"][locale] == weaponName:
            return weapon["key"]
    return ""