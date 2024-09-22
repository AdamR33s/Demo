### AUTHOR: Adam R33s (A.K.A R4ptor or Tot4ll3d) ###
### EMAIL:
# Adzz.GSAU@Gmail.com - My Personal Email
# R4ptor@KYRGaming.com - My Gaming Server Queries Email
# Tot4ll3d@KYRGaming.com - My Community Queries Email
### CREATED: 07/08/2024 ### (COPY)
### VERSION: V2.0.0 ###
### SUMMARY: GraphQL Project in progress. Enormous Data return from API in structured text format (tarkov_caches.txt). Need to process and store in cache." ###

import discord
import controls
import db
import utils
from collections import namedtuple
from dataclasses import dataclass
from discord.ext import tasks
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.dsl import DSLQuery, DSLSchema, dsl_gql, DSLInlineFragment


@dataclass
class TarkovAPI:
    schema: DSLSchema
    item_query: DSLQuery


class Weapon:
    def __init__(self: "Weapon"):
        name: str
        short_name: str
        category: str
        size: tuple
        weight: float
        images: dict = {
            "icon_image": "",
            "image8xLink": "",
            "inspection_image_link": "",
        }
        barters_for: dict = {"Trader": "", "Required_Items": ""}
        barters_with: dict = {"Trader": "", "Required_Items": ""}
        trader_cost_information: dict = {}
        market_cost_uinformation: dict = {}

    async def load(weapon_name: str, preset: bool = True) -> "Weapon":
        pass


default_cache = {}
weapon_cache = {}
ammo_cache = {}
ammo_box_cache = {}
grenade_cache = {}
gear_cache = {}
mods_cache = {}
meds_cache = {}
keys_cache = {}
provisions_cache = {}
containers_cache = {}
barteritem_cache = {}
otheritems_cache = {}

cache_namelist = {
    "default_cache": default_cache,
    "weapons_cache": weapon_cache,
    "ammo_cache": ammo_cache,
    "ammo_box_cache": ammo_box_cache,
    "gear_cache": gear_cache,
    "mods_cache": mods_cache,
    "meds_cache": meds_cache,
    "key_cache": keys_cache,
    "provisions_cache": provisions_cache,
    "containers_cache": containers_cache,
    "utiltools_cache": barteritem_cache,
    "otheritems_cache": otheritems_cache,
}


@tasks.loop(seconds=60)
async def tarkov_api_ratelimit_cleaner():
    tarkov_control: controls.Control = controls.Control.load("tarkov_api")
    tarkov_control.number = 0
    tarkov_control.update()


async def write_caches_to_file():
    bot_control_room = utils.active_channels["bot-control-room"]
    file_path = f"./data/tarkov_caches.txt"
    with open(file_path, "w", encoding="utf-8") as cache_file:
        for cache_name, cache in cache_namelist.items():
            cache_file.write(f"------- CACHE NAME :: {cache_name} -------\n")
            for key, value in cache.items():
                cache_file.write(f"KEY:  {key} || VALUE:  {value}\n\n")
            cache_file.write(f"------- END OF CACHE :: {cache_name} -------\n\n")
    discord_file = discord.File(f"./data/tarkov_caches.txt")
    await bot_control_room.send(file=discord_file)


async def create_item_query(itemName, *fields):
    fieldString = "\n   ".join(fields)
    return f"""
		{{
				items(name: "{itemName}") {{
						{fieldString}
				}}
		}}
		"""


async def print_tarkov_caches():
    # bot_control_room = utils.active_channels['bot-control-room']
    for cache_name, cache in cache_namelist.items():
        print(f"Cache Name: {cache_name}")
        # await bot_control_room.send(f'Cache Name: {cache_name}')
        for key, value in cache.items():
            print(f"KEY: {key}, VALUE: {value}")
        #    await bot_control_room.send(f'KEY: {key}, VALUE: {value}')
        print(f"End of {cache_name}")
        # await bot_control_room.send(f'End of {cache_name}')


################################################################################################
######################################### Sub Filters ####################################
################################################################################################
def check_stats(item_section):
    modifiers_list = []
    if item_section["accuracyModifier"] is not None:
        modifiers_list.append("accuracyModifier")
    if item_section["recoilModifier"] is not None:
        modifiers_list.append("recoilModifier")
    if item_section["ergonomicsModifier"] is not None:
        modifiers_list.append("ergonomicsModifier")
    if item_section["velocity"] is not None:
        modifiers_list.append("velocity")
    if item_section["loudness"] is not None:
        modifiers_list.append("loudness")
    return modifiers_list


def check_properties(item_section):
    if item_section["properties"] is not None:
        return True


section_data_keys = [
    "width",
    "height",
    "weight",
    "iconLink",
    "image8xLink",
]


