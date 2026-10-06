<!-- 生成檔，請勿手改。重新生成：uv run scripts/map_tracker.py road-scan --prefer <steamcmd content 根> --write（每日追蹤器也會在作者更新後自動更新） -->

# 道路資料清單（Road data）

地圖作者會在地圖 MOD 內附上道路資料（`streets.xml`）。小地圖的這些功能都靠它：

- 地圖上的**路名**顯示與滑鼠移上去的**路名提示**
- **路名搜尋**
- **導航**與**自動駕駛**的路網

作者沒附道路資料的地圖，圖像照常顯示，但該區域沒有路名、搜不到路，也無法導航。這不是本包漏做翻譯；本包會視情況補上道路資料（見下方「本包補過道路資料的地圖」）。

## 圖例（Legend）

| 標示 | 意思 |
|------|------|
| ✅ N 條 | 作者附有道路資料，共 N 條街（Author provides N streets） |
| ❌ 無 | 作者沒有附道路資料（No road data from the author） |
| ❔ 未確認 | 尚未取得作者目前版本的資料（Not checked yet） |
| — | 本包沒有這項資料（None） |

- **路名翻譯**：作者原本的英文路名，本包提供繁中／簡中／日文翻譯（英文與其他語言維持原名）。
- **本包修正**：作者道路資料有問題的地方，本包另外修正；作者改版後對不上的修正會自動略過。
- **本包補充道路**：作者沒放進道路資料的路，本包補上並標明「小地圖補」；作者日後提供道路資料時自動停用。

## 統計（Summary）

- 收錄地圖（Maps）：**103** 張
- 作者附道路資料（Author road data）：**23** 張；沒有 **80** 張
- 本包路名翻譯（Translated names）：**17** 張
- 本包道路修正（Fixes）：**4** 張
- 本包補充道路（Added roads）：**2** 張

## 本包補過道路資料的地圖（Maps we fixed or extended）

- **卡姆登郡（Camden County）**
  - 斷點接線 3 處：作者的路停在路口前，導航／自動駕駛到不了；接回路網後可以走
- **康斯鎮（Constown, KY）**
  - 補充道路 37 條：作者沒放進道路資料的路由本包補上，路名 `康斯鎮 01 號路（小地圖補）`～`康斯鎮 37 號路（小地圖補）`（英文 `Constown Rd 01 (MiniMap)`～`Constown Rd 37 (MiniMap)`）；作者日後提供道路資料時，遊戲內自動改用作者的
- **雛菊郡（Daisy County）**
  - 輪廓道路改中心線 44 條：作者把路畫成外框，路名會上下各顯示一次；改成中心線後顯示與導航都正常
- **馬爾德勞 1993（Muldraugh 1993）**
  - 重複路名隱藏 913 筆：與官方地圖逐點相同的複本，只藏玩家地圖上重疊的路名，導航不受影響
- **渡鴉溪（Raven Creek）**
  - 移除多餘轉折點 1 處：作者的路在路口旁多畫了轉折點或尾巴，導航會把路線拉到隔壁路上或走成 Z 字而偏離路面；拿掉這些點後沿實際路面走
  - 補充道路 1 條：作者沒放進道路資料的路由本包補上，路名 `渡鴉溪 01 號路（小地圖補）`（英文 `Raven Creek Rd 01 (MiniMap)`）；作者日後提供道路資料時，遊戲內自動改用作者的

## 全部地圖（All maps）

