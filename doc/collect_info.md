# 玩家数据库初始化

script/AllenTargetLogger是一个简单的采集当前目标的玩家信息的插件，可用于初始化数据。

拷贝script/AllenTargetLogger目录至World of Warcraft/_classic_/interface/AddOnes/下。在设置-插件中启用该插件。启用插件后，在玩家切换目标时，若目标是玩家，会记录玩家的信息。

可以在目标服务器和目标阵营建小号跑到铁或奥格，随机选取目标。已记录的目标会在登出游戏后保存在 World of Warcraft/_classic_/WTF/Account/你的游戏id/SavedVariables/AllenTargetLogger.lua文件中。将该文件复制到./data/player_lua/AllenTargetLogger.lua。然后执行

```bash
./import_player.py
```

即可把AllenTargetLogger.lua中采集的玩家导入到数据库中，会有自动去重

也可以通过MySQL手动插入用户信息，需要对应的guid和角色名，可以是真实的也可以是伪造的