################################################################################################
######################################### Process Ammo ####################################
################################################################################################
def process_ammo(item_section):
    try:
        categories = item_section["categories"]
        primary_cat = categories[0]["name"]
        if primary_cat != "Ammo":
            return False
        item_name = item_section["name"]
        caliber_string = item_prop.get("caliber", None)
        caliber = caliber_string.format("Caliber", "")
        if caliber not in ammo_cache:
            ammo_cache[caliber] = {}
        if item_name not in ammo_cache[caliber]:
            ammo_cache[caliber][item_name] = {}
        ammo_ent_point = ammo_cache[caliber][item_name]
        item_shortname = item_section["shortName"]
        ammo_ent_point["shortName"] = item_shortname
        ammo_ent_point["types"] = item_section.get("types", [])
        ammo_ent_point["parentCat"] = item_section["categories"][0]["parent"]["name"]
        for key in section_data_keys:
            ammo_ent_point[key] = item_section.get(key, None)
        stats_list = check_stats(item_section)
        if stats_list:
            for key in stats_list:
                ammo_ent_point[key] = item_section.get(key, None)
        if check_properties(item_section):
            item_prop = item_section["properties"]
            for key in item_prop.keys():
                ammo_ent_point[key] = item_prop.get(key, None)
        return True
    except Exception as e:
        print(f"Error in processing Ammo Details: {e}")
        print(f"Problem Data Section: {item_section}")


def process_ammo_containers(item_section):
    try:
        categories = item_section["categories"]
        primary_cat = categories[0]["name"]
        if primary_cat != "Ammo container":
            return False
        item_name = item_section["name"]
        if item_name not in ammo_box_cache:
            ammo_box_cache[item_name] = {}
        item_shortname = item_section["shortName"]
        ammo_ent_point = ammo_box_cache[item_shortname]
        ammo_ent_point["name"] = item_name
        ammo_ent_point["types"] = item_section.get("types", [])
        ammo_ent_point["parentat"] = item_section["categories"][0]["parent"]["name"]
        for key in section_data_keys:
            ammo_ent_point[key] = item_section.get(key, None)
        stats_list = check_stats(item_section)
        if stats_list:
            for key in stats_list:
                ammo_ent_point[key] = item_section.get(key, None)
        if check_properties(item_section):
            item_prop = item_section["properties"]
            for key in item_prop.keys():
                ammo_ent_point[key] = item_prop.get(key, None)
        return True
    except Exception as e:
        print(f"Error in processing Ammo Containers: {e}")
        print(f"Problem ItemSection: {item_section}")


################################################################################################
######################################### Process Weapons ####################################
################################################################################################


def process_weapons(item_section):
    section_data_keys = [
        "width",
        "height",
        "weight",
        "accuracyModifier",
        "recoilModifier",
        "ergonomicsModifier",
        "iconLink",
        "image8xLink",
    ]
    try:
        categories = item_section["categories"]
        primary_cat_parent = categories[0]["parent"]["name"]
        if primary_cat_parent != "Weapon":
            return False
        item_name = item_section["name"]
        item_shortname = item_section["shortName"]
        item_prop = item_section["name"]["properties"]
        primary_cat = categories[0]["name"]
        if primary_cat not in weapon_cache:
            weapon_cache[primary_cat] = {}
        if item_name not in weapon_cache[primary_cat]:
            weapon_cache[primary_cat][item_name] = {}
        weapon_ent_point = weapon_cache[primary_cat][item_name]
        weapon_ent_point["shortName"] = item_shortname
        weapon_ent_point["types"] = item_section.get("types", [])
        weapon_ent_point["parentCat"] = item_section["categories"][0]["parent"]["name"]
        for key in section_data_keys:
            weapon_ent_point[key] = item_section.get(key, None)
        stats_list = check_stats(item_section)
        if stats_list:
            for key in stats_list:
                weapon_ent_point[key] = item_section.get(key, None)
        if check_properties(item_section):
            item_prop = item_section["properties"]
            for key in item_prop.keys():
                weapon_ent_point[key] = item_prop.get(key, None)
        return True
    except Exception as e:
        print(f"Error in processing Weapon: {e}")
        print(f"Problem ItemSection: {item_section}")


def process_grenades(item_section):
    section_data_keys = [
        "width",
        "height",
        "weight",
        "accuracyModifier",
        "recoilModifier",
        "ergonomicsModifier",
        "iconLink",
        "image8xLink",
    ]
    try:
        primary_cat = categories[0]["name"]
        if primary_cat != "Throwable weapon":
            return False
        categories = item_section["categories"]
        item_name = item_section["name"]
        item_shortname = item_section["shortName"]
        item_prop = item_section["name"]["properties"]
        if primary_cat not in grenade_cache:
            grenade_cache[primary_cat] = {}
        if item_name not in grenade_cache[primary_cat]:
            grenade_cache[primary_cat][item_name] = {}
        grenade_ent_point = grenade_cache[primary_cat][item_name]
        grenade_ent_point["shortName"] = item_shortname
        grenade_ent_point["types"] = item_section.get("types", [])
        grenade_ent_point["parentCat"] = item_section["categories"][0]["parent"]["name"]
        for key in section_data_keys:
            grenade_ent_point[key] = item_section.get(key, None)
        stats_list = check_stats(item_section)
        if stats_list:
            for key in stats_list:
                grenade_ent_point[key] = item_section.get(key, None)
        if check_properties(item_section):
            item_prop = item_section["properties"]
            for key in item_prop.keys():
                grenade_ent_point[key] = item_prop.get(key, None)
        return True
    except Exception as e:
        print(f"Error in processing Weapon: {e}")
        print(f"Problem ItemSection: {item_section}")


