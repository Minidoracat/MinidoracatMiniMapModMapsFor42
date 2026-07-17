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

單機理論上同樣會中（同一套 `IsoWorld.init`），只是玩家較少同時啟用大量地圖。

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

觸發者不限於 MOD 建築：**vanilla 自己的建築**跨 cell 邊界伸進 MOD 擁有的 cell 也會經
`addRoomsToAdjacentCells` 觸發（本次實際案例：vanilla 建築 `40_39_6` 東跨進
Muldraugh 1993 的 cell 41,39，被 RaccoonCity 的 bg300 外溢誤傷）。

## 解法：Map= 排序

掃描只往「低優先」方向走 → **把肇事圖排在 `Map=` 最前面（優先序最高）**，任何 cell 的
掃描都不會經過它們，會一路落到有正確 lotheader 的目錄（通常是 vanilla）安全返回。

目前組合（72 張支援地圖）驗證安全的順序：

```
Map=AnruisiTown;Taylorsville;RaccoonCity;Camden County B42;<其餘任意序>;Muldraugh, KY
```

- 與 Coryerdon 作者頁面警告「Coryerdon 必須排在 Taylorsville 下面否則 crash」完全一致
  ——社群早就在個案撞過這顆雷。
- 注意：把某圖提前會改變重疊 cell 的擁有權，可能冒出新的肇事對——**改完必重跑偵測器
  迭代至歸零**（本次 AnruisiTown 就是第二輪迭代加進來的）。

## 工具

- `scripts/check_map_conflicts.ps1`：離線完整模擬引擎判定（讀 lotheader 檔名重建
  bg300／cell 擁有權，pzmap `poi` 取建築矩形找實際觸發者）。**每次新增支援地圖後必跑**；
  「危險組合」非 0 就把 culprit 加入 `link_workshop.ps1` 的 `$MapOrderFirst` 再重跑驗證。
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

## 玩家回報支援 SOP

玩家回報「訂閱收藏後開服／讀檔 crash」且 log 含 `getZombieIntensityForChunk`／
`lotHeader2 is null` → 不是本 MOD 的問題；請對方把上述四張圖移到伺服器 `Map=` 最前
（單機為地圖 MOD 載入順序最上面），或告知其實際地圖組合後用偵測器算安全順序。
