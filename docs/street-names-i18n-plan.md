# MOD 地圖街名多語化（street names i18n）定案規劃

2026-08-26 定案。三方審查：Claude（主導調查）＋ Codex GPT-5.6（thread 01a039c3，兩輪）＋ Grok（兩輪），
證據基準：42.20.3 反編譯快照（`../pz-decompiled-reference/snapshots/42.20.3-20260817/`）、
vanilla lua、本機 Workshop 副本實查。玩家回報源頭：2026-08-25 Mad Man（雛菊郡/安瑞斯路名英文、
浣熊市無路名、蒂基鎮「正常」）。

## 已定案因果（背景，不必重驗）

- 引擎**無街名翻譯機制**：`WorldMapStreetsXML.parseStreet:78` 直接拿 `streets.xml` 的 `name`
  原樣繪製；整個 `zombie/worldMap/streets/` 零 Translator 呼叫。`translatedText` 欄位＝
  「呼叫者填入的最終顯示字串」。
- vanilla 街名中文＝漢化 MOD（LangFor42 `MapStreets_Flx.lua`）整份取代官方英文檔，只涵蓋官方地圖。
- 蒂基鎮的中文是 `MapLabel_*` 地名標籤（Translator 有此類別；ModLangFor42 CN/MapLabel.json 翻的），
  與街名是兩套機制；其 99 條街名同樣英文。
- 浣熊市（RaccoonCityB42）無 `streets.xml`——無字可畫，不做（補了是替作者創作路網，非翻譯）。
- 熱改不可行：繪製走 `combinedStreets` 複本（`createCopy` 複製當下文字）；`WorldMapStreetV1`
  只有 getter；editor API 觸發 rebuild 會踩 `WorldMapStreets.clear()` 不清 `StreetLookup`
  空間索引的幽靈街名坑。`StreetRenderData.init` 首次繪製的 clear+recombine 是同坑第二路徑
  （同語言 recombine 僅疊粗、無害；先英後改必中英混雜）→ **唯一安全路徑＝替換式 add-only**。

## 使用者決策

1. 資料放本 repo（隨地圖追蹤器聯動上游更新）；載入行為放主 MOD（家規：本 repo 只放資料）。
2. **多語系全做：CH／CN／JP 三份；EN 與其他語言＝上游英文原樣**。
3. ModLangFor42 維持 JSON-only，不參與。

## 定案架構

### 身分機制（Codex 方案，仲裁採納）

`registerMaps` 條目新增選配欄位 `streetI18n = "<dataset-id>"`（安全字元 `[A-Za-z0-9._-]+`）。
含此欄位的條目**必須**同時明確填 `mapDir`。

- 真 alias（同 zip 同圖資，如 Chinatown 與 Less Traffic Jam 變體）：多條目指同一 dataset ID。
- **同 mapDir 不同圖資**（實證反例：`RavenCreekB42` 與 `kardinal_ravencreek_B42` 同
  `mapDir='Raven Creek B42'`，streets.xml 各 45 條、SHA 不同、街名集合幾乎不相交）：各自 dataset ID，
  loader 以「啟用的 mapMod」選資料集；同時匹配兩個資料集＝異常，警告並退回英文，不猜。
- 為何不用純 mapDir 約定路徑（Grok 原案）：Raven Creek 反例使 mapDir 不構成唯一身分；
  顯式 ID 同時是 `street-names/<id>/` 與生成物路徑的同一把鍵。

### 資料層（本 repo）

- 單一真相：`street-names/<dataset-id>/names.json` — 每個 **unique** 英文名 →
  `{ch, cn, jp}`；metadata 含來源 workshop id、mapMod、mapDir、上游 streets.xml sha256、擷取日期。
  同名街共用翻譯（除非未來實證需要 per-occurrence 覆寫再擴）。
- 生成物（進 git）：
  `MOD/.../42/media/minimapstreets/MinidoracatMiniMapModMapsFor42/<dataset-id>/streets_{CH,CN,JP}.xml`
  - 帶包名前綴：`activeFileMap` 全域共享，防未來兄弟包同路徑碰撞。
  - **絕不放 `media/maps/` 下**：`MapGroups.handleMapDirectory` 會掃該樹（LangFor42 踩過
    「漢化包內建真地圖目錄被引擎當地圖來源」坑）。`searchFolders` 把所有 mod 檔案登錄進
    `activeFileMap`（不限 media/maps/），`fileExists`＋`addStreetData` 對完整檔路徑即可解析
    （`ZomboidFileSystem.java:637`、`WorldMap.java:193`）。
