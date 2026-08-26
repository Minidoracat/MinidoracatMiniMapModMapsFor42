-- 街名多語化驗收（離線）：用主 MOD 的「真實」buildStreetI18nIndex／
-- resolveStreetI18nCandidate／composeStreetI18nPath 程式碼，餵本包的真實註冊表與真實
-- media/minimapstreets/ 檔案，驗證每個 dataset 都能被解析、三語檔齊備、同 mapDir 互斥
-- 變體靠啟用 mapMod 各自命中、未啟用時退回英文。補「靜態驗證」與「進遊戲目視」之間的
-- 空隙：遊戲一次只能看一張圖一種語言，這裡一次覆蓋全部 dataset × 3 語。
-- 新增/移除街名 dataset 後必跑。
--
-- 用法（cwd＝本 repo 根）：lua scripts/verify_street_i18n.lua [主MOD的_StreetI18n.lua]
local HOST = arg[1] or "../MinidoracatMiniMapFor42/MOD/MinidoracatMiniMapFor42/Contents/mods/"
    .. "MinidoracatMiniMapFor42/42/media/lua/client/MinidoracatMiniMap_StreetI18n.lua"
local PACK_ROOT = "MOD/MinidoracatMiniMapModMapsFor42/Contents/mods/"
    .. "MinidoracatMiniMapModMapsFor42/42/"
local PACK_LUA = PACK_ROOT .. "media/lua/client/MinidoracatMiniMapModMaps.lua"
local PACK_ID = "MinidoracatMiniMapModMapsFor42"
local LANGS = { "CH", "CN", "JP" }

-- 1) 地圖包真實註冊表：提供 API stub 讓它自己註冊進來
local entries, owner
MinidoracatMiniMapAPI = { registerMaps = function(o, list) owner, entries = o, list end }
assert(loadfile(PACK_LUA))()
assert(entries and owner == PACK_ID, "抽不到地圖包註冊表")

-- 2) 主 MOD 真實程式碼區段（同 verify_pack_mount.lua 的離線手法）
local fh = assert(io.open(HOST, "rb"), "找不到主 MOD 街名載入層：" .. HOST)
local src = fh:read("*a"):gsub("\r\n", "\n")
fh:close()
local seg = assert(src:match("%-%- test:street%-i18n:start\n(.-)\n%-%- test:street%-i18n:end"),
    "找不到區段 street-i18n")
local api = assert(load(seg .. "\nreturn { compose = composeStreetI18nPath,"
    .. " build = buildStreetI18nIndex, resolve = resolveStreetI18nCandidate }",
    "street-i18n"))()

local fails, checks = {}, 0
local function ok(cond, msg)
    checks = checks + 1
    if not cond then fails[#fails + 1] = msg end
end
local function fileExists(rel)
    local h = io.open(PACK_ROOT .. rel:gsub("^media/", "media/"), "rb")
    if h then h:close(); return true end
    return false
end

-- 3) 索引：以真實註冊表建構
local byDir = api.build({ { owner = owner, entries = entries } }, nil)

-- 期望 dataset：註冊表裡每個帶 streetI18n 的條目
local expect, expectCount = {}, 0
for _, e in ipairs(entries) do
    if e.streetI18n then
        ok(type(e.mapDir) == "string" and e.mapDir ~= "",
            "streetI18n 條目缺 mapDir：" .. e.streetI18n)
        expect[e.streetI18n] = e
        expectCount = expectCount + 1
    end
end
ok(expectCount > 0, "註冊表沒有任何 streetI18n 條目")

-- 4) 每個 dataset：能從其 mapDir 解析回自己，且三語檔齊備
local seenDatasets = 0
for id, e in pairs(expect) do
    local cands = byDir[e.mapDir]
    ok(cands ~= nil, id .. "：mapDir '" .. tostring(e.mapDir) .. "' 未進索引")
    if cands then
        -- 只啟用該條目的 mapMod → 必須恰好解析到自己
        local chosen = api.resolve(cands, e.mapMod and { [e.mapMod] = true } or nil)
        ok(chosen ~= nil and chosen.id == id,
            id .. "：啟用 " .. tostring(e.mapMod) .. " 時未解析到自己（得 "
            .. tostring(chosen and chosen.id) .. "）")
        for _, lang in ipairs(LANGS) do
            local rel = api.compose(owner, id, lang)
            ok(rel == "media/minimapstreets/" .. owner .. "/" .. id .. "/streets_" .. lang .. ".xml",
                id .. "：路徑組合不符契約：" .. rel)
            ok(fileExists(rel), id .. "：缺 " .. lang .. " 檔 " .. rel)
        end
        seenDatasets = seenDatasets + 1
    end
end
ok(seenDatasets == expectCount,
    "解析到的 dataset 數 " .. seenDatasets .. " ≠ 註冊表 " .. expectCount)

