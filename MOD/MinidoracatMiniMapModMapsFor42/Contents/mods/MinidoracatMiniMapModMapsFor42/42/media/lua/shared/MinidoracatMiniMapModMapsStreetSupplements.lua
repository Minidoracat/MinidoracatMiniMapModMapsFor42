-- MinidoracatMiniMapModMapsStreetSupplements.lua（生成檔，勿手編）
-- 由 scripts/gen_road_supplements.py 從 road-supplements/*.json 編譯
-- 12 個 dataset／232 條補充道路
--
-- 作者沒放進 streets.xml 的路由本包補上；路名帶「(MiniMap)」＝不是作者取的名字。
-- 執行期（主 MOD）：地圖目錄自己的 streets.xml 街道數 ≠ upstreamStreetCount 就整份停用，
-- 載入的 file 街道數 ≠ roadCount 也停用。names＝英文原名 → UI 翻譯鍵。

MinidoracatMiniMapModMapsStreetSupplements = MinidoracatMiniMapModMapsStreetSupplements or {}
local Supplements = MinidoracatMiniMapModMapsStreetSupplements

-- ==== bedford-falls (BedfordFallsB42 / BedfordFalls) ====
Supplements["bedford-falls"] = {
    schemaVersion = 1, mapMod = "BedfordFallsB42", mapDir = "BedfordFalls",
    file = "media/minimap/streets/bedford-falls.xml", upstreamStreetCount = 0, roadCount = 75,
    names = {
        ["Bedford Falls Rd 01 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_01",
        ["Bedford Falls Rd 02 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_02",
        ["Bedford Falls Rd 03 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_03",
        ["Bedford Falls Rd 04 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_04",
        ["Bedford Falls Rd 05 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_05",
        ["Bedford Falls Rd 06 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_06",
        ["Bedford Falls Rd 07 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_07",
        ["Bedford Falls Rd 08 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_08",
        ["Bedford Falls Rd 09 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_09",
        ["Bedford Falls Rd 10 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_10",
        ["Bedford Falls Rd 11 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_11",
        ["Bedford Falls Rd 12 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_12",
        ["Bedford Falls Rd 13 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_13",
        ["Bedford Falls Rd 14 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_14",
        ["Bedford Falls Rd 15 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_15",
        ["Bedford Falls Rd 16 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_16",
        ["Bedford Falls Rd 17 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_17",
        ["Bedford Falls Rd 18 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_18",
        ["Bedford Falls Rd 19 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_19",
        ["Bedford Falls Rd 20 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_20",
        ["Bedford Falls Rd 21 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_21",
        ["Bedford Falls Rd 22 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_22",
        ["Bedford Falls Rd 23 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_23",
        ["Bedford Falls Rd 24 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_24",
        ["Bedford Falls Rd 25 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_25",
        ["Bedford Falls Rd 26 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_26",
        ["Bedford Falls Rd 27 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_27",
        ["Bedford Falls Rd 28 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_28",
        ["Bedford Falls Rd 29 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_29",
        ["Bedford Falls Rd 30 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_30",
        ["Bedford Falls Rd 31 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_31",
        ["Bedford Falls Rd 32 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_32",
        ["Bedford Falls Rd 33 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_33",
        ["Bedford Falls Rd 34 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_34",
        ["Bedford Falls Rd 35 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_35",
        ["Bedford Falls Rd 36 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_36",
        ["Bedford Falls Rd 37 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_37",
        ["Bedford Falls Rd 38 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_38",
        ["Bedford Falls Rd 39 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_39",
        ["Bedford Falls Rd 40 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_40",
        ["Bedford Falls Rd 41 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_41",
        ["Bedford Falls Rd 42 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_42",
        ["Bedford Falls Rd 43 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_43",
        ["Bedford Falls Rd 44 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_44",
        ["Bedford Falls Rd 45 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_45",
        ["Bedford Falls Rd 46 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_46",
        ["Bedford Falls Rd 47 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_47",
        ["Bedford Falls Rd 48 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_48",
        ["Bedford Falls Rd 49 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_49",
        ["Bedford Falls Rd 50 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_50",
        ["Bedford Falls Rd 51 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_51",
        ["Bedford Falls Rd 52 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_52",
        ["Bedford Falls Rd 53 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_53",
        ["Bedford Falls Rd 54 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_54",
        ["Bedford Falls Rd 55 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_55",
        ["Bedford Falls Rd 56 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_56",
        ["Bedford Falls Rd 57 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_57",
        ["Bedford Falls Rd 58 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_58",
        ["Bedford Falls Rd 59 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_59",
        ["Bedford Falls Rd 60 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_60",
        ["Bedford Falls Rd 61 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_61",
        ["Bedford Falls Rd 62 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_62",
        ["Bedford Falls Rd 63 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_63",
        ["Bedford Falls Rd 64 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_64",
        ["Bedford Falls Rd 65 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_65",
        ["Bedford Falls Rd 66 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_66",
        ["Bedford Falls Rd 67 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_67",
        ["Bedford Falls Rd 68 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_68",
        ["Bedford Falls Rd 69 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_69",
        ["Bedford Falls Rd 70 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_70",
        ["Bedford Falls Rd 71 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_71",
        ["Bedford Falls Rd 72 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_72",
        ["Bedford Falls Rd 73 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_73",
        ["Bedford Falls Rd 74 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_74",
        ["Bedford Falls Rd 75 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_bedford-falls_75",
    },
}

-- ==== big-bear-lake (bigbearlake42 / BBL_b42) ====
Supplements["big-bear-lake"] = {
    schemaVersion = 1, mapMod = "bigbearlake42", mapDir = "BBL_b42",
    file = "media/minimap/streets/big-bear-lake.xml", upstreamStreetCount = 87, roadCount = 6,
    names = {
        ["Big Bear Lake Rd 01 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_big-bear-lake_01",
        ["Big Bear Lake Rd 02 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_big-bear-lake_02",
        ["Big Bear Lake Rd 03 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_big-bear-lake_03",
        ["Big Bear Lake Rd 04 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_big-bear-lake_04",
        ["Big Bear Lake Rd 05 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_big-bear-lake_05",
        ["Big Bear Lake Rd 06 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_big-bear-lake_06",
    },
}

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
    file = "media/minimap/streets/dirkerdam.xml", upstreamStreetCount = 0, roadCount = 8,
    names = {
        ["Dirkerdam Rd 01 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_dirkerdam_01",
        ["Dirkerdam Rd 02 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_dirkerdam_02",
        ["Dirkerdam Rd 03 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_dirkerdam_03",
        ["Dirkerdam Rd 04 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_dirkerdam_04",
        ["Dirkerdam Rd 05 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_dirkerdam_05",
        ["Dirkerdam Rd 06 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_dirkerdam_06",
        ["Dirkerdam Rd 07 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_dirkerdam_07",
        ["Dirkerdam Rd 08 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_dirkerdam_08",
    },
}

-- ==== jib-factory (jibsMap / jibs) ====
Supplements["jib-factory"] = {
    schemaVersion = 1, mapMod = "jibsMap", mapDir = "jibs",
    file = "media/minimap/streets/jib-factory.xml", upstreamStreetCount = 0, roadCount = 4,
    names = {
        ["JIB Peanut Butter Factory Rd 01 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_jib-factory_01",
        ["JIB Peanut Butter Factory Rd 02 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_jib-factory_02",
        ["JIB Peanut Butter Factory Rd 03 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_jib-factory_03",
        ["JIB Peanut Butter Factory Rd 04 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_jib-factory_04",
    },
}

-- ==== moores-mechanic (MooresMechanicPlus / Moores Mechanic Plus) ====
Supplements["moores-mechanic"] = {
    schemaVersion = 1, mapMod = "MooresMechanicPlus", mapDir = "Moores Mechanic Plus",
    file = "media/minimap/streets/moores-mechanic.xml", upstreamStreetCount = 0, roadCount = 1,
    names = {
        ["Moores Mechanic Rd 01 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_moores-mechanic_01",
    },
}

-- ==== oakshire (Oakshire42 / Oakshire42) ====
Supplements["oakshire"] = {
    schemaVersion = 1, mapMod = "Oakshire42", mapDir = "Oakshire42",
    file = "media/minimap/streets/oakshire.xml", upstreamStreetCount = 0, roadCount = 88,
    names = {
        ["Oakshire Rd 01 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_01",
        ["Oakshire Rd 02 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_02",
        ["Oakshire Rd 03 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_03",
        ["Oakshire Rd 04 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_04",
        ["Oakshire Rd 05 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_05",
        ["Oakshire Rd 06 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_06",
        ["Oakshire Rd 07 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_07",
        ["Oakshire Rd 08 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_08",
        ["Oakshire Rd 09 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_09",
        ["Oakshire Rd 10 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_10",
        ["Oakshire Rd 11 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_11",
        ["Oakshire Rd 12 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_12",
        ["Oakshire Rd 13 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_13",
        ["Oakshire Rd 14 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_14",
        ["Oakshire Rd 15 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_15",
        ["Oakshire Rd 16 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_16",
        ["Oakshire Rd 17 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_17",
        ["Oakshire Rd 18 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_18",
        ["Oakshire Rd 19 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_19",
        ["Oakshire Rd 20 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_20",
        ["Oakshire Rd 21 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_21",
        ["Oakshire Rd 22 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_22",
        ["Oakshire Rd 23 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_23",
        ["Oakshire Rd 24 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_24",
        ["Oakshire Rd 25 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_25",
        ["Oakshire Rd 26 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_26",
        ["Oakshire Rd 27 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_27",
        ["Oakshire Rd 28 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_28",
        ["Oakshire Rd 29 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_29",
        ["Oakshire Rd 30 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_30",
        ["Oakshire Rd 31 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_31",
        ["Oakshire Rd 32 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_32",
        ["Oakshire Rd 33 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_33",
        ["Oakshire Rd 34 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_34",
        ["Oakshire Rd 35 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_35",
        ["Oakshire Rd 36 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_36",
        ["Oakshire Rd 37 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_37",
        ["Oakshire Rd 38 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_38",
        ["Oakshire Rd 39 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_39",
        ["Oakshire Rd 40 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_40",
        ["Oakshire Rd 41 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_41",
        ["Oakshire Rd 42 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_42",
        ["Oakshire Rd 43 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_43",
        ["Oakshire Rd 44 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_44",
        ["Oakshire Rd 45 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_45",
        ["Oakshire Rd 46 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_46",
        ["Oakshire Rd 47 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_47",
        ["Oakshire Rd 48 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_48",
        ["Oakshire Rd 49 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_49",
        ["Oakshire Rd 50 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_50",
        ["Oakshire Rd 51 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_51",
        ["Oakshire Rd 52 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_52",
        ["Oakshire Rd 53 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_53",
        ["Oakshire Rd 54 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_54",
        ["Oakshire Rd 55 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_55",
        ["Oakshire Rd 56 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_56",
        ["Oakshire Rd 57 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_57",
        ["Oakshire Rd 58 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_58",
        ["Oakshire Rd 59 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_59",
        ["Oakshire Rd 60 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_60",
        ["Oakshire Rd 61 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_61",
        ["Oakshire Rd 62 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_62",
        ["Oakshire Rd 63 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_63",
        ["Oakshire Rd 64 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_64",
        ["Oakshire Rd 65 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_65",
        ["Oakshire Rd 66 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_66",
        ["Oakshire Rd 67 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_67",
        ["Oakshire Rd 68 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_68",
        ["Oakshire Rd 69 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_69",
        ["Oakshire Rd 70 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_70",
        ["Oakshire Rd 71 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_71",
        ["Oakshire Rd 72 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_72",
        ["Oakshire Rd 73 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_73",
        ["Oakshire Rd 74 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_74",
        ["Oakshire Rd 75 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_75",
        ["Oakshire Rd 76 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_76",
        ["Oakshire Rd 77 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_77",
        ["Oakshire Rd 78 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_78",
        ["Oakshire Rd 79 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_79",
        ["Oakshire Rd 80 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_80",
        ["Oakshire Rd 81 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_81",
        ["Oakshire Rd 82 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_82",
        ["Oakshire Rd 83 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_83",
        ["Oakshire Rd 84 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_84",
        ["Oakshire Rd 85 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_85",
        ["Oakshire Rd 86 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_86",
        ["Oakshire Rd 87 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_87",
        ["Oakshire Rd 88 (MiniMap)"] = "UI_MinidoracatMiniMapModMaps_Road_oakshire_88",
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