- generator `scripts/gen_streets_i18n.py`（`--prefer <workshop content 根>` 同 map_tracker 模式）：
  上游 streets.xml 幾何 ＋ names.json 名稱 → 三份 XML。幾何永不手改。
  - 名稱正規化：折疊多重空白（上游有 `Forest  St` 髒名）後查表。
  - 後綴詞典（見下）自動建議譯名，人工可逐條覆寫。
- 驗證閘門（出貨前必跑，fail-closed）：
  1. 生成 XML 與上游逐條一致：street 數、順序、points、width 完全相同，只允許 `name` 差異。
  2. 三語完整性：任一 unique 名缺 CH/CN/JP 任一 → 該 dataset 整組 fail、不覆寫既有生成檔
     （generator 支援 `--allow-partial` 供本機邊譯邊看，出貨/CI 拒收）。
     刻意保留英文的專名＝顯式填等值英文，不允許缺欄位。
  3. **譯後撞名檢查**：同 dataset 內譯後名不得撞（引擎 `initConnectedStreets` 用
     `getTranslatedText().equals` 接路段、搜尋索引同鍵——譯後撞名會誤接路網）。
  4. UTF-8 無 BOM。
- 覆蓋率以 **unique name** 計（AnruisiTown 59 條僅 32 個 unique）。

### 行為層（主 MOD）

- 攔截點：wrap `MapUtils.initDirectoryStreetData`（ISMapDefinitions.lua:32-39）。
  vanilla `initDefaultStreetData` 與 LangFor42 取代版的迴圈都動態呼叫它 → 兩環境自然命中，
  與 LangFor42 wrapper 正交（它攔官方目錄、本層攔 MOD 地圖目錄）。
  **不碰 `initDefaultStreetData`**（LangFor42 已 wrap 該層，再疊＝後載者贏互踩）。
- 邏輯：`Translator.getLanguage():name()` ∈ {CH, CN, JP}（實證值；JP 非 JA）
  且由「目錄＋啟用 mapMod」解析出 dataset（用主 MOD 既有 mapMod↔mapDir 解析鏈）
  且 `fileExists('media/minimapstreets/MinidoracatMiniMapModMapsFor42/<id>/streets_<LANG>.xml')`
  → `addStreetData(替代檔)` 並跳過原英文檔；任何條件不成立 → 呼叫原函式（英文原樣）。
- 全程 add-only；**絕不清除非空 street set**（vanilla 首次空集 `clearStreetData()` 無害，不攔）。
- 與小地圖 `count==0` gate 相容（gate 只控要不要跑載入；替換在載入函式內部）。
- debug log：替換成功／fallback 英文／同 dataset 衝突警告（比版本協定有用）。
- 版本相容天然成立，**不做** feature 版本協定：主 MOD registerMaps 驗證器不拒未知欄位
  （MinidoracatMiniMap.lua:68）→ 舊主 MOD＋新地圖包＝忽略欄位照舊英文；反向＝探測不到檔案照舊。
- MP：純 client 顯示資料，各 client 依自身語言載入，無網路同步、無 server 狀態。

### 追蹤器整合（使用者核心動機；Codex 抓到的 blocker）

`map_tracker.py` 現行只 hash `.lotheader/.lotpack/.bin`（map_tracker.py:73）——**street 名稱變更
不會被追蹤**。必須新增獨立 `streets_sha256` 軸：

- 對每個含 `streetI18n` 的地圖記錄上游 streets.xml sha256。
- 變更 → 開「街名翻譯需更新」判定（**不可混入 render hash**，否則街名文字更新誤報重渲 pyramid）。
- SOP：追蹤 issue → 重跑 generator → names.json 出現新 unique 英文條目 → 補譯三語 → 重生 → 驗證 → commit。

### 後綴表（實作定案；CH 沿用 LangFor42 1098 條實檔慣例）

CH 慣例由 LangFor42 中文 streets.xml 與官方英文檔位置對齊後統計得出（權威、非自訂）：
St→街 439/451、Road→路 328/334、Lane→巷 104/105、Dr→大道 57/60、Ave/Av→大道、
Ct/Court→苑、Pl→廣場、Trail→小徑、Loop→環路。

