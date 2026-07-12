# media/minimap/ — 地圖包 pyramid zip

本地圖包收錄的各地圖 MOD 小地圖圖像（檔名＝地圖原名，pzmap Studio 預設輸出名）。

- 新增支援地圖：pzmap Studio 選該地圖 →「遊戲內小地圖」模式輸出 zip 丟進來，
  並在 `media/lua/client/MinidoracatMiniMapMaps.lua` 的註冊清單加一行
  （mapMod＝該地圖 MOD 的 mod ID；bounds 抄渲染輸出的 `pyramid.txt` 第二行）。
- 翻譯：`Translate/<LANG>/UI.json` 加對應 nameKey。
- `*.pyramid.zip` 為渲染產物，**不進版控**（見專案 .gitignore）。
