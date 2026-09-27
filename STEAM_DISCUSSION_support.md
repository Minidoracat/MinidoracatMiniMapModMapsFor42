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
以下地圖圖片照常顯示，但沒有路名、搜尋與導航（除了上方本包補過的地圖）：
Muldraugh Fire Dept、Estate 39、Atlas Underground Complex (Surface)、Chinatown Expansion、Chinatown、Asakusa Lake Town、Ashenwood、Atlanta Safe Zone、Atlanta Tower Survival、Atlanta、Blackpine County、Cathaya Valley 2.0 Highway、Cathaya Valley 2.0、Constown, KY、Coryerdon、Dawn Town、EchoCreek Military Base、Erika's Furniture Store、Floatopia、Foxtrot Warehouse、Fort Benning、Fort JadeLake、Fort Waterfront、Fort Boonesborough、Grapeseed、Greenleaf、Hartburg, KY、Hunter's Base、Hunter's Base (Small)、Hazelnut Manor、Hazelnut Manor (Poor)、Iris Eyot、KillMingLake、Kingsmouth North、White Forest、Louisville Riverboat、Muldraugh Checkpoint - Overpass、Fort Preston、Nekomata Ridge、Nettle Township、Path of Zenith、New Coalfield、Raccoon City、Riverside Mansion (Unofficial)、RustBury、Safeharbor Garrison、SafeWayHamlet、Sunset Lake Town、Sunset Tower、SecretZ Bunker 3、SecretZ Checkpoint 1、SecretZ Checkpoint 6、SecretZ Deerhead Lake Base、SecretZ Louisville Military Complex、SecretZ Train Depot Refugee Camp、SecretZ Crossroads Checkpoint、SecretZ North Checkpoint、SecretZ The Mall、Taibei Road、Taylorsville、Trapala Lake Town、Trelai 4x4 (Kardinal port)、Vila Z、Willowbrook Bastion、Willowbrook Bastion 2026、Bunker 42、New Ellroy、Shadyside、White Forest Ridge、Yanghu Town、Begonia Town、Frogtown、Haven Fall、Macon (TWD)、Xixi's Serene Cottage、VaultTec Vault - Louisville、VaultTec Vault - Muldraugh、VaultTec Road、VaultTec Vault - Rosewood

[h2]相關討論串[/h2]
[list]
[*][url=https://steamcommunity.com/workshop/filedetails/discussion/3763913359/569297034317714443/]小地圖：地圖作者道路資料完整規範[/url]
[*][url=https://steamcommunity.com/workshop/filedetails/discussion/3792675881/569297034317714529/]AutoDrive：道路需求、多人測試範圍與已知問題[/url]
[/list]
收錄於圖片包或收藏，不代表每張地圖都已通過導航、自駕或與所有其他地圖共存的驗證。圖片支援申請請使用地圖許願串；道路資料及駕駛問題請參考上方討論串。
