#!/usr/bin/python3

import argparse
from model.logparser import *
from model import config
import re
from model import static
from model.static import Common
from model.util import get_time_string_from_guid, get_pet_uid_from_guid, ensure_same_value
import datetime
from typing import Dict

def class_identify(spell_name):
    identify_map = {
        '嫁祸诀窍': Common.CLASS_ROGUE,
        '炎爆术': Common.CLASS_MAGE,
        '复仇之怒': Common.CLASS_PALADIN,
        '圣光术': Common.CLASS_PALADIN,
        '暗影箭': Common.CLASS_WARLOCK,
        '腐蚀之种': Common.CLASS_WARLOCK,
        '英勇打击': Common.CLASS_WARRIOR,
        '爆炸射击': Common.CLASS_HUNTER,
        '暗影魔': Common.CLASS_PRIEST,
        '真言术：盾': Common.CLASS_PRIEST,
        '鲜血打击': Common.CLASS_DEATHKNIGHT,
        '冰冷触摸': Common.CLASS_DEATHKNIGHT,
        '治疗链': Common.CLASS_SHAMAN,   
        '烈焰震击': Common.CLASS_SHAMAN,
        '月火术': Common.CLASS_DRUID,
        '回春术': Common.CLASS_DRUID,
        '横扫（豹）': Common.CLASS_DRUID,
    }
    spell_name = spell_name.strip('"')
    if spell_name in identify_map:
        return identify_map[spell_name]
    return None

def calculate_duration(raid_time, log_time): 
    start_dt = datetime.datetime.strptime(raid_time, "%Y-%m-%d %H:%M:%S")
    end_dt_without_year = datetime.datetime.strptime(log_time, "%m/%d %H:%M:%S.%f")
    end_dt = end_dt_without_year.replace(year=start_dt.year)

    if end_dt < start_dt:
        end_dt = end_dt.replace(year=start_dt.year + 1)
    duration = end_dt - start_dt

    return duration

def clean_log(in_path, out_path, conf: config.Config):
    buffer = None
    encounter = None
    encounter_players = set()
    player_map: Dict[str, config.Player] = {}
    faction = ''
    raid_time = None
    log_time = None
    # thorim_light = False
    pets = set()
    log_server = None
    raid_id = None
    with open(in_path, 'r') as fin, open(out_path, 'w') as fout:
        for line in fin:

            #清洗日志
            item = log_object_factory(line)
            if isinstance(item, EncounterStartLog) and item.is_wcl_encounter():
                raid_id = ensure_same_value(raid_id, item.raid_id)
                buffer = [line]
                encounter = item.encounter_id
            elif isinstance(item, EncounterEndLog):
                #成功并是积分boss
                if item.success == '1' and encounter == item.encounter_id:
                    buffer.append(line)
                    fout.writelines(buffer)
                buffer = None
                encounter = None
            else:
                if encounter:
                    buffer.append(line)
                    log_time = item.time
            
            #提取玩家列表
            if encounter:
                guid, name, server = extract_player_from_line(line)
                if guid:
                    log_server = ensure_same_value(log_server, server)
                    if not guid in player_map:
                        player_map[guid] = config.Player(source_guid=guid, source_name=name)

                if item.event == KEY_EVENT_SPELL_CAST_SUCCESS and item.player_id in player_map:
                    class_name = class_identify(item.spell_name)

                    if class_name :
                        player_map[item.player_id].class_name = ensure_same_value(player_map[item.player_id].class_name, class_name)

                #提取owner
                if item.event == KEY_EVENT_SPELL_CAST_FAILED:
                    player_map[item.player_id].is_owner = True

                #根据guid中的时间戳提取副本初始化时间
                units = extract_guid_from_line(line)
                for unit in units:
                    unit_time = get_time_string_from_guid(unit)
                    #pet类型的unit的spawn id不是时间戳，而是和玩家一样的唯一计数，不能用于提取时间
                    if unit.startswith('Pet-'):
                        #提取pet列表
                        pets.add(get_pet_uid_from_guid(unit))
                    else:
                        if not raid_time or unit_time < raid_time:
                            raid_time = unit_time
            if item.event == KEY_EVENT_COMBATANT_INFO:
                encounter_players.add(item.player_id)
                faction = item.get_faction()
                # if item.check_aura(AURA_ID_THORIM):
                #     thorim_light = True
    player_list = []

    for id in player_map:
        print(player_map[id].source_guid, player_map[id].source_name, player_map[id].class_name)
        assert id in encounter_players
        #没通过需完善class_identify
        assert player_map[id].class_name!=None
        player_list.append(player_map[id])

    for pet in pets:
        conf.pets.append(config.Pet(source_uid=pet))

    player_list = sorted(player_list, key=lambda x:x.class_name)
    conf.players = player_list
    conf.source_info.faction = faction
    conf.source_info.raid_time = raid_time
    duration = calculate_duration(raid_time, log_time)
    conf.source_info.duration = int(duration.total_seconds())
    conf.source_info.server_name = log_server
    conf.source_info.raid = Common.RAID_CODE_TO_NAME[raid_id]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', required=True, type=str, help='input origin log file')
    args = parser.parse_args()

    dt = ''
    m =re.search(r'WoWCombatLog-(\d{4})\d{2}_\d{6}\.txt', args.i)
    if m:
        dt = m[1]
    else:
        raise ValueError('origin path format error.')

    clean_path = f'{static.Path.CLEAN_LOG_DIR}WoWCombatLog-{dt}.txt'

    conf = config.Config(source_info={})
    conf.source_info.log_path = clean_path

    clean_log(args.i, clean_path, conf)
    tpl_path = f'{static.Path.TEMPLATE_DIR}{conf.source_info.raid}_{dt}.yaml'
    config.write_config_to_yaml(conf, tpl_path) 


  