**實作時發現的撞名**：LangFor42 官方 `Way` 也譯「路」（12/14），與 Road 相同。
`raven-creek` 有 David Blane **Av / Rd / Way** 三條同專名 → 會撞。故 **Way 改「道」**
（LangFor42 有 2 例先例）。實測三者為 大衛·布蘭大道／路／道，互異。

| EN | CH | JP（片假名專名） | JP（漢字/和語專名） |
|---|---|---|---|
| St / Street | 街 | ・通り | 通り |
| Ave / Av / Avenue | 大道 | ・アベニュー | 大通り |
| Rd / Road | 路 | ・ロード | 通り |
| Dr / Drive | 大道 | ・ドライブ | 通り |
| Way | **道** | ・ウェイ | 道 |
| Ln / Lane | 巷 | ・レーン | 小路 |
| Blvd / Boulevard | 大道 | 大通り | 大通り |
| Ct / Court | 苑 | ・コート | 通り |
| Pl / Place | 廣場 | ・プレイス | 広場 |
| Pike | 公路 | ・パイク | 街道 |
| Trail | 小徑 | ・トレイル | 小径 |
| Trace | 古道 | ・トレース | 古道 |
| Bend | 彎 | ・ベンド | 曲がり |
| Loop / Circle | 環路 | ・ループ／・サークル | 環状線／環状 |
| Spur | 支線 | ・スパー | 支線 |
| Terrace | 台 | ・テラス | 台 |
| Hwy / Highway | 高速公路 | ・ハイウェイ | 高速道路 |
| Parkway | 園道 | ・パークウェイ | 園道 |
| Path | 步道 | ・パス | 小径 |

**JP 雙軌規則（實作時新增，文件原案未涵蓋）**：詞幹含片假名 → 片假名後綴＋`・`；
詞幹為漢字/和語（中文源專名如 成華／台北／明石／紫霄，或意譯漢語詞如 農業／希望／
安全／工兵）→ 漢字後綴。原案一律片假名後綴會產出 `成華ロード` 這種不自然組合，
實作已改為 `成華通り`、`農業大通り`、`紫霄小径`。

**與官方重名者一律複用官方譯名**（17 條，含跨 dataset）——保跨地圖用詞一致。這也推翻
原案「`KY-`/`US-` 路線號保留拉丁字元」：官方譯 `KY-60 → 60號公路`、
`KY-163 → 163號公路`，CH/CN 沿用官方，JP 保留 `KY-60`（日文地圖慣例）。
官方另已有 `Northwestern Railroad (Muldraugh - Brandenburg) → 西北鐵路 (馬爾德勞 - 勃蘭登堡)`、
`Dixie Highway (Route 31W)`、`Fiddler's Trail`、`Rock Ridge Road` 等 SecretZ 沿用的街名。

- 專名片假名音譯；數字路 `10th St` → `10番通り`；括號註記照譯（`(Under Construction)` → `（工事中）`）。
- 撞名閘門兜底：任何風格選擇導致譯後撞名＝generator fail，逐條覆寫解決。
- CN 由 CH 經 OpenCC `tw2sp` 轉出（同本包 Steam 描述既有做法）；人名音譯沿用台灣慣例。
- 出貨前日語母語覆核（遺留開口）。

## 範圍：全收錄權威普查（2026-08-26 實查，取代先前估算）

方法：解析 registerMaps 全部 92 條目 → 以本機 Workshop `mod.info` 的 `id=` 建索引
（**注意 `mod.info` 可能在 `<mod>/42/` 版本子目錄，索引須含該層**，第一次普查漏此層導致
Daisy／Anruisi 誤判為「無副本」）→ 掃各 mod `media/maps/*/streets.xml`。
本機副本覆蓋率 **92/92（100%）**。

結果：**23 個 (mapMod, mapDir) 組合有 streets.xml，計 1,494 條／1,282 unique**。
其餘收錄圖（含 Chinatown、RaccoonCity）無 streets.xml。
**CJK 檢查全數為 0——沒有任何地圖作者自帶中文/日文街名，全部都需翻譯。**

納入本次實作的 20 個 dataset（不含 Muldraugh 1993）＝ **340 unique**：

