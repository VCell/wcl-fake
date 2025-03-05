
import re
from .static import Common
import random

KEY_EVENT_ENCOUNTER_START = 'ENCOUNTER_START'
KEY_EVENT_ENCOUNTER_END = 'ENCOUNTER_END'
KEY_EVENT_COMBATANT_INFO = 'COMBATANT_INFO'
KEY_EVENT_SPELL_DAMAGE = 'SPELL_DAMAGE'
KEY_EVENT_SWING_DAMAGE = 'SWING_DAMAGE'
KEY_EVENT_SWING_DAMAGE_LANDED = 'SWING_DAMAGE_LANDED'
KEY_EVENT_SPELL_PERIODIC_DAMAGE = 'SPELL_PERIODIC_DAMAGE'
KEY_EVENT_SPELL_PERIODIC_HEAL = 'SPELL_PERIODIC_HEAL'
KEY_EVENT_SPELL_HEAL = 'SPELL_HEAL'
KEY_EVENT_SPELL_ABSORBED = 'SPELL_ABSORBED'
KEY_EVENT_SPELL_CAST_SUCCESS = 'SPELL_CAST_SUCCESS'
KEY_EVENT_SPELL_CAST_FAILED = 'SPELL_CAST_FAILED'

DAMAGE_MAX_FACTOR = 2.0

ENHANCE_EVENT = [KEY_EVENT_SPELL_DAMAGE, 
                 KEY_EVENT_SWING_DAMAGE, 
                 KEY_EVENT_SWING_DAMAGE_LANDED, 
                 KEY_EVENT_SPELL_PERIODIC_DAMAGE,
                 KEY_EVENT_SPELL_PERIODIC_HEAL,
                 KEY_EVENT_SPELL_HEAL,
                 #KEY_EVENT_SPELL_ABSORBED,
                 ]

FACTION_SPELL_LIST = [
    ['32182,"英勇"', '2825,"嗜血"'],
    ['31801,"复仇圣印"', '348704,"腐蚀圣印"'],  #圣印本身和buff
    ['42463,"复仇圣印"', '53739,"腐蚀圣印"'],   #触发伤害的技能
    ['31803,"神圣复仇"', '53742,"血之腐蚀"'],   #debuff和周期伤害
]

#物理系德莱尼光环 英雄灵气
AURA_ID_DRAENEI_1 = '6562'
#法术系德莱尼光环 英雄灵气
AURA_ID_DRAENEI_2 = '28878'
#肯瑞托智慧
AURA_ID_KIRINTOR = '464972'
#托里姆的一灯buff 风暴之怒
AURA_ID_THORIM = '402919'

random.seed(9999)

class LogItem:

    def __init__(self, time, event, content) -> None:
        self.time = time
        self.event = event
        self.content = content
        self.items = split_log_item(content)

    #默认直接用content，需要编辑items的情况需要重写函数
    def get_line(self):
        return f'{self.time}  {self.event},{self.content}\n'

# 12/19 20:00:38.332  ENCOUNTER_START,745,"掌炉者伊格尼斯",176,25,603,11
class EncounterStartLog(LogItem):
    def __init__(self, t, event, content) -> None:
        super().__init__(t, event, content)
        self.encounter_id = self.items[0]
        self.raid_id = self.items[4]

    def is_wcl_encounter(self):
        raid_name = Common.RAID_CODE_TO_NAME[self.raid_id]
        map = Common.get_encounter_id_to_name_map(raid_name)
        return self.encounter_id in map

# 12/19 20:02:30.937  ENCOUNTER_END,745,"掌炉者伊格尼斯",176,25,1
class EncounterEndLog(LogItem):
    def __init__(self, t, event, content) -> None:
        super().__init__(t, event, content)
        self.encounter_id = self.items[0]
        self.success = self.items[4]

