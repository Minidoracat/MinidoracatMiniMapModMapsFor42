-- MinidoracatMiniMapModMaps.lua — Minidoracat 小地圖「地圖包」（純資料註冊，
-- 掛載/框線/選項等本體邏輯全在主 MOD MinidoracatMiniMapFor42）。
-- mod.info 的 require=MinidoracatMiniMapFor42 保證主 MOD 的 client lua 先載入，
-- 此時 MinidoracatMiniMapAPI 已存在；主 MOD 於 OnGameBoot 檢查「有註冊」才會
-- 顯示地圖包相關選項（顯示 MOD 地圖區塊／框線開關／框線顏色）。
--
-- 條目格式（同主 MOD MAPS manifest）：
--   zip     = 本 MOD media/minimap/ 下的 pyramid zip 檔名（pzmap 渲染輸出）
--   mapMod  = 對應地圖 MOD 的 mod ID（啟用才掛載）
--   mapDir  = 選配，地圖目錄名（該 MOD media/maps/ 下資料夾）：一 mod 多地圖
--             （SecretZ、NewEllroy+Shadyside）才指定——MP 伺服器 Map= 未載入
--             該目錄就不顯示（未載入的據點不誤畫）；單地圖 mod 免填
--   bounds  = 渲染時 pyramid.txt 的世界 square 座標（右/下排他）
--   nameKey = UI.json 翻譯鍵（缺譯退 mapMod）
--   streetI18n = 選配，街名翻譯資料集 ID（[A-Za-z0-9._-]+）：主 MOD 依遊戲語言
--             （CH/CN/JP）載入 media/minimapstreets/<本包ID>/<id>/streets_<LANG>.xml
--             取代該圖英文 streets.xml（見 docs/street-names-i18n-plan.md）。
--             含此欄位的條目必須明確填 mapDir（同 mapDir 多變體時以啟用 mod 甄別）
if MinidoracatMiniMapAPI and MinidoracatMiniMapAPI.registerMaps then
    MinidoracatMiniMapAPI.registerMaps("MinidoracatMiniMapModMapsFor42", {
        { zip = "Muldraugh_FireDept.pyramid.zip", mapMod = "beek_muldraugh_firedept",
            bounds = { 10496, 8960, 11008, 9472 }, nameKey = "UI_MinidoracatMiniMapModMaps_MuldraughFireDept" },
        { zip = "Estate 39.pyramid.zip", mapMod = "Estate 39",
            bounds = { 8192, 9728, 8704, 10240 }, nameKey = "UI_MinidoracatMiniMapModMaps_Estate39" },
        -- 唐人街群組＝兩個 Workshop 項目、三個 mod ID，彼此**不是**依賴關係：
        --   3703704638 拓展（本條與下一條，同項目互斥變體）cell 42-43 × 32-35
        --   3703704021 本體（再下一條）cell 43-44 × 33-36
        -- 兩張圖在 cell (43,33)(43,34)(43,35) 三格交疊，卻無 require/incompatible 互相
        -- 宣告 ⇒ 玩家可能只裝其中一張，伺服器 Map= 也通常只列一張。故三條都明寫
        -- mapDir 設掛載閘門（省略＝一律放行，未載入的那張會照樣畫框——同 SecretZ 據點回報）
        { zip = "Chinatown Expansion B42 version.pyramid.zip", mapMod = "Chinatown Expansion B42 version",
            mapDir = "Chinatown Expansion B42 version",
            bounds = { 10752, 8192, 11264, 9216 }, nameKey = "UI_MinidoracatMiniMapModMaps_Chinatown" },
        -- 同 Workshop 互斥變體（mod.info incompatible=本體）：同 zip/bounds 作 ID alias，
        -- 主 MOD 掛載（絕對路徑）與建層（indexOfLayer）自帶去重
        { zip = "Chinatown Expansion B42 version.pyramid.zip", mapMod = "Chinatown Expansion B42 version (Less Traffic Jam)",
            mapDir = "Chinatown Expansion B42 version",
            bounds = { 10752, 8192, 11264, 9216 }, nameKey = "UI_MinidoracatMiniMapModMaps_Chinatown" },
        { zip = "Chinatown B42 version.pyramid.zip", mapMod = "Chinatown B42 version",
            mapDir = "Chinatown B42 version",
            bounds = { 11008, 8448, 11520, 9472 }, nameKey = "UI_MinidoracatMiniMapModMaps_ChinatownBase" },
        { zip = "AnruisiTown.pyramid.zip", mapMod = "AnruisiTown", mapDir = "AnruisiTown",
            streetI18n = "anruisi-town",
            bounds = { 11776, 11008, 13056, 12032 }, nameKey = "UI_MinidoracatMiniMapModMaps_AnruisiTown" },
        { zip = "Asakusa lake town.pyramid.zip", mapMod = "Asakusa lake town",
            bounds = { 10496, 11264, 11264, 12032 }, nameKey = "UI_MinidoracatMiniMapModMaps_AsakusaLakeTown" },
        { zip = "AshenwoodNewB42.pyramid.zip", mapMod = "AshenwoodmodNewB42",
            bounds = { 11264, 11008, 11776, 11776 }, nameKey = "UI_MinidoracatMiniMapModMaps_Ashenwood" },
        { zip = "Atlanta - Safe Zone.pyramid.zip", mapMod = "Atlanta - Safe Zone-Chinese Survivors’ Community",
            bounds = { 8448, 7680, 9216, 8448 }, nameKey = "UI_MinidoracatMiniMapModMaps_AtlantaSafeZone" },
        { zip = "Atlanta Tower Survival.pyramid.zip", mapMod = "Atlanta Tower Survival",
            bounds = { 11008, 12544, 11520, 13056 }, nameKey = "UI_MinidoracatMiniMapModMaps_AtlantaTower" },
        { zip = "Atlanta.pyramid.zip", mapMod = "Atlanta",
            bounds = { 10496, 12288, 13056, 14592 }, nameKey = "UI_MinidoracatMiniMapModMaps_Atlanta" },
        { zip = "BlackpineCounty.pyramid.zip", mapMod = "BlackpineCounty",
            bounds = { 9728, 14080, 11776, 15360 }, nameKey = "UI_MinidoracatMiniMapModMaps_BlackpineCounty" },
        { zip = "Camden County B42.pyramid.zip", mapMod = "CamdenCountyB42", mapDir = "Camden County B42",
            streetI18n = "camden-county",
            bounds = { 12800, 8448, 19200, 14848 }, nameKey = "UI_MinidoracatMiniMapModMaps_CamdenCounty" },
        { zip = "Cathaya Valley2.0 highway.pyramid.zip", mapMod = "Cathaya Valley 2.0 B42 version highway",
            bounds = { 7424, 12288, 7936, 13312 }, nameKey = "UI_MinidoracatMiniMapModMaps_CathayaValleyHighway" },
        { zip = "Cathaya Valley2.0.pyramid.zip", mapMod = "Cathaya Valley 2.0 B42 version",
            bounds = { 7168, 12544, 7680, 13312 }, nameKey = "UI_MinidoracatMiniMapModMaps_CathayaValley" },
        { zip = "Constown, KY.pyramid.zip", mapMod = "Constown42",
            bounds = { 4864, 10752, 6400, 11520 }, nameKey = "UI_MinidoracatMiniMapModMaps_Constown" },
        { zip = "Coryerdon B42.pyramid.zip", mapMod = "CoryerdonB42",
            bounds = { 7168, 5632, 10752, 7424 }, nameKey = "UI_MinidoracatMiniMapModMaps_Coryerdon" },
        { zip = "Daisy County.pyramid.zip", mapMod = "Daisy County B42 version", mapDir = "Daisy County",
            streetI18n = "daisy-county",
            bounds = { 9728, 7168, 10752, 8192 }, nameKey = "UI_MinidoracatMiniMapModMaps_DaisyCounty" },
        { zip = "DawnTown.pyramid.zip", mapMod = "dawn_town",
            bounds = { 2816, 7936, 3328, 8448 }, nameKey = "UI_MinidoracatMiniMapModMaps_DawnTown" },
        { zip = "EchoCreek MilitaryBase.pyramid.zip", mapMod = "EchoCreek MilitaryBase",
            bounds = { 2816, 9984, 3840, 11008 }, nameKey = "UI_MinidoracatMiniMapModMaps_EchoCreek" },
        { zip = "EdsAutoSalvageB42.pyramid.zip", mapMod = "EdsAutoSalvageB42", mapDir = "EdsAutoSalvageB42",
            streetI18n = "eds-auto-salvage",
            bounds = { 8448, 8192, 9216, 8704 }, nameKey = "UI_MinidoracatMiniMapModMaps_EdsAutoSalvage" },
        { zip = "Erikas_Furniture_Store.pyramid.zip", mapMod = "Erikas_Furniture_Store",
            bounds = { 11264, 7936, 11776, 8448 }, nameKey = "UI_MinidoracatMiniMapModMaps_ErikasFurniture" },
        { zip = "Floatopia.pyramid.zip", mapMod = "Floatopia",
            bounds = { 4352, 5376, 4864, 5888 }, nameKey = "UI_MinidoracatMiniMapModMaps_Floatopia" },
        { zip = "Fort Benning B42.pyramid.zip", mapMod = "FortBenningB42",
            bounds = { 5888, 6656, 6400, 7424 }, nameKey = "UI_MinidoracatMiniMapModMaps_FortBenning" },
        { zip = "Fort JadeLake.pyramid.zip", mapMod = "Fort JadeLake",
            bounds = { 11008, 8448, 11520, 9216 }, nameKey = "UI_MinidoracatMiniMapModMaps_FortJadeLake" },
        { zip = "Fort Waterfront B42.pyramid.zip", mapMod = "Fort Waterfront B42",
            bounds = { 9984, 10752, 10752, 11264 }, nameKey = "UI_MinidoracatMiniMapModMaps_FortWaterfront" },
        { zip = "Fort_Boonesborough.pyramid.zip", mapMod = "Fort_Boonesborough",
            bounds = { 13824, 1792, 14592, 2048 }, nameKey = "UI_MinidoracatMiniMapModMaps_FortBoonesborough" },
        { zip = "Grapeseed.pyramid.zip", mapMod = "42Grapeseed",
            bounds = { 6144, 10752, 7680, 11776 }, nameKey = "UI_MinidoracatMiniMapModMaps_Grapeseed" },
        { zip = "Greenleaf.pyramid.zip", mapMod = "Greenleaf B42 version",
            bounds = { 6144, 9984, 6912, 11008 }, nameKey = "UI_MinidoracatMiniMapModMaps_Greenleaf" },
        { zip = "Hartburg, KY.pyramid.zip", mapMod = "hartburgb42",
            bounds = { 6400, 11008, 6912, 11776 }, nameKey = "UI_MinidoracatMiniMapModMaps_Hartburg" },
        -- 獵人基地：同 Workshop 兩個 mod ID（完整版／小型版），bounds 相同但 4 個 cell
        -- 檔有 1 個不同（cell 23_22 的 lotheader／lotpack／chunkdata／worldmap 全異）
        -- ⇒ 圖像不同，不能作同 zip alias（會讓裝小型版的玩家看到完整版的建築）
        { zip = "hunter's_base.pyramid.zip", mapMod = "Hunter'sBaseB42", mapDir = "hunter's_base",
            bounds = { 5888, 5632, 6400, 6144 }, nameKey = "UI_MinidoracatMiniMapModMaps_HuntersBase" },
        { zip = "hunter's_base_small.pyramid.zip", mapMod = "Hunter'sBaseB42Small", mapDir = "hunter's_base_small",
            bounds = { 5888, 5632, 6400, 6144 }, nameKey = "UI_MinidoracatMiniMapModMaps_HuntersBaseSmall" },
        { zip = "Hazelnut Manor.pyramid.zip", mapMod = "HazelnutManor",
            bounds = { 12544, 5888, 13056, 6400 }, nameKey = "UI_MinidoracatMiniMapModMaps_HazelnutManor" },
        { zip = "Hazelnut Manor[Poor Version].pyramid.zip", mapMod = "HazelnutManor[Poor Version]",
            bounds = { 12544, 5888, 13056, 6400 }, nameKey = "UI_MinidoracatMiniMapModMaps_HazelnutManorPoor" },
        { zip = "IrisEyot.pyramid.zip", mapMod = "IrisEyot",
            bounds = { 4096, 11008, 4864, 11520 }, nameKey = "UI_MinidoracatMiniMapModMaps_IrisEyot" },
        { zip = "Kentucky Center Manor_Renovation_B42.pyramid.zip", mapMod = "Kentucky Center Manor_Renovation",
            bounds = { 7936, 9472, 8448, 9984 }, nameKey = "UI_MinidoracatMiniMapModMaps_KentuckyCenterManor" },
        { zip = "KillMingLake.pyramid.zip", mapMod = "KillMingLake",
            bounds = { 8192, 11776, 8704, 12544 }, nameKey = "UI_MinidoracatMiniMapModMaps_KillMingLake" },
        { zip = "Kingsmouth North B42.pyramid.zip", mapMod = "KingsmouthNorthB42",
            bounds = { 0, 3840, 1280, 5120 }, nameKey = "UI_MinidoracatMiniMapModMaps_KingsmouthNorth" },
        { zip = "linzi.pyramid.zip", mapMod = "linzimod",
            bounds = { 8960, 11008, 9728, 11776 }, nameKey = "UI_MinidoracatMiniMapModMaps_WhiteForest" },
        { zip = "LittleTownshipB42.pyramid.zip", mapMod = "LittleTownshipB42", mapDir = "LittleTownshipB42",
            streetI18n = "little-township",
            bounds = { 7936, 8192, 8448, 8704 }, nameKey = "UI_MinidoracatMiniMapModMaps_LittleTownship" },
        -- 楓木林鎮與上面的小鎮區佔用**完全相同的 4 個 cell**（31-32 × 32-33），但 22 個
        -- 同名檔內容全異＝兩位作者的兩張不同地圖搶同一塊地（小鎮區作者自述「原作者出
        -- B42 版就會刪」，而本圖正是原作的 B42 版）⇒ 事實上互斥，靠 mapDir 閘門擇一顯示
        { zip = "Maplewood.pyramid.zip", mapMod = "Maplewood", mapDir = "Maplewood",
            streetI18n = "maplewood",
            bounds = { 7936, 8192, 8448, 8704 }, nameKey = "UI_MinidoracatMiniMapModMaps_Maplewood" },
        { zip = "Louisville_Riverboat.pyramid.zip", mapMod = "Louisville_Riverboat",
            bounds = { 13056, 1024, 13312, 1280 }, nameKey = "UI_MinidoracatMiniMapModMaps_LouisvilleRiverboat" },
        { zip = "Megurigaoka City, Kanagawa.pyramid.zip", mapMod = "Project Gurashi",
            mapDir = "Megurigaoka City, Kanagawa", streetI18n = "megurigaoka-city",
            bounds = { 0, 2304, 1280, 4864 }, nameKey = "UI_MinidoracatMiniMapModMaps_Megurigaoka" },
        -- 街名只保留本圖獨有的 175 條：另 917 條與 vanilla Muldraugh 同座標（本圖是
        -- 重製版），保留會與本體漢化的中文疊畫；見 street-names/muldraugh-1993 的 keep_geometry
        { zip = "Muldraugh 1993 B42.pyramid.zip", mapMod = "muldraugh1993b42",
            mapDir = "Muldraugh 1993 B42", streetI18n = "muldraugh-1993",
            bounds = { 10496, 8960, 11264, 11008 }, nameKey = "UI_MinidoracatMiniMapModMaps_Muldraugh1993" },
        { zip = "Muldraugh-SouthernCheckpoint.pyramid.zip", mapMod = "Muldraugh-Checkpoint",
            bounds = { 10496, 10752, 11008, 11520 }, nameKey = "UI_MinidoracatMiniMapModMaps_MuldraughOverpass" },
        { zip = "muldraughmilitarybaseas24.pyramid.zip", mapMod = "muldraughmilitarybaseas24",
            bounds = { 8448, 10752, 9472, 11520 }, nameKey = "UI_MinidoracatMiniMapModMaps_FortPreston" },
        { zip = "Nekomata Ridge.pyramid.zip", mapMod = "Nekomata Ridge",
            mapDir = "Nekomata Ridge",
            bounds = { 11776, 8192, 13312, 9216 }, nameKey = "UI_MinidoracatMiniMapModMaps_NekomataRidge" },
        { zip = "Nettle Township.pyramid.zip", mapMod = "Nettle Township B42 version",
            bounds = { 6400, 8960, 7424, 9728 }, nameKey = "UI_MinidoracatMiniMapModMaps_NettleTownship" },
        { zip = "Path of Zenith, Louisville.pyramid.zip", mapMod = "PZ_ACSM_LV",
            bounds = { 12800, 768, 13312, 1280 }, nameKey = "UI_MinidoracatMiniMapModMaps_PathOfZenith" },
        { zip = "pzkNewCoalfield.pyramid.zip", mapMod = "PZKNewCoalfieldTownMap",
            bounds = { 2816, 8192, 3584, 8960 }, nameKey = "UI_MinidoracatMiniMapModMaps_NewCoalfield" },
        { zip = "RaccoonCity.pyramid.zip", mapMod = "RaccoonCityB42",
            bounds = { 9728, 9728, 10496, 10752 }, nameKey = "UI_MinidoracatMiniMapModMaps_RaccoonCity" },
        { zip = "Raven Creek B42.pyramid.zip", mapMod = "RavenCreekB42", mapDir = "Raven Creek B42",
            streetI18n = "raven-creek",
            bounds = { 4096, 14336, 6656, 17920 }, nameKey = "UI_MinidoracatMiniMapModMaps_RavenCreek" },
        -- Kardinal 團隊的另一個 B42 移植版：與上者同地圖資料夾名（二選一，勿同時啟用），
        -- 但圖資內容不同且範圍更大，故獨立渲染；靠 mapMod 各自偵測
        { zip = "Kardinal Raven Creek B42.pyramid.zip", mapMod = "kardinal_ravencreek_B42",
            mapDir = "Raven Creek B42", streetI18n = "raven-creek-kardinal",
            bounds = { 4096, 14336, 7168, 18176 }, nameKey = "UI_MinidoracatMiniMapModMaps_RavenCreekKardinal" },
        { zip = "RMSafeHouseUnofficial.pyramid.zip", mapMod = "RMSafeHouseUnofficial",
            bounds = { 5376, 4864, 5888, 5632 }, nameKey = "UI_MinidoracatMiniMapModMaps_RiversideMansion" },
        { zip = "RustBury.pyramid.zip", mapMod = "rustbury_2026_b42", mapDir = "RustBury",
            bounds = { 8960, 12544, 9472, 13056 }, nameKey = "UI_MinidoracatMiniMapModMaps_RustBury" },
        -- 安泊戍鎮（Safeharbor Garrison，Workshop 3522517059）：上游 mod.info 真的是
        -- id=modid（作者未改模板佔位符，2026-08-11 實查本機訂閱檔確認），勿「修正」此值
        { zip = "SafeharborGarrison.pyramid.zip", mapMod = "modid",
            bounds = { 11520, 10496, 12800, 11520 }, nameKey = "UI_MinidoracatMiniMapModMaps_SafeharborGarrison" },
        { zip = "SafeWayHamlet.pyramid.zip", mapMod = "SafeWayHamlet",
            bounds = { 12544, 10752, 13056, 11520 }, nameKey = "UI_MinidoracatMiniMapModMaps_SafeWayHamlet" },
        -- 日落湖鎮的 story addon（id 同名加 "(story addon)"）沒有自己的 media/maps，
        -- 且 require= 本圖 ⇒ 不需另立條目
        { zip = "Sunset Lake Town B42 version.pyramid.zip", mapMod = "Sunset Lake Town B42 version",
            mapDir = "Sunset Lake Town B42 version",
            bounds = { 9472, 11008, 10240, 12032 }, nameKey = "UI_MinidoracatMiniMapModMaps_SunsetLakeTown" },
        { zip = "Sunset Tower.pyramid.zip", mapMod = "SunsetTower", mapDir = "Sunset Tower",
            bounds = { 11264, 7168, 11776, 7680 }, nameKey = "UI_MinidoracatMiniMapModMaps_SunsetTower" },
        -- SecretZ：單一 mod 內 12 個獨立據點目錄，MP 伺服器常只挑部分進 Map=
        -- ——逐條指定 mapDir，未載入的據點不畫（需主 MOD ≥ mapDir 支援版）
        { zip = "SZ_Bunker_3.pyramid.zip", mapMod = "Secretz42", mapDir = "SZ_Bunker_3",
            bounds = { 5888, 11520, 6400, 12032 }, nameKey = "UI_MinidoracatMiniMapModMaps_SZBunker3" },
        { zip = "SZ_Checkpoint1.pyramid.zip", mapMod = "Secretz42", mapDir = "SZ_Checkpoint1",
            bounds = { 11776, 7936, 12544, 8448 }, nameKey = "UI_MinidoracatMiniMapModMaps_SZCheckpoint1" },
        { zip = "SZ_Checkpoint5.pyramid.zip", mapMod = "Secretz42", mapDir = "SZ_Checkpoint5",
            bounds = { 10752, 11008, 11264, 11520 }, nameKey = "UI_MinidoracatMiniMapModMaps_SZCheckpoint5" },
        { zip = "SZ_Checkpoint6.pyramid.zip", mapMod = "Secretz42", mapDir = "SZ_Checkpoint6",
            bounds = { 5632, 5632, 6144, 6144 }, nameKey = "UI_MinidoracatMiniMapModMaps_SZCheckpoint6" },
        { zip = "SZ_Checkpoint8.pyramid.zip", mapMod = "Secretz42", mapDir = "SZ_Checkpoint8",
            bounds = { 6400, 11008, 6912, 11520 }, nameKey = "UI_MinidoracatMiniMapModMaps_SZCheckpoint8" },
        { zip = "SZ_DeerheadLake_Base.pyramid.zip", mapMod = "Secretz42", mapDir = "SZ_DeerheadLake_Base",
            bounds = { 4352, 8192, 4864, 8704 }, nameKey = "UI_MinidoracatMiniMapModMaps_SZDeerheadLake" },
        { zip = "SZ_Louisville_Military_Complex.pyramid.zip", mapMod = "Secretz42", mapDir = "SZ_Louisville_Military_Complex",
            bounds = { 13568, 1792, 15360, 3072 }, nameKey = "UI_MinidoracatMiniMapModMaps_SZLouisvilleMilitary" },
        { zip = "SZ_MarchRidge_ResearchFacility.pyramid.zip", mapMod = "Secretz42", mapDir = "SZ_MarchRidge_ResearchFacility",
            bounds = { 9984, 11776, 10752, 12800 }, nameKey = "UI_MinidoracatMiniMapModMaps_SZMarchRidgeResearch" },
        { zip = "SZ_Muldraugh_Traindepot_Refugee.pyramid.zip", mapMod = "Secretz42", mapDir = "SZ_Muldraugh_Traindepot_Refugee",
            bounds = { 11264, 9472, 12032, 10752 }, nameKey = "UI_MinidoracatMiniMapModMaps_SZTrainDepot" },
        { zip = "SZ_MuldraughCrossroads_Checkpoint.pyramid.zip", mapMod = "Secretz42", mapDir = "SZ_MuldraughCrossroads_Checkpoint",
            bounds = { 10496, 11008, 11008, 11520 }, nameKey = "UI_MinidoracatMiniMapModMaps_SZCrossroads" },
        { zip = "SZ_North_Checkpoint.pyramid.zip", mapMod = "Secretz42", mapDir = "SZ_North_Checkpoint",
            bounds = { 3584, 6400, 4352, 7424 }, nameKey = "UI_MinidoracatMiniMapModMaps_SZNorthCheckpoint" },
        { zip = "SZ_The_Mall.pyramid.zip", mapMod = "Secretz42", mapDir = "SZ_The_Mall",
            bounds = { 13568, 5632, 14336, 6144 }, nameKey = "UI_MinidoracatMiniMapModMaps_SZTheMall" },
        { zip = "SZ_Westpoint_Bridge_Checkpoint.pyramid.zip", mapMod = "Secretz42", mapDir = "SZ_Westpoint_Bridge_Checkpoint",
            bounds = { 12288, 6400, 12800, 6912 }, nameKey = "UI_MinidoracatMiniMapModMaps_SZWestpointBridge" },
        { zip = "SZ_Riverside_Checkpoint_1.pyramid.zip", mapMod = "Secretz42", mapDir = "SZ_Riverside_Checkpoint_1",
            bounds = { 6400, 6400, 6912, 6912 }, nameKey = "UI_MinidoracatMiniMapModMaps_SZRiverside1" },
        -- Riverside_2 與六號檢查站同 bounds 但內容不同（作者重建版）：mapDir 閘門依伺服器載入者擇一顯示
        { zip = "SZ_Riverside_Checkpoint_2.pyramid.zip", mapMod = "Secretz42", mapDir = "SZ_Riverside_Checkpoint_2",
            bounds = { 5632, 5632, 6144, 6144 }, nameKey = "UI_MinidoracatMiniMapModMaps_SZRiverside2" },
        { zip = "taibeiroad.pyramid.zip", mapMod = "Taibeiroad4",
            bounds = { 7936, 9984, 9216, 11776 }, nameKey = "UI_MinidoracatMiniMapModMaps_Taibeiroad" },
        { zip = "Taylorsville.pyramid.zip", mapMod = "Taylorsville",
            bounds = { 8960, 6144, 10496, 7680 }, nameKey = "UI_MinidoracatMiniMapModMaps_Taylorsville" },
        { zip = "Tikitown.pyramid.zip", mapMod = "tikitown", mapDir = "Tikitown",
            streetI18n = "tikitown",
            bounds = { 6400, 6656, 7936, 7936 }, nameKey = "UI_MinidoracatMiniMapModMaps_Tikitown" },
        { zip = "Trapalaketown.pyramid.zip", mapMod = "TrapalaketownB42",
            bounds = { 8192, 11520, 9216, 12032 }, nameKey = "UI_MinidoracatMiniMapModMaps_Trapalaketown" },
        -- Kardinal 團隊把 B41 的 Trelai 4x4 移植到 B42（作者自述重映射到 cell 25,25..30,30）：
        -- 與上面的提基鎮範圍大幅重疊（cell 25-30 × 26-30），兩者都靠 mapDir 閘門擇一顯示
        { zip = "Trelai_4x4.pyramid.zip", mapMod = "Trelai_B42", mapDir = "Trelai_4x4",
            bounds = { 6400, 6400, 7936, 7936 }, nameKey = "UI_MinidoracatMiniMapModMaps_TrelaiKardinal" },
        { zip = "vilaz.pyramid.zip", mapMod = "VilaZMap",
            bounds = { 9472, 9472, 9984, 9984 }, nameKey = "UI_MinidoracatMiniMapModMaps_VilaZ" },
        { zip = "West Point Expansion_B42.pyramid.zip", mapMod = "WestPointExpansionB42",
            mapDir = "West Point Expansion_B42", streetI18n = "west-point-expansion",
            bounds = { 11776, 6400, 13312, 7680 }, nameKey = "UI_MinidoracatMiniMapModMaps_WestPointExpansion" },
        { zip = "WILDSTEEL.pyramid.zip", mapMod = "WILDSTEEL", mapDir = "WILDSTEEL",
            streetI18n = "wildsteel",
            bounds = { 14336, 5632, 14848, 6144 }, nameKey = "UI_MinidoracatMiniMapModMaps_FortSpiffo" },
        { zip = "Willowbrook Bastion!.pyramid.zip", mapMod = "Willowbrook Bastion!",
            bounds = { 8448, 9472, 9728, 10240 }, nameKey = "UI_MinidoracatMiniMapModMaps_WillowbrookBastion" },
        -- 同 Workshop 互斥變體（雙向 incompatible=），但 2026 版是重製圖（59 個 cell
        -- 檔 50 個不同、作者描述 2x2→3x2）＝圖像不同，不能作同 zip alias（那會讓啟用
        -- 2026 版的玩家看到舊城鎮的圖）：各自一顆 zip、各自 nameKey，bounds 恰好相同
        { zip = "Willowbrook Bastion! 2026.pyramid.zip", mapMod = "Willowbrook Bastion! 2",
            bounds = { 8448, 9472, 9728, 10240 }, nameKey = "UI_MinidoracatMiniMapModMaps_WillowbrookBastion2026" },
        { zip = "Clover Lake.pyramid.zip", mapMod = "Clover Lake", mapDir = "Clover Lake",
            streetI18n = "clover-lake",
            bounds = { 9472, 8960, 9984, 9984 }, nameKey = "UI_MinidoracatMiniMapModMaps_CloverLake" },
        { zip = "Bunker 42.pyramid.zip", mapMod = "Bunker42",
            bounds = { 11008, 9728, 11520, 10240 }, nameKey = "UI_MinidoracatMiniMapModMaps_Bunker42" },
        { zip = "Greenport, KY.pyramid.zip", mapMod = "GreenportB42", mapDir = "Greenport, KY",
            streetI18n = "greenport",
            bounds = { 7936, 7168, 8704, 7936 }, nameKey = "UI_MinidoracatMiniMapModMaps_Greenport" },
        -- NewEllroy+Shadyside：一 mod 兩鎮，同 SecretZ 逐條 mapDir
        { zip = "New Ellroy.pyramid.zip", mapMod = "NewEllroyShadysideB42", mapDir = "New Ellroy",
            bounds = { 4864, 9728, 5888, 10752 }, nameKey = "UI_MinidoracatMiniMapModMaps_NewEllroy" },
        { zip = "Shadyside.pyramid.zip", mapMod = "NewEllroyShadysideB42", mapDir = "Shadyside",
            bounds = { 5632, 9728, 6400, 10752 }, nameKey = "UI_MinidoracatMiniMapModMaps_Shadyside" },
        { zip = "Blackmaze_wp.pyramid.zip", mapMod = "blackmaze_wp", mapDir = "Blackmaze_wp",
            streetI18n = "blackmaze-wp",
            bounds = { 10752, 6144, 11264, 6656 }, nameKey = "UI_MinidoracatMiniMapModMaps_BridgeCitadel" },
        { zip = "ningzi.pyramid.zip", mapMod = "White_forest_ridge",
            bounds = { 8960, 11520, 9728, 12800 }, nameKey = "UI_MinidoracatMiniMapModMaps_WhiteForestRidge" },
        { zip = "Yanghu Town.pyramid.zip", mapMod = "Yanghu Town",
            bounds = { 8448, 8960, 9728, 9728 }, nameKey = "UI_MinidoracatMiniMapModMaps_YanghuTown" },
        { zip = "Begonia_Town.pyramid.zip", mapMod = "Begonia_Town",
            bounds = { 11264, 7424, 12544, 7936 }, nameKey = "UI_MinidoracatMiniMapModMaps_BegoniaTown" },
        { zip = "Frogtown.pyramid.zip", mapMod = "Frogtown",
            bounds = { 2816, 6656, 4096, 7680 }, nameKey = "UI_MinidoracatMiniMapModMaps_Frogtown" },
        { zip = "HavenFall.pyramid.zip", mapMod = "HavenFall",
            bounds = { 4096, 8448, 5120, 9472 }, nameKey = "UI_MinidoracatMiniMapModMaps_HavenFall" },
        { zip = "Macon.pyramid.zip", mapMod = "Macon",
            bounds = { 3584, 6400, 4608, 6912 }, nameKey = "UI_MinidoracatMiniMapModMaps_MaconTWD" },
        { zip = "Xixi's Serene Cottage.pyramid.zip", mapMod = "Xixi's Serene Cottage",
            bounds = { 7424, 7936, 7936, 8448 }, nameKey = "UI_MinidoracatMiniMapModMaps_XixiCottage" },
        -- VaultTec：一 mod 四座避難所，逐條 mapDir（MP 伺服器 Map= 未載入的不誤畫）；
        -- Louisville 座與 SecretZ 路易斯維爾軍事複合區範圍重疊（各自依啟用 mod 顯示，非衝突）
        { zip = "VaultTec_Louisville.pyramid.zip", mapMod = "VaultTec B42 version", mapDir = "VaultTec_Louisville",
            bounds = { 14336, 2560, 14848, 3072 }, nameKey = "UI_MinidoracatMiniMapModMaps_VaultTecLouisville" },
        { zip = "VaultTec_Muldraugh.pyramid.zip", mapMod = "VaultTec B42 version", mapDir = "VaultTec_Muldraugh",
            bounds = { 12288, 8960, 12800, 9472 }, nameKey = "UI_MinidoracatMiniMapModMaps_VaultTecMuldraugh" },
        { zip = "VaultTec_road.pyramid.zip", mapMod = "VaultTec B42 version", mapDir = "VaultTec_road",
            bounds = { 11776, 8960, 12544, 9472 }, nameKey = "UI_MinidoracatMiniMapModMaps_VaultTecRoad" },
        { zip = "VaultTec_Rosewood.pyramid.zip", mapMod = "VaultTec B42 version", mapDir = "VaultTec_Rosewood",
            bounds = { 5888, 10496, 6400, 11008 }, nameKey = "UI_MinidoracatMiniMapModMaps_VaultTecRosewood" },
    })
else
    print("[MinidoracatMiniMapModMaps] 找不到主 MOD API（MinidoracatMiniMapAPI）——請安裝並啟用 Minidoracat MiniMap for B42 主 MOD")
end