| dataset ID | mapMod | mapDir | 條/unique |
|---|---|---|---|
| tikitown | tikitown | Tikitown | 99/95 |
| anruisi-town | AnruisiTown | AnruisiTown | 59/32 |
| raven-creek | RavenCreekB42 | Raven Creek B42 | 45/21 |
| raven-creek-kardinal | kardinal_ravencreek_B42 | Raven Creek B42 | 45/44 |
| daisy-county | Daisy County B42 version | Daisy County | 44/44 |
| camden-county | CamdenCountyB42 | Camden County B42 | 40/40 |
| west-point-expansion | WestPointExpansionB42 | West Point Expansion_B42 | 18/18 |
| greenport | GreenportB42 | Greenport, KY | 15/15 |
| little-township | LittleTownshipB42 | LittleTownshipB42 | 4/4 |
| wildsteel | WILDSTEEL | WILDSTEEL | 4/4 |
| blackmaze-wp | blackmaze_wp | Blackmaze_wp | 4/4 |
| sz-riverside2 | Secretz42 | SZ_Riverside_Checkpoint_2 | 4/4 |
| sz-westpoint-bridge | Secretz42 | SZ_Westpoint_Bridge_Checkpoint | 4/2 |
| eds-auto-salvage | EdsAutoSalvageB42 | EdsAutoSalvageB42 | 3/3 |
| sz-checkpoint8 | Secretz42 | SZ_Checkpoint8 | 2/2 |
| sz-marchridge-research | Secretz42 | SZ_MarchRidge_ResearchFacility | 2/2 |
| sz-riverside1 | Secretz42 | SZ_Riverside_Checkpoint_1 | 2/2 |
| megurigaoka-city | Project Gurashi | Megurigaoka City, Kanagawa | 2/2 |
| clover-lake | Clover Lake | Clover Lake | 1/1 |
| sz-checkpoint5 | Secretz42 | SZ_Checkpoint5 | 1/1 |

`raven-creek` 與 `raven-creek-kardinal` 是規劃預期的「同 mapDir 不同圖資」實例
（21 vs 44 unique，內容互不相交）——loader 必須以啟用 mapMod 甄別，這也是不採純 mapDir
約定路徑的理由。

未納入的兩類：
- **Muldraugh 1993**（`muldraugh1993b42`，1,092 條／938 unique）：與官方 1,098 條有 891 個重名。
  CH/CN 可高比例複用 LangFor42 既有中文街名（891/938 ≈ 95%），但 **JP 需新譯 938 條**——
  工作量不對稱且該圖正式服不上，**單獨決策**。
- **Project Gurashi 的兩個 spawn 小圖**（`Challenge Spawns`、`Megurigaoka High Spawns`，各 2 條）：
  非我方註冊的 pyramid 底圖，registry 無對應條目可掛 dataset；主圖 `Megurigaoka City, Kanagawa`
  已納入。

引擎側無容量風險：`StreetLookup` 稀疏 cell 索引只查視窗；`ObjectPool` 1024 是**回收池**上限
非 live 物件上限（ObjectPool.java:55 池空直接 new）；替換式載入不增 live 街道數
（跳過英文，只載一份所選語言）。三份 XML 只費磁碟。

遺留開口：出貨前做密集市區遊戲內 smoke test（中日文較長標籤的避讓/縮放視覺確認），
不必建 benchmark。

## 實作狀態（2026-08-26 完成）

程式與資料全數落地，離線驗收全綠；**僅剩遊戲內視覺驗收待人工**。

| 項目 | 狀態 |
|---|---|
| 主 MOD `MinidoracatMiniMap_StreetI18n.lua`（177 行，wrap 目錄層、add-only、per-call 語言 gate、mapMod 甄別、pcall fallback、logOnce） | ✅ |
| 主 MOD `Core.getRegisteredPacks()`＋validator 白名單加 `streetI18n` | ✅ |
| 安裝可觀測性：`StreetI18n armed` / `StreetI18n DISABLED: ...` 各一行 log | ✅ |
| registerMaps 20 條目加 `streetI18n`＋明確 `mapDir` | ✅ |
| `street-names/<id>/names.json` 20 組 / 340 unique 三語 | ✅ |
| `scripts/gen_streets_i18n.py`（gen/verify/--selftest 50 項） | ✅ |
| 搜尋雙語：`MinidoracatMiniMapModMapsStreetNames.lua`（398 條英文原名＋首點，append 進主 MOD 同一全域表；主 MOD 搜尋零改動） | ✅ |
| 生成物 60 檔（20×3 語）/ 320 KB / 無 BOM / 不被 gitignore 擋 | ✅ |
| `scripts/map_tracker.py streets-scan` ＋ `tracker-state/streets_hashes.json` | ✅ |
| `scripts/verify_street_i18n.lua`（197 項，含 append 行為與英文原名可搜斷言） | ✅ |
| 掛載回歸（新增 11 個 mapDir 後 91 顆 zip 全掛、identity 0 未解析） | ✅ |
| AGENTS.md 鐵則／端到端第 3-4,6 步／追蹤器判定／發布驗收 | ✅ |
| CHANGELOG（本包 0.7.0、主 MOD 0.21.0）＋ mod.info bump ＋ README | ✅ |
| **遊戲內視覺驗收** | ⬜ 待人工 |