# 12/12 16:04:41.708  COMBATANT_INFO,Player-4781-037FBDDF,1,337,338,1579,1424,787,0,0,0,749,749,749,372,372,372,327,327,327,0,0,0,18488,0,(58,0,13),(),[(46191,232,(3820,0,0),(),(41285,80,42144,80)),(45933,239,(),(),(40048,80)),(46196,232,(3810,0,0),(),(40026,80)),(0,0,(),(),()),(46194,232,(3832,0,0),(),(39998,80,40048,80)),(45455,239,(),(),(40048,80,39998,80)),(46192,232,(3719,0,0),(),(40048,80,40026,80)),(45537,252,(1147,0,0),(),(42144,80,40026,80)),(44008,226,(2326,0,0),(),(42144,80)),(46045,239,(3246,0,0),(),(39998,80,39998,80)),(211847,232,(3840,0,0),(),()),(45168,232,(3840,0,0),(),()),(45308,225,(),(),()),(230757,225,(),(),()),(46042,239,(3831,0,0),(),(40048,80)),(45620,252,(3834,0,0),(),(40026,80)),(45617,252,(),(),()),(40321,213,(),(),()),(43157,75,(),(),())],[Player-4781-053CF9BF,25898,Player-4781-04AD207A,57623,Player-4781-037FBDDF,57399,Player-4781-055A96E7,48934,Player-4781-037FBDDF,48470,Player-4781-037FBDDF,53755,Player-4781-019B6D2C,24907,Player-4781-037FBDDF,24907,Player-4781-065A5A1E,24932,Player-4781-039B4834,28878,Player-4781-037FBDDF,464972],0,0,(176,435,433,178,434,631)
class CombatantInfoLog(LogItem):

    def __init__(self, t, event, content) -> None:
        super().__init__(t, event, content)
        self.player_id = self.items[0]

    def set_faction(self, faction):
        assert faction in [Common.FACTION_ALLIANCE, Common.FACTION_HORDE]
        assert self.items[1] in ['0', '1']
        if faction == Common.FACTION_HORDE and self.items[1] == '1':
            self.items[1] = '0'
            self.delete_aura(AURA_ID_DRAENEI_1)
            self.delete_aura(AURA_ID_DRAENEI_2)
        elif faction == Common.FACTION_ALLIANCE and self.items[1] == '0':
            self.items[1] = '1'
        self.content = ','.join(self.items)

    def delete_aura(self, aura_id):   
        data = self.items[27].strip('[]').split(',')
        result = []
        for i in range(0, len(data), 2):
            provider = data[i].strip()
            aura = data[i + 1].strip()
            if aura != aura_id:
                result.extend([provider, aura])
        self.items[27] = f"[{','.join(result)}]"
        self.content = ','.join(self.items)

    def check_aura(self, aura_id):
        data = self.items[27].strip('[]').split(',')
        for i in range(0, len(data), 2):
            if aura_id == data[i + 1].strip():
                return True
        return False

    def set_equip(self, equip):
        self.items[26] = equip
        self.content = ','.join(self.items)
        
    def get_faction(self):
        if self.items[1] == '0':
            return Common.FACTION_HORDE
        else :
            return Common.FACTION_ALLIANCE


# SPELL_DAMAGE & SPELL_PERIODIC_DAMAGE

# 9/26 22:59:37.277  SPELL_DAMAGE,Player-4781-04A6182D,"超仁-狮心",0x514,0x0,Creature-0-4514-603-17544-32871-0000757664,"观察者奥尔加隆",0x10a28,0x0,51460,"骨疽",0x20,Creature-0-4514-603-17544-32871-0000757664,0000000000000000,34076343,41834998,0,0,0,-1,0,0,0,1617.55,-341.53,148,5.4731,83,143,143,-1,32,0,0,0,nil,nil,nil
# 9/26 22:59:37.303  SPELL_PERIODIC_DAMAGE,Player-4781-04BEF411,"技能正在冷却-狮心",0x514,0x0,Creature-0-4514-603-17544-32871-0000757664,"观察者奥尔加隆",0x10a28,0x0,55095,"冰霜疫病",0x10,Creature-0-4514-603-17544-32871-0000757664,0000000000000000,34072112,41834998,0,0,0,-1,0,0,0,1617.55,-341.53,148,5.4731,83,1324,901,-1,16,0,0,0,nil,nil,nil
class SpellDamageLog(LogItem):

    def __init__(self, t, event, content) -> None:
        super().__init__(t, event, content)
        self.player_id = self.items[0]

    def enhance(self, factor:float):
        if factor>DAMAGE_MAX_FACTOR:
            factor = DAMAGE_MAX_FACTOR
        self.items[27] = str(int(int(self.items[27])*factor))
        self.items[28] = str(int(int(self.items[28])*factor))
        self.content = ','.join(self.items)

#SPELL_PERIODIC_HEAL & KEY_EVENT_SPELL_HEAL
class SpellHealLog(LogItem):

    def __init__(self, t, event, content) -> None:
        super().__init__(t, event, content)
        self.player_id = self.items[0]

    def enhance(self, factor:float):
        # self.items[27] 排除吸收(血肉成灰)后的有效治疗
        # self.items[28] 原始治疗量
        # self.items[29] 过量治疗
        # self.items[30] 吸收量
        # self.items[31] 是否暴击
        assert int(self.items[27]) + int(self.items[30]) == int(self.items[28])
        heal = int(self.items[27]) 
        over_heal = int(self.items[29])
        assert heal >= over_heal
        
        valuefactor = factor
        if valuefactor>1.3:
            valuefactor = 1.3
        heal *= valuefactor
        over_heal *= valuefactor

        if over_heal == heal:
            if 0.05*(factor-1) > random.random():
                over_heal=0
        else:
            real_heal = int((heal - over_heal)*factor)
            over_heal = heal-real_heal
            if over_heal<0:
                over_heal=0
        
        self.items[27] = str(int(heal))
        self.items[28] = str(int(heal) + int(self.items[30]))
        self.items[29] = str(int(over_heal))
        self.content = ','.join(self.items)