################################################################################################
######################################### Process Modifications ################################
################################################################################################


def process_barrels(item_section):
    try:
        categories = item_section["categories"]
        primary_cat = categories[0]["name"]
        if "Barrel" not in types:
            return False
        types = item_section["types"]
        if primary_cat not in mods_cache:
            mods_cache[primary_cat] = {}
        item_name = item_section["name"]
        if item_name not in mods_cache[primary_cat]:
            mods_cache[primary_cat][item_name] = {}
        item_shortname = item_section["shortName"]

        mods_ent_point = mods_cache[primary_cat][item_name]
        mods_ent_point["shortName"] = item_shortname
        mods_ent_point["types"] = types
        mods_ent_point["parentCat"] = item_section["categories"][0]["parent"]["name"]
        for key in section_data_keys:
            mods_ent_point[key] = item_section.get(key, None)
        stats_list = check_stats(item_section)
        if stats_list:
            for key in stats_list:
                mods_ent_point[key] = item_section.get(key, None)
        if check_properties(item_section):
            item_prop = item_section["name"]["properties"]
            for key in item_prop.keys():
                mods_ent_point[key] = item_prop.get(key, None)
        return True
    except Exception as e:
        print(f"Error in processing Mods: {e}")
        print(f"Problem ItemSection: {item_section}")


def process_scopes(item_section):
    try:
        categories = item_section["categories"]
        primary_cat = categories[0]["name"]
        if "Barrel" not in types:
            return False
        types = item_section["types"]
        if primary_cat not in mods_cache:
            mods_cache[primary_cat] = {}
        item_name = item_section["name"]
        if item_name not in mods_cache[primary_cat]:
            mods_cache[primary_cat][item_name] = {}
        item_shortname = item_section["shortName"]
        mods_ent_point = mods_cache[primary_cat][item_name]
        mods_ent_point["shortName"] = item_shortname
        mods_ent_point["types"] = types
        mods_ent_point["parentCat"] = item_section["categories"][0]["parent"]["name"]
        for key in section_data_keys:
            mods_ent_point[key] = item_section.get(key, None)
        stats_list = check_stats(item_section)
        if stats_list:
            for key in stats_list:
                mods_ent_point[key] = item_section.get(key, None)
        if check_properties(item_section):
            item_prop = item_section["name"]["properties"]
            for key in item_prop.keys():
                mods_ent_point[key] = item_prop.get(key, None)

        return True
    except Exception as e:
        print(f"Error in processing Mods: {e}")
        print(f"Problem ItemSection: {item_section}")


def process_chest_rigs(item_section):
    try:
        categories = item_section["categories"]
        primary_cat_parent = categories[0]["parent"]["name"]
        if (
            primary_cat_parent != "Equipment"
            and primary_cat_parent != "Armored equipment"
        ):
            return False
        primary_cat = categories[0]["name"]
        if primary_cat not in gear_cache:
            gear_cache[primary_cat] = {}
        item_name = item_section["name"]
        if item_name not in gear_cache[primary_cat]:
            gear_cache[primary_cat][item_name] = {}
        item_shortname = item_section["shortName"]
        item_properties = item_section["name"]["properties"]
        gear_cache[primary_cat][item_name]["shortName"] = item_shortname
        gear_cache[primary_cat][item_name]["types"] = item_section.get("types", [])
        gear_cache[primary_cat][item_name]["dimensions"] = Dimensions(
            x=item_section.get("width", None), y=item_section.get("height", None)
        )
        gear_cache[primary_cat][item_name]["height"] = item_section.get("height", None)
        gear_cache[primary_cat][item_name]["weight"] = item_section.get("weight", None)
        gear_cache[primary_cat][item_name]["iconLink"] = item_section.get(
            "iconLink", None
        )
        gear_cache[primary_cat][item_name]["image8xLink"] = item_section.get(
            "image8xLink", None
        )
        gear_cache[primary_cat][item_name]["armorType"] = item_properties.get(
            "armorType", None
        )
        gear_cache[primary_cat][item_name]["class"] = item_properties.get("class", None)
        gear_cache[primary_cat][item_name]["durability"] = item_properties.get(
            "durability", None
        )
        gear_cache[primary_cat][item_name]["repairCost"] = item_properties.get(
            "repairCost", None
        )
        gear_cache[primary_cat][item_name]["turnPenalty"] = item_properties.get(
            "turnPenalty", None
        )
        gear_cache[primary_cat][item_name]["ergoPenalty"] = item_properties.get(
            "ergoPenalty", None
        )
        gear_cache[primary_cat][item_name]["speedPenalty"] = item_properties.get(
            "speedPenalty", None
        )
        gear_cache[primary_cat][item_name]["deafening"] = item_properties.get(
            "capacity", None
        )
        gear_cache[primary_cat][item_name]["material"] = Material(
            name=item_properties.get("material", None),
            minRepairDegrade=item_properties.get("minRepairDegradation", None),
            maxRepairDegrade=item_properties.get("maxRepairDegradation", None),
            minRepairKitDegrade=item_properties.get("minRepairKitDegradation", None),
            maxRepairKitDegrade=item_properties.get("maxRepairKitDegradation", None),
        )
        return True
    except Exception as e:
        print(f"Error in processing Gear: {e}")
        print(f"Problem ItemSection: {item_section}")