遊戲內驗收步驟（2026-08-26 更新：伺服器測試改走 `maptest`，見 AGENTS.md「測試與 Log」）：
1. `link_workshop.bat` → `4`：建連結並把地圖 MOD 寫進 **`maptest.ini`**（servertest 保持乾淨）。
2. `PZ_Test.bat` → `7`（只開伺服器）或 `8`（伺服器＋客戶端），連 `127.0.0.1:16271`。
   已實測伺服器可正常啟動（44 秒、89 張圖載入）。
3. **主畫面／伺服器啟動後驗第一關**：客戶端 `console.txt` 應有
   `[MinidoracatMiniMap] StreetI18n armed`（伺服器端不載 client lua，這行只在客戶端）。
   看到 `StreetI18n DISABLED` ＝ lua 載入序假設被打破，wrapper 沒安裝。
4. 進世界走到該地圖範圍、開小地圖與世界地圖（M）：路名應為中文/日文。
   `console.txt` 應有 `streetI18n loaded <dataset> (CH|CN|JP) from ...`。
5. 三語各抽一次（主選單切語言→新建地圖 UI 即生效，不必重啟）。
6. **提基鎮（tikitown）必須用單機驗**——它在伺服器／多人會因引擎 animset 大小寫 bug
   崩服，已列入 `$MapModExclude`（完整因果見 AGENTS.md）。其 99 條街名功能本身無問題。
7. 密集市區目視中日文較長標籤的避讓/縮放（規劃遺留開口）。
8. 搜尋雙語抽驗：搜中文譯名（引擎索引）與英文原名（烘焙表）各一次。

## 實施順序

1. **主 MOD**：`initDirectoryStreetData` wrapper＋dataset 解析＋語言 gate＋debug log（新版本發布）。
2. **本 repo**：`gen_streets_i18n.py`＋驗證閘門＋`street-names/` 20 組 names.json
   （CH 先行，CN 走 OpenCC＋人工校，JP 按後綴表＋人工）＋registerMaps 加 `streetI18n`
   欄位（**已完成**：20 條目，各帶明確 mapDir）＋生成物。
3. **追蹤器**：`streets_sha256` 軸＋issue 判定文案＋AGENTS.md SOP 補「街名翻譯需更新」處置。
4. **驗證**：`verify_pack_mount.lua` 擴充（或旁掛）street 替換斷言；進遊戲三語各抽一圖目視；
   密集市區 smoke test。
5. 發版：CHANGELOG＋四語 Steam 描述提及新特性；README 收錄地圖表加「街名翻譯」欄。

## 明確不做

- 動態原地改寫（`setTranslatedText` 任一變體）、載英文後追加中文（雙份疊畫）、
  VFS 覆寫原 `streets.xml`（語言不可知，會污染英文玩家）、Translate JSON 新 API、版本握手。
- RaccoonCityB42 等無 streets.xml 地圖不補做路網。
- ModLangFor42 不參與（維持 JSON-only 邊界）。

## 實作後的設計調整（2026-08-26，發版前實測驅動）

規劃階段假設「上游 `streets.xml` 只含該地圖自己的街道」。實測推翻此假設，衍生兩個
規劃時未預見的機制。**兩者都由玩家回報驅動**，故一併記錄根因與判定依據。

### 1. `keep_geometry` ＋ `keep-scan`（新增剔除層）

根因：引擎每張官方地圖目錄都放**同一份全世界 1098 條街道**，作者複製後改幾筆就當
自己的圖用。我方無條件翻譯 ⇒ 與本體漢化同座標疊成「Rac浣熊路oad」。

