# MOD 地圖街名與獨立道路修正

名稱翻譯不再替換整份語系 XML；已確認的道路修正改為另一組與語言無關的 pins。
公開介面的單一來源為 [小地圖 Addon API](../../MinidoracatMiniMapFor42/docs/addon-api.md)。

## 目標與分工

- 地圖原作者的 `streets.xml` 是來源；翻譯只決定名字，獨立修正決定已核准的幾何調整。
- 本包提供 `street-names/` 名稱對照與 `road-repairs/` 修正 pins，兩支生成器各自運作。
- 小地圖本體負責來源核對、顯示副本的暫時套用／還原，以及讓導航使用相同修正。
- 不修改 AutoDrive 控制邏輯；本輪不調整 LangFor42 的原版中文街道來源。

## 資料來源與生成物

`names.json` 的 `names` 為原始街名到 `{ch, cn, jp}` 的對照。鍵保留上游原字串，包含空格；
例如 AnruisiTown 的 `Forest  St` 有兩個空格，不能只保存一個空格的版本。
來源 `workshop_id`、`map_mod`、`map_dir`、hash 等中繼資料用於上游追蹤，不限制執行期道路。
舊 `keep_geometry` 若仍留在歷史來源中，不再參與生成或載入。

生成器輸出：

1. `shared/MinidoracatMiniMapModMapsStreetNames.lua`：
   `MinidoracatMiniMapModMapsStreetNames[dataset][原名] = UI鍵`，不含座標與譯文。
2. `shared/Translate/{EN,CH,CN,JP}/UI.json`：名稱譯文；保留其餘既有 UI 鍵。
   EN 與缺譯語言保持原名，三語全缺的街名不建立翻譯鍵。字面 `%` 依 PZ 規則轉為 `%%`。
3. client registry 的 `streetNames` 引用對應 dataset 字典；保留 `mapMod` 與 `mapDir`。

Lua 字串中的非 ASCII 原名以 UTF-8 十進位位元組跳脫，避免 Kahlua 字面量編碼問題。
本包不再 append 主 MOD 的 `MinidoracatMiniMapStreetNames`；MOD 地圖的原名搜尋由即時路網索引提供。

`road-repairs/<dataset>.json` 是另一組顯式核准資料，不從譯名推導：

- `scripts/gen_street_repairs.py` 只編譯 pins，輸出
  `shared/MinidoracatMiniMapModMapsStreetRepairs.lua`；registry 用 `streetRepairs` 引用。
- 每筆保存來源 ID／目錄、0-based 街道 index、原始完整點列及路寬。執行期不符就略過；
  不會在 `gen` 時自動接受上游新座標。
- 現有核准內容：Daisy County 44 條輪廓→中心線；Muldraugh 1993 913 筆完整複本標籤候選。
- 名稱、points 與 width 的來源追蹤可以各自更新；原版道路修補仍由主 MOD 既有 RoadPatches 管理。

## 來源辨識

以 `mapDir` 找候選，再依啟用 `mapMod` 選唯一字典。Raven Creek 的兩個移植版共用目錄名，
必須分別提供字典；兩版同時命中則保留原名，不按註冊順序任選。真正 alias 可引用同一張字典。
未知來源或未知街名（包含第三方已改過而無法辨認的名稱）保持原樣，不做譯名反查猜測。

## 引擎流程

```text
原作者 streets.xml
    ↓ 原生載入
分別查名稱對照與符合原始幾何的修正 pins
    ↓ 顯示窗口暫時套用名稱／修正／安全的重複顯示抑制
原生 combine 建立獨立顯示副本，之後還原 raw
    ├─ 玩家地圖顯示修正結果與譯名
    └─ 導航讀 raw，再套同一份幾何修正；搜尋共用修正後錨點
```

主要實作為主 MOD `_StreetData.lua`（載入協調）與 `_StreetRepairs.lua`（獨立修正）：

- `WorldMap.addStreetData` 同步把來源 `splitStreets` 複製到地圖的 `combinedStreets`
  （`WorldMap.java:193-218`、`WorldMapStreets.java:419-431`）。單改 raw 名稱不會改既有顯示副本。
- 一次性、未加入 UIManager 的 `UIWorldMap` 取得 raw 來源；以原生 `setPoint`／
  `addPoint`／`removePoint` 與 `setTranslatedText`、`clipToObscuredCells` 暫時準備副本，
  不用會通知 dirty 的 editor setter。原 loader 結束後還原 raw 原名與點列，再 clip。