-- 5) 同 mapDir 多變體（Raven Creek 本體 vs Kardinal 移植版）：靠啟用 mapMod 甄別
for dir, cands in pairs(byDir) do
    if #cands > 1 then
        for _, c in ipairs(cands) do
            local chosen = api.resolve(cands, { [c.mapMod] = true })
            ok(chosen ~= nil and chosen.id == c.id,
                dir .. "：啟用 " .. tostring(c.mapMod) .. " 應命中 " .. c.id
                .. "（得 " .. tostring(chosen and chosen.id) .. "）")
        end
        -- 全未啟用 → nil（呼叫端退回英文，不猜）
        ok(api.resolve(cands, {}) == nil, dir .. "：全未啟用時應回 nil（英文 fallback）")
    end
end

-- 6) 無 streetI18n 的條目不得進索引（避免誤替換）
for _, e in ipairs(entries) do
    if not e.streetI18n and e.mapDir and byDir[e.mapDir] then
        for _, c in ipairs(byDir[e.mapDir]) do
            ok(c.mapMod ~= e.mapMod or c.id ~= nil,
                e.mapDir .. "：無 streetI18n 卻進索引")
        end
    end
end

-- 7) 壞值中和：非法 ID／空 mapDir 應被忽略且不影響其他條目
local dirty = { { owner = owner, entries = {
    { zip = "a.pyramid.zip", mapMod = "M1", mapDir = "D1", streetI18n = "../escape" },
    { zip = "b.pyramid.zip", mapMod = "M2", mapDir = "",   streetI18n = "ok-id" },
    { zip = "c.pyramid.zip", mapMod = "M3", mapDir = "D3", streetI18n = "good.id-1" },
} } }
local di = api.build(dirty, nil)
ok(di["D1"] == nil, "路徑穿越 ID 未被忽略")
ok(di[""] == nil, "空 mapDir 未被忽略")
ok(di["D3"] and #di["D3"] == 1 and di["D3"][1].id == "good.id-1", "合法條目被誤丟")

-- 8) 搜尋雙語：英文原名表必須 append 到主 MOD 的同一張全域表
-- 街名替換成中文/日文後，引擎索引只剩譯名，用英文原名搜尋會無結果（主 MOD 對官方
-- 地圖早有同一問題）。本包烘焙 MOD 地圖那段補上；這裡模擬 PZ 載入序（require= 保證
-- 主 MOD 的 shared 表先載）驗證 append 真的生效、且不影響官方那 1098 條。
local HOST_EN = (arg[2] or "../MinidoracatMiniMapFor42/MOD/MinidoracatMiniMapFor42/Contents/mods/"
    .. "MinidoracatMiniMapFor42/42/media/lua/shared/MinidoracatMiniMapStreetNames.lua")
local PACK_EN = PACK_ROOT .. "media/lua/shared/MinidoracatMiniMapModMapsStreetNames.lua"
local baseCount = 0
if io.open(HOST_EN, "rb") then
    local fh2 = io.open(HOST_EN, "rb"); fh2:close()
    dofile(HOST_EN)
    baseCount = #MinidoracatMiniMapStreetNames
    ok(baseCount > 0, "主 MOD 官方英文原名表為空（gen_street_names.py 沒跑？）")
else
    ok(false, "找不到主 MOD 英文原名表：" .. HOST_EN)
end
local packEnFh = io.open(PACK_EN, "rb")
ok(packEnFh ~= nil, "缺英文原名表 " .. PACK_EN .. "（跑 gen_streets_i18n.py gen）")
if packEnFh then
    packEnFh:close()
    dofile(PACK_EN)
    local total = #MinidoracatMiniMapStreetNames
    ok(total > baseCount, "英文原名表未 append（總數未增加）")
    -- 上游條數總和＝各 dataset streets 條數；用 CH 生成檔反推（幾何與上游逐條一致）
    local expectAdd = 0
    for id in pairs(expect) do
        local xf = io.open(PACK_ROOT .. "media/minimapstreets/" .. owner .. "/" .. id
            .. "/streets_CH.xml", "rb")
        if xf then
            local s = xf:read("*a"); xf:close()
            for _ in s:gmatch("<street%s") do expectAdd = expectAdd + 1 end
        end
    end
    ok(total - baseCount == expectAdd,
        "英文原名表條數 " .. (total - baseCount) .. " ≠ 各 dataset 上游街道數 " .. expectAdd)
    -- 抽查：MOD 地圖英文原名能被搜尋端的小寫子串比對命中（同 _Search.lua 手法）
    local function findLow(q)
        q = q:lower()
        for i = 1, total do
            local e = MinidoracatMiniMapStreetNames[i]
            if type(e) == "table" and type(e.l) == "string" and e.l:find(q, 1, true)
                and type(e.x) == "number" and type(e.y) == "number" then
                return e
            end
        end
    end
    for _, q in ipairs({ "weinifan", "anruisi", "toucan", "mcclellan" }) do
        ok(findLow(q) ~= nil, "英文原名搜不到 MOD 地圖街名：" .. q)
    end
    ok(findLow("oak st") ~= nil, "官方英文原名被破壞：oak st")
end

print(string.format("街名 dataset %d 個｜語言 %d｜檢查 %d 項",
    expectCount, #LANGS, checks))
if #fails > 0 then
    print("FAIL " .. #fails .. " 項：")
    for _, m in ipairs(fails) do print("  - " .. m) end
    os.exit(1)
end
print("PASS")
