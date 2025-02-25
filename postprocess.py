#!/usr/bin/python3

from model.log import init_logging
import argparse
import yaml
from datetime import datetime
from model.static import DBConf,Path
from model.db import DB
from model.util import get_server_from_player_guid
from model import config
import shutil

if __name__ == "__main__":
    init_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', default='config.yaml', type=str, help='config file')
    args = parser.parse_args()

    conf = config.read_config_from_yaml(args.c)

    #归档配置文件
    assert conf.result_info is not None
    history_path = f'{Path.HISTORY}{conf.result_info.raid_start}.yaml'
    shutil.copy(args.c, history_path)
    print(f'归档配置文件到 {history_path}')
    dt = datetime.strptime(conf.result_info.raid_start, '%Y-%m-%d %H:%M:%S')
    dt = dt.strftime("%Y-%m-%d")

    with DB(DBConf.HOST, DBConf.USER, DBConf.PWD, DBConf.DB) as db:
        for player in conf.players:
            if player.is_client:
                db.insert_client(player.result_name, player.result_guid, conf.job_config.faction, 
                                 player.class_name, dt)
            else:
                db.update_player_active(player.result_guid, dt)

    
    
    