| 地圖 Map | Workshop | 作者道路資料<br>Author roads | 路名翻譯<br>Translated names | 本包修正<br>Fixes | 本包補充道路<br>Added roads |
|---|---|---|---|---|---|
| 馬爾德勞消防局<br>Muldraugh Fire Dept | [3585472912](https://steamcommunity.com/sharedfiles/filedetails/?id=3585472912) | ❌ 無 | — | — | — |
| Estate 39 莊園<br>Estate 39 | [3606927986](https://steamcommunity.com/sharedfiles/filedetails/?id=3606927986) | ❌ 無 | — | — | — |
| 阿特拉斯地下複合設施（地表）<br>Atlas Underground Complex (Surface) | [3717208771](https://steamcommunity.com/sharedfiles/filedetails/?id=3717208771) | ❌ 無 | — | — | — |
| 唐人街擴張區<br>Chinatown Expansion | [3703704638](https://steamcommunity.com/sharedfiles/filedetails/?id=3703704638) | ❌ 無 | — | — | — |
| 唐人街<br>Chinatown | [3703704021](https://steamcommunity.com/sharedfiles/filedetails/?id=3703704021) | ❌ 無 | — | — | — |
| 安瑞斯鎮（軍事堡壘）<br>AnruisiTown (Military Bastion) | [3659676359](https://steamcommunity.com/sharedfiles/filedetails/?id=3659676359) | ✅ 59 條 | ✅ 32 條 | — | — |
| 淺草湖畔小鎮<br>Asakusa Lake Town | [3482962418](https://steamcommunity.com/sharedfiles/filedetails/?id=3482962418) | ❌ 無 | — | — | — |
| 灰木鎮<br>Ashenwood | [3493916941](https://steamcommunity.com/sharedfiles/filedetails/?id=3493916941) | ❌ 無 | — | — | — |
| 亞特蘭大安全區（華人社區）<br>Atlanta Safe Zone | [3580819781](https://steamcommunity.com/sharedfiles/filedetails/?id=3580819781) | ❌ 無 | — | — | — |
| 亞特蘭大大廈生存<br>Atlanta Tower Survival | [3525104670](https://steamcommunity.com/sharedfiles/filedetails/?id=3525104670) | ❌ 無 | — | — | — |
| 亞特蘭大<br>Atlanta | [3580819781](https://steamcommunity.com/sharedfiles/filedetails/?id=3580819781) | ❌ 無 | — | — | — |
| 黑松郡<br>Blackpine County | [3565649631](https://steamcommunity.com/sharedfiles/filedetails/?id=3565649631) | ❌ 無 | — | — | — |
| 卡姆登郡<br>Camden County | [3504080284](https://steamcommunity.com/sharedfiles/filedetails/?id=3504080284) | ✅ 40 條 | ✅ 40 條 | 斷點接線 3 處 | — |
| 銀杉谷 2.0－公路<br>Cathaya Valley 2.0 Highway | [3576150391](https://steamcommunity.com/sharedfiles/filedetails/?id=3576150391) | ❌ 無 | — | — | — |
| 銀杉谷 2.0<br>Cathaya Valley 2.0 | [3576150391](https://steamcommunity.com/sharedfiles/filedetails/?id=3576150391) | ❌ 無 | — | — | — |
| 康斯鎮<br>Constown, KY | [3480990544](https://steamcommunity.com/sharedfiles/filedetails/?id=3480990544) | ❌ 無 | — | — | ✅ 37 條 |
| 科里爾登<br>Coryerdon | [3502623745](https://steamcommunity.com/sharedfiles/filedetails/?id=3502623745) | ❌ 無 | — | — | — |
| 雛菊郡<br>Daisy County | [3390753141](https://steamcommunity.com/sharedfiles/filedetails/?id=3390753141) | ✅ 44 條 | ✅ 44 條 | 輪廓道路改中心線 44 條 | — |
| 拂曉鎮<br>Dawn Town | [3666180085](https://steamcommunity.com/sharedfiles/filedetails/?id=3666180085) | ❌ 無 | — | — | — |
| 迴音河軍事基地<br>EchoCreek Military Base | [3476333350](https://steamcommunity.com/sharedfiles/filedetails/?id=3476333350) | ❌ 無 | — | — | — |
| 艾德汽車回收場<br>Ed's Auto Salvage | [3478900814](https://steamcommunity.com/sharedfiles/filedetails/?id=3478900814) | ✅ 3 條 | ✅ 3 條 | — | — |
| 艾莉卡家具店<br>Erika's Furniture Store | [3363546437](https://steamcommunity.com/sharedfiles/filedetails/?id=3363546437) | ❌ 無 | — | — | — |
| 漂浮烏托邦<br>Floatopia | [3693913206](https://steamcommunity.com/sharedfiles/filedetails/?id=3693913206) | ❌ 無 | — | — | — |
| 狐步軍事倉庫<br>Foxtrot Warehouse | [3600377019](https://steamcommunity.com/sharedfiles/filedetails/?id=3600377019) | ❌ 無 | — | — | — |
| 班寧堡<br>Fort Benning | [3490580478](https://steamcommunity.com/sharedfiles/filedetails/?id=3490580478) | ❌ 無 | — | — | — |
| 翠湖堡<br>Fort JadeLake | [3537326669](https://steamcommunity.com/sharedfiles/filedetails/?id=3537326669) | ❌ 無 | — | — | — |
| 濱水堡壘<br>Fort Waterfront | [3486814612](https://steamcommunity.com/sharedfiles/filedetails/?id=3486814612) | ❌ 無 | — | — | — |
| 布恩斯伯勒堡<br>Fort Boonesborough | [2968421358](https://steamcommunity.com/sharedfiles/filedetails/?id=2968421358) | ❌ 無 | — | — | — |
| 葡萄籽鎮<br>Grapeseed | [2463499011](https://steamcommunity.com/sharedfiles/filedetails/?id=2463499011) | ❌ 無 | — | — | — |
| 綠葉鎮<br>Greenleaf | [3602388131](https://steamcommunity.com/sharedfiles/filedetails/?id=3602388131) | ❌ 無 | — | — | — |
| 哈特堡<br>Hartburg, KY | [3576750203](https://steamcommunity.com/sharedfiles/filedetails/?id=3576750203) | ❌ 無 | — | — | — |
| 獵人基地<br>Hunter's Base | [3664225685](https://steamcommunity.com/sharedfiles/filedetails/?id=3664225685) | ❌ 無 | — | — | — |
| 獵人基地（小型版）<br>Hunter's Base (Small) | [3664225685](https://steamcommunity.com/sharedfiles/filedetails/?id=3664225685) | ❌ 無 | — | — | — |
| 榛果莊園<br>Hazelnut Manor | [3495993590](https://steamcommunity.com/sharedfiles/filedetails/?id=3495993590) | ❌ 無 | — | — | — |
| 榛果莊園（簡樸版）<br>Hazelnut Manor (Poor) | [3495993590](https://steamcommunity.com/sharedfiles/filedetails/?id=3495993590) | ❌ 無 | — | — | — |
| 鳶尾島<br>Iris Eyot | [3545473388](https://steamcommunity.com/sharedfiles/filedetails/?id=3545473388) | ❌ 無 | — | — | — |
| 落明湖<br>KillMingLake | [3446958402](https://steamcommunity.com/sharedfiles/filedetails/?id=3446958402) | ❌ 無 | — | — | — |
| 金斯茅斯北區<br>Kingsmouth North | [3498573050](https://steamcommunity.com/sharedfiles/filedetails/?id=3498573050) | ❌ 無 | — | — | — |
| 白森林<br>White Forest | [3519054686](https://steamcommunity.com/sharedfiles/filedetails/?id=3519054686) | ❌ 無 | — | — | — |
| 小鎮區<br>LittleTownship | [3477336014](https://steamcommunity.com/sharedfiles/filedetails/?id=3477336014) | ✅ 4 條 | ✅ 4 條 | — | — |
| 楓木林鎮<br>Maplewood | [3644794945](https://steamcommunity.com/sharedfiles/filedetails/?id=3644794945) | ✅ 12 條 | ✅ 5 條 | — | — |
| 路易斯維爾河船<br>Louisville Riverboat | [2963883586](https://steamcommunity.com/sharedfiles/filedetails/?id=2963883586) | ❌ 無 | — | — | — |
| 巡之丘市（學園孤島）<br>Megurigaoka, Kanagawa | [3318210146](https://steamcommunity.com/sharedfiles/filedetails/?id=3318210146) | ✅ 2 條 | ✅ 2 條 | — | — |
| 烏鴉山市<br>Mount Crow City | [3500846812](https://steamcommunity.com/sharedfiles/filedetails/?id=3500846812) | ✅ 87 條 | ✅ 83 條 | — | — |
| 馬爾德勞 1993<br>Muldraugh 1993 | [3701834205](https://steamcommunity.com/sharedfiles/filedetails/?id=3701834205) | ✅ 1092 條 | ✅ 61 條 | 重複路名隱藏 913 筆 | — |
| 馬爾德勞軍事檢查站－天橋<br>Muldraugh Checkpoint - Overpass | [3677600363](https://steamcommunity.com/sharedfiles/filedetails/?id=3677600363) | ❌ 無 | — | — | — |
| 普雷斯頓堡<br>Fort Preston | [3496507146](https://steamcommunity.com/sharedfiles/filedetails/?id=3496507146) | ❌ 無 | — | — | — |
| 貓又嶺<br>Nekomata Ridge | [3782173659](https://steamcommunity.com/sharedfiles/filedetails/?id=3782173659) | ❌ 無 | — | — | — |
| 內利斯空軍基地<br>Nellis Air Force Base | [3783433804](https://steamcommunity.com/sharedfiles/filedetails/?id=3783433804) | ❌ 無 | — | — | — |
| 蕁麻鎮<br>Nettle Township | [3391349130](https://steamcommunity.com/sharedfiles/filedetails/?id=3391349130) | ❌ 無 | — | — | — |
| 天頂號郵輪<br>Path of Zenith | [3589905072](https://steamcommunity.com/sharedfiles/filedetails/?id=3589905072) | ❌ 無 | — | — | — |
| 新煤田鎮<br>New Coalfield | [3452917446](https://steamcommunity.com/sharedfiles/filedetails/?id=3452917446) | ❌ 無 | — | — | — |
| 浣熊市<br>Raccoon City | [3388468313](https://steamcommunity.com/sharedfiles/filedetails/?id=3388468313) | ❌ 無 | — | — | — |
| 渡鴉溪<br>Raven Creek | [3484263516](https://steamcommunity.com/sharedfiles/filedetails/?id=3484263516) | ✅ 45 條 | ✅ 21 條 | 移除多餘轉折點 1 處 | ✅ 1 條 |
| 渡鴉溪（Kardinal 移植版）<br>Raven Creek (Kardinal port) | [3769577696](https://steamcommunity.com/sharedfiles/filedetails/?id=3769577696) | ✅ 45 條 | ✅ 44 條 | — | — |
| 河畔豪宅（非官方修改版）<br>Riverside Mansion (Unofficial) | [3485388592](https://steamcommunity.com/sharedfiles/filedetails/?id=3485388592) | ❌ 無 | — | — | — |
| 鏽堡鎮<br>RustBury | [3721711345](https://steamcommunity.com/sharedfiles/filedetails/?id=3721711345) | ❌ 無 | — | — | — |
| 安泊戍鎮<br>Safeharbor Garrison | [3522517059](https://steamcommunity.com/sharedfiles/filedetails/?id=3522517059) | ❌ 無 | — | — | — |
| 途安里<br>SafeWayHamlet | [3533315055](https://steamcommunity.com/sharedfiles/filedetails/?id=3533315055) | ❌ 無 | — | — | — |
| 日落湖鎮<br>Sunset Lake Town | [3752069346](https://steamcommunity.com/sharedfiles/filedetails/?id=3752069346) | ❌ 無 | — | — | — |
| 日落塔（17 層住宅樓）<br>Sunset Tower | [3748141823](https://steamcommunity.com/sharedfiles/filedetails/?id=3748141823) | ❌ 無 | — | — | — |
| SecretZ 三號地堡<br>SecretZ Bunker 3 | [3494374578](https://steamcommunity.com/sharedfiles/filedetails/?id=3494374578) | ❌ 無 | — | — | — |
| SecretZ 一號檢查站<br>SecretZ Checkpoint 1 | [3494374578](https://steamcommunity.com/sharedfiles/filedetails/?id=3494374578) | ❌ 無 | — | — | — |
| SecretZ 五號檢查站<br>SecretZ Checkpoint 5 | [3494374578](https://steamcommunity.com/sharedfiles/filedetails/?id=3494374578) | ✅ 1 條 | — | — | — |
| SecretZ 六號檢查站<br>SecretZ Checkpoint 6 | [3494374578](https://steamcommunity.com/sharedfiles/filedetails/?id=3494374578) | ❌ 無 | — | — | — |
| SecretZ 八號檢查站<br>SecretZ Checkpoint 8 | [3494374578](https://steamcommunity.com/sharedfiles/filedetails/?id=3494374578) | ✅ 2 條 | — | — | — |
| SecretZ 鹿頭湖基地<br>SecretZ Deerhead Lake Base | [3494374578](https://steamcommunity.com/sharedfiles/filedetails/?id=3494374578) | ❌ 無 | — | — | — |
| SecretZ 路易斯維爾軍事複合區<br>SecretZ Louisville Military Complex | [3494374578](https://steamcommunity.com/sharedfiles/filedetails/?id=3494374578) | ❌ 無 | — | — | — |
| SecretZ 三月嶺研究設施<br>SecretZ March Ridge Research Facility | [3494374578](https://steamcommunity.com/sharedfiles/filedetails/?id=3494374578) | ✅ 2 條 | — | — | — |
| SecretZ 火車站難民營<br>SecretZ Train Depot Refugee Camp | [3494374578](https://steamcommunity.com/sharedfiles/filedetails/?id=3494374578) | ❌ 無 | — | — | — |
| SecretZ 十字路口檢查站<br>SecretZ Crossroads Checkpoint | [3494374578](https://steamcommunity.com/sharedfiles/filedetails/?id=3494374578) | ❌ 無 | — | — | — |
| SecretZ 北方檢查站<br>SecretZ North Checkpoint | [3494374578](https://steamcommunity.com/sharedfiles/filedetails/?id=3494374578) | ❌ 無 | — | — | — |
| SecretZ 購物中心<br>SecretZ The Mall | [3494374578](https://steamcommunity.com/sharedfiles/filedetails/?id=3494374578) | ❌ 無 | — | — | — |
| SecretZ 西點大橋檢查站<br>SecretZ West Point Bridge Checkpoint | [3494374578](https://steamcommunity.com/sharedfiles/filedetails/?id=3494374578) | ✅ 4 條 | — | — | — |
| SecretZ 河畔鎮一號檢查站<br>SecretZ Riverside Checkpoint 1 | [3494374578](https://steamcommunity.com/sharedfiles/filedetails/?id=3494374578) | ✅ 2 條 | — | — | — |
| SecretZ 河畔鎮二號檢查站<br>SecretZ Riverside Checkpoint 2 | [3494374578](https://steamcommunity.com/sharedfiles/filedetails/?id=3494374578) | ✅ 4 條 | — | — | — |
| 台北路<br>Taibei Road | [3401261192](https://steamcommunity.com/sharedfiles/filedetails/?id=3401261192) | ❌ 無 | — | — | — |
| 泰勒斯維爾<br>Taylorsville | [3134394569](https://steamcommunity.com/sharedfiles/filedetails/?id=3134394569) | ❌ 無 | — | — | — |
| 提基鎮＆發電廠<br>Tikitown & PowerPlant | [3037854728](https://steamcommunity.com/sharedfiles/filedetails/?id=3037854728) | ✅ 103 條 | ✅ 99 條 | — | — |
| 特拉帕湖鎮<br>Trapala Lake Town | [3390327877](https://steamcommunity.com/sharedfiles/filedetails/?id=3390327877) | ❌ 無 | — | — | — |
| 特雷萊 4x4（Kardinal 移植版）<br>Trelai 4x4 (Kardinal port) | [3768876083](https://steamcommunity.com/sharedfiles/filedetails/?id=3768876083) | ❌ 無 | — | — | — |
| Z 村<br>Vila Z | [3524981481](https://steamcommunity.com/sharedfiles/filedetails/?id=3524981481) | ❌ 無 | — | — | — |
| 西點擴張區<br>West Point Expansion | [3475754603](https://steamcommunity.com/sharedfiles/filedetails/?id=3475754603) | ✅ 18 條 | ✅ 18 條 | — | — |
| 斯皮福堡（WILDSTEEL）<br>WILDSTEEL - Fort Spiffo | [3691773420](https://steamcommunity.com/sharedfiles/filedetails/?id=3691773420) | ✅ 4 條 | ✅ 4 條 | — | — |
| 柳溪堡壘<br>Willowbrook Bastion | [3479667649](https://steamcommunity.com/sharedfiles/filedetails/?id=3479667649) | ❌ 無 | — | — | — |
| 柳溪堡壘 2026<br>Willowbrook Bastion 2026 | [3479667649](https://steamcommunity.com/sharedfiles/filedetails/?id=3479667649) | ❌ 無 | — | — | — |
| 四葉草湖畔農莊<br>Clover Lake Farmhouse | [3759558202](https://steamcommunity.com/sharedfiles/filedetails/?id=3759558202) | ✅ 1 條 | ✅ 1 條 | — | — |
| 42 號地堡<br>Bunker 42 | [3762184916](https://steamcommunity.com/sharedfiles/filedetails/?id=3762184916) | ❌ 無 | — | — | — |
| 綠港<br>Greenport, KY | [3747595202](https://steamcommunity.com/sharedfiles/filedetails/?id=3747595202) | ✅ 15 條 | ✅ 15 條 | — | — |
| 新艾爾羅伊<br>New Ellroy | [3747339147](https://steamcommunity.com/sharedfiles/filedetails/?id=3747339147) | ❌ 無 | — | — | — |
| 沙德賽德<br>Shadyside | [3747339147](https://steamcommunity.com/sharedfiles/filedetails/?id=3747339147) | ❌ 無 | — | — | — |
| 西點橋城<br>West Point: The Bridge Citadel | [3711035052](https://steamcommunity.com/sharedfiles/filedetails/?id=3711035052) | ✅ 4 條 | ✅ 4 條 | — | — |
| 白森嶺<br>White Forest Ridge | [3659221974](https://steamcommunity.com/sharedfiles/filedetails/?id=3659221974) | ❌ 無 | — | — | — |
| 楊湖鎮<br>Yanghu Town | [3638880637](https://steamcommunity.com/sharedfiles/filedetails/?id=3638880637) | ❌ 無 | — | — | — |
| 海棠鎮<br>Begonia Town | [3736155379](https://steamcommunity.com/sharedfiles/filedetails/?id=3736155379) | ❌ 無 | — | — | — |
| 青蛙鎮<br>Frogtown | [3449473111](https://steamcommunity.com/sharedfiles/filedetails/?id=3449473111) | ❌ 無 | — | — | — |
| 海文弗爾<br>Haven Fall | [3728357493](https://steamcommunity.com/sharedfiles/filedetails/?id=3728357493) | ❌ 無 | — | — | — |
| 梅肯（陰屍路）<br>Macon (TWD) | [3701164856](https://steamcommunity.com/sharedfiles/filedetails/?id=3701164856) | ❌ 無 | — | — | — |
| 汐汐的靜謐小屋<br>Xixi's Serene Cottage | [3685508479](https://steamcommunity.com/sharedfiles/filedetails/?id=3685508479) | ❌ 無 | — | — | — |
| VaultTec 避難所－路易斯維爾<br>VaultTec Vault - Louisville | [3697082724](https://steamcommunity.com/sharedfiles/filedetails/?id=3697082724) | ❌ 無 | — | — | — |
| VaultTec 避難所－馬爾德勞<br>VaultTec Vault - Muldraugh | [3697082724](https://steamcommunity.com/sharedfiles/filedetails/?id=3697082724) | ❌ 無 | — | — | — |
| VaultTec 聯絡道路<br>VaultTec Road | [3697082724](https://steamcommunity.com/sharedfiles/filedetails/?id=3697082724) | ❌ 無 | — | — | — |
| VaultTec 避難所－羅斯伍德<br>VaultTec Vault - Rosewood | [3697082724](https://steamcommunity.com/sharedfiles/filedetails/?id=3697082724) | ❌ 無 | — | — | — |