- replacement 共用 preflight 限制為有效、非零長度、float32 可精確表示且至多 383 點；
  不能讓 Java 寫入量化後無法還原，也不能讓顯示與 Nav 單側接受超大點列。
- 巢狀新 map 載入會暫停外層 owned 修改，內層依自己的參照狀態重新判斷，結束再恢復外層；
  不能讓有參照的外層 mask 借到沒有參照的內層，或把暫存譯名再翻一次。
- 最後只清一次性 scratch 解除 listener，並丟棄它；絕不清玩家地圖。scratch 的死 lookup
  不再被使用，因此不會踩到 `WorldMapStreets.clear` 不清 lookup 的玩家地圖幽靈問題。
- 已有該來源的玩家地圖不重建；第三方提前載入、繞過／覆寫 loader 仍可能影響顯示。
- raw 原名用於鐵路辨識；搜尋同時匹配原名與譯名，兩者使用同一個即時道路錨點。

這是載入時的名稱處理，不是檔案熱更新。更新 XML／MOD 後應完整重啟遊戲。

## 取捨與邊界

翻譯不負責修路，必要的舊修正則獨立保留：

- Daisy County 44 條已確認的細長輪廓使用固定原始幾何 pins 改成中心線，所有語系一致。
- Muldraugh 1993 的 913 筆 exact-copy 僅是候選：同張 map 必須已載入幾何／路寬相同的
  canonical 或 carrier，且參照不被地圖優先序遮蔽，才抑制重複顯示。
- 不以空名稱留下可被 hover 選中的空框；在顯示窗口暫縮為兩重合點，native Clipper 不產生
  這個重複副本，隨即還原 raw。導航保留這條路，不用刪路藏字。
- 不同名字且該區由原 MOD 地圖勝出時，保留該 MOD 的名稱。原版尚未載入時也保留，
  不預測未來載入、不反向修改較晚加入的原版資料；部分 EN 同名疊繪仍可能存在。
- 舊 near、60% overlay、oob 剔除不搬回；19 筆只有 full-cover 的標籤候選也已撤回，
  因為幾何覆蓋不證明另一個標籤真的可用。部分重疊與未核准錯路維持來源行為。
- 沒有 `streets.xml` 的地圖不會因安裝本包就憑空獲得導航道路。
- Tikitown 的本機多人初始化阻礙與名稱處理無關；離線道路測試不等於伺服器成功啟動或實機駕駛驗收。

## 維護與驗證

```sh
python scripts/gen_streets_i18n.py gen
python scripts/gen_streets_i18n.py verify
python scripts/gen_streets_i18n.py --selftest
python scripts/gen_street_repairs.py gen
python scripts/gen_street_repairs.py verify
python scripts/gen_street_repairs.py --selftest
uv run scripts/verify_mod.py
```

`gen` 不要求已安裝上游副本：名稱資料可獨立生成。若找到上游，會非阻擋地提示未收錄原名；
`--update-hash` 可更新來源追蹤中繼資料。`map_tracker.py streets-scan` 仍獨立追蹤上游變更，
不要把街名更新誤判成圖片必須重渲。

主 MOD 的 `test_street_names.lua` 驗來源分離、幾何保留、缺譯、第三方改名、例外還原與重入；
`test_nav_kick.lua` 比較原名／譯名下的路線與鐵路排除；`test_search_logic.lua` 驗雙語共用錨點。
`test_street_repairs.lua` 驗共同幾何、upstream 漂移、reference 缺席／被裁、重入、
float32／native buffer 邊界與 byIndex 去重。真實 42.20.4 jar＋Clipper＋Kahlua 另驗：
Daisy 四語 44 條中線與同一路線；Muldraugh 1993 在參照已載的條件下抑制 913 個副本但
保留全部 1092 raw 街道；內層無參照保留自己的顯示；native MapFiles 將參照裁光時不誤藏。
這些是原生資料與路線冒煙，不代表已完成遊戲字型排版或實際駕駛驗收。

## 譯名慣例

沿用既有譯文，不因這次機制切換重譯：St→街、Road→路、Lane→巷、Ave/Dr/Blvd→大道、
Way→道（避免與 Road 撞名）；與官方同名者優先沿用既定譯名。日文片假名專名使用片假名後綴，
漢字／和語專名用漢字後綴。不同原名的譯文應避免造成不必要的同名歧義。