#KEY_EVENT_SWING_DAMAGE & KEY_EVENT_SWING_DAMAGE_LANDED
class SwingDamageLog(LogItem):

    def __init__(self, t, event, content) -> None:
        super().__init__(t, event, content)
        self.player_id = self.items[0]

    def enhance(self, factor:float):
        if factor>DAMAGE_MAX_FACTOR:
            factor = DAMAGE_MAX_FACTOR
        
        self.items[24] = str(int(int(self.items[24])*factor))
        self.items[25] = str(int(int(self.items[25])*factor))
        self.content = ','.join(self.items)

# KEY_EVENT_SPELL_ABSORBED
class SpellAbsorbedLog(LogItem):

    def __init__(self, t, event, content) -> None:
        super().__init__(t, event, content)
        self.player_id = self.items[11]

    def enhance(self, factor:float):
        self.items[18] = str(int(int(self.items[18])*factor))
        self.items[19] = str(int(int(self.items[19])*factor))
        self.content = ','.join(self.items)

# SPELL_CAST_SUCCESS
class SpellCastSuccessLog(LogItem):

    def __init__(self, t, event, content) -> None:
        super().__init__(t, event, content)
        self.player_id = self.items[0]
        self.spell_name = self.items[9]
        self.spell_id = self.items[8]
        self.equip_level = self.items[26]

    def set_equip_level(self, lvl):
        self.equip_level = str(lvl)
        self.items[26] = self.equip_level
        self.content = ','.join(self.items)

# KEY_EVENT_SPELL_CAST_FAILED
class SpellCastFailedLog(LogItem):

    def __init__(self, t, event, content) -> None:
        super().__init__(t, event, content)
        self.player_id = self.items[0]

def log_object_factory(line) -> LogItem:
    m = re.match(r'^([0-9/]+ [0-9\:\.]+)  ([A-Z_]+)\,(.+)$', line)
    assert m
    time = m.group(1)
    event = m.group(2)
    content = m.group(3)
    log_classes = {
        KEY_EVENT_ENCOUNTER_START: EncounterStartLog,
        KEY_EVENT_ENCOUNTER_END: EncounterEndLog,
        KEY_EVENT_COMBATANT_INFO: CombatantInfoLog,
        KEY_EVENT_SPELL_DAMAGE: SpellDamageLog,
        KEY_EVENT_SPELL_PERIODIC_DAMAGE: SpellDamageLog,
        KEY_EVENT_SWING_DAMAGE: SwingDamageLog,
        KEY_EVENT_SWING_DAMAGE_LANDED: SwingDamageLog,
        KEY_EVENT_SPELL_PERIODIC_HEAL: SpellHealLog,
        KEY_EVENT_SPELL_HEAL: SpellHealLog,
        KEY_EVENT_SPELL_ABSORBED: SpellAbsorbedLog,
        KEY_EVENT_SPELL_CAST_SUCCESS: SpellCastSuccessLog,
        KEY_EVENT_SPELL_CAST_FAILED: SpellCastFailedLog,
    }
    log_class = log_classes.get(event, LogItem)
    return log_class(time, event, content)

# 用逗号分割日志项，但是屏蔽括号和中括号内的逗号
def split_log_item(content):

    def find_balanced_chunks(s, open_char, close_char):
        chunks = []
        stack = []
        start = None

        for i, char in enumerate(s):
            if char == open_char:
                if not stack:
                    start = i
                stack.append(char)
            elif char == close_char:
                stack.pop()
                if not stack:
                    chunks.append(s[start:i + 1])
        return chunks

    def split_respecting_brackets(s):
        result = []
        i = 0
        while i < len(s):
            if s[i] == '(':
                chunks = find_balanced_chunks(s[i:], '(', ')')
                if chunks:
                    result.append(chunks[0])
                    i += len(chunks[0])
                    continue
            elif s[i] == '[':
                chunks = find_balanced_chunks(s[i:], '[', ']')
                if chunks:
                    result.append(chunks[0])
                    i += len(chunks[0])
                    continue
            else:
                j = i
                while j < len(s) and s[j] not in ',()[]':
                    j += 1
                result.append(s[i:j].strip())
                i = j

            if i < len(s) and s[i] == ',':
                i += 1  

        return [item for item in result if item]

    return split_respecting_brackets(content)


def process_faction_spell(content, faction):
    for item in FACTION_SPELL_LIST:
        if faction == Common.FACTION_HORDE:
            content = content.replace(item[0], item[1])
        elif faction == Common.FACTION_ALLIANCE:
            content = content.replace(item[1], item[0])
    return content

def extract_player_from_line(line):
    pattern = re.compile(r'\,(Player\-\d{4}\-[0-9A-F]{8})\,\"([^"-]+)\-([^"-]+)\"')
    res = pattern.search(line)
    if res == None:
        return None, None, None 
    id, name, server =  res.groups()
    return id, name, server

def extract_guid_from_line(line):
    pattern = re.compile(r'[A-Za-z]+-\d+-\d+-\d+-\d+-\d+-[0-9A-F]+')
    result = pattern.findall(line)
    return result

