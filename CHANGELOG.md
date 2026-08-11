# Changelog

## [42.20.0-0.5.0] - 2026-08-11

### 新增

- **9 張新地圖**，累計 **69 個地圖 MOD／90 張地圖**。
- **SecretZ 三個新據點**：西點大橋檢查站、河濱鎮一號／二號檢查站
  （二號與六號檢查站同區域、為作者重建版本，依伺服器實際載入自動擇一顯示）。
- **汐汐的靜謐小屋**（Xixi's Serene Cottage，許願串點播）。
- **VaultTec 四座避難所**（Louisville／Muldraugh／聯絡道路／Rosewood，
  許願串點播；逐據點偵測，未載入的避難所不誤畫）。
- **渡鴉溪（Kardinal 移植版）**（Kardinal Raven Creek B42，商店頁點播）：Kardinal 團隊的
  另一個 B42 移植版，範圍比原版往東南各多兩格 cell，已獨立渲染。與原版渡鴉溪
  **二選一**（兩者地圖資料夾同名，勿同時啟用）——裝哪一版就顯示哪一版的圖。
- 問題回報與新地圖申請新增 **GitHub 表單管道**（商店頁與許願串有連結，
  含地圖支援申請與圖像問題回報兩種表單）。

### 更新

- **全量重渲 90 張 pyramid**：17 個地圖 MOD 上游於 7 月底全量重渲後又有更新，
  本版全部吃到最新內容（其中 Tikitown、SecretZ、Haven Fall 有實際圖資變更）。
- **SecretZ 北方檢查站**：上游地圖向北擴張一格 cell，範圍框線與圖像已同步擴展。
- 支援地圖收藏移除兩個已下架項目（美雅鎮、Sector-7——支援已於 0.4.1 移除，
  收藏不再掛訂閱不到的死連結）。

> 技術要點：新增每日上游追蹤器（收藏 watchlist＋圖資 hash 重渲精準判定＋遊戲
> buildid 軸，CI 三 job 權限分離）；rebuild_pyramids 新增 --prefer／--skip-fresh-min
> 並修 require 反斜線前綴解析；安泊戍鎮 mapMod="modid" 查證為上游原樣已加註。

## [42.20.0-0.4.1] - 2026-07-29

### 更新

- **遊戲 42.20 全量重渲 81 張 pyramid（收錄全數）**：42.20 更新了主世界 950 個 cell
  （Muldraugh／Rosewood／Riverside／West Point 城區），MOD 未覆蓋的 cell 會
  透出 vanilla 基底——71 張與更新區有交集；一併吃到渲染工具 42.20 巨樹修正
  （JumboTreesBigs2x 補載＋JUMBOXL/XXL anchor）與 Tiles2x 重打包。全部輸出
  bounds 與 Lua 註冊表逐張驗證一致，註冊表零改動。
- 0.4.0 備忘的 **Frogtown／HavenFall** 亦已重渲。
- **移除 3 張已下架地圖的支援**（Workshop 原項目已下架，無法再重渲且下架項
  會造成伺服器安裝問題）：Meiya'sTown、Sector-7 Breach、Sector-7 Breach
  Highway——Lua 註冊、四語翻譯、pyramid zip 與收錄清單一併移除，收錄降為
  **66 個地圖 MOD／81 張地圖**。
- 新增 `scripts/rebuild_pyramids.py`：讀 Lua 註冊表批次重渲（workshop 定位
  mod 根目錄、bounds→--region 還原、require= 一層 tile pack 依賴、渲後
  bounds 驗證），支援 `--dry-run`／`--only`。
- 支援版本字樣 42.20.0+（mod.info modversion=42.20.0-0.4.1、versionMin=42.20.0）。

## [42.19.0-0.4.0] - 2026-07-20

### 新增

- 新增 **4 張地圖**（4 個 Workshop 項目，baker 於許願串點播）：海棠鎮
  （`Begonia_Town`）、青蛙鎮（`Frogtown`）、海文弗爾（`HavenFall`）、
  梅肯／陰屍路（`Macon`）；對應四語翻譯 4 組。累計 **68 個地圖 MOD／84 張地圖**。
- 注意：Frogtown 與 Haven Fall 原作者仍在施工（Alpha／部分地圖），
  日後地圖更新時需重渲對應 pyramid。

### 修正

- **SecretZ／NewEllroy+Shadyside 逐圖顯示**（玩家 baker 於許願串回報）：
  這兩個「單一 mod 內含多張地圖」的項目，MP 伺服器可在 `Map=` 只挑部分地圖載入，
  原本只看 mod ID 會把未載入的據點也畫出來。14 個條目（SecretZ 12 據點＋
  New Ellroy＋Shadyside）逐條補上 `mapDir`（主 MOD 新增的選配欄位），
  未載入的地圖不再誤畫；單機與其餘單地圖 MOD 行為不變。需搭配主 MOD 對應版本。

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
