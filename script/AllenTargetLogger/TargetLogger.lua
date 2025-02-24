-- 初始化 SavedVariables 表
TargetLoggerData = TargetLoggerData or {}

-- 添加事件监听框架
local frame = CreateFrame("Frame")

local CLASS_ENGLISH_NAMES = {
    ["PALADIN"] = "Paladin",
    ["PRIEST"] = "Priest",
    ["WARLOCK"] = "Warlock",
    ["WARRIOR"] = "Warrior",
    ["HUNTER"] = "Hunter",
    ["SHAMAN"] = "Shaman",
    ["MAGE"] = "Mage",
    ["ROGUE"] = "Rogue",
    ["DRUID"] = "Druid",
    ["DEATHKNIGHT"] = "DeathKnight",
}

-- 工具函数：生成字符串记录
local function CreateLogEntry(guid, name, class, faction)
    return string.format("%s %s %s", guid, name, class, faction)
end

-- 工具函数：记录日志到数组
local function LogPlayerInfo(guid, name, class, faction)
    local logEntry = CreateLogEntry(guid, name, class, faction)

    -- 检查是否已经存在相同的记录，避免重复
    for _, entry in ipairs(TargetLoggerData) do
        if entry == logEntry then
            print(string.format("玩家已记录：%s", logEntry))
            return
        end
    end

    -- 添加新记录
    table.insert(TargetLoggerData, logEntry)
    print(string.format("记录玩家：%s", logEntry))
end

-- 事件处理函数
local function OnEvent(self, event, ...)
    if event == "PLAYER_TARGET_CHANGED" then
        -- 获取当前目标的信息
        if UnitIsPlayer("target") and UnitFactionGroup("target") == UnitFactionGroup("player") then
            local name = UnitName("target") -- 获取名字
            local _, classID = UnitClass("target") -- 获取职业
            local guid = UnitGUID("target") -- 获取 GUID
            local faction = UnitFactionGroup("target") 
            if name and classID and guid then
                -- 将职业 ID 转换为英文职业名
                local englishClass = CLASS_ENGLISH_NAMES[classID]
                if englishClass then
                    LogPlayerInfo(guid, name, englishClass, faction)
                else
                    print("未知职业 ID: " .. tostring(classID))
                end
            end
        end
    end
end

-- 注册事件
frame:RegisterEvent("PLAYER_TARGET_CHANGED")

-- 设置事件处理函数
frame:SetScript("OnEvent", OnEvent)

-- 插件加载时的消息
print("TargetLogger 已加载：将记录目标为己方玩家的信息。")
