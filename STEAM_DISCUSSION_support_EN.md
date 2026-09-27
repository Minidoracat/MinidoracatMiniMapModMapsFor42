<!-- Steam discussion source; lists come from docs/road-data.md (road-scan output) — keep in sync -->
<!-- 討論串網址：https://steamcommunity.com/workshop/filedetails/discussion/3763914102/586187095760050473/ -->
<!-- 標題：📢 MOD Map Support Notice: Images, Road Data & Navigation -->

[b]繁體中文版：[/b][url=https://steamcommunity.com/workshop/filedetails/discussion/3763914102/569297034317714585/]MOD 地圖支援告知[/url]

[b]The supported-maps list describes map imagery support, not a guarantee of road navigation or autonomous driving.[/b]

[h2]What this pack provides[/h2]
This addon supplies map images, street-name translations and a small amount of road data that we made or corrected ourselves. Translations change names only; road fixes and added roads are separate, language-independent data that MiniMap applies only when the expected source geometry matches. This is not a universal automatic road fixer and does not change terrain or buildings. Update this pack together with MiniMap and restart the game.

[h2]Street names, search and navigation come from the map author's road data[/h2]
Street labels, street search, navigation and the AutoDrive road network all come from the native streets.xml that the map author ships inside the map MOD. Maps without road data still show their image, but that area has no street names, no search results and no navigation — this is not a missing translation.
Road coordinates, widths, bends and junctions must match the actual road. Missing, disconnected or offset data can cause missing routes, detours or off-road navigation. Map overlap and priority also matter: require only orders the main MOD before this addon and does not make conflicting maps compatible. In multiplayer the server Map= order decides priority, and lower-priority street sections can be excluded so both original and translated names return no result.
The [b]MOD map: map name[/b] label in street search identifies a known source; it is not an error flag or a driving certification.

[h2]🛠️ Roads we made or fixed[/h2]
[list]
[*] [b]Constown, KY[/b]: 37 added roads. Roads missing from the author's data are added by this pack, named "Constown Rd 01 (MiniMap)" to "Constown Rd 37 (MiniMap)", searchable and routable. If the author later ships road data, the game switches to the author's roads automatically. [i](next update)[/i]
[*] [b]Camden County[/b]: 3 gap bridges. Author roads stopped short of junctions so navigation/AutoDrive could not reach them; they now connect to the network and keep the author's street names. [i](next update)[/i]
[*] [b]Daisy County[/b]: 44 outline roads converted to centre lines, so names are not shown twice and routes follow the road centre.
[*] [b]Muldraugh 1993[/b]: 913 street labels that exactly duplicate the vanilla map are hidden on display only; navigation roads are not deleted, and uncertain or partial overlaps keep their labels.
[/list]

[h2]✅ Maps with author road data (22)[/h2]
[list]
[*] AnruisiTown (Military Bastion): 59 streets
[*] Camden County: 40 streets
[*] Daisy County: 44 streets
[*] Ed's Auto Salvage: 3 streets
[*] LittleTownship: 4 streets
[*] Maplewood: 12 streets
[*] Megurigaoka, Kanagawa: 2 streets
[*] Muldraugh 1993: 1092 streets
[*] Raven Creek: 45 streets
[*] Raven Creek (Kardinal port): 45 streets
[*] SecretZ Checkpoint 5: 1 streets
[*] SecretZ Checkpoint 8: 2 streets
[*] SecretZ March Ridge Research Facility: 2 streets
[*] SecretZ West Point Bridge Checkpoint: 4 streets
[*] SecretZ Riverside Checkpoint 1: 2 streets
[*] SecretZ Riverside Checkpoint 2: 4 streets
[*] Tikitown & PowerPlant: 99 streets
[*] West Point Expansion: 18 streets
[*] WILDSTEEL - Fort Spiffo: 4 streets
[*] Clover Lake Farmhouse: 1 streets
[*] Greenport, KY: 15 streets
[*] West Point: The Bridge Citadel: 4 streets
[/list]

[h2]❌ Maps without author road data (79)[/h2]
These maps show their image, but have no street names, search or navigation (except the roads we added above).
[list]
[*] Muldraugh Fire Dept
[*] Estate 39
[*] Atlas Underground Complex (Surface)
[*] Chinatown Expansion
[*] Chinatown
[*] Asakusa Lake Town
[*] Ashenwood
[*] Atlanta Safe Zone
[*] Atlanta Tower Survival
[*] Atlanta
[*] Blackpine County
[*] Cathaya Valley 2.0 Highway
[*] Cathaya Valley 2.0
[*] Constown, KY
[*] Coryerdon
[*] Dawn Town
[*] EchoCreek Military Base
[*] Erika's Furniture Store
[*] Floatopia
[*] Foxtrot Warehouse
[*] Fort Benning
[*] Fort JadeLake
[*] Fort Waterfront
[*] Fort Boonesborough
[*] Grapeseed
[*] Greenleaf
[*] Hartburg, KY
[*] Hunter's Base
[*] Hunter's Base (Small)
[*] Hazelnut Manor
[*] Hazelnut Manor (Poor)
[*] Iris Eyot
[*] KillMingLake
[*] Kingsmouth North
[*] White Forest
[*] Louisville Riverboat
[*] Muldraugh Checkpoint - Overpass
[*] Fort Preston
[*] Nekomata Ridge
[*] Nettle Township
[*] Path of Zenith
[*] New Coalfield
[*] Raccoon City
[*] Riverside Mansion (Unofficial)
[*] RustBury
[*] Safeharbor Garrison
[*] SafeWayHamlet
[*] Sunset Lake Town
[*] Sunset Tower
[*] SecretZ Bunker 3
[*] SecretZ Checkpoint 1
[*] SecretZ Checkpoint 6
[*] SecretZ Deerhead Lake Base
[*] SecretZ Louisville Military Complex
[*] SecretZ Train Depot Refugee Camp
[*] SecretZ Crossroads Checkpoint
[*] SecretZ North Checkpoint
[*] SecretZ The Mall
[*] Taibei Road
[*] Taylorsville
[*] Trapala Lake Town
[*] Trelai 4x4 (Kardinal port)
[*] Vila Z
[*] Willowbrook Bastion
[*] Willowbrook Bastion 2026
[*] Bunker 42
[*] New Ellroy
[*] Shadyside
[*] White Forest Ridge
[*] Yanghu Town
[*] Begonia Town
[*] Frogtown
[*] Haven Fall
[*] Macon (TWD)
[*] Xixi's Serene Cottage
[*] VaultTec Vault - Louisville
[*] VaultTec Vault - Muldraugh
[*] VaultTec Road
[*] VaultTec Vault - Rosewood
[/list]

[h2]Related topics[/h2]
[list]
[*][url=https://steamcommunity.com/workshop/filedetails/discussion/3763913359/586187095760051259/]Full road-data requirements for map authors — MiniMap[/url]
[*][url=https://steamcommunity.com/workshop/filedetails/discussion/3792675881/586187095760051144/]AutoDrive road requirements and known issues[/url]
[/list]
Being included in the image pack or collection does not mean every map has been tested for navigation, AutoDrive, or compatibility with every other map. Use the map-request topic for image support requests; use the linked topics for road-data and driving reports.
