<!-- Steam 討論區貼文稿源；清單來自 docs/road-data.md（road-scan 生成），清單變動時同步 -->
<!-- 討論串網址：https://steamcommunity.com/workshop/filedetails/discussion/3763914102/569297034317714585/ -->
<!-- 標題：📢 MOD 地圖支援告知：圖片、道路資料與導航 -->

[b]English version:[/b] [url=https://steamcommunity.com/workshop/filedetails/discussion/3763914102/586187095760050473/]MOD Map Support Notice[/url]

[b]「支援地圖清單」表示圖片支援，不是道路導航或自動駕駛保證。[/b]

[h2]本包提供什麼[/h2]
此 addon 提供地圖圖片、街名對照，以及少數本包自製或修正的道路資料。翻譯只換名稱；道路修正與補充道路另走與語言無關的資料，由小地圖本體在來源幾何符合預期時套用。這不是自動補齊或修好所有道路，也不修改實際地形或建築。本包與小地圖本體請一起更新並重啟遊戲。

[h2]路名、搜尋與導航靠作者的道路資料[/h2]
地圖上的路名、路名搜尋、導航與自動駕駛路網，都來自地圖作者在 MOD 內附的原生 streets.xml。作者沒附道路資料的地圖，圖片照常顯示，但該區域沒有路名、搜不到路，也無法導航——這不是本包漏做翻譯。
道路座標、路寬、彎道與路口必須符合實際路面；缺漏、斷路或錯位可能造成無路線、繞路或偏離道路。地圖重疊及優先序也會影響採用的道路：require 只安排主 MOD 與本包的相依順序，不保證衝突地圖能共存；多人模式依伺服器 Map= 的地圖順序，低優先區域的街道可能被排除，讓原名與譯名都搜不到。
街道搜尋的[b]「MOD 地圖：地圖名稱」[/b]只辨識可確認的來源，不是錯誤標記或自駕認證。

[h2]🛠️ 本包自製或修正的道路[/h2]
[list]
[*] [b]康斯鎮（Constown, KY）[/b]：補充道路 37 條。作者沒放進道路資料的路由本包補上，路名為「康斯鎮 01 號路（小地圖補）」～「康斯鎮 37 號路（小地圖補）」，可搜尋與導航；作者日後提供道路資料時自動改用作者的。[i]（下一版推出）[/i]
[*] [b]卡姆登郡（Camden County）[/b]：斷點接線 3 處。作者的路停在路口前，導航／自動駕駛到不了；接回路網後沿用作者路名。[i]（下一版推出）[/i]
[*] [b]雛菊郡（Daisy County）[/b]：輪廓道路改中心線 44 條，避免路名上下各顯示一次並讓導航走路中央。
[*] [b]馬爾德勞 1993（Muldraugh 1993）[/b]：與官方地圖逐點相同的 913 筆重複路名只隱藏顯示，不刪導航道路；不確定或部分重疊仍保留名稱。
[/list]

[h2]✅ 作者有提供道路資料的地圖（22 張）[/h2]
[list]
[*] 安瑞斯鎮（軍事堡壘） — AnruisiTown (Military Bastion)：59 條
[*] 卡姆登郡 — Camden County：40 條
[*] 雛菊郡 — Daisy County：44 條
[*] 艾德汽車回收場 — Ed's Auto Salvage：3 條
[*] 小鎮區 — LittleTownship：4 條
[*] 楓木林鎮 — Maplewood：12 條
[*] 巡之丘市（學園孤島） — Megurigaoka, Kanagawa：2 條
[*] Muldraugh 1993：1092 條
[*] 渡鴉溪 — Raven Creek：45 條
[*] 渡鴉溪（Kardinal 移植版） — Raven Creek (Kardinal port)：45 條
[*] SecretZ 五號檢查站 — SecretZ Checkpoint 5：1 條
[*] SecretZ 八號檢查站 — SecretZ Checkpoint 8：2 條
[*] SecretZ 馬奇嶺研究設施 — SecretZ March Ridge Research Facility：2 條
[*] SecretZ 西點大橋檢查站 — SecretZ West Point Bridge Checkpoint：4 條
[*] SecretZ 河濱鎮一號檢查站 — SecretZ Riverside Checkpoint 1：2 條
[*] SecretZ 河濱鎮二號檢查站 — SecretZ Riverside Checkpoint 2：4 條
[*] 提基鎮＆發電廠 — Tikitown & PowerPlant：99 條
[*] 西點擴張區 — West Point Expansion：18 條
[*] 斯皮福堡（WILDSTEEL） — WILDSTEEL - Fort Spiffo：4 條
[*] 四葉草湖畔農莊 — Clover Lake Farmhouse：1 條
[*] 綠港 — Greenport, KY：15 條
[*] 西點橋城 — West Point: The Bridge Citadel：4 條
[/list]

[h2]❌ 作者沒有提供道路資料的地圖（79 張）[/h2]
以下地圖圖片照常顯示，但沒有路名、搜尋與導航（除了上方本包補過的地圖）。
[list]
[*] Muldraugh 消防局 — Muldraugh Fire Dept
[*] Estate 39 莊園 — Estate 39
[*] 阿特拉斯地下複合設施（地表） — Atlas Underground Complex (Surface)
[*] 唐人街擴張區 — Chinatown Expansion
[*] 唐人街 — Chinatown
[*] 淺草湖畔小鎮 — Asakusa Lake Town
[*] 灰木鎮 — Ashenwood
[*] 亞特蘭大安全區（華人社區） — Atlanta Safe Zone
[*] 亞特蘭大大廈生存 — Atlanta Tower Survival
[*] 亞特蘭大 — Atlanta
[*] 黑松郡 — Blackpine County
[*] 銀杉谷 2.0－公路 — Cathaya Valley 2.0 Highway
[*] 銀杉谷 2.0 — Cathaya Valley 2.0
[*] 康斯鎮 — Constown, KY
[*] 科里爾登 — Coryerdon
[*] 拂曉鎮 — Dawn Town
[*] 回音河軍事基地 — EchoCreek Military Base
[*] 艾莉卡家具店 — Erika's Furniture Store
[*] 漂浮烏托邦 — Floatopia
[*] 狐步軍事倉庫 — Foxtrot Warehouse
[*] 班寧堡 — Fort Benning
[*] 翠湖堡 — Fort JadeLake
[*] 濱水堡壘 — Fort Waterfront
[*] 布恩斯伯勒堡 — Fort Boonesborough
[*] 葡萄籽鎮 — Grapeseed
[*] 綠葉鎮 — Greenleaf
[*] 哈特堡 — Hartburg, KY
[*] 獵人基地 — Hunter's Base
[*] 獵人基地（小型版） — Hunter's Base (Small)
[*] 榛果莊園 — Hazelnut Manor
[*] 榛果莊園（簡樸版） — Hazelnut Manor (Poor)
[*] 鳶尾島 — Iris Eyot
[*] 落明湖 — KillMingLake
[*] 金斯茅斯北區 — Kingsmouth North
[*] 白森林 — White Forest
[*] 路易斯維爾河船 — Louisville Riverboat
[*] Muldraugh 軍事檢查站－天橋 — Muldraugh Checkpoint - Overpass
[*] 普雷斯頓堡 — Fort Preston
[*] 貓又嶺 — Nekomata Ridge
[*] 蕁麻鎮 — Nettle Township
[*] 天頂號郵輪 — Path of Zenith
[*] 新煤田鎮 — New Coalfield
[*] 浣熊市 — Raccoon City
[*] 河畔豪宅（非官方修改版） — Riverside Mansion (Unofficial)
[*] 鏽堡鎮 — RustBury
[*] 安泊戍鎮 — Safeharbor Garrison
[*] 途安里 — SafeWayHamlet
[*] 日落湖鎮 — Sunset Lake Town
[*] 日落塔（17 層住宅樓） — Sunset Tower
[*] SecretZ 三號地堡 — SecretZ Bunker 3
[*] SecretZ 一號檢查站 — SecretZ Checkpoint 1
[*] SecretZ 六號檢查站 — SecretZ Checkpoint 6
[*] SecretZ 鹿頭湖基地 — SecretZ Deerhead Lake Base
[*] SecretZ 路易斯維爾軍事複合區 — SecretZ Louisville Military Complex
[*] SecretZ 火車站難民營 — SecretZ Train Depot Refugee Camp
[*] SecretZ 十字路口檢查站 — SecretZ Crossroads Checkpoint
[*] SecretZ 北方檢查站 — SecretZ North Checkpoint
[*] SecretZ 購物中心 — SecretZ The Mall
[*] 台北路 — Taibei Road
[*] 泰勒斯維爾 — Taylorsville
[*] 特拉帕湖鎮 — Trapala Lake Town
[*] 特雷萊 4x4（Kardinal 移植版） — Trelai 4x4 (Kardinal port)
[*] Z 村 — Vila Z
[*] 柳溪堡壘 — Willowbrook Bastion
[*] 柳溪堡壘 2026 — Willowbrook Bastion 2026
[*] 42 號地堡 — Bunker 42
[*] 新艾爾羅伊 — New Ellroy
[*] 沙德賽德 — Shadyside
[*] 白森嶺 — White Forest Ridge
[*] 楊湖鎮 — Yanghu Town
[*] 海棠鎮 — Begonia Town
[*] 青蛙鎮 — Frogtown
[*] 海文弗爾 — Haven Fall
[*] 梅肯（陰屍路） — Macon (TWD)
[*] 汐汐的靜謐小屋 — Xixi's Serene Cottage
[*] VaultTec 避難所－路易斯維爾 — VaultTec Vault - Louisville
[*] VaultTec 避難所－Muldraugh — VaultTec Vault - Muldraugh
[*] VaultTec 聯絡道路 — VaultTec Road
[*] VaultTec 避難所－羅斯伍德 — VaultTec Vault - Rosewood
[/list]

[h2]相關討論串[/h2]
[list]
[*][url=https://steamcommunity.com/workshop/filedetails/discussion/3763913359/569297034317714443/]小地圖：MOD 地圖道路導航需求與相容性[/url]
[*][url=https://steamcommunity.com/workshop/filedetails/discussion/3792675881/569297034317714529/]AutoDrive：MOD 地圖自動駕駛的道路需求與已知問題[/url]
[/list]
收錄於圖片包或收藏，不代表每張地圖都已通過導航、自駕或與所有其他地圖共存的驗證。圖片支援申請請使用地圖許願串；道路資料及駕駛問題請參考上方討論串。
