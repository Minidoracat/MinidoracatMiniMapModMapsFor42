# B42 多地圖伺服器崩服筆記：getZombieIntensityForChunk NPE 與 Map= 排序

2026-07-17 首次在本機 -nosteam 測試伺服器（73 張支援地圖全上）撞到並解決。
**與本 MOD（主 MOD／地圖包）無關**——純引擎 bug＋地圖 MOD 組合觸發，但玩家可能在
「訂閱支援地圖收藏後開服／開檔」時撞到並回報給我們，故記錄完整因果與解法。

## 症狀

伺服器啟動於世界初始化階段直接終止：

```
java.lang.NullPointerException: Cannot invoke "zombie.iso.LotHeader.getZombieIntensity(int)"
    because "lotHeader2" is null at LotHeader.getZombieIntensityForChunk(LotHeader.java:81)
  at zombie.iso.IsoMetaCell.getChunk / addRoom / addRooms
  at zombie.iso.IsoMetaGrid.addRoomsToAdjacentCells (CreateStep2)
  at zombie.iso.IsoWorld.init → GameServer.main
LOG: Server Terminated.
```

沒有建築踩到危險位置時，崩在稍後的 `MapCollisionData.init`，NPE 訊息相同：

```
java.lang.NullPointerException: Cannot invoke "zombie.iso.LotHeader.getZombieIntensity(int)"
    because "lotHeader2" is null at LotHeader.getZombieIntensityForChunk(LotHeader.java:81)
  at zombie.MapCollisionData.init
  at zombie.iso.IsoWorld.init → GameServer.main
LOG: Server Terminated.
```

單機照程式同樣會中（同一套 `IsoWorld.init`，`MapCollisionData.init` 在客戶端以外都跑），沒有實測；只是玩家較少同時啟用大量地圖。

## 根因（42.19 反編譯查證）

引擎在「這個 chunk 的殭屍密度該問哪個地圖目錄」的判定裡**混用兩套 cell 網格**：

1. `MapFiles.bgHasCell300`（MapFiles.java:120-135）：每個地圖目錄的覆蓋圖，用 **B41 的
   300 格網格**建立，且一格要求 `hasCell(對角兩個 256-cell)` 同時存在才標記——
   粒度粗、邊緣外溢。
2. `LotHeader.getZombieIntensityForChunk`（LotHeader.java:63-83）：從該 cell 擁有者的
   priority 沿 `Map=` 順序**往低優先方向**掃，第一個 bgHasCell300 命中的目錄就用
   **B42 的 256 格座標** `getLotHeader(cellX, cellY)` 拿資料——**沒有 null 檢查**。

當鄰近地圖 B 的 300 格覆蓋圖「聲稱」蓋到地圖 A 的 cell（300≠256 的外溢），但 B 實際
沒有那個 256-cell 的 lotheader → `lotHeader2` 為 null → NPE。

觸發不需要建築：`MapCollisionData.init` 對每個 cell 的全部 chunk 各問一次殭屍密度，只要有一個 chunk 落在這種
位置就崩（2026-11-10 實機確認，見下方「42.22.2 複查」）。有建築跨在上面時更早崩在 `addRoomsToAdjacentCells`，
**vanilla 自己的建築**跨 cell 邊界伸進 MOD 擁有的 cell 也算（2026-07-17 的實際案例：vanilla 建築 `40_39_6` 東跨進
Muldraugh 1993 的 cell 41,39，被 RaccoonCity 的 bg300 外溢誤傷）。地圖區域註冊（`IsoMetaGrid.registerZone`）踩到時
只在 log 留一筆同樣的 NPE，不中斷。

## 解法：Map= 排序

掃描只往「低優先」方向走 → **把肇事圖排在 `Map=` 最前面（優先序最高）**，任何 cell 的
掃描都不會經過它們，會一路落到有正確 lotheader 的目錄（通常是 vanilla）安全返回。

本包收錄的地圖兩兩枚舉（2026-11-10），會崩的先後關係共 10 對，前者必須排在後者前面：

| 要排前面 | 要排後面 |
|---|---|
| `Taylorsville` | `Coryerdon B42`、`Coryerdon`、`Daisy County` |
| `Coryerdon B42`、`Coryerdon` | `Greenport, KY` |
| `AnruisiTown` | `Camden County B42`、`Mount Crow City` |
| `Camden County B42` | `Atlanta` |
| `RaccoonCity` | `Muldraugh 1993 B42` |
| `pzkNewCoalfield` | `BBL_b42` |

照這個順序開頭就全部滿足，其餘任意序：

```
Map=AnruisiTown;Taylorsville;Coryerdon B42;RaccoonCity;Camden County B42;pzkNewCoalfield;<其餘任意序>;Muldraugh, KY
```

（用科里爾登 2026 移植版時，`Coryerdon B42` 換成 `Coryerdon`。）