def process_meds(item_section):
    try:
        categories = item_section["categories"]
        primary_cat_parent = categories[0]["parent"]["name"]
        if primary_cat_parent != "Meds":
            return False
        primary_cat = categories[0]["name"]
        if primary_cat not in meds_cache:
            meds_cache[primary_cat] = {}
        item_name = item_section["name"]
        if item_name not in meds_cache[primary_cat]:
            meds_cache[primary_cat][item_name] = {}
        item_shortname = item_section["shortName"]
        item_properties = item_section["name"]["properties"]
        types = item_section["types"]
        meds_cache[primary_cat][item_name]["shortName"] = item_shortname
        meds_cache[primary_cat][item_name]["types"] = types
        meds_cache[primary_cat][item_name]["dimensions"] = Dimensions(
            x=item_section.get("width", None), y=item_section.get("height", None)
        )
        meds_cache[primary_cat][item_name]["weight"] = item_section.get("weight", None)
        meds_cache[primary_cat][item_name]["hitpoints"] = item_properties.get(
            "hitpoints", None
        )
        meds_cache[primary_cat][item_name]["maxHealPerUse"] = item_properties.get(
            "maxHealPerUse", None
        )
        meds_cache[primary_cat][item_name]["uses"] = item_properties.get("uses", None)
        meds_cache[primary_cat][item_name]["useTime"] = item_properties.get(
            "useTime", None
        )
        meds_cache[primary_cat][item_name]["cures"] = item_properties.get("cures", None)
        meds_cache[primary_cat][item_name]["hpCostHeavyBleeding"] = item_properties.get(
            "hpCostHeavyBleeding", None
        )
        meds_cache[primary_cat][item_name]["hpCostLightBleeding"] = item_properties.get(
            "hpCostLightBleeding", None
        )
        meds_cache[primary_cat][item_name]["painkillerDuration"] = item_properties.get(
            "painkillerDuration", None
        )
        meds_cache[primary_cat][item_name]["hydrationImpact"] = item_properties.get(
            "hydrationImpact", None
        )
        meds_cache[primary_cat][item_name]["energyImpact"] = item_properties.get(
            "energyImpact", None
        )
        provisions_cache[primary_cat][item_name]["stimEffects"] = item_properties.get(
            "stimEffects", []
        )
        return True
    except Exception as e:
        print(f"Error in processing Meds: {e}")
        print(f"Problem ItemSection: {item_section}")


def process_keys(item_section):
    try:
        categories = item_section["categories"]
        primary_cat_parent = categories[0]["parent"]["name"]
        if primary_cat_parent != "Key":
            return False
        primary_cat = categories[0]["name"]
        if primary_cat not in keys_cache:
            keys_cache[primary_cat] = {}
        item_name = item_section["name"]
        if item_name not in keys_cache[primary_cat]:
            keys_cache[primary_cat][item_name] = {}
        item_shortname = item_section["shortName"]
        item_properties = item_section["name"]["properties"]
        types = item_section["types"]
        keys_cache[primary_cat][item_name]["shortName"] = item_shortname
        keys_cache[primary_cat][item_name]["types"] = types
        keys_cache[primary_cat][item_name]["dimensions"] = Dimensions(
            x=item_section.get("width", None), y=item_section.get("height", None)
        )
        keys_cache[primary_cat][item_name]["weight"] = item_section.get("weight", None)
        keys_cache[primary_cat][item_name]["uses"] = item_properties.get("uses", None)
        return True
    except Exception as e:
        print(f"Error in processing Keys: {e}")
        print(f"Problem ItemSection: {item_section}")


