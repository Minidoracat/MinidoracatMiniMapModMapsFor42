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
[*] [b]道路名の翻訳[/b]（0.7.0 追加）：15 マップの道路名を繁体字／簡体字／日本語で表示、検索は訳名でも英語原名でも可
[/list]

[h2]🗺️ 収録マップとリクエスト[/h2]
現在 [b]71 個のマップ MOD（93 マップ）[/b]に対応。[url=https://steamcommunity.com/sharedfiles/filedetails/?id=3766382352]対応マップコレクション[/url]から一括サブスクライブ可能。対応リスト・原作者クレジット・マップリクエストは
[url=https://steamcommunity.com/workshop/filedetails/discussion/3763914102/568165880361411088/]ディスカッション[/url]へどうぞ！
[url=https://github.com/Minidoracat/MinidoracatMiniMapModMapsFor42/issues/new/choose]GitHub Issue フォーム[/url]からのリクエストも歓迎です（開発バックログに直行、対応が最速）。

[h2]🛣️ 道路名の翻訳（0.7.0 追加）[/h2]
[b]15 マップ[/b]の道路名が[b]繁体字／簡体字／日本語[/b]に対応（355 件）。公式マップと表記を統一し、訳名でも英語原名でも検索できます。本体 MOD [b]0.21.0+[/b] が必要です。
他のマップは作者が元々道路名データを用意していないだけ（例：ラクーンシティ）で、翻訳漏れではありません。

[h2]⚠️ 一部マップで 1 本の道に名前が 2 つ出ます[/h2]
[b]原因は該当マップ MOD 側で、本パックではありません。[/b]各マップは自分の道路だけを定義するのが規約ですが、一部の作者が[b]公式の道路データをそのままコピー、または改名して自分の MOD に入れており[/b]、エンジンは両方を描画します。
本パックでは重複分を自動除外済み（SecretZ の拠点は全て公式のコピー→道路名翻訳なし、マルドロー 1993 は自前の 52 件のみ、デイジー郡なども数件除外）。
残るのは交差部だけの短い重なりで、消すには[b]公式[/b]の道路データを書き換える必要があり車両ナビに影響するため、そのままにしています——[b]元のマップ作者[/b]へご報告ください。

[h2]🔧 サポート範囲[/h2]
本パックが担当するのは[b]ミニマップ／ワールドマップの画像描画のみ[/b]です。
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
[*] [b]前提 MOD:[/b] [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3763913359]Minidoracat MiniMap for B42[/url]（本体 MOD。無いと本パックは機能しません）
[*] [b]ロード順:[/b] 手動調整は不要——require で依存を宣言済みのため、ゲームが自動的に本体を先に読み込みます
[*] [b]対応バージョン:[/b] Build 42.20.0+
[*] シングル / マルチ両対応（クライアントサイドの画像のみ、ワールドは変更しません）
[/list]

[h2]💬 不具合報告・交流[/h2]
[url=https://github.com/Minidoracat/MinidoracatMiniMapModMapsFor42/issues]🐛 GitHub Issues[/url]——マップリクエスト＆画像問題報告フォーム
[url=https://discord.gg/Gur2V67]👉 Discord サーバーに参加[/url]

[b]#map #minimap #worldmap #Minidoracat[/b]

Workshop ID: 3763914102
Mod ID: MinidoracatMiniMapModMapsFor42
