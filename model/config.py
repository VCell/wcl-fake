from typing import List, Optional, Dict
import yaml

class BaseModel:
    def to_dict(self) -> dict:
        """通用的 to_dict 方法，是对象的话调用其to_dict，否则直接用vars"""
        result = {}
        for key, value in vars(self).items():
            if value is None:
                continue
            if isinstance(value, BaseModel):  # 处理嵌套模型
                result[key] = value.to_dict()
            elif isinstance(value, list):  # 处理列表中的嵌套模型
                result[key] = [
                    item.to_dict() if isinstance(item, BaseModel) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

class Player(BaseModel):
    def __init__(self, class_name: Optional[str] = None,
                 source_guid: Optional[str] = None, source_name: Optional[str] = None,
                 result_guid: Optional[str] = None, result_name: Optional[str] = None,
                 is_client: Optional[bool] = None, is_owner: Optional[bool] = None, 
                 equip: Optional[str] = None, equip_level: Optional[str] = None,
                 enhance: Optional[Dict[str, float]] = None):
        self.class_name = class_name
        self.result_guid = result_guid
        self.result_name = result_name
        self.source_guid = source_guid
        self.source_name = source_name
        self.is_client = is_client
        self.is_owner = is_owner
        self.equip = equip
        self.equip_level = equip_level
        self.enhance = enhance


class JobConfig(BaseModel):
    def __init__(self, template: str, faction: str, 
                 time_factor: float=1.0, is_heroic: bool = False,
                 raid_instance: Optional[str] = None, clients: List = [],
                 server_name: Optional[str] = None):
        self.template = template
        self.faction = faction
        self.time_factor = time_factor
        self.is_heroic = is_heroic
        self.raid_instance = raid_instance
        self.clients = [Player(**player) for player in clients]
        self.server_name = server_name

class ResultInfo(BaseModel):
    def __init__(self, raid_server: Optional[str] = None,
                 raid_start: Optional[str] = None, raid_end: Optional[str] = None,
                 server_name: Optional[str] = None, zone_uid: Optional[str] = None, 
                 ):
        self.raid_server = raid_server
        self.raid_start = raid_start
        self.raid_end = raid_end
        self.server_name = server_name
        self.zone_uid = zone_uid

class SourceInfo(BaseModel):
    def __init__(self, log_path: Optional[str] = None,
                 duration: Optional[int] = None, faction: Optional[str] = None,
                server_name: Optional[str] = None, raid_time: Optional[str] = None, 
                raid: Optional[str] = None,
                ):
        self.log_path = log_path
        self.duration = duration
        self.faction = faction
        self.server_name = server_name
        self.raid_time = raid_time
        self.raid = raid

class Pet(BaseModel):
    def __init__(self, source_uid: Optional[str] = None, result_uid: Optional[str] = None):
        self.source_uid = source_uid
        self.result_uid = result_uid

class Config(BaseModel):
    def __init__(self, job_config: Optional[Dict] = None, raid_name: Optional[str] = None,
                 source_info: Optional[Dict] = None, result_info: Optional[Dict] = None,
                 pets: Optional[List] = [], players: Optional[List] = []):
        self.job_config = JobConfig(**job_config) if job_config!=None else None
        self.source_info = SourceInfo(**source_info)  if source_info!=None else None
        self.result_info = ResultInfo(**result_info)  if result_info!=None else None
        self.players = [Player(**player) for player in players]
        self.pets = [Pet(**pet) for pet in pets]
        self.raid_name = raid_name


# Example function to write Config object to YAML file
def write_config_to_yaml(config: Config, yaml_file: str):
    with open(yaml_file, 'w') as file:
        yaml.dump(config.to_dict(), file, default_flow_style=False, encoding='utf-8', allow_unicode=True)

# Function to read Config object from YAML file
def read_config_from_yaml(yaml_file: str) -> Config:
    with open(yaml_file, 'r') as file:
        yaml_dict = yaml.safe_load(file)
    return Config(**yaml_dict)

# Example usage
# config = parse_config(yaml_data)
# write_config_to_yaml(config, 'output.yaml')
