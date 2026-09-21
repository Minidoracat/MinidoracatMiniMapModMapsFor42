[h1]🗺️ Minidoracat MiniMap - MOD Maps for B42[/h1]
[h3]By Minidoracat[/h3]

[hr][/hr]

[h2]✨ これは何？[/h2]
[b]Minidoracat MiniMap for B42[/b] 本体 MOD 用の[b]マップパック addon[/b]：
複数のマップ MOD のミニマップ画像（実際のゲーム画面からレンダリング）と
範囲枠線データを収録しています。
[list]
[*] [u]自動検出[/u]：対応するマップ MOD が有効なときだけ表示——入れていない地図を誤描画しません
[*] 範囲枠線＋名前ラベル（多言語対応）で、ミニマップ／ワールドマップ上の MOD マップをすぐ発見
[*] 本パック導入時のみ現れる専用オプション：MOD マップ画像の表示切替・枠線切替・枠線色（デフォルト緑）
[*] [b]道路名の翻訳[/b]：16 組のマップデータに繁体字／簡体字／日本語で対応し、原名と訳名の両方で検索可能
[/list]

[h2]🗺️ 収録マップとリクエスト[/h2]
現在 [b]79 個のマップ MOD（102 マップ）[/b]に対応。[url=https://steamcommunity.com/sharedfiles/filedetails/?id=3766382352]対応マップコレクション[/url]から必要なマップを選んでサブスクライブできます。対応リスト・原作者クレジット・マップリクエストは
[url=https://steamcommunity.com/workshop/filedetails/discussion/3763914102/568165880361411088/]ディスカッション[/url]へどうぞ！
[url=https://github.com/Minidoracat/MinidoracatMiniMapModMapsFor42/issues/new/choose]GitHub Issue フォーム[/url]からのリクエストも歓迎です（開発バックログに直行、対応が最速）。

[h2]道路名の翻訳[/h2]
[b]16 組・360 件[/b]の道路名を[b]繁体字／簡体字／日本語[/b]に翻訳します。名前だけを翻訳し、道路座標は元のマップ作者のデータを使用します。原名と訳名の検索先は同じ現在の道路位置です。[b]本体 MOD 42.20.4-0.27.0 以降が必要[/b]——両方を同時に更新し、ゲームを再起動してください。
未登録の道路名は原名のまま表示します。道路データがないマップにナビ用道路網を追加する機能ではありません。
道路名検索結果の「MOD マップ：マップ名」という出典表示は本体 MOD が提供します（繁体字／簡体字／英語／日本語）。本パックは名前の対応表と道路修正データのみを提供します。

[h2]道路データと対応範囲[/h2]
道路修正は言語に依存しない別データで行い、確認済みの輪郭道路を中心線に変更します。元の形状が一致しなければ適用しません。確実な重複表示だけを抑制し、ナビ用道路は削除しません。不確かな重複は残ります。画像対応はナビや自動運転の動作保証ではありません。
要件と既知の制限は[url=https://steamcommunity.com/workshop/filedetails/discussion/3763914102/569297034317714585/]英語・繁体字の固定トピック[/url]をご覧ください。
Foxtrot Warehouse は Atlanta と全セルが重なるため、どちらか一方を選んでください。Atlas Underground Complex は[b]地表画像のみで、地下階の平面図はありません[/b]。SecretZ などと一部が重なり、併用の互換性は保証しません。

[h2]🔧 サポート範囲[/h2]
本パックは[b]ミニマップ／ワールドマップ画像と道路名翻訳データ[/b]を提供し、実際のゲーム地形は変更しません。
[list]
[*] 画像の問題（表示ずれ・枠線位置・名前の翻訳）→ 本ページ、または [url=https://github.com/Minidoracat/MinidoracatMiniMapModMapsFor42/issues/new/choose]GitHub Issue フォーム[/url]へどうぞ（スクリーンショット添付可、対応が最速）
[*] マップMOD自体の不具合（タイル欠け・建物バグ・マップ間の競合・セーブ問題・[b]道路名データの規約違反[/b]）→ 元のマップ作者へ報告してください
[/list]

[h2]🔗 シリーズ MOD[/h2]
[list]
[*] [b]本体 MOD（必須）[/b]：[url=https://steamcommunity.com/sharedfiles/filedetails/?id=3763913359]Minidoracat MiniMap for B42[/url]——地図画像化の本体
[*] [b]このページ[/b]：MOD Maps——マップ MOD 用マップパック addon
[*] [b]任意[/b]：[url=https://steamcommunity.com/sharedfiles/filedetails/?id=3765182411]MOD Compatibility[/url]——サードパーティ MOD 互換パック（犬・馬などの動物アイコン）
[*] [b]任意[/b]：[url=https://steamcommunity.com/sharedfiles/filedetails/?id=3768276209]Zones[/url]——サーバーカスタムゾーン表示
[/list]

[h2]📋 MOD 情報[/h2]
[list]
[*] [b]Mod ID:[/b] MinidoracatMiniMapModMapsFor42
[*] [b]前提 MOD:[/b] [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3763913359]Minidoracat MiniMap for B42[/url]（本体 MOD。[b]42.20.4-0.27.0 以降が必要[/b]。無いと本パックは機能しません）
[*] [b]ロード順:[/b] 手動調整は不要——require で依存を宣言済みのため、ゲームが自動的に本体を先に読み込みます
[*] [b]対応バージョン:[/b] Build 42.20.0+
[*] シングル / マルチ両対応（クライアントサイドの画像のみ、ワールドは変更しません）
[/list]

[h2]💬 不具合報告・交流[/h2]
[url=https://github.com/Minidoracat/MinidoracatMiniMapModMapsFor42/issues]🐛 GitHub Issues[/url]——マップリクエスト＆画像問題報告フォーム
[url=https://discord.gg/Gur2V67]👉 Discord サーバーに参加[/url]

[h2]☕ 作者を応援[/h2]
この MOD は今後もずっと無料です。気に入ったらコーヒーを一杯おごってください。支援はサーバーと MOD 開発に使います。ソースコードは GitHub で公開しています。
[url=https://ko-fi.com/minidoracat][img]https://raw.githubusercontent.com/Minidoracat/workshop-resources/refs/heads/main/badges/badge_kofi.png[/img][/url] [url=https://github.com/Minidoracat/MinidoracatMiniMapModMapsFor42][img]https://raw.githubusercontent.com/Minidoracat/workshop-resources/refs/heads/main/badges/badge_github.png[/img][/url]

[b]#map #minimap #worldmap #Minidoracat[/b]

Workshop ID: 3763914102
Mod ID: MinidoracatMiniMapModMapsFor42
