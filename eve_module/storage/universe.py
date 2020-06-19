from alento_bot import StorageManager, cache_transformer
from eve_module.storage.eve_config import EVEConfig
from pathlib import Path
import logging
import typing
import yaml
import os


logger = logging.getLogger("main_bot")


class RegionData:
    def __init__(self, path: str = None, state: dict = None, name: str = "Missing Name"):
        self.constellations: typing.Dict[str, ConstellationData] = dict()
        self.name: str = name

        self.name_id: int = 0
        self.id: int = 0

        if path:
            self.load_from_path(path)
        elif state:
            self.from_staticdata(state)

    def from_staticdata(self, state: dict):
        self.name_id = state.get("nameID", 0)
        self.id = state.get("regionID", 0)

    def load_from_path(self, path: str):
        file = open(path, "r")
        static_state = yaml.safe_load(file)
        file.close()
        self.from_staticdata(static_state)


class ConstellationData:
    def __init__(self, path: str = None, state: dict = None, region: int = 0):
        self.region: int = region
        self.solar_systems: typing.Dict[str, SolarSystemData] = dict()

        self.name_id: int = 0

        if path:
            self.load_from_path(path)
        elif state:
            self.from_staticdata(state)

    def from_staticdata(self, state: dict):
        self.name_id = state.get("nameID", 0)

    def load_from_path(self, path: str):
        file = open(path, "r")
        static_data = yaml.safe_load(file)
        file.close()
        self.from_staticdata(static_data)


class SolarSystemData:
    def __init__(self, path: str = None, state: dict = None, name: str = "Missing Name", region: int = 0,
                 constellation: int = 0):
        self.region: int = region
        self.constellation: int = constellation
        self.name: str = name
        self.planets: typing.Dict[int, PlanetData] = dict()

        self.name_id: int = 0
        self.id: int = 0
        if path:
            self.load_from_path(path)
        elif state:
            self.from_staticdata(state)

    def from_staticdata(self, state: dict):
        self.name_id = state.get("solarSystemNameID", 0)
        self.id = state.get("solarSystemID", 0)
        for planet_id in state.get("planets", dict()):
            self.planets[planet_id] = PlanetData()

    def load_from_path(self, path: str):
        file = open(path, "r")
        static_data = yaml.safe_load(file)
        file.close()
        self.from_staticdata(static_data)


class PlanetData:
    def __init__(self, state: dict = None, solar_system_id: int = 0):
        self.solar_system: int = solar_system_id
        self.index: int = 0

        if state:
            self.from_state(state)

    def from_state(self, state: dict):
        self.index = state.get("celestialIndex", 0)


