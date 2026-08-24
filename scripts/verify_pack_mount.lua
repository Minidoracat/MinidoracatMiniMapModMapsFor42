-- 掛載驗收（離線）：用主 MOD 的「真實」collectPyramids／passesMapDir／resolveMapDirByMod／
-- orderByMapPriority／registerMaps 程式碼，餵本包的真實註冊表、真實 minimap 目錄檔案，
-- 驗證每張圖只在該地圖 MOD 啟用時掛載、互斥變體各自掛對、alias 去重、優先序 identity
-- 全數解析。補上「靜態驗證（verify_mod）」與「進遊戲點擊驗收」之間的空隙：GUI 一次只
-- 能看一張圖，這裡一次覆蓋全部註冊條目。新增/移除地圖後必跑。
--
-- 用法（cwd＝本 repo 根）：lua scripts/verify_pack_mount.lua [主MOD的MinidoracatMiniMap.lua]
local HOST = arg[1] or "../MinidoracatMiniMapFor42/MOD/MinidoracatMiniMapFor42/Contents/mods/"
    .. "MinidoracatMiniMapFor42/42/media/lua/client/MinidoracatMiniMap.lua"
local PACK_ROOT = "MOD/MinidoracatMiniMapModMapsFor42/Contents/mods/"
    .. "MinidoracatMiniMapModMapsFor42/42/"
local PACK_LUA = PACK_ROOT .. "media/lua/client/MinidoracatMiniMapModMaps.lua"
local MINIMAP_DIR = PACK_ROOT .. "media/minimap/"
local PACK_ID = "MinidoracatMiniMapModMapsFor42"

-- 1) 地圖包真實註冊表：提供 API stub 讓它自己註冊進來
local entries, owner
MinidoracatMiniMapAPI = { registerMaps = function(o, list) owner, entries = o, list end }
assert(loadfile(PACK_LUA))()
assert(entries and owner == PACK_ID, "抽不到地圖包註冊表")

-- 2) zipFiles＝真實檔案系統存在性（不是假資料）
local zipFiles, zipCount = {}, 0
for _, e in ipairs(entries) do
    local key = PACK_ID .. "|" .. e.zip
    if not zipFiles[key] then
        local fh = io.open(MINIMAP_DIR .. e.zip, "rb")
        assert(fh, "註冊表指名但檔案不存在：" .. e.zip)
        fh:close()
        zipFiles[key], zipCount = true, zipCount + 1
    end
end

-- 3) 主 MOD 真實程式碼區段（同 scripts/test_mapdir_gate.lua 的離線手法）
local fh = assert(io.open(HOST, "rb"))
local src = fh:read("*a"):gsub("\r\n", "\n")
fh:close()
local function seg(name)
    return assert(src:match("%-%- test:" .. name .. ":start\n(.-)\n%-%- test:" .. name .. ":end"),
        "找不到區段 " .. name)
