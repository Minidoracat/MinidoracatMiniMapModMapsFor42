-- MinidoracatMiniMapModMaps.lua — Minidoracat 小地圖「地圖包」（純資料註冊，
-- 掛載/框線/選項等本體邏輯全在主 MOD MinidoracatMiniMapFor42）。
-- mod.info 的 require=MinidoracatMiniMapFor42 保證主 MOD 的 client lua 先載入，
-- 此時 MinidoracatMiniMapAPI 已存在；主 MOD 於 OnGameBoot 檢查「有註冊」才會
-- 顯示地圖包相關選項（顯示 MOD 地圖區塊／框線開關／框線顏色）。
--
-- 條目格式（同主 MOD MAPS manifest）：
--   zip     = 本 MOD media/minimap/ 下的 pyramid zip 檔名（pzmap Studio 預設輸出名）
--   mapMod  = 對應地圖 MOD 的 mod ID（啟用才掛載）
--   bounds  = 渲染時 pyramid.txt 的世界 square 座標（右/下排他）
--   nameKey = UI.json 翻譯鍵（缺譯退 mapMod）
if MinidoracatMiniMapAPI and MinidoracatMiniMapAPI.registerMaps then
    MinidoracatMiniMapAPI.registerMaps("MinidoracatMiniMapModMapsFor42", {
        { zip = "Muldraugh_FireDept.pyramid.zip", mapMod = "beek_muldraugh_firedept",
            bounds = { 10496, 8960, 11008, 9472 }, nameKey = "UI_MinidoracatMiniMapModMaps_MuldraughFireDept" },
        { zip = "Estate 39.pyramid.zip", mapMod = "Estate 39",
            bounds = { 8192, 9728, 8704, 10240 }, nameKey = "UI_MinidoracatMiniMapModMaps_Estate39" },
        { zip = "Chinatown Expansion B42 version.pyramid.zip", mapMod = "Chinatown Expansion B42 version",
            bounds = { 10752, 8192, 11264, 9216 }, nameKey = "UI_MinidoracatMiniMapModMaps_Chinatown" },
        -- 同 Workshop 互斥變體（mod.info incompatible=本體）：同 zip/bounds 作 ID alias，
        -- 主 MOD 掛載（絕對路徑）與建層（indexOfLayer）自帶去重
        { zip = "Chinatown Expansion B42 version.pyramid.zip", mapMod = "Chinatown Expansion B42 version (Less Traffic Jam)",
            bounds = { 10752, 8192, 11264, 9216 }, nameKey = "UI_MinidoracatMiniMapModMaps_Chinatown" },
    })
else
    print("[MinidoracatMiniMapModMaps] 找不到主 MOD API（MinidoracatMiniMapAPI）——請安裝並啟用 Minidoracat MiniMap for B42 主 MOD")
end
