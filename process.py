#!/usr/bin/python3

import argparse
from model.log import init_logging
from model.logparser import *
from datetime import datetime
from model.util import get_datetime_from_logtime, get_datetime_from_guid
from model.config import read_config_from_yaml, Config
from model.static import Common

def get_new_time(conf: Config, ori_time: datetime) -> datetime:
   
    new_start = datetime.strptime(conf.result_info.raid_start, '%Y-%m-%d %H:%M:%S').timestamp()
    ori_start = datetime.strptime(conf.source_info.raid_time, '%Y-%m-%d %H:%M:%S').timestamp()
    time_offset = new_start - ori_start
    new_dt = ori_start + (ori_time.timestamp() - ori_start)*conf.job_config.time_factor + time_offset
    dt = datetime.fromtimestamp(new_dt)
    return dt

def process_guid(conf:Config, content):
    guids = extract_guid_from_line(content)
    MASK = 0x7fffff
    if not guids:
        return content
    repl = {}
    for guid in guids:
        items = guid.split('-')
        items[2] = str(conf.result_info.raid_server)
        items[4] = str(conf.result_info.zone_uid)

        #https://warcraft.wiki.gg/wiki/GUID
        if items[0] != 'Pet':
            ori_dt = get_datetime_from_guid(guid)
            new_dt = get_new_time(conf, ori_dt)
            
            spawnid = int(items[6],16)
            spawnid -= (spawnid & MASK)
            spawnid += (int(new_dt.timestamp()) & MASK)

            items[6] = '%010x'%(spawnid)
            items[6] = items[6].upper()
        else:
            spawnid = int(items[6],16)
            spawnid += 2
            items[6] = '%010x'%(spawnid)
            items[6] = items[6].upper()
        new_guid = '-'.join(items)
        repl[guid] = new_guid
    for k in repl:
        content = content.replace(k, repl[k])

    return content

def process_player(conf:Config, content):
    
    for player in conf.players:
        content = content.replace(player.source_guid, player.result_guid)
        content = content.replace(f"{player.source_name}-{conf.source_info.server_name}", 
                                  f"{player.result_name}-{conf.result_info.server_name}")
        # 处理EMOTE
        content = content.replace(f'"{player.source_name}"', 
                                  f'"{player.result_name}"')
    return content

def get_filter(conf: Config):
    keywords = []
    # if conf.source_info.thorim_light:
    #     keywords = ['泰坦风暴', '风暴之怒', ['UNIT_DIED', '不朽守护者']]
    if conf.job_config.faction == Common.FACTION_HORDE:
        keywords.extend(['逃命专家','生存意志','石像形态','纳鲁的赐福','影遁'])
    else:
        keywords.extend(['被遗忘者的意志'])
    if conf.job_config.is_heroic:
        keywords.append('肯瑞托的智慧')
    return lambda log: any(
        all(
            sub_keyword in log for sub_keyword in keyword
        ) if isinstance(keyword, list)
        else keyword in log for keyword in keywords
    )

def check_pre_yaml(conf: Config):
    assert conf.source_info.faction in [Common.FACTION_ALLIANCE, Common.FACTION_HORDE]
    assert conf.job_config.faction in [Common.FACTION_ALLIANCE, Common.FACTION_HORDE]
    assert conf.job_config.time_factor > 0.9 and conf.job_config.time_factor < 1.1
    assert conf.source_info.server_name
    assert conf.result_info.server_name

if __name__ == "__main__":
    init_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', default='config.yaml', type=str, help='config file')
    args = parser.parse_args()

    conf = read_config_from_yaml(args.c)

    check_pre_yaml(conf)
    time_offset = 0 
    time_start = 0
    file_key = "test"
    if len(conf.job_config.clients) > 0:
        file_key = conf.job_config.clients[0].result_name
    output_path = f'./data/log_result/WoWCombatLog-{file_key}.txt'
    enhance_map = {}
    equip_map = {}
    
    #提取需要定制装备和调整数值的表
    encounter_map = Common.get_encounter_name_to_id_map(conf.source_info.raid)
    for player in conf.job_config.clients:
        if player.enhance:
            player_enhance = {}
            for name in player.enhance:
                player_enhance[encounter_map[name]] = player.enhance[name]
            enhance_map[player.source_guid] = player_enhance
        if player.equip:
            equip_map[player.source_guid] = [player.equip, player.equip_level]

    line_filter = get_filter(conf)
    print(enhance_map)
    with open(conf.source_info.log_path, 'r', encoding='utf-8') as fin, open(output_path, 'w', encoding='utf-8') as fout:
        encounter = 0
        count = 0
        for line in fin:
            count += 1
            if count % 100000 == 0:
                print(f'processing line {count}')
            item  = log_object_factory(line)
            if not item:
                continue
            ori_dt = get_datetime_from_logtime(item.time)
            new_dt = get_new_time(conf, ori_dt)
            item.time = '%d/%d %02d:%02d:%02d.%03d'%(new_dt.month, new_dt.day, 
                                                     new_dt.hour, new_dt.minute, 
                                                     new_dt.second, new_dt.microsecond/1000)

            if isinstance(item, EncounterStartLog):
                encounter = item.encounter_id
            elif isinstance(item, EncounterEndLog):
                encounter = 0
            elif item.event in ENHANCE_EVENT:
                if item.player_id in enhance_map:
                    if encounter in enhance_map[item.player_id]:
                        item.enhance(enhance_map[item.player_id][encounter])
            elif isinstance(item, CombatantInfoLog):
                item.set_faction(conf.job_config.faction)
                if conf.job_config.is_heroic:
                    item.delete_aura(AURA_ID_KIRINTOR)
                if item.player_id in equip_map:
                    item.set_equip(equip_map[item.player_id][0])
                    print ('equip done!')
                # if conf.ori_info.thorim_light:
                #     item.delete_aura(AURA_ID_THORIM)
            elif isinstance(item, SpellCastSuccessLog):
                if item.player_id in equip_map:
                    item.set_equip_level(equip_map[item.player_id][1])
            #过滤
            if line_filter(item.content):
                continue
            #替换玩家
            item.content = process_player(conf, item.content)
            #替换阵营技能
            item.content = process_faction_spell(item.content, conf.job_config.faction)
            #调整单位的GUID
            item.content = process_guid(conf, item.content)

            fout.write(item.get_line())

    


    


