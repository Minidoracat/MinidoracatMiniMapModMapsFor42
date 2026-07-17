# Changelog

## [42.19.0-0.2.0] - 2026-07-17

### 新增

- 一口氣新增 **69 張地圖**註冊（54 個 Workshop 項目，含 SecretZ 12 個據點、
  Sector-7／銀杉谷／亞特蘭大的子模組變體、榛果莊園簡樸版），全部由
  pzmap CLI 依 lotheader 佔用 cell 批次渲染（bounds 取自 pyramid.txt，零手算）。
- 對應四語（繁中/簡中/英/日）地圖名稱翻譯 69 組。
- 支援清單同步至 [Steam 收藏 3766382352](https://steamcommunity.com/sharedfiles/filedetails/?id=3766382352)。

### 已知限制

- 少數地圖引用未上架／未安裝的第三方材質包（台北路、特拉帕湖鎮最多），
  或不存在的表名（裸 `roofs_06` 等）——這些在遊戲內同樣不顯示，
  小地圖行為與遊戲一致。（B42.19 新版 ramps／時鐘包缺口已於渲染器端修復，
  全部地圖以修復後版本重渲。）
- White Wolf Ridge（3499861271）已從 Workshop 下架，未收錄。

## [42.19.0-0.1.0] - 2026-07-12

### 新增

- 專案初始版本：主 MOD 的地圖包 addon（`require=MinidoracatMiniMapFor42`），
  經 `MinidoracatMiniMapAPI.registerMaps` 註冊地圖清單。
- 首批三張地圖：Muldraugh 消防局（`beek_muldraugh_firedept`，overlay 型）、
  Estate 39（獨立區域）、唐人街擴張區（`Chinatown Expansion B42 version`，
  含 Less Traffic Jam 互斥變體 alias）。
- 四語（繁中/簡中/英/日）地圖名稱翻譯。
