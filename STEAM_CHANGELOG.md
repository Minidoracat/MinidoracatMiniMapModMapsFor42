[h1]Minidoracat MiniMap - MOD Maps for B42 42.20.0-0.4.1[/h1]
[i]2026-07-29[/i]

[h3]• 更新[/h3]
[list]
[*] [b]遊戲 42.20 全量重渲 81 張 pyramid（收錄全數）[/b]：42.20 更新了主世界 950 個 cell
[/list]
（Muldraugh／Rosewood／Riverside／West Point 城區），MOD 未覆蓋的 cell 會
透出 vanilla 基底——71 張與更新區有交集；一併吃到渲染工具 42.20 巨樹修正
（JumboTreesBigs2x 補載＋JUMBOXL/XXL anchor）與 Tiles2x 重打包。全部輸出
bounds 與 Lua 註冊表逐張驗證一致，註冊表零改動。
[list]
[*] 0.4.0 備忘的 [b]Frogtown／HavenFall[/b] 亦已重渲。
[*] [b]移除 3 張已下架地圖的支援[/b]（Workshop 原項目已下架，無法再重渲且下架項
[/list]
會造成伺服器安裝問題）：Meiya'sTown、Sector-7 Breach、Sector-7 Breach
Highway——Lua 註冊、四語翻譯、pyramid zip 與收錄清單一併移除，收錄降為
[b]66 個地圖 MOD／81 張地圖[/b]。
[list]
[*] 新增 scripts/rebuild_pyramids.py：讀 Lua 註冊表批次重渲（workshop 定位
[/list]
mod 根目錄、bounds→--region 還原、require= 一層 tile pack 依賴、渲後
bounds 驗證），支援 --dry-run／--only。
[list]
[*] 支援版本字樣 42.20.0+（mod.info modversion=42.20.0-0.4.1、versionMin=42.20.0）。
[/list]
