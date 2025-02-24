#!/usr/bin/python3

import argparse
from collections import defaultdict
from model.static import DBConf, Path, Common
from model import util
from model.db import DB
from model.log import init_logging
from datetime import datetime, timedelta
from model import config
import random
from typing import Dict

def process_players(conf: config.Config):
    class_count = defaultdict(int)
    class_data = {}
    start_date = util.get_cd_start_time()
    
    client_map: Dict[str, config.Player] = {}
    for client in conf.job_config.clients:
        client_map[client.source_name] = client

    for player in conf.players:
        if player.source_name in client_map:
            assert not player.is_owner
            player.is_client = True
            player.result_guid = client_map[player.source_name].result_guid
            player.result_name = client_map[player.source_name].result_name
        else:
            class_count[player.class_name] += 1

    server_code = Common.SERVER_NAME_TO_CODE[conf.result_info.server_name]

    with DB(DBConf.HOST, DBConf.USER, DBConf.PWD, DBConf.DB) as db:
        for cls in class_count:
            if class_count[cls] > 0:
                class_data[cls] = list(db.get_player_by_class(server_code, cls, start_date, class_count[cls], conf.job_config.faction))
                assert len(class_data[cls]) == class_count[cls]

    for player in conf.players:
        if not player.result_guid:
            items = class_data[player.class_name].pop()
            player.result_name = items['name']
            player.result_guid = items['guid']

def process_pet(conf: config.Config):
    for pet in conf.pets:
        offset = random.randint(1,10000)
        uid = int(pet.source_uid, 16) + offset
        pet.result_uid = '%08x'%(uid)
        pet.result_uid =  pet.result_uid.upper()


def process_raid_info(conf: config.Config):

    tplt = config.read_config_from_yaml(conf.job_config.template)
    conf.source_info = tplt.source_info
    conf.pets = tplt.pets
    conf.players = tplt.players
    conf.result_info = config.ResultInfo()

    raid_dt = None
    #有raid_instance就从中提取raid_server、zone_uid、raid_dt，否则随机生成
    if conf.job_config.raid_instance:
        items = conf.job_config.raid_instance.split('-')
        conf.result_info.raid_server = items[2]
        conf.result_info.zone_uid = items[4]
        raid_dt = util.get_datetime_from_guid(conf.job_config.raid_instance) 
    else:
        conf.result_info.raid_server = random.choice(Common.RAID_SERVERS)
        conf.result_info.zone_uid = random.randint(1, 32767)
        raid_dt = datetime.now() - timedelta(seconds=conf.source_info.duration)

    conf.result_info.raid_start = raid_dt.strftime('%Y-%m-%d %H:%M:%S')
    conf.result_info.raid_end = (raid_dt + timedelta(seconds=conf.source_info.duration)).strftime('%Y-%m-%d %H:%M:%S')

    #clients不为空，则从clients提取服务器，否则读server_name
    if len(conf.job_config.clients) > 0:
        server_code = None
        for client in conf.job_config.clients:
            server_code = util.ensure_same_value(server_code, util.get_server_from_player_guid(client.result_guid))
        conf.result_info.server_name = Common.SERVER_CODE_TO_NAME[server_code]
    else:
        assert conf.job_config.server_name in Common.SERVER_NAME_TO_CODE
        conf.result_info.server_name = conf.job_config.server_name


if __name__ == "__main__":
    init_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', default='config.yaml', type=str, help='config file')
    args = parser.parse_args()

    conf = config.read_config_from_yaml(args.c)

    process_raid_info(conf)
    process_players(conf)
    process_pet(conf)

    config.write_config_to_yaml(conf, args.c)
    