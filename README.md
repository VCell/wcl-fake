# wcl-fake

## 简介
将一份现有的魔兽世界战斗日志，通过替换玩家和单位的guid、修改数值和难度，来生成一份新的可提交wcl的战斗日志，从而提升指定角色的wcl评分

适用游戏版本：魔兽世界中国怀旧服wlk版本

目前支持的副本：奥杜尔普通难度、奥杜尔英雄难度（无buff）、十字军试炼普通难度

## 环境和依赖
Python 3.9.6 

MySql 5+

## 使用步骤

### 1 初始化DB

参考 [mysql](./script/mysql)

### 2 准备日志
将一份日志拷至./data/log_origin/,保持其原始文件名。例如./data/log_origin/WoWCombatLog-021325_231023.txt

然后执行clean脚本清洗日志并生成模版
```bash
./clean.py -i ./data/log_origin/WoWCombatLog-021325_231023.txt
```
以上脚本会在./data/log_clean/生成清洗日志，形如./data/log_clean/WoWCombatLog-0213.txt，会在./data/template/生成模版文件,形如./data/template/TOC_0213.yaml。

### 3 采集团队成员的信息
所要生成的的战斗日志的团队成员由两部分组成：要提升wcl分的目标角色，和从玩家库里自动匹配的角色。我们需要这两种角色的名字、guid、职业

**获取目标角色的信息：**

登录游戏后，在聊天窗口输入:
```bash
/dump UnitGUID("player")
```
之后在聊天窗口会获得形如Player-0000-00000000的显示，即guid。

**自动匹配的角色信息**

会自动在数据库中匹配和目标角色的服务器、阵营相同，职业和模版匹配的角色。

数据库中的角色可以通过插件采集 [采集插件](./doc/collect_info.md)

### 4 获取副本ID（可选）

可通过让任意没CD的角色进本，采集任意一个npc的guid并在配置文件中填写，来让改分脚本使用实际的副本zone uid，来提升战斗记录的可信度。若不填写该项，脚本会自动生成zone uid，这样该记录的被ban可能性略有提高。

让任意无cd角色，重置全部副本后进本，选中任意npc为目标后，输入/dump UnitGUID("target")或编辑成宏点击。之后在对话框中会由类似 Creature-0-4526-649-18798-34816-00002F0145 的显示，记录下来。

### 5 填写配置文件

创建一个yaml配置文件来填写上述过程获得的信息。例如[example.yaml](./doc/example.yaml)

### 6 执行脚本

```bash
./preprocess.py -c default.yaml
./process.py -c default.yaml
./postprocess.py -c default.yaml
```

preprocess.py会根据模版在default.yaml中填充源日志信息，结果日志信息；并从数据库中匹配玩家信息，填充玩家列表和宠物列表

process.py会根据default.yaml中的信息替换日志内容并生成新的日志

postprocess.py会归档yaml，在数据库中更新背景玩家的cd情况，记录目标玩家的信息

### 7 完成并上传

日志路径在./data/log_result/下，通过wcl客户端进行上传即可

## 关于封禁的注意事项

wcl会根据日志中 SPELL_CAST_FAILED 事件来判断日志的owner，然后自动绑定owner角色和上传wcl的账号。而wcl发现伪造日志时，只会ban上传wcl账号绑定的角色。因此，上传伪造日志的wcl账号不能上传真实战斗记录，并且owner的角色信息尽量使用伪造的。

上传日志尽量使用不同的wcl账号和不同的ip。

尽量避免团队中出现对应职业前100名的战绩。

尽量使用真实的副本id