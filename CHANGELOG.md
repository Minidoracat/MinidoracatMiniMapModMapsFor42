# Changelog

## [42.19.0-0.3.0] - 2026-07-17

### 新增

- 新增 **8 張地圖**（7 個 Workshop 項目）：四葉草湖畔農莊、42 號地堡、綠港、
  新艾爾羅伊＋沙德賽德（同項目雙地圖）、西點橋城、白森嶺、楊湖鎮；
  對應四語翻譯 8 組。累計 **64 個地圖 MOD／80 張地圖**。
- 收藏頁描述新增「載入順序提醒」區（Coryerdon/途安里/四葉草湖畔農莊之作者聲明）。
- link_workshop 的 Map= 安全順序表加入 Clover Lake（作者要求高於 7 號淪陷區公路，
  否則湖心小屋地下室消失）與 Coryerdon（bg300 潛在雷，需在 Greenport 前）。
- 三語描述、收藏頁與許願串新增「支援範圍」分流說明：本包只負責小地圖圖像渲染，
  圖像問題回報本包、地圖 MOD 本身的 BUG 回報原作者。

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