class UniverseStorage:
    def __init__(self, storage: StorageManager, eve_config: EVEConfig):
        self.storage: StorageManager = storage
        self.eve_config = eve_config
        self.locations = dict()
        # noinspection PyArgumentList
        self.lite_cache = EVEUniverseLiteCache(self.storage.config)
        self.storage.caches.register_cache(self.lite_cache, "eve_universe_lite_cache")

        self.regions: typing.Dict[str, RegionData] = dict()
        self.constellations: typing.Dict[str, ConstellationData] = dict()
        self.solar_systems: typing.Dict[str, SolarSystemData] = dict()

    def load(self):
        if not self.lite_cache.loaded():
            self.populate_lite_cache()

    def populate_lite_cache(self):
        logger.info("Loading lite location cache from SDE, this may take some time.")
        logger.debug("Loading location data...")
        self.populate_locations_lite_cache()
        logger.debug("Loading location names...")
        self.populate_names_lite_cache()
        self.lite_cache.save()
        logger.info("Finished populating lite location cache. Updates to the SDE may require deleting this cache.")

    def populate_locations_lite_cache(self):
        base_path = f"{self.eve_config.sde_location}/fsd/universe"
        for space_category in get_folders_in_path(base_path):
            logger.debug(f"Reading space category {space_category}")
            for region_name in get_folders_in_path(f"{base_path}/{space_category}"):
                logger.debug(f"Reading region {space_category}/{region_name}")
                file = open(f"{base_path}/{space_category}/{region_name}/region.staticdata", "r")
                raw_data = yaml.safe_load(file)
                file.close()
                self.lite_cache.locations[raw_data["regionID"]] = f"fsd/universe/{space_category}/{region_name}/region.staticdata"
                for constellation_name in get_folders_in_path(f"{base_path}/{space_category}/{region_name}"):
                    # file = open(f"{base_path}/{space_category}/{region_name}/{constellation_name}/"
                    #             f"constellation.staticdata", "r")
                    # raw_data = yaml.safe_load(file)
                    # file.close()
                    # self.lite_cache.locations[raw_data[""]]
                    for solarsystem_name in get_folders_in_path(
                            f"{base_path}/{space_category}/{region_name}/{constellation_name}"):
                        file = open(
                            f"{base_path}/{space_category}/{region_name}/{constellation_name}/{solarsystem_name}/"
                            f"solarsystem.staticdata", "r")
                        raw_data = yaml.safe_load(file)
                        file.close()
                        self.lite_cache.locations[raw_data["solarSystemID"]] = \
                            f"fsd/universe/{space_category}/{region_name}/{constellation_name}/{solarsystem_name}" \
                            f"/solarsystem.staticdata"

    def populate_names_lite_cache(self):
        file = open(f"{self.eve_config.sde_location}/bsd/invUniqueNames.yaml", "r")
        raw_data = yaml.safe_load(file)
        file.close()

        for name_data in raw_data:
            if name_data["itemID"] in self.lite_cache.locations:
                self.lite_cache.names[name_data["itemName"]] = name_data["itemID"]

    def get_region(self, region_name, is_id: bool = False) -> typing.Optional[RegionData]:
        if is_id:
            region_id = region_name
        else:
            region_id = self.lite_cache.get_id(region_name)
        if region_id and self.lite_cache.locations[region_id].endswith("region.staticdata"):
            if region_id in self.locations:
                return self.locations[region_id]
            else:
                # if location_id and self.lite_cache.locations[location_id].endswith("region.staticdata"):
                file_path = self.lite_cache.locations[region_id]
                region_data = RegionData(path=f"{self.eve_config.sde_location}/{file_path}",
                                         name=self.lite_cache.get_name(region_id))
                self.locations[region_id] = region_data
                return self.locations[region_id]
        else:
            return None

    # def get_constellation(self, constellation_name: str):
    #     if constellation_name.lower() in self.constellations:
    #         return self.constellations[constellation_name.lower()]
    #     else:
    #         # base_folder = "{}/fsd/universe/eve".format(self.eve_config.sde_folder_name)
    #         base_folder = f"{self.eve_config.sde_location}/fsd/universe/eve"
    #         regions = get_folders_in_path(base_folder)
    #         for region in regions:
    #             # region_path = "{}/{}".format(base_folder, region)
    #             region_path = f"{base_folder}/{region}"
    #             constellations = get_folders_in_path(region_path)
    #             for constellation in constellations:
    #                 if constellation_name.lower() == constellation.lower():
    #                     region_data = self.get_region(region)
    #                     if region_data:
    #                         # logger.debug("Adding constellation {} to cache.".format(constellation.lower()))
    #                         logger.debug(f"Adding constellation {constellation.lower()} to cache.")
    #                         # constellation_path = "{}/{}/constellation.staticdata".format(region_path, constellation)
    #                         constellation_path = f"{region_path}/{constellation}/constellation.staticdata"
    #                         region_data.constellations[constellation.lower()] = ConstellationData(
    #                             path=constellation_path, region=region)
    #                         self.constellations[constellation.lower()] = region_data.constellations[constellation.lower()]
    #                         return self.constellations[constellation.lower()]
    #                     else:
    #                         # logger.error("Constellation {} should be under region {}, but was unable to fetch from "
    #                         #              "cache?".format(constellation, region))
    #                         logger.error(f"Constellation {constellation.lower()} should be under region "
    #                                      f"{region.lower()}, but was unable to fetch from cache?")
    #
    # def get_solar_system(self, solar_system_name: str):
    #     if solar_system_name.lower() in self.solar_systems:
    #         return self.solar_systems[solar_system_name.lower()]
    #     else:
    #         # base_folder = "{}/fsd/universe/eve".format(self._config.sde_folder_name)
    #         base_folder = f"{self.eve_config.sde_location}/fsd/universe/eve"
    #         for region in get_folders_in_path(base_folder):
    #             for constellation in get_folders_in_path("{}/{}".format(base_folder, region)):
    #                 # for solar_system in get_folders_in_path("{}/{}/{}".format(base_folder, region, constellation)):
    #                 for solar_system in get_folders_in_path(f"{base_folder}/{region}/{constellation}"):
    #                     if solar_system.lower() == solar_system_name.lower():
    #                         constellation_data = self.get_constellation(constellation)
    #                         if constellation_data:
    #                             logger.debug("Adding solar system {} to cache.".format(solar_system.lower()))
    #                             # solar_system_path = "{}/{}/{}/{}/solarsystem.staticdata".format(base_folder, region,
    #                             #                                                                 constellation,
    #                             #                                                                 solar_system)
    #                             solar_system_path = f"{base_folder}/{region}/{constellation}/{solar_system}/" \
    #                                                 f"solarsystem.staticdata"
    #                             constellation_data.solar_systems[solar_system.lower()] = SolarSystemData(
    #                                 path=solar_system_path, region=constellation_data.region,
    #                                 constellation=constellation, name=solar_system)
    #                             self.solar_systems[solar_system.lower()] = constellation_data.solar_systems[solar_system.lower()]
    #                             return self.solar_systems[solar_system.lower()]
    #                         else:
    #                             # logger.error("Constellation {} should have {} as solar system, but the constellation "
    #                             #              "was unable to be fetched from cache?".format(constellation.lower(),
    #                             #                                                            solar_system.lower()))
    #                             logger.error(f"Constellation {constellation.lower()} should have {solar_system.lower()}"
    #                                          f" as solar system, but the constellation was unable to be fetched from "
    #                                          f"cache?")

    # def get_any(self, any_name: str):
    #     any_data = self.get_region(any_name)
    #     if any_data:
    #         return any_data
    #     any_data = self.get_constellation(any_name)
    #     if any_data:
    #         return any_data
    #     any_data = self.get_solar_system(any_name)
    #     if any_data:
    #         return any_data
    #     return None
    def get_any(self, location_name: str):
        location_id = self.lite_cache.get_id(location_name)
        if location_id:
            if location_id in self.locations:
                return self.locations[location_id]
            else:
                file_path = self.lite_cache.locations[location_id]
                if self.lite_cache.locations[location_id].endswith("region.staticdata"):
                    location_data = RegionData(path=f"{self.eve_config.sde_location}/{file_path}",
                                               name=self.lite_cache.get_name(location_id))
                elif file_path.endswith("solarsystem.staticdata"):
                    region_id = self.lite_cache.get_id(file_path.split("/")[3])
                    location_data = SolarSystemData(path=f"{self.eve_config.sde_location}/{file_path}",
                                                    name=self.lite_cache.get_name(location_id), region=region_id)
                else:
                    logger.warning("Path doesn't end with solarsystem.staticdata or region.staticdata. "
                                   "Add proper support or put a stop to this! Assuming solar system.")
                    region_id = self.lite_cache.get_id(file_path.split("/")[3])
                    location_data = SolarSystemData(path=f"{self.eve_config.sde_location}/{file_path}",
                                                    name=self.lite_cache.get_name(location_id), region=region_id)
                self.locations[location_id] = location_data
                return self.locations[location_id]
        else:
            return None


@cache_transformer(name="eve_universe_lite_cache", save_on_exit=False)
class EVEUniverseLiteCache:
    def __init__(self):
        self.locations: typing.Dict[int, str] = dict()
        self.names: typing.Dict[str, int] = dict()

    def get_id(self, location_name: str) -> typing.Optional[int]:
        for key_name in self.names:
            if location_name.lower() == key_name.lower() or location_name.lower() == key_name.replace(" ", "").lower():
                return self.names[key_name]
        return None

    def get_name(self, location_id: int) -> typing.Optional[str]:
        for name, loc_id in self.names.items():
            if location_id == loc_id:
                return name
        return None


def get_folders_in_path(path: str) -> typing.Set[str]:
    output = set()
    for folder in os.listdir(path):
        if Path(f"{path}/{folder}").is_dir():
            output.add(folder)
    return output