def process_food_drink(item_section):
    try:
        categories = item_section["categories"]
        primary_cat_parent = categories[0]["parent"]["name"]
        if primary_cat_parent != "Food and drink":
            return False
        primary_cat = categories[0]["name"]
        if primary_cat not in provisions_cache:
            provisions_cache[primary_cat] = {}
        item_name = item_section["name"]
        if item_name not in provisions_cache[primary_cat]:
            provisions_cache[primary_cat][item_name] = {}
        types = item_section["types"]
        item_shortname = item_section["shortName"]
        item_properties = item_section["name"]["properties"]
        provisions_cache[primary_cat][item_name]["shortName"] = item_shortname
        provisions_cache[primary_cat][item_name]["types"] = types
        provisions_cache[primary_cat][item_name]["dimensions"] = Dimensions(
            x=item_section.get("width", None), y=item_section.get("height", None)
        )
        provisions_cache[primary_cat][item_name]["weight"] = item_section.get(
            "weight", None
        )
        provisions_cache[primary_cat][item_name]["units"] = item_properties.get(
            "units", None
        )
        provisions_cache[primary_cat][item_name]["hydration"] = item_properties.get(
            "hydration", None
        )
        provisions_cache[primary_cat][item_name]["energy"] = item_properties.get(
            "energy", None
        )
        provisions_cache[primary_cat][item_name]["stimEffects"] = item_properties.get(
            "stimEffects", []
        )
        return True
    except Exception as e:
        print(f"Error in processing Provisions: {e}")
        print(f"Problem ItemSection: {item_section}")


def process_containers(item_section):
    try:
        categories = item_section["categories"]
        primary_cat = categories[0]["name"]
        if primary_cat != "Port. container":
            return False
        item_name = item_section["name"]
        if item_name not in containers_cache:
            containers_cache[item_name] = {}
        item_shortname = item_section["shortName"]
        types = item_section["types"]
        containers_cache[item_name]["shortName"] = item_shortname
        containers_cache[item_name]["types"] = types
        return True
    except Exception as e:
        print(f"Error in processing Containers: {e}")
        print(f"Problem ItemSection: {item_section}")


def process_barteritems(item_section):
    try:
        categories = item_section["categories"]
        primary_cat_parent = categories[0]["parent"]["name"]
        if primary_cat_parent != "Barter item":
            return False
        primary_cat = categories[0]["name"]
        if primary_cat not in barteritem_cache:
            barteritem_cache[primary_cat] = {}
        item_name = item_section["name"]
        if item_name not in barteritem_cache[primary_cat]:
            barteritem_cache[primary_cat][item_name] = {}
        item_shortname = item_section["shortName"]
        types = item_section["types"]
        barteritem_cache[primary_cat][item_name]["shortName"] = item_shortname
        barteritem_cache[primary_cat][item_name]["types"] = types
        return True
    except Exception as e:
        print(f"Error in processing Barter Items: {e}")
        print(f"Problem ItemSection: {item_section}")


def process_otheritems(item_section):
    try:
        categories = item_section["categories"]
        item_name = item_section["name"]
        if item_name not in otheritems_cache:
            otheritems_cache[item_name] = {}
        item_shortname = item_section["shortName"]
        types = item_section["types"]
        otheritems_cache[item_name]["shortName"] = item_shortname
        otheritems_cache[item_name]["types"] = types
        otheritems_cache[item_name]["categories"] = categories
        return True
    except Exception as e:
        print(f"Error in processing Other Items: {e}")
        print(f"Problem ItemSection: {item_section}")


item_filters = [
    process_ammo,
    process_ammo_containers,
    process_otheritems,
]


async def process_tarkov_item_data(data: dict[str, any]):
    items = data["items"]
    for item_section in items:
        item_name = item_section["name"]
        filtered_item = False
        for filter in item_filters:
            filtered_item = filter(item_section)
            if filtered_item:
                break
        else:
            print(f"{item_name} not Matched to Filter")


transport = AIOHTTPTransport(url="https://api.tarkov.dev/graphql")
client = Client(transport=transport, fetch_schema_from_transport=True)


async def build_api_class():
    try:
        async with client as session:
            ts = DSLSchema(client.schema)
            tarkovapi = TarkovAPI(
                schema=ts,
                item_query=dsl_gql(
                    DSLQuery(
                        ts.Query.items.select(
                            ts.Item.name,
                            ts.Item.shortName,
                            ts.Item.width,
                            ts.Item.height,
                            ts.Item.weight,
                            ts.Item.accuracyModifier,
                            ts.Item.recoilModifier,
                            ts.Item.ergonomicsModifier,
                            ts.Item.velocity,
                            ts.Item.loudness,
                            ts.Item.iconLink,
                            ts.Item.image8xLink,
                            ts.Item.types,
                            ts.Item.categories.select(
                                ts.ItemCategory.name,
                                ts.ItemCategory.parent.select(ts.ItemCategory.name),
                            ),
                            ts.Item.properties.select(
                                DSLInlineFragment()
                                .on(ts.ItemPropertiesAmmo)
                                .select(
                                    ts.ItemPropertiesAmmo.caliber,
                                    ts.ItemPropertiesAmmo.stackMaxSize,
                                    ts.ItemPropertiesAmmo.tracer,
                                    ts.ItemPropertiesAmmo.tracerColor,
                                    ts.ItemPropertiesAmmo.ammoType,
                                    ts.ItemPropertiesAmmo.projectileCount,
                                    ts.ItemPropertiesAmmo.damage,
                                    ts.ItemPropertiesAmmo.armorDamage,
                                    ts.ItemPropertiesAmmo.fragmentationChance,
                                    ts.ItemPropertiesAmmo.ricochetChance,
                                    ts.ItemPropertiesAmmo.penetrationChance,
                                    ts.ItemPropertiesAmmo.penetrationPower,
                                    ts.ItemPropertiesAmmo.accuracyModifier,
                                    ts.ItemPropertiesAmmo.recoilModifier,
                                    ts.ItemPropertiesAmmo.initialSpeed,
                                    ts.ItemPropertiesAmmo.lightBleedModifier,
                                    ts.ItemPropertiesAmmo.heavyBleedModifier,
                                    ts.ItemPropertiesAmmo.staminaBurnPerDamage,
                                ),
                            ),
                        )
                    )
                ),
            )
        return tarkovapi
    except Exception as e:
        print(f"Error in Building API Class: {e}")
        return None


