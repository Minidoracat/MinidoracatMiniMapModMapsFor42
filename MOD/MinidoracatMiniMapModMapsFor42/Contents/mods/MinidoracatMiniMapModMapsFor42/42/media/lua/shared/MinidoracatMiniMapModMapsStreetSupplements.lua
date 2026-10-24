-- MinidoracatMiniMapModMapsStreetSupplements.lua（生成檔，勿手編）
-- 由 scripts/gen_road_supplements.py 從 road-supplements/*.json 編譯
-- 7 個 dataset／51 條補充道路
--
-- 作者沒放進 streets.xml 的路由本包補上；路名帶「(MiniMap)」＝不是作者取的名字。
-- 執行期（主 MOD）：地圖目錄自己的 streets.xml 街道數 ≠ upstreamStreetCount 就整份停用，
-- 載入的 file 街道數 ≠ roadCount 也停用。names＝英文原名 → UI 翻譯鍵。

MinidoracatMiniMapModMapsStreetSupplements = MinidoracatMiniMapModMapsStreetSupplements or {}
local Supplements = MinidoracatMiniMapModMapsStreetSupplements

-- ==== constown (Constown42 / Constown, KY) ====
Supplements["constown"] = {
    schemaVersion = 1, mapMod = "Constown42", mapDir = "Constown, KY",
    file = "media/minimap/streets/constown.xml", upstreamStreetCount = 0, roadCount = 38,
    names = {
        ["Constown Rd 01 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_01",
        ["Constown Rd 02 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_02",
        ["Constown Rd 03 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_03",
        ["Constown Rd 04 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_04",
        ["Constown Rd 05 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_05",
        ["Constown Rd 06 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_06",
        ["Constown Rd 07 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_07",
        ["Constown Rd 08 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_08",
        ["Constown Rd 09 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_09",
        ["Constown Rd 10 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_10",
        ["Constown Rd 11 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_11",
        ["Constown Rd 12 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_12",
        ["Constown Rd 13 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_13",
        ["Constown Rd 14 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_14",
        ["Constown Rd 15 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_15",
        ["Constown Rd 16 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_16",
        ["Constown Rd 17 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_17",
        ["Constown Rd 18 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_18",
        ["Constown Rd 19 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_19",
        ["Constown Rd 20 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_20",
        ["Constown Rd 21 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_21",
        ["Constown Rd 22 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_22",
        ["Constown Rd 23 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_23",
        ["Constown Rd 24 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_24",
        ["Constown Rd 25 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_25",
        ["Constown Rd 26 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_26",
        ["Constown Rd 27 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_27",
        ["Constown Rd 28 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_28",
        ["Constown Rd 29 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_29",
        ["Constown Rd 30 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_30",
        ["Constown Rd 31 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_31",
        ["Constown Rd 32 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_32",
        ["Constown Rd 33 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_33",
        ["Constown Rd 34 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_34",
        ["Constown Rd 35 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_35",
        ["Constown Rd 36 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_36",
        ["Constown Rd 37 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_37",
        ["Constown Rd 38 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_constown_38",
    },
}

-- ==== coryerdon (CoryerdonB42 / Coryerdon B42) ====
Supplements["coryerdon"] = {
    schemaVersion = 1, mapMod = "CoryerdonB42", mapDir = "Coryerdon B42",
    file = "media/minimap/streets/coryerdon.xml", upstreamStreetCount = 0, roadCount = 2,
    names = {
        ["Coryerdon Rd 01 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_coryerdon_01",
        ["Coryerdon Rd 02 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_coryerdon_02",
    },
}

-- ==== coryerdon-2026 (CoryerdonB42 / Coryerdon) ====
Supplements["coryerdon-2026"] = {
    schemaVersion = 1, mapMod = "CoryerdonB42", mapDir = "Coryerdon",
    file = "media/minimap/streets/coryerdon-2026.xml", upstreamStreetCount = 0, roadCount = 6,
    names = {
        ["Coryerdon Rd 01 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_coryerdon-2026_01",
        ["Coryerdon Rd 02 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_coryerdon-2026_02",
        ["Coryerdon Rd 03 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_coryerdon-2026_03",
        ["Coryerdon Rd 04 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_coryerdon-2026_04",
        ["Coryerdon Rd 05 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_coryerdon-2026_05",
        ["Coryerdon Rd 06 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_coryerdon-2026_06",
    },
}

-- ==== dirkerdam (DirkerdamIntegratedB42 / Dirkerdam Integrated B42) ====
Supplements["dirkerdam"] = {
    schemaVersion = 1, mapMod = "DirkerdamIntegratedB42", mapDir = "Dirkerdam Integrated B42",
    file = "media/minimap/streets/dirkerdam.xml", upstreamStreetCount = 0, roadCount = 1,
    names = {
        ["Dirkerdam Rd 01 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_dirkerdam_01",
    },
}

-- ==== raven-creek (RavenCreekB42 / Raven Creek B42) ====
Supplements["raven-creek"] = {
    schemaVersion = 1, mapMod = "RavenCreekB42", mapDir = "Raven Creek B42",
    file = "media/minimap/streets/raven-creek.xml", upstreamStreetCount = 45, roadCount = 1,
    names = {
        ["Raven Creek Rd 01 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_raven-creek_01",
    },
}

-- ==== snake-factory (SMP_Factory / Factory) ====
Supplements["snake-factory"] = {
    schemaVersion = 1, mapMod = "SMP_Factory", mapDir = "Factory",
    file = "media/minimap/streets/snake-factory.xml", upstreamStreetCount = 0, roadCount = 1,
    names = {
        ["Snake's Factory Rd 01 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_snake-factory_01",
    },
}

-- ==== twd-prison (FCooperTWDPrison / FCooperTWDPrison) ====
Supplements["twd-prison"] = {
    schemaVersion = 1, mapMod = "FCooperTWDPrison", mapDir = "FCooperTWDPrison",
    file = "media/minimap/streets/twd-prison.xml", upstreamStreetCount = 0, roadCount = 2,
    names = {
        ["The Walking Dead Prison Rd 01 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_twd-prison_01",
        ["The Walking Dead Prison Rd 02 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_twd-prison_02",
    },
}
