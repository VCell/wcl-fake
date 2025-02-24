from typing import Dict

class Path:
    TEMPLATE_DIR = 'data/template/'
    CLEAN_LOG_DIR = 'data/log_clean/'
    PLAYER_LUA_FILE = 'data/player_lua/AllenTargetLogger.lua'
    PRE_YAML_DIR = 'data/yaml_pre/'
    POST_YAML_DIR = 'data/yaml_post/'

class Common:
    FACTION_HORDE = 'Horde'
    FACTION_ALLIANCE = 'Alliance'

    CLASS_PALADIN = 'Paladin'
    CLASS_SHAMAN = 'Shaman'
    CLASS_PRIEST = 'Priest'
    CLASS_WARLOCK = 'Warlock'
    CLASS_WARRIOR = 'Warrior'
    CLASS_HUNTER = 'Hunter'
    CLASS_ROGUE = 'Rogue'
    CLASS_MAGE = 'Mage'
    CLASS_DRUID = 'Druid'
    CLASS_DEATHKNIGHT = 'DeathKnight'

    ALL_CLASS = [
        CLASS_PALADIN,
        CLASS_PRIEST,
        CLASS_WARLOCK,
        CLASS_WARRIOR,
        CLASS_HUNTER,
        CLASS_SHAMAN,
        CLASS_ROGUE,
        CLASS_MAGE,
        CLASS_DRUID,
        CLASS_DEATHKNIGHT,
    ]

    RAID_SERVERS = [
        '4502','4503','4504','4505',
        '4514','4515','4516','4517',
        '4525','4526','4527',
        '4536','4537','4538','4539',
        '4887','4888','4889',
        '4890','4892','4893','4894',
        '4982',
        '4993','4994','4996','4997','4999',
        '5002',
    ]

    SERVER_CODE_TO_NAME = {
        '4499': '埃提耶什',
        '4500': '龙之召唤',
        '4501': '加丁',
        '4509': '哈霍兰',
        '4532': '范克瑞斯',
        '4533': '维希度斯',
        '4534': '帕奇维克',
        '4535': '比格沃斯',
        '4707': '霜语',
        '4712': '比斯巨兽',
        '4770': '萨弗拉斯',
        '4774': '奥金斧',
        '4777': '震地者',
        '4778': '祈福',
        '4780': '觅心者',
        '4781': '狮心',
        '4786': '卓越',
        '4789': '秩序之源',
        '4791': '碧空之歌',
        '4819': '席瓦莱恩',
        '4820': '火锤',
        '4827': '无畏',
        '4829': '安娜丝塔丽',
        '4913': '寒冰之王',
        '4920': '龙牙',
        '4940': '巫妖王',
        '4941': '银色北伐军',
        '4942': '吉安娜',
        '4943': '死亡猎手',
        '4945': '红玉圣殿',
    }

    SERVER_NAME_TO_CODE = {v: k for k, v in SERVER_CODE_TO_NAME.items()}

    RAID_NAME_TOC = 'TOC'
    RAID_NAME_ULD = 'ULD'

    RAID_CODE_TO_NAME = {
        '649': RAID_NAME_TOC,
        '603': RAID_NAME_ULD,
    }
    ENCOUNTER_MAP = {
        RAID_NAME_TOC: {
            'NorthrendBeasts': '629',
            'Jaraxxus': '633',
            # 'FactionChampions': '637',
            'Twins': '641',
            'Anubarak': '645',
        },
        RAID_NAME_ULD: {
            'Ignis': '745',
            'Razorscale': '746',
            'XT002': '747',
            'Council': '748',
            'Kologarn': '749',
            'Auriaya': '750',
            'Thorim': '752',
            'Mimiron': '754',
            'YoggSaron': '756',
            'Algalon': '757',
        },
    }

    @staticmethod
    def get_encounter_id_to_name_map(raid_name:str) -> Dict[str,str]:
        encounter_map = Common.ENCOUNTER_MAP[raid_name]
        map = {v: k for k, v in encounter_map.items()}
        return map
    
    @staticmethod
    def get_encounter_name_to_id_map(raid_name:str) -> Dict[str,str]:
        return Common.ENCOUNTER_MAP[raid_name]

class DBConf:
    USER = 'wcl_user'
    PWD = 'wcl_password'
    DB = 'wcl_db'
    HOST = 'localhost'
