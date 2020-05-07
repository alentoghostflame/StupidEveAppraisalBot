from storage_module.formats.config_storage import ConfigData
import logging
import typing
import yaml
import os


logger = logging.getLogger("Main")


class UniverseStorage:
    def __init__(self, config: ConfigData):
        self._config: ConfigData = config
        self.abyssal: dict = dict()
        self.eve: EveStorage = EveStorage(self._config)
        self.penalty: dict = dict()
        self.wormhole: dict = dict()


class EveStorage:
    def __init__(self, config: ConfigData):
        self._config = config
        self.regions: typing.Dict[str, RegionData] = dict()
        self.constellations: typing.Dict[str, ConstellationData] = dict()
        self.solar_systems: typing.Dict[str, SolarSystemData] = dict()

    def get_region(self, region_name: str):
        if region_name.lower() in self.regions:
            return self.regions[region_name.lower()]
        else:
            base_folder = "{}/fsd/universe/eve".format(self._config.sde_folder_name)
            regions = get_folders_in_path(base_folder)
            for region in regions:
                if region_name.lower() == region.lower():
                    logger.debug("Adding region {} to cache.".format(region.lower()))
                    region_path = "{}/{}/region.staticdata".format(base_folder, region)
                    region_data = RegionData(path=region_path, name=region)
                    self.regions[region.lower()] = region_data
                    return self.regions[region.lower()]
            return None

    def get_constellation(self, constellation_name: str):
        if constellation_name.lower() in self.constellations:
            return self.constellations[constellation_name.lower()]
        else:
            base_folder = "{}/fsd/universe/eve".format(self._config.sde_folder_name)
            regions = get_folders_in_path(base_folder)
            for region in regions:
                region_path = "{}/{}".format(base_folder, region)
                constellations = get_folders_in_path(region_path)
                for constellation in constellations:
                    if constellation_name.lower() == constellation.lower():
                        region_data = self.get_region(region)
                        if region_data:
                            logger.debug("Adding constellation {} to cache.".format(constellation.lower()))
                            constellation_path = "{}/{}/constellation.staticdata".format(region_path, constellation)
                            region_data.constellations[constellation.lower()] = ConstellationData(
                                path=constellation_path, region=region)
                            self.constellations[constellation.lower()] = region_data.constellations[constellation.lower()]
                            return self.constellations[constellation.lower()]
                        else:
                            logger.error("Constellation {} should be under region {}, but was unable to fetch from "
                                         "cache?".format(constellation, region))

    def get_solar_system(self, solar_system_name: str):
        if solar_system_name.lower() in self.solar_systems:
            return self.solar_systems[solar_system_name.lower()]
        else:
            base_folder = "{}/fsd/universe/eve".format(self._config.sde_folder_name)
            for region in get_folders_in_path(base_folder):
                for constellation in get_folders_in_path("{}/{}".format(base_folder, region)):
                    for solar_system in get_folders_in_path("{}/{}/{}".format(base_folder, region, constellation)):
                        if solar_system.lower() == solar_system_name.lower():
                            constellation_data = self.get_constellation(constellation)
                            if constellation_data:
                                logger.debug("Adding solar system {} to cache.".format(solar_system.lower()))
                                solar_system_path = "{}/{}/{}/{}/solarsystem.staticdata".format(base_folder, region,
                                                                                                constellation,
                                                                                                solar_system)
                                constellation_data.solar_systems[solar_system.lower()] = SolarSystemData(
                                    path=solar_system_path, region=constellation_data.region,
                                    constellation=constellation, name=solar_system)
                                self.solar_systems[solar_system.lower()] = constellation_data.solar_systems[solar_system.lower()]
                                return self.solar_systems[solar_system.lower()]
                            else:
                                logger.error("Constellation {} should have {} as solar system, but the constellation "
                                             "was unable to be fetched from cache?".format(constellation.lower(),
                                                                                           solar_system.lower()))

    def get_any(self, any_name: str):
        any_data = self.get_region(any_name)
        if any_data:
            return any_data
        any_data = self.get_constellation(any_name)
        if any_data:
            return any_data
        any_data = self.get_solar_system(any_name)
        if any_data:
            return any_data
        return None


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
    def __init__(self, path: str = None, state: dict = None, region: str = "Missing Region"):
        self.region: str = region
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
    def __init__(self, path: str = None, state: dict = None, name: str = "Missing Name", region: str = "Missing Region",
                 constellation: str = "Missing Constellation"):
        self.region: str = region
        self.constellation: str = constellation
        self.name: str = name

        self.name_id: int = 0
        self.id: int = 0
        if path:
            self.load_from_path(path)
        elif state:
            self.from_staticdata(state)

    def from_staticdata(self, state: dict):
        self.name_id = state.get("solarSystemNameID", 0)
        self.id = state.get("solarSystemID", 0)

    def load_from_path(self, path: str):
        file = open(path, "r")
        static_data = yaml.safe_load(file)
        file.close()
        self.from_staticdata(static_data)


def get_folders_in_path(path: str) -> typing.Set[str]:
    output = set()
    for folder in os.listdir(path):
        if os.path.isdir("{}/{}".format(path, folder)):
            output.add(folder)
    return output