end
local prelude = [=[
local mapStr, worldError, activeMods, registeredPacks = nil, false, {}, {}
local mapOverlays, logs = {}, {}
local function log(msg) logs[#logs + 1] = msg end
local print = function(msg) logs[#logs + 1] = msg end
MinidoracatMiniMapAPI = {}
local mapFolders = {}
local function getMapFoldersForMod(id)
    local list = mapFolders[id]
    if list == nil then return nil end
    return { size = function(_) return #list end, get = function(_, i) return list[i + 1] end }
end
local MAPS, OWN_MOD_ID = {}, "MinidoracatMiniMapFor42"
local LEGACY_CANONICAL = "minidoracat_minimap.pyramid.zip"
local boolOptions, knownMods, zipFiles = {}, {}, {}
local function getFileSeparator() return "/" end
local function getBoolOption(key, default)
    local v = boolOptions[key]
    if v == nil then return default end
    return v
end
local function getModInfoByID(id)
    if not knownMods[id] then return nil end
    return { id = id }
end
local function findZip(modInfo, sep, zip)
    if zipFiles[modInfo.id .. "|" .. zip] then
        return "/mods" .. sep .. modInfo.id .. sep .. "media" .. sep .. "minimap" .. sep .. zip
    end
    return nil
end
local function getWorld()
    if worldError then error("boom") end
    if mapStr == nil then return nil end
    return { getMap = function(_) return mapStr end }
end
local function getActivatedMods()
    return { size = function(_) return #activeMods end, get = function(_, i) return activeMods[i + 1] end }
end
]=]
local suffix = [=[
return {
    collectPyramids = collectPyramids,
    logs = logs,
    setup = function(o)
        mapStr = o.mapStr
        activeMods = o.activeMods or {}
        registeredPacks = o.packs and { { owner = o.owner, entries = o.packs } } or {}
        mapFolders = o.mapFolders or {}
        MAPS = o.maps or {}
        knownMods = o.knownMods or {}
        zipFiles = o.zipFiles or {}
        boolOptions = o.boolOptions or {}
        for i = #logs, 1, -1 do logs[i] = nil end
    end,
}
]=]
local mod = assert(load(prelude .. "\n" .. seg("mapdir%-gate") .. "\n" .. seg("resolve%-mapdir")
    .. "\n" .. seg("map%-priority") .. "\n" .. seg("collect%-pyramids") .. "\n"
    .. seg("register%-maps") .. "\n" .. suffix, "pack-mount"))()

-- 4) 案例：只有「該地圖 MOD 啟用」時才掛，互斥變體各自掛對
local OLD_ID, NEW_ID = "Willowbrook Bastion!", "Willowbrook Bastion! 2"
local OLD_ZIP, NEW_ZIP = "Willowbrook Bastion!.pyramid.zip", "Willowbrook Bastion! 2026.pyramid.zip"
local OLD_DIR, NEW_DIR = "Willowbrook Bastion!", "Willowbrook Bastion! 2026"

local function run(active, dirs, extraFolders)
    local known = { [PACK_ID] = true }
    local folders = { [OLD_ID] = { OLD_DIR }, [NEW_ID] = { NEW_DIR } }
    for id, list in pairs(extraFolders or {}) do folders[id] = list end
    for _, id in ipairs(active) do known[id] = true end
    local mods = { PACK_ID }
    for _, id in ipairs(active) do mods[#mods + 1] = id end
    mod.setup({ owner = PACK_ID, packs = entries, activeMods = mods, knownMods = known,
        zipFiles = zipFiles, mapFolders = folders, mapStr = dirs })
    local got = {}
    for _, p in ipairs(mod.collectPyramids()) do got[p.zip] = p.path end
    return got
end

local function check(label, cond) print((cond and "  OK   " or "  FAIL ") .. label); return cond end
local pass = true

local g = run({ NEW_ID }, NEW_DIR .. ";Muldraugh, KY")
pass = check("啟用 2026 版 → 掛 " .. NEW_ZIP, g[NEW_ZIP] ~= nil) and pass
pass = check("啟用 2026 版 → 不掛舊版 zip", g[OLD_ZIP] == nil) and pass

g = run({ OLD_ID }, OLD_DIR .. ";Muldraugh, KY")
pass = check("啟用舊版 → 掛 " .. OLD_ZIP, g[OLD_ZIP] ~= nil) and pass
pass = check("啟用舊版 → 不掛 2026 zip", g[NEW_ZIP] == nil) and pass

g = run({}, "Muldraugh, KY")
pass = check("兩者皆未啟用 → 兩張都不掛", g[OLD_ZIP] == nil and g[NEW_ZIP] == nil) and pass

-- 5) 全量：所有 mapMod 啟用且所有地圖目錄都載入 → 91 顆 zip 全數掛上（alias 去重後）。
--    有 mapDir 的條目（SecretZ 據點類）吃「該目錄實際載入」閘門，故 mapStr 要含全部目錄
local allMods, uniq, dirList, folders = {}, {}, {}, {}
for _, e in ipairs(entries) do
    local dir = e.mapDir or e.zip:gsub("%.pyramid%.zip$", "")
    if e.mapMod then
        allMods[#allMods + 1] = e.mapMod
        folders[e.mapMod] = folders[e.mapMod] or {}
        folders[e.mapMod][#folders[e.mapMod] + 1] = dir
    end
    dirList[#dirList + 1] = dir
    uniq[e.zip] = true
end
dirList[#dirList + 1] = "Muldraugh, KY"
local total = 0
for _ in pairs(uniq) do total = total + 1 end
g = run(allMods, table.concat(dirList, ";"), folders)
local mounted = 0
for _ in pairs(g) do mounted = mounted + 1 end
pass = check(("全部啟用＋全部載入 → 掛載 %d／註冊 %d 顆不同 zip（檔案實測 %d）")
    :format(mounted, total, zipCount), mounted == total and total == zipCount) and pass
-- 疊層優先序的 identity 必須全數解析成功（正式資料應 0 筆 cannot resolve）
local unresolved = {}
for _, l in ipairs(mod.logs) do
    if l:find("cannot resolve map directory", 1, true) then unresolved[#unresolved + 1] = l end
end
pass = check(("疊層優先序 identity 全數解析（cannot resolve %d 筆）"):format(#unresolved),
    #unresolved == 0) and pass
if #unresolved > 0 then for _, l in ipairs(unresolved) do print("       " .. l) end end

-- 6) 選項關閉時不掛地圖包（回歸保護）
mod.setup({ owner = PACK_ID, packs = entries, activeMods = { PACK_ID, NEW_ID },
    knownMods = { [PACK_ID] = true, [NEW_ID] = true }, zipFiles = zipFiles,
    mapFolders = { [NEW_ID] = { NEW_DIR } }, mapStr = NEW_DIR,
    boolOptions = { MapPackLayers = false } })
local off = #mod.collectPyramids()
pass = check("「顯示 MOD 地圖區塊」關閉 → 0 顆", off == 0) and pass

print(("\n註冊 %d 條／不同 zip %d 顆；%s"):format(#entries, total, pass and "全部通過" or "有失敗"))
os.exit(pass and 0 or 1)
