-- 離線導航：照 Map= 順序載入地圖目錄的 streets.xml，套本包道路修正、加上本包補充道路，用主 MOD 的 NavCore 與 cell 覆蓋規則（makeWinnerOf）算路線。
-- 寫 E2E 情境前，先用它算預期值（可搜名稱數、補前／補後路線長度），不要猜。
-- 用法（repo 根目錄，主 MOD repo 在 ../MinidoracatMiniMapFor42）：
--   lua scripts/offline_nav.lua --map "<地圖目錄>" [--map ...] [--sup <dataset>]... [--route sx sy tx ty]... [--dump]
--   --map    地圖目錄的完整路徑（含 X_Y.lotheader 的那層），照 Map= 順序、第一個優先；原版 Muldraugh, KY 自動補在最後
--   --sup    media/minimap/streets/<dataset>.xml，掛在註冊清單引用它的 mapDir 下，和遊戲一樣受該目錄的 cell 覆蓋規則裁段
--   --route  起點與終點；有 --sup 或該目錄有本包道路修正時印補前（作者原始資料）、補後（套修正＋補充道路）兩組
--   --dump   印出路線的每個點（判斷有沒有跨過某座橋、某條線）
-- 道路修正讀生成的 shared 表（MinidoracatMiniMapModMapsStreetRepairs.lua），照主 MOD 規則逐筆比對 expectedWidth／
-- expectedPoints，相符才換 replacementPoints／replacementWidth；hideLabel 只影響顯示，這裡不管。
-- 例：lua scripts/offline_nav.lua --map "D:/SteamCMD/steamapps/workshop/content/108600/3821470553/mods/Coryerdon/common/media/maps/Coryerdon" \
--       --sup coryerdon-2026 --route 7300 5500 7422 6000
-- ponytail: 不重做主 MOD 的跨目錄重複街道去重（seenSig），重複的街只會多一份同樣的邊，路線長度不變。
local MAIN = "../MinidoracatMiniMapFor42/MOD/MinidoracatMiniMapFor42/Contents/mods/MinidoracatMiniMapFor42/42/media/lua/client/MinidoracatMiniMap_NavRoute.lua"
local PACK = "MOD/MinidoracatMiniMapModMapsFor42/Contents/mods/MinidoracatMiniMapModMapsFor42/42/media"
local VANILLA = "D:/SteamLibrary/steamapps/common/ProjectZomboid/media/maps/Muldraugh, KY"

local function slurp(path)
    local f = assert(io.open(path, "rb"))
    local s = f:read("*a")
    f:close()
    return (s:gsub("\r\n", "\n"))
end

local function block(src, tag)
    local t = tag:gsub("%-", "%%-")
    return assert(src:match("%-%- test:" .. t .. ":start\n(.-)\n%-%- test:" .. t .. ":end"), "主 MOD 找不到 " .. tag .. " 區段")
end

local function base(path)
    return (path:gsub("[/\\]+$", "")):match("([^/\\]+)$")
end