"""                         DSLInlineFragment()
                                .on(ts.ItemPropertiesPreset)
                                .select(
                                    ts.ItemPropertiesPreset.baseItem.select(
                                        ts.Item.shortName
                                    ),
                                    ts.ItemPropertiesPreset.moa,
                                    ts.ItemPropertiesPreset.recoilVertical,
                                    ts.ItemPropertiesPreset.recoilHorizontal,
                                    ts.ItemPropertiesPreset.ergonomics,
                                ),
                            DSLInlineFragment()
                            .on(
                                ts.Item.ItemPropertiesWeapon
                            ).select(
                                ts.ItemPropertiesWeapon.fireRate,
                                ts.ItemPropertiesWeapon.effectiveDistance,
                                ts.ItemPropertiesWeapon.sightingRange,
                                ts.ItemPropertiesWeapon.defaultHeight,
                                ts.ItemPropertiesWeapon.defaultWidth,
                                ts.ItemPropertiesWeapon.defaultWeight,
                                ts.ItemPropertiesWeapon.defaultErgonomics,
                                ts.ItemPropertiesWeapon.defaultRecoilVertical,
                                ts.ItemPropertiesWeapon.defaultRecoilHorizontal,
                                ts.ItemPropertiesWeapon.caliber,
                                ts.ItemPropertiesWeapon.allowedAmmo.select(
                                    ts.allowedAmmo.name
                                ),
                                ts.ItemPropertiesWeapon.repairCost,
                            ),

                            DSLInlineFragment().on(
                                ts.Item.ItemPropertiesMagazine)
                            .select(
                                ts.ItemPropertiesMagazine.allowedAmmo.select(
                                    ts.allowedAmmo.name
                                ),
                                ts.ItemPropertiesMagazine.capacity,
                                ts.ItemPropertiesMagazine.ergonomics,
                                ts.ItemPropertiesMagazine.recoilModifier,
                                ts.ItemPropertiesMagazine.ammoCheckModifier,
                                ts.ItemPropertiesMagazine.loadModifier,
                                ts.ItemPropertiesMagazine.malfunctionChance,
                                ts.ItemPropertiesMagazine.slots.select(
                                    ts.slots.id, ts.slots.name, ts.slots.required
                                ),
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.Item.ItemPropertiesGrenade(
                            ts.ItemPropertiesGrenade.type,
                            ts.ItemPropertiesGrenade.fuse,
                            ts.ItemPropertiesGrenade.fragments,
                            ts.ItemPropertiesGrenade.contusionRadius,
                            ts.ItemPropertiesGrenade.minExplosionDistance,
                            ts.ItemPropertiesGrenade.maxExplosionDistance,
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.Item.ItemPropertiesMelee(
                            ts.ItemPropertiesMelee.hitRadius,
                            ts.ItemPropertiesMelee.slashDamage,
                            ts.ItemPropertiesMelee.stabDamage,
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.Item.ItemPropertiesScope(
                            ts.ItemPropertiesScope.ergonomics,
                            ts.ItemPropertiesScope.recoilModifier,
                            ts.ItemPropertiesScope.sightModes,
                            ts.ItemPropertiesScope.zoomLevels,
                            ts.ItemPropertiesScope.sightingRange,
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.Item.ItemPropertiesBarrel(
                            ts.ItemPropertiesBarrel.ergonomics,
                            ts.ItemPropertiesBarrel.recoilModifier,
                            ts.ItemPropertiesBarrel.deviationMax,
                            ts.ItemPropertiesBarrel.deviationCurve,
                            ts.ItemPropertiesBarrel.centerOfImpact,
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.Item.ItemPropertiesBarrel(
                            ts.ItemPropertiesBarrel.hitpoints,
                            ts.ItemPropertiesBarrel.maxHealPerUse,
                            ts.ItemPropertiesBarrel.useTime,
                            ts.ItemPropertiesBarrel.hpCostHeavyBleeding,
                            ts.ItemPropertiesBarrel.hpCostLightBleeding,
                            ts.ItemPropertiesBarrel.cures,
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.Item.ItemPropertiesPainkiller(
                            ts.ItemPropertiesPainkiller.painkillerDuration,
                            ts.ItemPropertiesPainkiller.cures,
                            ts.ItemPropertiesPainkiller.uses,
                            ts.ItemPropertiesPainkiller.useTime,
                            ts.ItemPropertiesPainkiller.hydrationImpact,
                            ts.ItemPropertiesPainkiller.energyImpact,
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.Item.ItemPropertiesStim(
                            ts.ItemPropertiesStim.cures,
                            ts.ItemPropertiesStim.useTime,
                            ts.ItemPropertiesStim.stimEffects.select(
                                ts.stimEffects.skillName,
                                ts.stimEffects.type,
                                ts.stimEffects.delay,
                                ts.stimEffects.chance,
                                ts.stimEffects.value,
                                ts.stimEffects.duration,
                                ts.stimEffects.percent,
                            ),
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.Item.ItemPropertiesHeadwear(
                            ts.ItemPropertiesHeadwear.Slots.select(
                                ts.Id, ts.Name, ts.Required
                            )
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.Item.ItemPropertiesGlasses(
                            ts.Class,
                            ts.BlindnessProtection,
                            ts.Material.select(ts.Name),
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.Item.ItemPropertiesHelmet.select(
                            ts.ArmorType,
                            ts.Class,
                            ts.Durability,
                            ts.RepairCost,
                            ts.TurnPenalty,
                            ts.ErgoPenalty,
                            ts.SpeedPenalty,
                            ts.Deafening,
                            ts.HeadZones,
                            ts.BlindnessProtection,
                            ts.RicochetX,
                            ts.RicochetY,
                            ts.RicochetZ,
                            ts.Material.select(
                                ts.Name,
                                ts.MinRepairDegradation,
                                ts.MaxRepairDegradation,
                                ts.MinRepairKitDegradation,
                                ts.MaxRepairKitDegradation,
                            ),
                            ts.ArmorSlots.select(ts.NameId, ts.Zones),
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.Item.ItemPropertiesBackpack.select(
                            ts.TurnPenalty,
                            ts.ErgoPenalty,
                            ts.SpeedPenalty,
                            ts.Capacity,
                            ts.Grids.select(ts.Width, ts.Height),
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.Item.ItemPropertiesArmor.select(
                            ts.ArmorType,
                            ts.Class,
                            ts.Durability,
                            ts.RepairCost,
                            ts.TurnPenalty,
                            ts.ErgoPenalty,
                            ts.SpeedPenalty,
                            ts.Material.select(
                                ts.Name,
                                ts.MinRepairDegradation,
                                ts.MaxRepairDegradation,
                                ts.MinRepairKitDegradation,
                                ts.MaxRepairKitDegradation,
                            ),
                            ts.ArmorSlots.select(ts.NameId, ts.Zones),
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.Item.ItemPropertiesChestRig.select(
                            ts.ArmorType,
                            ts.Class,
                            ts.Durability,
                            ts.RepairCost,
                            ts.TurnPenalty,
                            ts.ErgoPenalty,
                            ts.SpeedPenalty,
                            ts.Material.select(
                                ts.Name,
                                ts.MinRepairDegradation,
                                ts.MaxRepairDegradation,
                                ts.MinRepairKitDegradation,
                                ts.MaxRepairKitDegradation,
                            ),
                            ts.ArmorSlots.select(ts.NameId, ts.Zones),
                            ts.Capacity,
                            ts.Grids.select(ts.Width, ts.Height),
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.Item.ItemPropertiesContainer.select(
                            ts.Capacity, ts.Grids.select(ts.Width, ts.Height)
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.Item.ItemPropertiesFoodDrink.select(
                            ts.Units,
                            ts.Hydration,
                            ts.Energy,
                            ts.StimEffects.select(
                                ts.SkillName,
                                ts.Type,
                                ts.Delay,
                                ts.Chance,
                                ts.Value,
                                ts.Duration,
                                ts.Percent,
                            ),
                        )
                    ),
                    DSLInlineFragment().on(
                        ts.ItemPropertiesResource.select(ts.Units),
                    ),
                    DSLInlineFragment().on(
                        ts.ItemPropertiesKey.select(ts.Uses),
                    ),
                ),
            )"""


