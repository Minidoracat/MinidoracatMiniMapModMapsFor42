# Minidoracat MiniMap - MOD Maps for B42

**By Minidoracat**

[Minidoracat MiniMap for B42](../MinidoracatMiniMapFor42) 主 MOD 的**地圖包 addon**：
收錄多張地圖 MOD 的小地圖圖像（ImagePyramid）與範圍框線資料，依啟用的地圖 MOD 自動掛載。

- **需要主 MOD**（mod.info `require=MinidoracatMiniMapFor42`）
- 裝了本地圖包後，主 MOD 會多出三個選項（ESC 選項頁／小地圖齒輪）：
  - 顯示 MOD 地圖區塊（掛不掛地圖包圖像）
  - 顯示 MOD 地圖框線（範圍框＋名稱，含四語翻譯）
  - MOD 地圖框線顏色（預設綠，另有青/黃/紫/白）
- 沒裝本地圖包時，上述選項不出現，主 MOD 行為不變

## 截圖

![MOD 地圖框線與名稱](docs/screenshots/mod-map-outlines.png)

## 收錄地圖

共 **100 張**（77 個 Workshop 項目；亦見 [Steam 收藏](https://steamcommunity.com/sharedfiles/filedetails/?id=3766382352)）。
支援新地圖申請與圖像問題回報請走 [GitHub Issue 表單](https://github.com/Minidoracat/MinidoracatMiniMapModMapsFor42/issues/new/choose)。

**街名翻譯（0.7.0 起，需主 MOD 0.21.0＋）**：下列 **16 張**地圖的路名已提供繁中／簡中／
日文翻譯，共 360 條——提基鎮、安瑞斯鎮、渡鴉溪（本體與 Kardinal 移植版各一套）、雛菊郡、
坎登郡、西點擴張、綠港、小鎮、狂鋼、黑迷宮橋頭堡、艾德汽車回收場、三葉湖、目黑丘城、
馬爾德勞 1993 重製版、楓木林鎮。英文與其他語言維持地圖作者原本的英文路名。
與官方地圖同名的路直接沿用官方譯名，跨地圖用詞一致。
其餘地圖多半**上游本來就沒有路名資料**（如浣熊市），不是翻譯缺漏。

另外幾項行為值得知道：

- **路名重複顯示成上下兩行已修正**：部分作者把街道畫成矩形輪廓（雛菊郡 44 條全是），
  引擎會沿矩形上下兩邊各畫一次路名；生成時自動壓成中心線，粗細與導航不受影響。
- **搜尋中英皆可**：中文／日文查引擎索引（即譯名），英文原名查本包另附的原名表（417 條）。
- **只翻譯作者自己畫的路**：`keep-scan` 逐條比對官方路網，剔除整條照抄、微調座標、
  換寫法重畫（`Pony Trot Rd` vs 官方 `Pony Trot Road`）、**整條蓋在官方路上**（不分名字，
  累計共線 ≥60%）與落在本圖範圍外的條目——那些路的中文由本體漢化提供，重複翻譯會
  兩份中文疊在同一條路上。雛菊郡因此剔除 6 條（`Ivy Road`／`Meadow Way` 等 100% 蓋住
  官方浣熊路網），馬爾德勞 1993 的 1,092 條只取獨有的 52 條；SecretZ 的 6 處據點整份
  都是官方路網複本，不列入支援。
- **路口相接處仍可能看到兩個路名**：只有一小段壓在官方路上的新增路（例如 30 square 的
  路口）會保留，引擎兩份都畫。要全消得剔除官方街道、會影響尋路，本包不介入官方路網。

| 地圖 | 對應 MOD（mod ID) | 範圍（世界 square） |
|------|--------------------|---------------------|
| Muldraugh 消防局 | `beek_muldraugh_firedept` | 10496,8960 – 11008,9472 |
| Estate 39 | `Estate 39` | 8192,9728 – 8704,10240 |
| 唐人街擴張區 | `Chinatown Expansion B42 version`（含 Less Traffic Jam 變體） | 10752,8192 – 11264,9216 |
| 唐人街 | `Chinatown B42 version` | 11008,8448 – 11520,9472 |
| 安瑞斯鎮（軍事堡壘） | `AnruisiTown` | 11776,11008 – 13056,12032 |
| 淺草湖畔小鎮 | `Asakusa lake town` | 10496,11264 – 11264,12032 |
| 灰木鎮 | `AshenwoodmodNewB42` | 11264,11008 – 11776,11776 |
| 亞特蘭大安全區（華人社區） | `Atlanta - Safe Zone-Chinese Survivors’ Community` | 8448,7680 – 9216,8448 |
| 亞特蘭大大廈生存 | `Atlanta Tower Survival` | 11008,12544 – 11520,13056 |
| 亞特蘭大 | `Atlanta` | 10496,12288 – 13056,14592 |
| 黑松郡 | `BlackpineCounty` | 9728,14080 – 11776,15360 |
| 卡姆登郡 | `CamdenCountyB42` | 12800,8448 – 19200,14848 |
| 銀杉谷 2.0－公路 | `Cathaya Valley 2.0 B42 version highway` | 7424,12288 – 7936,13312 |
| 銀杉谷 2.0 | `Cathaya Valley 2.0 B42 version` | 7168,12544 – 7680,13312 |
| 康斯鎮 | `Constown42` | 4864,10752 – 6400,11520 |
| 科里爾登 | `CoryerdonB42` | 7168,5632 – 10752,7424 |
| 雛菊郡 | `Daisy County B42 version` | 9728,7168 – 10752,8192 |
| 拂曉鎮 | `dawn_town` | 2816,7936 – 3328,8448 |
| 回音河軍事基地 | `EchoCreek MilitaryBase` | 2816,9984 – 3840,11008 |
| 艾德汽車回收場 | `EdsAutoSalvageB42` | 8448,8192 – 9216,8704 |
| 艾莉卡家具店 | `Erikas_Furniture_Store` | 11264,7936 – 11776,8448 |
| 漂浮烏托邦 | `Floatopia` | 4352,5376 – 4864,5888 |
| 班寧堡 | `FortBenningB42` | 5888,6656 – 6400,7424 |
| 翠湖堡 | `Fort JadeLake` | 11008,8448 – 11520,9216 |
| 濱水堡壘 | `Fort Waterfront B42` | 9984,10752 – 10752,11264 |
| 布恩斯伯勒堡 | `Fort_Boonesborough` | 13824,1792 – 14592,2048 |
| 葡萄籽鎮 | `42Grapeseed` | 6144,10752 – 7680,11776 |
| 綠葉鎮 | `Greenleaf B42 version` | 6144,9984 – 6912,11008 |
| 哈特堡 | `hartburgb42` | 6400,11008 – 6912,11776 |
| 獵人基地 | `Hunter'sBaseB42` | 5888,5632 – 6400,6144 |
| 獵人基地（小型版） | `Hunter'sBaseB42Small` | 5888,5632 – 6400,6144 |
| 榛果莊園 | `HazelnutManor` | 12544,5888 – 13056,6400 |
| 榛果莊園（簡樸版） | `HazelnutManor[Poor Version]` | 12544,5888 – 13056,6400 |
| 鳶尾島 | `IrisEyot` | 4096,11008 – 4864,11520 |
| 肯塔基中央莊園（翻新） | `Kentucky Center Manor_Renovation` | 7936,9472 – 8448,9984 |
| 落明湖 | `KillMingLake` | 8192,11776 – 8704,12544 |
| 金斯茅斯北區 | `KingsmouthNorthB42` | 0,3840 – 1280,5120 |
| 白森林 | `linzimod` | 8960,11008 – 9728,11776 |
| 小鎮區 | `LittleTownshipB42` | 7936,8192 – 8448,8704 |
| 楓木林鎮 | `Maplewood` | 7936,8192 – 8448,8704 |
| 路易斯維爾河船 | `Louisville_Riverboat` | 13056,1024 – 13312,1280 |
| 巡之丘市（學園孤島） | `Project Gurashi` | 0,2304 – 1280,4864 |
| Muldraugh 1993 | `muldraugh1993b42` | 10496,8960 – 11264,11008 |
| Muldraugh 軍事檢查站－天橋 | `Muldraugh-Checkpoint` | 10496,10752 – 11008,11520 |
| 普雷斯頓堡 | `muldraughmilitarybaseas24` | 8448,10752 – 9472,11520 |
| 貓又嶺 | `Nekomata Ridge` | 11776,8192 – 13312,9216 |
| 蕁麻鎮 | `Nettle Township B42 version` | 6400,8960 – 7424,9728 |
| 天頂號郵輪 | `PZ_ACSM_LV` | 12800,768 – 13312,1280 |
| 新煤田鎮 | `PZKNewCoalfieldTownMap` | 2816,8192 – 3584,8960 |
| 浣熊市 | `RaccoonCityB42` | 9728,9728 – 10496,10752 |
| 渡鴉溪 | `RavenCreekB42` | 4096,14336 – 6656,17920 |
| 渡鴉溪（Kardinal 移植版） | `kardinal_ravencreek_B42` | 4096,14336 – 7168,18176 |
| 河畔豪宅（非官方修改版） | `RMSafeHouseUnofficial` | 5376,4864 – 5888,5632 |
| 鏽堡鎮 | `rustbury_2026_b42` | 8960,12544 – 9472,13056 |
| 安泊戍鎮 | `modid`（上游作者未改佔位符，非錯誤） | 11520,10496 – 12800,11520 |
| 途安里 | `SafeWayHamlet` | 12544,10752 – 13056,11520 |
| 日落湖鎮 | `Sunset Lake Town B42 version` | 9472,11008 – 10240,12032 |
| 日落塔（17 層住宅樓） | `SunsetTower` | 11264,7168 – 11776,7680 |
| SecretZ 三號地堡 | `Secretz42` | 5888,11520 – 6400,12032 |
| SecretZ 一號檢查站 | `Secretz42` | 11776,7936 – 12544,8448 |
| SecretZ 五號檢查站 | `Secretz42` | 10752,11008 – 11264,11520 |
| SecretZ 六號檢查站 | `Secretz42` | 5632,5632 – 6144,6144 |
| SecretZ 八號檢查站 | `Secretz42` | 6400,11008 – 6912,11520 |
| SecretZ 鹿頭湖基地 | `Secretz42` | 4352,8192 – 4864,8704 |
| SecretZ 路易斯維爾軍事複合區 | `Secretz42` | 13568,1792 – 15360,3072 |
| SecretZ 馬奇嶺研究設施 | `Secretz42` | 9984,11776 – 10752,12800 |
| SecretZ 火車站難民營 | `Secretz42` | 11264,9472 – 12032,10752 |
| SecretZ 十字路口檢查站 | `Secretz42` | 10496,11008 – 11008,11520 |
| SecretZ 北方檢查站 | `Secretz42` | 3584,6400 – 4352,7424 |
| SecretZ 購物中心 | `Secretz42` | 13568,5632 – 14336,6144 |
| SecretZ 西點大橋檢查站 | `Secretz42` | 12288,6400 – 12800,6912 |
| SecretZ 河濱鎮一號檢查站 | `Secretz42` | 6400,6400 – 6912,6912 |
| SecretZ 河濱鎮二號檢查站 | `Secretz42` | 5632,5632 – 6144,6144 |
| 台北路 | `Taibeiroad4` | 7936,9984 – 9216,11776 |
| 泰勒斯維爾 | `Taylorsville` | 8960,6144 – 10496,7680 |
| 提基鎮＆發電廠 | `tikitown` | 6400,6656 – 7936,7936 |
| 特拉帕湖鎮 | `TrapalaketownB42` | 8192,11520 – 9216,12032 |
| 特雷萊 4x4（Kardinal 移植版） | `Trelai_B42` | 6400,6400 – 7936,7936 |
| Z 村 | `VilaZMap` | 9472,9472 – 9984,9984 |
| 西點擴張區 | `WestPointExpansionB42` | 11776,6400 – 13312,7680 |
| 斯皮福堡（WILDSTEEL） | `WILDSTEEL` | 14336,5632 – 14848,6144 |
| 柳溪堡壘 | `Willowbrook Bastion!` | 8448,9472 – 9728,10240 |
| 柳溪堡壘 2026 | `Willowbrook Bastion! 2`（與上者互斥，同 Workshop 項目的重製版） | 8448,9472 – 9728,10240 |
| 四葉草湖畔農莊 | `Clover Lake` | 9472,8960 – 9984,9984 |
| 42 號地堡 | `Bunker42` | 11008,9728 – 11520,10240 |
| 綠港 | `GreenportB42` | 7936,7168 – 8704,7936 |
| 新艾爾羅伊 | `NewEllroyShadysideB42` | 4864,9728 – 5888,10752 |
| 沙德賽德 | `NewEllroyShadysideB42` | 5632,9728 – 6400,10752 |
| 西點橋城 | `blackmaze_wp` | 10752,6144 – 11264,6656 |
| 白森嶺 | `White_forest_ridge` | 8960,11520 – 9728,12800 |
| 楊湖鎮 | `Yanghu Town` | 8448,8960 – 9728,9728 |
| 海棠鎮 | `Begonia_Town` | 11264,7424 – 12544,7936 |
| 青蛙鎮 | `Frogtown` | 2816,6656 – 4096,7680 |
| 海文弗爾 | `HavenFall` | 4096,8448 – 5120,9472 |
| 梅肯（陰屍路） | `Macon` | 3584,6400 – 4608,6912 |
| 汐汐的靜謐小屋 | `Xixi's Serene Cottage` | 7424,7936 – 7936,8448 |
| VaultTec 避難所－路易斯維爾 | `VaultTec B42 version` | 14336,2560 – 14848,3072 |
| VaultTec 避難所－Muldraugh | `VaultTec B42 version` | 12288,8960 – 12800,9472 |
| VaultTec 聯絡道路 | `VaultTec B42 version` | 11776,8960 – 12544,9472 |
| VaultTec 避難所－羅斯伍德 | `VaultTec B42 version` | 5888,10496 – 6400,11008 |

### 已下架地圖（記錄保留、每日追蹤不含）

上游 Workshop 頁已無法存取，已自圖包移除支援（v42.20.0-0.4.1 起，見 CHANGELOG）：

| 地圖 | Workshop ID | 下架時間 | 備註 |
|------|-------------|----------|------|
| 美雅鎮（Meiya'sTownB42） | 3478788261 | 2026-07 | v0.4.1 移除支援 |
| 7號淪陷區（Sector-7 Breach，含 Highway） | 3513107552 | 2026-07-21 | v0.4.1 移除支援；正式伺服器移除（下架項目會讓開服崩潰） |
| White Wolf Ridge | 3499861271 | 收藏建立前 | 未收錄（無圖） |

## 專案結構

```
MinidoracatMiniMapModMapsFor42/
├── STEAM_DESCRIPTION.md           # Steam 商店頁描述（繁中）——改動時必同步 _EN / _JP
│                                  # 版；_CN 由 `opencc tw2sp` 自繁中轉出，勿手改
├── link_workshop.bat              # Workshop 符號連結管理（雙擊啟動）
├── PZ_Test.bat                    # PZ 本地測試啟動器（雙擊啟動）
├── .github/workflows/track_maps.yml  # 每日追蹤：地圖更新（含圖資 hash 重渲判定）＋遊戲 build
├── scripts/                       # PowerShell / Python 腳本（map_tracker.py＝追蹤器本體）
├── tracker-state/                 # 追蹤器基準（timestamps.json＋mapdata_hashes.json，進版控）
└── MOD/MinidoracatMiniMapModMapsFor42/Contents/mods/MinidoracatMiniMapModMapsFor42/42/
    ├── mod.info                   # require=MinidoracatMiniMapFor42
    └── media/
        ├── lua/client/MinidoracatMiniMapModMaps.lua   # 向主 MOD 註冊地圖清單
        ├── lua/shared/Translate/{CH,CN,EN,JP}/UI.json
        └── minimap/               # pyramid zip（渲染產物，不進版控）
```

## 授權

程式碼與設定以 [MIT License](LICENSE) 釋出。地圖圖像（pyramid.zip）不進版控；
其內容衍生自 Project Zomboid 遊戲資產與第三方地圖 MOD，發佈規範見上方授權清單。

## 新增支援地圖

1. pzmap Studio 選該地圖 MOD →「遊戲內小地圖」模式輸出 `<地圖名>.pyramid.zip`
   （預設輸出名，免改名）放進 `media/minimap/`
2. `MinidoracatMiniMapModMaps.lua` 註冊清單加一行（bounds 抄渲染輸出 pyramid.txt）；
   一 mod 多地圖（SecretZ 類）逐條加 `mapDir`＝該 MOD `media/maps/` 下的資料夾名，
   MP 伺服器 `Map=` 未載入的地圖才不會誤畫（單地圖 mod 免填）
3. `Translate/*/UI.json` 加地圖名翻譯鍵

