#!/usr/bin/env python3
"""產生 MOD/MinidoracatMiniMapModMapsFor42/workshop.txt（Workshop 上傳工具輸入）。

來源＝STEAM_DESCRIPTION_EN.md（EN＝上傳工具推成 Steam 主/預設語言槽，所有無專屬
語言槽的 fallback；繁中/簡中/日文靠網頁語言槽分別貼），metadata 內建於本腳本。

為何存在：本 repo 的 workshop.txt 進版控（與主 repo 不同），過去靠手動逐行加
`description=` 前綴同步——2026-08-25 就漏過一次（張數停在舊值）。改由腳本生成後，
發版前跑一次即與 EN 描述一致，不再有人工漏同步的空間。

遊戲上傳（或開上傳工具）後會回寫本檔——內容為 Steam 主語言槽描述＋CRLF＋結尾
"Workshop ID:" 行（getSubmitDescription，SteamWorkshopItem.java:164-181）。
本檔進版控，故回寫會弄髒工作樹：`git checkout --` 丟棄即可，勿 commit。
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN = os.path.join(ROOT, "STEAM_DESCRIPTION_EN.md")
OUT = os.path.join(
    ROOT, "MOD", "MinidoracatMiniMapModMapsFor42", "workshop.txt"
)

# Workshop metadata（來源真相在此）
META_HEAD = [
    "version=1",
    "id=3763914102",
    "title=Minidoracat MiniMap - MOD Maps for B42",
]
META_TAIL = [
    "tags=Build 42;Interface;Map;Multiplayer",
    "visibility=public",
]


def main():
    with open(EN, encoding="utf-8") as fh:
        en = fh.read().rstrip("\n").splitlines()
    lines = META_HEAD + ["description=" + l for l in en] + META_TAIL
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"workshop.txt: {len(en)} description lines, {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