async def call_tarkov_api(query: DSLQuery):
    async with client as session:
        data = await session.execute(query)
        return data


async def start_tarkov_spy():
    tarkov_control = await controls.Control.load("tarkov_api")
    tarkov_control.number = 0
    await tarkov_control.update()
    tarkovapi = await build_api_class()
    item_data = await call_tarkov_api(tarkovapi.item_query)
    await process_tarkov_item_data(item_data)
    # await print_tarkov_caches()
    await write_caches_to_file()


### MAIN QUERY ###
"""{
  items {
    name
    shortName
    height
    width
    weight
    accuracyModifier
    recoilModifier
    ergonomicsModifier
    velocity
    loudness
    recoilModifier
    iconLink
    image8xLink
    properties {
      ... on ItemPropertiesKey {
        uses
      }
      ... on ItemPropertiesAmmo {
        caliber
        stackMaxSize
        tracer
        tracerColor
        ammoType
        projectileCount
        damage
        armorDamage
        fragmentationChance
        ricochetChance
        penetrationChance
        penetrationPower
        accuracyModifier
        recoilModifier
        initialSpeed
        lightBleedModifier
        heavyBleedModifier
        staminaBurnPerDamage
      }
      ... on ItemPropertiesStim {
        cures
        useTime
        stimEffects {
          skillName
          type
          delay
          chance
          value
          duration
          percent
        }
      }
      ... on ItemPropertiesMelee {
        hitRadius
        slashDamage
        stabDamage
      }
      ... on ItemPropertiesScope {
        ergonomics
        recoilModifier
        sightModes
        zoomLevels
        sightingRange
      }
      ... on ItemPropertiesBarrel {
        ergonomics
        recoilModifier
        deviationMax
        deviationCurve
        centerOfImpact
      }
      ... on ItemPropertiesMedKit {
        hitpoints
        maxHealPerUse
        useTime
        hpCostHeavyBleeding
        hpCostLightBleeding
        cures
      }
      ... on ItemPropertiesPreset {
        baseItem {
          shortName
        }
        moa
        recoilVertical
        recoilHorizontal
        ergonomics
      }
      ... on ItemPropertiesWeapon {
        defaultPreset {
          name
        }
        fireRate
        effectiveDistance
        sightingRange
        defaultHeight
        defaultWidth
        defaultWeight
        defaultErgonomics
        defaultRecoilVertical
        defaultRecoilHorizontal
        caliber
        allowedAmmo {
          name
        }
        repairCost
      }
      ... on ItemPropertiesGlasses {
        class
        blindnessProtection
        material {
          name
        }
      }
      ... on ItemPropertiesGrenade {
        type
        fuse
        fragments
        contusionRadius
        minExplosionDistance
        maxExplosionDistance
      }
      ... on ItemPropertiesHelmet {
        armorType
        class
        durability
        repairCost
        turnPenalty
        ergoPenalty
        speedPenalty
        deafening
        headZones
        blindnessProtection
        ricochetX
        ricochetY
        ricochetZ
        material {
          name
          minRepairDegradation
          maxRepairDegradation
          minRepairKitDegradation
          maxRepairKitDegradation
        }
        armorSlots {
          nameId
          zones
        }
      }
      ... on ItemPropertiesBackpack {
        turnPenalty
        ergoPenalty
        speedPenalty
        capacity
        grids {
          width
          height
        }
      }
      ... on ItemPropertiesArmor {
        armorType
        class
        durability
        repairCost
        turnPenalty
        ergoPenalty
        speedPenalty
        material {
          name
          minRepairDegradation
          maxRepairDegradation
          minRepairKitDegradation
          maxRepairKitDegradation
        }
        armorSlots {
          nameId
          zones
        }
      }
      ... on ItemPropertiesChestRig {
        armorType
        class
        durability
        repairCost
        turnPenalty
        ergoPenalty
        speedPenalty
        material {
          name
          minRepairDegradation
          maxRepairDegradation
          minRepairKitDegradation
          maxRepairKitDegradation
        }
        armorSlots {
          nameId
          zones
        }
        capacity
        grids {
          width
          height
        }
      }
      ... on ItemPropertiesHeadwear {
        slots {
          id
          name
          required
        }
      }
      ... on ItemPropertiesMagazine {
        allowedAmmo {
          name
        }
        capacity
        ergonomics
        recoilModifier
        ammoCheckModifier
        loadModifier
        malfunctionChance
        slots {
          id
          name
          required
        }
      }
      ... on ItemPropertiesResource {
        units
      }
      ... on ItemPropertiesContainer {
        capacity
        grids {
          width
          height
        }
      }
      ... on ItemPropertiesFoodDrink {
        units
        stimEffects {
          skillName
          type
          delay
          chance
          value
          duration
          percent
        }
      }
    }
    types
    categories {
      name
      parent {
        name
      }
    }
  }
}
"""

### CURRENT ITEM QUERY ####
"""query {
		items (name: "m855a1"){
			name
			shortName
			height
			width
			weight
			accuracyModifier
			recoilModifier
			ergonomicsModifier
			velocity
			loudness
			recoilModifier
			iconLink
			image8xLink
		
			types	
			categories{
				name
					parent{
						name
					}
			}
		
			}
	}"""


### CURRENT PRICING QUERY ###
"""buyFor
			{
				price
				currency
				vendor{
					... on TraderOffer{
						minTraderLevel
						taskUnlock{
							name
						}
					}
					name
				}
			}
			sellFor
			{
				priceRUB
				price
				vendor{
					name
				}
			}
			low24hPrice
			high24hPrice
			avg24hPrice
		changeLast48h
		changeLast48hPercent
		lastOfferCount
			bartersFor{
				requiredItems{
					item{
						name
					}
				}
				rewardItems{
					item{
						name
					}
				}
				trader{
					name
					resetTime
				}
			}
			bartersUsing{
				trader{
					name
					resetTime
				}
			}"""