`gen_streets_i18n.py keep-scan` 對 vanilla 全域表逐條**五道**剔除（命中即停）：

|規則|判定|依據|
|---|---|---|
|`same`|幾何完全相同|整條照抄官方|
|`near`|同名且 ≤2 點、位移 ≤2 square|微調座標，視覺仍疊合|
|`clash`|比對鍵相同且共線重疊 ≥24 square|重畫同一條路（`Pony Trot Rd` vs 官方 `Pony Trot Road`）|
|`overlay`|**不分名字**累計共線重疊 ≥60%|把官方的路改名重畫|
|`oob`|過半點落在 registry `bounds` 外|全域表殘留，不屬本圖|

架構分離：**只有 `keep-scan` 需要遊戲安裝目錄**；`gen`/`verify` 只讀 `names.json` 的
指紋清單 ⇒ CI 無需 vanilla 參考檔。上游改街名或本體 build 更新都要重跑 `keep-scan`
（判定基準是官方路網）。

踩過的兩個坑（都有 selftest 守著）：

1. **共線判定用了正規化前的座標**。作者常把街道畫成矩形輪廓，原始四邊各偏中心線
   ±width/2 ⇒ 拿原始座標比會整批漏判。實測雛菊郡 `Ivy Road` 輪廓在 y=7446/7456、
   中心線 y=7451 才與官方 `Raccoon Road` 重疊 300 square。第一版 `overlay` 對
   daisy-county 判 0 命中，玩家回報「浣熊路還是跟常春藤路一起」才抓到。
   → 改為一律用 `drawn_points`（正規化後＝實際繪製）比對。
2. **`overlay` 用絕對長度會誤剔**。實測比例分佈涇渭分明：`Ivy Road`／`Meadow Way`
   等 6 條是 **100%** 蓋住官方路（該剔），而 `Dahlia Court` 33%、西點擴張
   `Hillcrest Ln` 13%、Kardinal 渡鴉溪 `Falmouth Road` 18% 只是**路口接到**官方路。
   用絕對長度會讓 753 square 的 `Hillcrest Ln` 因 98 square 的路口整條路名消失。
   → 門檻改為比例 60%，並保留 24 square 絕對下限濾雜訊。

另一個先前踩過的：**不可用「名稱白名單」**。同一張圖可能有同名不同段的街（1993 的
`Main St` 既有獨有段、也有與官方幾何相同的段），按名稱過濾會把後者放過去、照樣疊字
（實測名稱白名單產出 227 條、幾何指紋才是正確的數字）。

剔除清單同時套用在**英文原名表**（`bake_english_table`）：被剔除的街不是本包替換的，
主 MOD 的官方表已含其英文原名，重烘會讓搜尋結果出現兩筆同座標條目。

### 2. 收錄範圍縮減（21 → 15 dataset）

`keep-scan` 實測結果（上游 → 保留）：

|dataset|上游|剔除明細|保留|
|---|---|---|---|
|muldraugh-1993|1092|same 913／near 4／clash 83／overlay 7／oob 33|**52**|
|tikitown|99|clash 3／overlay 1|95|
|daisy-county|44|overlay 6|38|
|west-point-expansion|18|clash 4／overlay 2|12|
|eds-auto-salvage|3|clash 1|2|
|little-township|4|clash 1|3|
|SecretZ ×6|1–4|**same 全部**|**0**|
|其他 8 個|—|無|全保留|

**SecretZ 的 6 個據點 dataset 保留 0**——15 條街全部是官方路網的幾何複本，且譯名與
官方漢化逐字相同（`KY-60`→60號公路、`Otter Creek Road`→水獺溪路…）⇒ 翻譯它們只有
負面效果，已從 registry 與 street-names 移除。

最終：**15 dataset／355 unique 譯名／417 條替換街道／英文原名表 417 條**。

### 3. 刻意不做：官方路穿過 MOD 地圖

`overlay` 剔掉整條蓋住的，剩下比例低於門檻的短重疊（路口相接）仍會兩份都畫。
要全消得剔除**官方**街道 ⇒ 動 vanilla 路網、影響 NavRoute 尋路，不做。
四語 Steam 描述已寫明責任歸屬：這是地圖 MOD 未遵守「每張地圖只定義自己的路」的
資料問題，本包已剔除可剔的部分，剩下請向原地圖作者反映。