- 與 Coryerdon 作者頁面警告「Coryerdon 必須排在 Taylorsville 下面否則 crash」完全一致
  ——社群早就在個案撞過這顆雷。
- 注意：把某圖提前會改變重疊 cell 的擁有權，可能冒出新的肇事對——**改完必重跑偵測器
  迭代至歸零**（本次 AnruisiTown 就是第二輪迭代加進來的）。

## 42.22.2 複查（2026-11-10）

- `LotHeader`、`MapFiles` 兩版反編譯內容相同：雷照舊在，排序解法不變。42.22.2 快照行號：
  `LotHeader.getZombieIntensityForChunk` 在 LotHeader.java:64-84（`lotHeader2` 取值在 :75，仍無 null 檢查），
  `MapFiles.bgHasCell300` 在 MapFiles.java:124-131。上面症狀段的 `:81` 是遊戲 stack trace 的行號，和反編譯行號不同。
- `IsoMetaGrid.addRoomsToAdjacentCells` 改成把建築登記到它跨到的每個 cell（原本只到 2×2 個 cell），
  跨 3 個 cell 以上的大建築會多觸發幾次；危險組合的判定不受影響。
- 2026-11-10 實機（42.22.2 專用伺服器）：`Map=Coryerdon B42;Taylorsville;Muldraugh, KY`（偵測器算出 2 個危險組合、
  沒有建築踩到）開服崩在 `MapCollisionData.init`；兩張圖對調（`Taylorsville;Coryerdon B42;Muldraugh, KY`）正常開服。
  之前把「沒有建築踩到」當成只是潛在雷，這個說法不對：危險組合一個就崩。

## 工具

- `scripts/check_map_conflicts.ps1`：離線模擬引擎判定（讀 lotheader 檔名重建 bg300／cell 擁有權）。
  **每次新增支援地圖後必跑**；「危險組合」非 0（exit 1）就把 culprit 加入 `link_workshop.ps1` 的
  `$MapOrderFirst` 再重跑驗證。
- `scripts/link_workshop.ps1` 選單 4：寫入 `Map=` 時自動套 `$MapOrderFirst` 順序
  （含矯正既有錯序），vanilla `Muldraugh, KY` 自動墊底。

## 驗證心得

- 開服成功與否**別只看 log**：B42.19 重導 stdout 時啟動完成訊息可能不出現。鐵證是
  執行緒 dump（jstack）看到 main 執行緒穩定在 `GameServer.main` 主迴圈的
  `Thread.sleep`（serverUpdateLimiter 節流）。
- 無害噪音，不用理：`ZipBackup ... AccessDeniedException`（備份例程跳過 mods 目錄的
  符號連結）、`duplicate RoomDef.metaID`（重疊地圖的房間定義重複，引擎記錄後續行）。

## 附帶坑：Debug 模式連線＝黑畫面假死

客戶端用 **-debug** 連多地圖伺服器，若任一 MOD 的 Lua 出錯（實例：Taibeiroad4 的
`TCGMusicDefenitionsTCBoomboxtb1.lua` 對 nil 的 `GlobalMusic` 賦值——它引用未安裝的
True Music 框架，跟它漏宣告 tile 依賴同款粗糙），Debug 模式會停在
`UIManager.debugBreakpoint` 等人按繼續，但連線中途沒有 UI 可按 → **黑畫面永久卡住**
（jstack 可見邏輯執行緒停在 KahluaUtil.fail → debugBreakpoint）。
**解法：多地圖測試一律用一般模式連線**——同樣的錯誤只會記 log 然後繼續，不影響遊玩
（Taibeiroad 作者自己也聲明報錯不影響體驗）。

## 附帶坑 2：移除地圖 MOD 後存檔無法載入（WorldDictionary）

多數地圖 MOD 含自訂物品腳本；世界一旦在啟用狀態下運行過，物品就登記進該存檔的
WorldDictionary。之後移除地圖 MOD（如 link_workshop 選單 7）再載入同一存檔，客戶端
會在 `WorldDictionary.init` 拋致命錯誤（實例：移除鳶尾島後
`Missing dictionary script on client: Base.ESWineCask` →「未知的意外錯誤」黑畫面）。
**PZ 對既有存檔「加」內容 MOD 大致安全、「移除」不支援**。解法：開新存檔／重置伺服器
世界（刪或改名 `Saves\Multiplayer\<servername>`，ini 不動），或把 MOD 掛回去。

## 玩家回報支援 SOP

- log 含 `getZombieIntensityForChunk`／`lotHeader2 is null` → 不是本 MOD 的問題；
  請對方把上述肇事圖移到伺服器 `Map=` 最前（單機為地圖 MOD 載入順序最上面），
  或告知其實際地圖組合後用偵測器算安全順序。
- log 含 `WorldDictionaryException`／`Missing dictionary script` → 玩家從既有存檔
  移除了地圖 MOD；引導開新存檔或把 MOD 加回（見附帶坑 2），同樣不是本 MOD 的問題。
