#!/usr/bin/python3

import argparse
from model.logparser import *

from model.static import DBConf
from model.db import DB
from model.util import get_server_from_player_guid

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', default='data/player_lua/AllenTargetLogger.lua', type=str, help='input file')
    # parser.add_argument(
    #     '-f', '--faction',
    #     choices=['Alliance', 'Horde'],  
    #     required=True,
    #     help="Choose a faction: Alliance or Horde"
    # )
    args = parser.parse_args()
    
    pattern = r'"([^"]+)"' 
    players = []

    with open(args.i, 'r', encoding='utf-8') as fin, DB(DBConf.HOST, DBConf.USER, DBConf.PWD, DBConf.DB) as db:
        for line in fin:
            match = re.search(pattern, line)
            if match:

                content = match.group(1)
                parts = content.split(' ')

                if len(parts) == 4:
                    server = get_server_from_player_guid(parts[0])
                    id = db.insert_player(parts[0], parts[1], parts[2], server, parts[3])
                    if id == None :
                        print(f'insert error: {parts[0]} {parts[1]} {parts[2]} {parts[3]}')
                    else :
                        print(f'insert sucess {parts[0]} {parts[1]} {parts[2]} {parts[3]}')
    
    
    