local maps, sups, routes, dump = {}, {}, {}, false
local i = 1
while arg[i] do
    local a = arg[i]
    if a == "--map" or a == "--sup" then
        local list = a == "--map" and maps or sups
        list[#list + 1] = assert(arg[i + 1], a .. " 後面要接值")
        i = i + 2
    elseif a == "--route" then
        local r = { tonumber(arg[i + 1]), tonumber(arg[i + 2]), tonumber(arg[i + 3]), tonumber(arg[i + 4]) }
        assert(r[4], "--route 要四個數字：sx sy tx ty")
        routes[#routes + 1] = r
        i = i + 5
    elseif a == "--dump" then
        dump = true
        i = i + 1
    else
        error("不認得的參數：" .. a)
    end
end
if #maps == 0 or base(maps[#maps]) ~= "Muldraugh, KY" then maps[#maps + 1] = VANILLA end

-- 本包道路修正：dataset 的 mapDir → operations（0-based raw street index）
local repairsByDir = {}
do
    local chunk = assert((loadstring or load)(slurp(PACK .. "/lua/shared/MinidoracatMiniMapModMapsStreetRepairs.lua"), "repairs"))
    chunk()
    for _, ds in pairs(MinidoracatMiniMapModMapsStreetRepairs or {}) do repairsByDir[ds.mapDir] = ds.operations end
end

local function samePoints(a, b)
    if #a ~= #b then return false end
    for k = 1, #a do
        if math.abs(a[k] - b[k]) > 1e-3 then return false end
    end
    return true
end

local source = slurp(MAIN)
local NavCore = assert((loadstring or load)(block(source, "navroute-core") .. "\nreturn NavCore", "navcore"))()

-- cell 覆蓋規則直接跑主 MOD 的 makeWinnerOf：getLoadedMapDirs 換成 --map 的順序，fileExists 換成真檔案
local order, pathOf = {}, {}
for idx, path in ipairs(maps) do
    order[base(path)], pathOf[base(path)] = idx, path
end
local function fileExists(rel)
    local dir, file = rel:match("^media/maps/(.+)/([^/]+)$")
    local f = dir and pathOf[dir] and io.open(pathOf[dir] .. "/" .. file, "rb")
    if f then f:close() end
    return f and true or false
end
local winnerChunk = assert((loadstring or load)(
    "local Core, fileExists, STREET_CELL, LOT_CELL = ...\nlocal floor = math.floor\n"
    .. block(source, "nav-winner") .. "\nreturn makeWinnerOf", "nav-winner"))
local winnerOf = assert(winnerChunk({ getLoadedMapDirs = function() return order end }, fileExists,
    tonumber(source:match("local STREET_CELL = (%d+)")), tonumber(source:match("local LOT_CELL = (%d+)")))())

-- 遊戲抽街道時跳過鐵路（NavCore.isRailroadStreet），可搜名稱與路網都不含它們；ops＝本包修正（nil＝作者原始資料）
local function readStreets(path, src, out, ops)
    local f = io.open(path, "rb")
    if not f then return nil end
    local xml = f:read("*a")
    f:close()
    local names, searchable, rail, idx, fixed = {}, {}, 0, -1, 0
    for name, attrs, body in xml:gmatch('<street name="([^"]*)"([^>]*)>(.-)</street>') do
        idx = idx + 1
        local pts = {}
        for x, y in body:gmatch('<point x="([%d%.%-]+)" y="([%d%.%-]+)"') do
            pts[#pts + 1] = tonumber(x)
            pts[#pts + 1] = tonumber(y)
        end
        local width = tonumber(attrs:match('width="([%d%.]+)"'))
        local op = ops and ops[idx]
        if op and op.expectedWidth == width and samePoints(op.expectedPoints, pts)
            and (op.replacementPoints or op.replacementWidth) then
            pts = op.replacementPoints or pts
            width = op.replacementWidth or width
            fixed = fixed + 1
        end
        if #pts >= 4 then
            names[name] = true
            if NavCore.isRailroadStreet(name, pts[1], pts[2]) then
                rail = rail + 1
            else
                searchable[name] = true
                out[#out + 1] = { name = name, width = width, src = src, pts = pts }
            end
        end
    end
    local function count(t) local n = 0 for _ in pairs(t) do n = n + 1 end return n end
    return ("名稱 %d、可搜 %d、鐵路段 %d"):format(count(names), count(searchable), rail)
        .. (ops and ("、套用本包修正 %d 筆"):format(fixed) or "")
end

local base_streets, fixed_streets, anyRepair = {}, {}, false
for _, path in ipairs(maps) do
    local ops = repairsByDir[base(path)]
    print(("%s：%s"):format(base(path), readStreets(path .. "/streets.xml", base(path), base_streets) or "沒有 streets.xml"))
    if ops then
        anyRepair = true
        print(("  修正後：%s"):format(readStreets(path .. "/streets.xml", base(path), fixed_streets, ops) or "沒有 streets.xml"))
    else
        readStreets(path .. "/streets.xml", base(path), fixed_streets)
    end
end

local registry = slurp(PACK .. "/lua/client/MinidoracatMiniMapModMaps.lua")
local supDir = {}
for dir, ds in registry:gmatch('mapDir = "([^"]+)",%s*streetSupplement = StreetSupplements%["([^"]+)"%]') do supDir[ds] = dir end
local with = {}
for _, s in ipairs(fixed_streets) do with[#with + 1] = s end
for _, ds in ipairs(sups) do
    local dir = assert(supDir[ds], ds .. " 不在註冊清單的 streetSupplement")
    assert(order[dir], ds .. " 掛在 " .. dir .. "，--map 沒有這個目錄，遊戲不會載入它")
    print(("補充道路 %s（掛 %s）：%s"):format(ds, dir, readStreets(PACK .. "/minimap/streets/" .. ds .. ".xml", dir, with)))
end

local function build(streets)
    local b = NavCore.newBuild(streets, winnerOf)
    while not NavCore.step(b, 100000) do end
    return b.graph
end

local function show(tag, g, r)
    local route = NavCore.findRoute(g, r[1], r[2], r[3], r[4])
    if not route then
        print("  " .. tag .. " noroad")
        return
    end
    local pts, n = route.pts, #route.pts
    print(("  %s len %d  點 %d  終點離目標 %.1f"):format(tag, math.floor(route.len), n / 2,
        math.sqrt((pts[n - 1] - r[3]) ^ 2 + (pts[n] - r[4]) ^ 2)))
    if dump then
        for k = 1, n, 2 do print(("    %.1f,%.1f"):format(pts[k], pts[k + 1])) end
    end
end

if #routes > 0 then
    local before = (#sups > 0 or anyRepair) and build(base_streets) or nil
    local after = build(with)
    for _, r in ipairs(routes) do
        print(("路線 %g,%g → %g,%g"):format(r[1], r[2], r[3], r[4]))
        if before then show("補前", before, r) end
        show(before and "補後" or "", after, r)
    end
end
