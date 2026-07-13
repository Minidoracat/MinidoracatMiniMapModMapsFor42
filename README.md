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

## 收錄地圖

| 地圖 | 對應 MOD（mod ID） | 範圍（世界 square） |
|------|--------------------|---------------------|
| Muldraugh 消防局 | `beek_muldraugh_firedept` | 10496,8960 – 11008,9472 |
| Estate 39 | `Estate 39` | 8192,9728 – 8704,10240 |
| 唐人街擴張區 | `Chinatown Expansion B42 version`（含 Less Traffic Jam 變體） | 10752,8192 – 11264,9216 |

## 專案結構

```
MinidoracatMiniMapModMapsFor42/
├── STEAM_DESCRIPTION.md           # Steam 商店頁描述（中文）——改動時必同步 _EN / _JP 版
├── link_workshop.bat              # Workshop 符號連結管理（雙擊啟動）
├── PZ_Test.bat                    # PZ 本地測試啟動器（雙擊啟動）
├── scripts/                       # PowerShell 腳本
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
2. `MinidoracatMiniMapModMaps.lua` 註冊清單加一行（bounds 抄渲染輸出 pyramid.txt）
3. `Translate/*/UI.json` 加地圖名翻譯鍵
