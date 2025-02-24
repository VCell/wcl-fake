#!/usr/bin/python3

from model.log import init_logging
import argparse
import yaml
import datetime
from model.static import YamlKeys,DBConf
from model.db import DB
from model.util import get_server_from_player_guid

if __name__ == "__main__":
    init_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', default='default', type=str, help='key word for process flow')
    args = parser.parse_args()
    post_path = f'./data/yaml_post/{args.k}.yaml'
    conf = None
    with open(post_path, 'r') as fp:
        conf = yaml.load(fp, Loader=yaml.FullLoader)
    t = datetime.datetime.strptime(conf[YamlKeys.START_TIME], "%Y-%m-%d %H:%M:%S.%f")
    dt = t.strftime("%Y-%m-%d")
    print(dt)
    with DB(DBConf.HOST, DBConf.USER, DBConf.PWD, DBConf.DB) as db:
        for player in conf[YamlKeys.PLAYERS]:
            if YamlKeys.IS_CLIENT in player and player[YamlKeys.IS_CLIENT]:
                db.insert_client(player[YamlKeys.NEW_NAME], player[YamlKeys.NEW_GUID], conf[YamlKeys.FACTION], 
                                 player[YamlKeys.CLASS], dt)
            else:
                db.update_player_active(player[YamlKeys.NEW_GUID], dt)

    
    
    