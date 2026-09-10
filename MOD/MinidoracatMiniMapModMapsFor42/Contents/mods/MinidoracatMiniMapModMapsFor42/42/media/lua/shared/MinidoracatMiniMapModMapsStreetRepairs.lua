-- MinidoracatMiniMapModMapsStreetRepairs.lua（生成檔，勿手編）
-- 由 scripts/gen_street_repairs.py 從 road-repairs/*.json 編譯
-- 2 個 dataset／957 筆修正（改幾何 44、隱藏標籤候選 913）
--
-- 執行期契約：逐值比對 expectedWidth／expectedPoints，不符就略過該筆並 log
-- （上游改版＝安全退回原樣，不擋同圖其他修正、也不擋新道路）。
-- hideLabel 只影響玩家地圖上的路名顯示，**不從導航路網移除該道路**；
-- reference 是 vanilla 對應街道的 index/width/points，執行期須確認那條
-- canonical 道路仍在且看得見，才真的隱藏我方這份重複標籤。

MinidoracatMiniMapModMapsStreetRepairs = MinidoracatMiniMapModMapsStreetRepairs or {}
local Repairs = MinidoracatMiniMapModMapsStreetRepairs

-- ==== daisy-county (Daisy County B42 version / Daisy County) ====
-- 逐筆理由（rect-outline／exact-copy）在 road-repairs/daisy-county.json 的 reason；有 replacementPoints＝改幾何，有 hideLabel＝藏重複路名
do
    local ops = {}
    -- #0 Weinifan Street
    ops[0] = { expectedWidth = 10, expectedPoints = { 9928, 7308, 9938, 7308, 9938, 7491, 9928, 7491 }, replacementPoints = { 9933, 7308, 9933, 7491 } }
    -- #1 Little Flower Street
    ops[1] = { expectedWidth = 10, expectedPoints = { 9913, 7239, 10023, 7239, 10023, 7247, 9913, 7247 }, replacementPoints = { 9913, 7243, 10023, 7243 } }
    -- #2 Taibei Road
    ops[2] = { expectedWidth = 10, expectedPoints = { 9936, 7247, 9944, 7247, 9944, 7288, 9936, 7288 }, replacementPoints = { 9940, 7247, 9940, 7288 } }
    -- #3 Fishing Road
    ops[3] = { expectedWidth = 10, expectedPoints = { 9944, 7292, 10023, 7292, 10023, 7302, 9944, 7302 }, replacementPoints = { 9944, 7297, 10023, 7297 } }
    -- #4 Unnamed Road
    ops[4] = { expectedWidth = 10, expectedPoints = { 10023, 7221, 10031, 7221, 10031, 7269, 10023, 7269 }, replacementPoints = { 10027, 7221, 10027, 7269 } }
    -- #5 Er Xian Road
    ops[5] = { expectedWidth = 10, expectedPoints = { 10031, 7269, 10099, 7269, 10099, 7279, 10031, 7279 }, replacementPoints = { 10031, 7274, 10099, 7274 } }
    -- #6 Cheng Hua Road
    ops[6] = { expectedWidth = 10, expectedPoints = { 10109, 7269, 10200, 7269, 10200, 7279, 10109, 7279 }, replacementPoints = { 10109, 7274, 10200, 7274 } }
    -- #7 Kill Mingshi Road
    ops[7] = { expectedWidth = 10, expectedPoints = { 10158, 7279, 10166, 7279, 10166, 7342, 10158, 7342 }, replacementPoints = { 10162, 7279, 10162, 7342 } }
    -- #8 Yu Lin Road
    ops[8] = { expectedWidth = 10, expectedPoints = { 10099, 7235, 10109, 7235, 10109, 7337, 10099, 7337 }, replacementPoints = { 10104, 7235, 10104, 7337 } }
    -- #9 Daisy Road
    ops[9] = { expectedWidth = 10, expectedPoints = { 10087, 7225, 10179, 7225, 10179, 7235, 10087, 7235 }, replacementPoints = { 10087, 7230, 10179, 7230 } }
    -- #10 Daisy Lane
    ops[10] = { expectedWidth = 10, expectedPoints = { 10169, 7235, 10179, 7235, 10179, 7269, 10169, 7269 }, replacementPoints = { 10174, 7235, 10174, 7269 } }
    -- #11 Clover Street
    ops[11] = { expectedWidth = 10, expectedPoints = { 10114, 7342, 10200, 7342, 10200, 7352, 10114, 7352 }, replacementPoints = { 10114, 7347, 10200, 7347 } }
    -- #12 Maple Street
    ops[12] = { expectedWidth = 10, expectedPoints = { 9978, 7302, 9986, 7302, 9986, 7372, 9978, 7372 }, replacementPoints = { 9982, 7302, 9982, 7372 } }
    -- #13 Pine Ridge Road
    ops[13] = { expectedWidth = 10, expectedPoints = { 10013, 7302, 10023, 7302, 10023, 7446, 10013, 7446 }, replacementPoints = { 10018, 7302, 10018, 7446 } }
    -- #14 Meadow Way
    ops[14] = { expectedWidth = 10, expectedPoints = { 9986, 7446, 10200, 7446, 10200, 7456, 9986, 7456 }, replacementPoints = { 9986, 7451, 10200, 7451 } }
    -- #15 Buttercup Court
    ops[15] = { expectedWidth = 10, expectedPoints = { 10027, 7482, 10076, 7482, 10076, 7492, 10027, 7492 }, replacementPoints = { 10027, 7487, 10076, 7487 } }
    -- #16 Dewdrop Lane
    ops[16] = { expectedWidth = 10, expectedPoints = { 10200, 7269, 10236, 7269, 10236, 7279, 10200, 7279 }, replacementPoints = { 10200, 7274, 10236, 7274 } }
    -- #17 Rosemary Way
    ops[17] = { expectedWidth = 10, expectedPoints = { 10207, 7224, 10217, 7224, 10217, 7269, 10207, 7269 }, replacementPoints = { 10212, 7224, 10212, 7269 } }
    -- #18 Thistle Lane
    ops[18] = { expectedWidth = 10, expectedPoints = { 10221, 7210, 10438, 7210, 10438, 7220, 10221, 7220 }, replacementPoints = { 10221, 7215, 10438, 7215 } }
    -- #19 Violet Street
    ops[19] = { expectedWidth = 10, expectedPoints = { 10428, 7220, 10438, 7220, 10438, 7342, 10428, 7342 }, replacementPoints = { 10433, 7220, 10433, 7342 } }
    -- #20 Holly Drive
    ops[20] = { expectedWidth = 10, expectedPoints = { 10239, 7282, 10249, 7282, 10249, 7342, 10239, 7342 }, replacementPoints = { 10244, 7282, 10244, 7342 } }
    -- #21 Cedar Avenue
    ops[21] = { expectedWidth = 10, expectedPoints = { 10200, 7342, 10464, 7342, 10464, 7352, 10200, 7352 }, replacementPoints = { 10200, 7347, 10464, 7347 } }
    -- #22 Birch Lane
    ops[22] = { expectedWidth = 10, expectedPoints = { 10468, 7356, 10478, 7356, 10478, 7446, 10468, 7446 }, replacementPoints = { 10473, 7356, 10473, 7446 } }
    -- #23 Ivy Road
    ops[23] = { expectedWidth = 10, expectedPoints = { 10200, 7446, 10500, 7446, 10500, 7456, 10200, 7456 }, replacementPoints = { 10200, 7451, 10500, 7451 } }
    -- #24 Beech Street
    ops[24] = { expectedWidth = 10, expectedPoints = { 10333, 7352, 10341, 7352, 10341, 7446, 10333, 7446 }, replacementPoints = { 10337, 7352, 10337, 7446 } }
    -- #25 unknown
    ops[25] = { expectedWidth = 10, expectedPoints = { 10239, 7352, 10249, 7352, 10249, 7446, 10239, 7446 }, replacementPoints = { 10244, 7352, 10244, 7446 } }
    -- #26 Fir Drive
    ops[26] = { expectedWidth = 10, expectedPoints = { 10249, 7393, 10333, 7393, 10333, 7401, 10249, 7401 }, replacementPoints = { 10249, 7397, 10333, 7397 } }
    -- #27 Jasmine Way
    ops[27] = { expectedWidth = 10, expectedPoints = { 10363, 7383, 10373, 7383, 10373, 7446, 10363, 7446 }, replacementPoints = { 10368, 7383, 10368, 7446 } }
    -- #28 Tulip Lane
    ops[28] = { expectedWidth = 10, expectedPoints = { 10419, 7456, 10428, 7456, 10428, 7501, 10419, 7501 }, replacementPoints = { 10423.5, 7456, 10423.5, 7501 } }
    -- #29 Orchid Court
    ops[29] = { expectedWidth = 10, expectedPoints = { 9936, 7500, 9946, 7500, 9946, 7752, 9936, 7752 }, replacementPoints = { 9941, 7500, 9941, 7752 } }
    -- #30 Magnolia Lane
    ops[30] = { expectedWidth = 10, expectedPoints = { 10027, 7500, 10037, 7500, 10037, 7702, 10027, 7702 }, replacementPoints = { 10032, 7500, 10032, 7702 } }
    -- #31 Dogwood Road
    ops[31] = { expectedWidth = 10, expectedPoints = { 9946, 7546, 10027, 7546, 10027, 7556, 9946, 7556 }, replacementPoints = { 9946, 7551, 10027, 7551 } }
    -- #32 Peony Way
    ops[32] = { expectedWidth = 10, expectedPoints = { 10044, 7696, 10119, 7696, 10119, 7706, 10044, 7706 }, replacementPoints = { 10044, 7701, 10119, 7701 } }
    -- #33 Palm Drive
    ops[33] = { expectedWidth = 10, expectedPoints = { 9946, 7738, 10009, 7738, 10009, 7748, 9946, 7748 }, replacementPoints = { 9946, 7743, 10009, 7743 } }
    -- #34 Hazel Road
    ops[34] = { expectedWidth = 10, expectedPoints = { 9998, 7748, 10008, 7748, 10008, 7801, 9998, 7801 }, replacementPoints = { 10003, 7748, 10003, 7801 } }
    -- #35 Aster Lane
    ops[35] = { expectedWidth = 10, expectedPoints = { 10419, 7501, 10428, 7501, 10428, 7800, 10419, 7800 }, replacementPoints = { 10423.5, 7501, 10423.5, 7800 } }
    -- #36 Zinnia Way
    ops[36] = { expectedWidth = 10, expectedPoints = { 10199, 7772, 10419, 7772, 10419, 7781, 10199, 7781 }, replacementPoints = { 10199, 7776.5, 10419, 7776.5 } }
    -- #37 Dahlia Court
    ops[37] = { expectedWidth = 10, expectedPoints = { 10275, 7612, 10281, 7612, 10281, 7772, 10275, 7772 }, replacementPoints = { 10278, 7612, 10278, 7772 } }
    -- #38 Sunflower Road
    ops[38] = { expectedWidth = 10, expectedPoints = { 10353, 7557, 10419, 7557, 10419, 7566, 10353, 7566 }, replacementPoints = { 10353, 7561.5, 10419, 7561.5 } }
    -- #39 Fern Way
    ops[39] = { expectedWidth = 10, expectedPoints = { 9996, 7803, 10010, 7803, 10010, 8055, 9996, 8055 }, replacementPoints = { 10003, 7803, 10003, 8055 } }
    -- #40 Pansy Street
    ops[40] = { expectedWidth = 10, expectedPoints = { 9900, 8055, 10201, 8055, 10201, 8063, 9900, 8063 }, replacementPoints = { 9900, 8059, 10201, 8059 } }
    -- #41 Sycamore Drive
    ops[41] = { expectedWidth = 10, expectedPoints = { 10130, 8010, 10136, 8010, 10136, 8055, 10130, 8055 }, replacementPoints = { 10133, 8010, 10133, 8055 } }
    -- #42 Mingshi Road
    ops[42] = { expectedWidth = 10, expectedPoints = { 10419, 7800, 10428, 7800, 10428, 8055, 10419, 8055 }, replacementPoints = { 10423.5, 7800, 10423.5, 8055 } }
    -- #43 Lily Lane
    ops[43] = { expectedWidth = 10, expectedPoints = { 10201, 8055, 10500, 8055, 10500, 8063, 10201, 8063 }, replacementPoints = { 10201, 8059, 10500, 8059 } }
    Repairs["daisy-county"] = { schemaVersion = 1, mapMod = "Daisy County B42 version", mapDir = "Daisy County", operations = ops }
end

-- ==== muldraugh-1993 (muldraugh1993b42 / Muldraugh 1993 B42) ====
-- 逐筆理由（rect-outline／exact-copy）在 road-repairs/muldraugh-1993.json 的 reason；有 replacementPoints＝改幾何，有 hideLabel＝藏重複路名
do
    local ops = {}
    -- #3 Goggins St
    ops[3] = { expectedWidth = 8, expectedPoints = { 11238, 6848, 11396, 6848 }, hideLabel = true, reference = { index = 3, width = 8, points = { 11238, 6848, 11396, 6848 } } }
    -- #4 Young St
    ops[4] = { expectedWidth = 9, expectedPoints = { 11404, 6823.5, 11547.900390625, 6823.5 }, hideLabel = true, reference = { index = 4, width = 9, points = { 11404, 6823.5, 11547.900390625, 6823.5 } } }
    -- #6 2nd St
    ops[6] = { expectedWidth = 8, expectedPoints = { 12106, 6904, 12106, 7176 }, hideLabel = true, reference = { index = 6, width = 8, points = { 12106, 6904, 12106, 7176 } } }
    -- #11 8th St
    ops[11] = { expectedWidth = 8, expectedPoints = { 11552, 6755, 11552, 6953 }, hideLabel = true, reference = { index = 11, width = 8, points = { 11552, 6755, 11552, 6953 } } }
    -- #16 3rd St
    ops[16] = { expectedWidth = 8, expectedPoints = { 12000, 6777, 12000, 7072 }, hideLabel = true, reference = { index = 16, width = 8, points = { 12000, 6777, 12000, 7072 } } }
    -- #48 South St
    ops[48] = { expectedWidth = 8, expectedPoints = { 11404, 6949, 11696, 6949 }, hideLabel = true, reference = { index = 46, width = 8, points = { 11404, 6949, 11696, 6949 } } }
    -- #52 River St
    ops[52] = { expectedWidth = 8, expectedPoints = { 11370, 6695, 11370, 6747 }, hideLabel = true, reference = { index = 50, width = 8, points = { 11370, 6695, 11370, 6747 } } }
    -- #56 Doctors Lane
    ops[56] = { expectedWidth = 6, expectedPoints = { 8026, 11480, 8026, 11575 }, hideLabel = true, reference = { index = 54, width = 6, points = { 8026, 11480, 8026, 11575 } } }
    -- #65 South Main St
    ops[65] = { expectedWidth = 6, expectedPoints = { 7932, 11777, 8276, 11777 }, hideLabel = true, reference = { index = 61, width = 6, points = { 7932, 11777, 8276, 11777 } } }
    -- #66 North Main St
    ops[66] = { expectedWidth = 8, expectedPoints = { 8106, 11212, 8106, 11774 }, hideLabel = true, reference = { index = 62, width = 8, points = { 8106, 11212, 8106, 11774 } } }
    -- #67 St Martin's Road
    ops[67] = { expectedWidth = 6, expectedPoints = { 8369, 11682, 8369, 11777, 8276, 11777 }, hideLabel = true, reference = { index = 63, width = 6, points = { 8369, 11682, 8369, 11777, 8276, 11777 } } }
    -- #74 Cattle Road
    ops[74] = { expectedWidth = 6, expectedPoints = { 2565, 13880, 2565, 13732, 2574, 13715, 2848, 13441, 2864, 13433, 3023, 13433, 3191, 13517, 3834, 13517, 3860, 13530, 3936, 13607, 3947, 13628, 3947, 14185, 3934, 14211, 3863, 14282.5, 3852, 14304.5, 3852, 14497 }, hideLabel = true, reference = { index = 68, width = 6, points = { 2565, 13880, 2565, 13732, 2574, 13715, 2848, 13441, 2864, 13433, 3023, 13433, 3191, 13517, 3834, 13517, 3860, 13530, 3936, 13607, 3947, 13628, 3947, 14185, 3934, 14211, 3863, 14282.5, 3852, 14304.5, 3852, 14497 } } }
    -- #75 Lincoln St
    ops[75] = { expectedWidth = 6, expectedPoints = { 2396, 13883, 2698, 13883 }, hideLabel = true, reference = { index = 69, width = 6, points = { 2396, 13883, 2698, 13883 } } }
    -- #76 1st Ave
    ops[76] = { expectedWidth = 10, expectedPoints = { 2500, 14277, 2500, 14496 }, hideLabel = true, reference = { index = 70, width = 10, points = { 2500, 14277, 2500, 14496 } } }
    -- #77 1st Ave
    ops[77] = { expectedWidth = 8, expectedPoints = { 2501, 14006.5, 2501, 14277 }, hideLabel = true, reference = { index = 71, width = 8, points = { 2501, 14006.5, 2501, 14277 } } }
    -- #78 1st Ave
    ops[78] = { expectedWidth = 6, expectedPoints = { 2502, 13886, 2502, 14006.5 }, hideLabel = true, reference = { index = 72, width = 6, points = { 2502, 13886, 2502, 14006.5 } } }
    -- #79 Orwell Dr
    ops[79] = { expectedWidth = 5, expectedPoints = { 2400, 13886, 2400, 13907, 2405, 13917, 2499, 14011 }, hideLabel = true, reference = { index = 73, width = 5, points = { 2400, 13886, 2400, 13907, 2405, 13917, 2499, 14011 } } }
    -- #80 Pearl Lane
    ops[80] = { expectedWidth = 5, expectedPoints = { 2302, 13966, 2302, 14030 }, hideLabel = true, reference = { index = 74, width = 5, points = { 2302, 13966, 2302, 14030 } } }
    -- #81 Peach St
    ops[81] = { expectedWidth = 6, expectedPoints = { 2401, 13964, 2401, 14344 }, hideLabel = true, reference = { index = 75, width = 6, points = { 2401, 13964, 2401, 14344 } } }
    -- #82 Merino St
    ops[82] = { expectedWidth = 6, expectedPoints = { 2205, 14012, 2205, 14496 }, hideLabel = true, reference = { index = 76, width = 6, points = { 2205, 14012, 2205, 14496 } } }
    -- #83 Hall Road
    ops[83] = { expectedWidth = 6, expectedPoints = { 2208, 14099, 2697, 14099 }, hideLabel = true, reference = { index = 77, width = 6, points = { 2208, 14099, 2697, 14099 } } }
    -- #84 5th St
    ops[84] = { expectedWidth = 6, expectedPoints = { 2600, 14102, 2600, 14297 }, hideLabel = true, reference = { index = 78, width = 6, points = { 2600, 14102, 2600, 14297 } } }
    -- #85 6th St
    ops[85] = { expectedWidth = 6, expectedPoints = { 2700, 14096, 2700, 14296 }, hideLabel = true, reference = { index = 79, width = 6, points = { 2700, 14096, 2700, 14296 } } }
    -- #86 Bullet Dr
    ops[86] = { expectedWidth = 5, expectedPoints = { 2253.5, 14102, 2253.5, 14294 }, hideLabel = true, reference = { index = 80, width = 5, points = { 2253.5, 14102, 2253.5, 14294 } } }
    -- #87 Rant St
    ops[87] = { expectedWidth = 6, expectedPoints = { 2303, 14102, 2303, 14294 }, hideLabel = true, reference = { index = 81, width = 6, points = { 2303, 14102, 2303, 14294 } } }
    -- #88 Frog St
    ops[88] = { expectedWidth = 5, expectedPoints = { 2352.5, 14102, 2352.5, 14294 }, hideLabel = true, reference = { index = 82, width = 5, points = { 2352.5, 14102, 2352.5, 14294 } } }
    -- #89 W Kentucky St
    ops[89] = { expectedWidth = 6, expectedPoints = { 1902, 14297, 2398, 14297 }, hideLabel = true, reference = { index = 83, width = 6, points = { 1902, 14297, 2398, 14297 } } }
    -- #90 N Carl St
    ops[90] = { expectedWidth = 6, expectedPoints = { 1899, 14300, 1899, 14496 }, hideLabel = true, reference = { index = 84, width = 6, points = { 1899, 14300, 1899, 14496 } } }
    -- #91 Mule Lane
    ops[91] = { expectedWidth = 6, expectedPoints = { 2000, 14300, 2000, 14399 }, hideLabel = true, reference = { index = 85, width = 6, points = { 2000, 14300, 2000, 14399 } } }
    -- #92 Center St
    ops[92] = { expectedWidth = 6, expectedPoints = { 2101, 14300, 2101, 14496 }, hideLabel = true, reference = { index = 86, width = 6, points = { 2101, 14300, 2101, 14496 } } }
    -- #93 High St
    ops[93] = { expectedWidth = 5, expectedPoints = { 1902, 14401, 2202, 14401 }, hideLabel = true, reference = { index = 87, width = 5, points = { 1902, 14401, 2202, 14401 } } }
    -- #94 Irvington St
    ops[94] = { expectedWidth = 6, expectedPoints = { 1795, 14499, 2208, 14499 }, hideLabel = true, reference = { index = 88, width = 6, points = { 1795, 14499, 2208, 14499 } } }
    -- #95 West St
    ops[95] = { expectedWidth = 5, expectedPoints = { 1797.5, 14700, 1797.5, 14835 }, hideLabel = true, reference = { index = 89, width = 5, points = { 1797.5, 14700, 1797.5, 14835 } } }
    -- #96 West St
    ops[96] = { expectedWidth = 6, expectedPoints = { 1798, 14502, 1798, 14700 }, hideLabel = true, reference = { index = 90, width = 6, points = { 1798, 14502, 1798, 14700 } } }
    -- #97 Main St
    ops[97] = { expectedWidth = 6, expectedPoints = { 2002, 14502, 2002, 14742 }, hideLabel = true, reference = { index = 91, width = 6, points = { 2002, 14502, 2002, 14742 } } }
    -- #98 Church St
    ops[98] = { expectedWidth = 6, expectedPoints = { 2404, 14199, 2697, 14199 }, hideLabel = true, reference = { index = 92, width = 6, points = { 2404, 14199, 2697, 14199 } } }
    -- #99 2nd St
    ops[99] = { expectedWidth = 6, expectedPoints = { 2601, 13886, 2601, 13981 }, hideLabel = true, reference = { index = 93, width = 6, points = { 2601, 13886, 2601, 13981 } } }
    -- #100 Grass Lane
    ops[100] = { expectedWidth = 6, expectedPoints = { 2604, 13933, 2697, 13933 }, hideLabel = true, reference = { index = 94, width = 6, points = { 2604, 13933, 2697, 13933 } } }
    -- #101 Lake St
    ops[101] = { expectedWidth = 6, expectedPoints = { 2505, 13984, 2836, 13984 }, hideLabel = true, reference = { index = 95, width = 6, points = { 2505, 13984, 2836, 13984 } } }
    -- #102 3rd St
    ops[102] = { expectedWidth = 5, expectedPoints = { 2700, 13855, 2700, 13981 }, hideLabel = true, reference = { index = 96, width = 5, points = { 2700, 13855, 2700, 13981 } } }
    -- #103 Beaver St
    ops[103] = { expectedWidth = 6, expectedPoints = { 2703, 13917, 2830, 13917 }, hideLabel = true, reference = { index = 97, width = 6, points = { 2703, 13917, 2830, 13917 } } }
    -- #104 Old Church St
    ops[104] = { expectedWidth = 6, expectedPoints = { 2697.5, 13852, 2836, 13852 }, hideLabel = true, reference = { index = 98, width = 6, points = { 2697.5, 13852, 2836, 13852 } } }
    -- #105 4th St
    ops[105] = { expectedWidth = 6, expectedPoints = { 2833, 13855, 2833, 13981 }, hideLabel = true, reference = { index = 99, width = 6, points = { 2833, 13855, 2833, 13981 } } }
    -- #106 Oak Lane
    ops[106] = { expectedWidth = 6, expectedPoints = { 2650, 13987, 2650, 14047 }, hideLabel = true, reference = { index = 100, width = 6, points = { 2650, 13987, 2650, 14047 } } }
    -- #107 Webster Road
    ops[107] = { expectedWidth = 5, expectedPoints = { 1893, 14194, 1936, 14194, 1949, 14187, 1957, 14179, 2004, 14085, 2004, 14047, 2012, 14031, 2024, 14019, 2040, 14012, 2202, 14012 }, hideLabel = true, reference = { index = 101, width = 5, points = { 1893, 14194, 1936, 14194, 1949, 14187, 1957, 14179, 2004, 14085, 2004, 14047, 2012, 14031, 2024, 14019, 2040, 14012, 2202, 14012 } } }
    -- #108 Rosewater Road
    ops[108] = { expectedWidth = 8, expectedPoints = { 2500, 14506, 2500, 14955 }, hideLabel = true, reference = { index = 102, width = 8, points = { 2500, 14506, 2500, 14955 } } }
    -- #109 Woodlawn Dr
    ops[109] = { expectedWidth = 6, expectedPoints = { 2505, 14351, 2601, 14351, 2610, 14356, 2616, 14362, 2620, 14372, 2620, 14384, 2617, 14391, 2610, 14398, 2603, 14402, 2505, 14402 }, hideLabel = true, reference = { index = 103, width = 6, points = { 2505, 14351, 2601, 14351, 2610, 14356, 2616, 14362, 2620, 14372, 2620, 14384, 2617, 14391, 2610, 14398, 2603, 14402, 2505, 14402 } } }
    -- #110 Woodlawn Ave
    ops[110] = { expectedWidth = 6, expectedPoints = { 2577, 14405, 2577, 14430, 2585, 14446, 2595, 14456, 2598, 14463, 2598, 14497 }, hideLabel = true, reference = { index = 104, width = 6, points = { 2577, 14405, 2577, 14430, 2585, 14446, 2595, 14456, 2598, 14463, 2598, 14497 } } }
    -- #111 Grand Ave
    ops[111] = { expectedWidth = 6, expectedPoints = { 2505, 14299, 2703, 14299 }, hideLabel = true, reference = { index = 105, width = 6, points = { 2505, 14299, 2703, 14299 } } }
    -- #114 Pine Road
    ops[114] = { expectedWidth = 6, expectedPoints = { 2504.5, 14938, 2526, 14959.5, 2535, 14964, 3355.5, 14964, 3423.5, 14930, 3811, 14930, 3828, 14921.5, 3843, 14906.5, 3852, 14888.5, 3852, 14505 }, hideLabel = true, reference = { index = 107, width = 6, points = { 2504.5, 14938, 2526, 14959.5, 2535, 14964, 3355.5, 14964, 3423.5, 14930, 3811, 14930, 3828, 14921.5, 3843, 14906.5, 3852, 14888.5, 3852, 14505 } } }
    -- #115 Clover Road
    ops[115] = { expectedWidth = 5, expectedPoints = { 2703, 14200, 2714, 14200, 2723, 14204, 2757, 14238, 2773, 14246, 3000, 14246 }, hideLabel = true, reference = { index = 108, width = 5, points = { 2703, 14200, 2714, 14200, 2723, 14204, 2757, 14238, 2773, 14246, 3000, 14246 } } }
    -- #116 Hay St
    ops[116] = { expectedWidth = 5, expectedPoints = { 2952, 14248, 2952, 14497 }, hideLabel = true, reference = { index = 109, width = 5, points = { 2952, 14248, 2952, 14497 } } }
    -- #117 Donkey Road
    ops[117] = { expectedWidth = 6, expectedPoints = { 2618, 14518, 3101, 14518, 3101, 14629 }, hideLabel = true, reference = { index = 110, width = 6, points = { 2618, 14518, 3101, 14518, 3101, 14629 } } }
    -- #118 Valley St
    ops[118] = { expectedWidth = 6, expectedPoints = { 2848, 14521, 2848, 14666, 2953, 14666, 2953, 14521 }, hideLabel = true, reference = { index = 111, width = 6, points = { 2848, 14521, 2848, 14666, 2953, 14666, 2953, 14521 } } }
    -- #119 Temple Way
    ops[119] = { expectedWidth = 6, expectedPoints = { 2851, 14592, 2950, 14592 }, hideLabel = true, reference = { index = 112, width = 6, points = { 2851, 14592, 2950, 14592 } } }
    -- #120 Driveway Road
    ops[120] = { expectedWidth = 6, expectedPoints = { 3027, 14521, 3027, 14835, 3025, 14839, 3020, 14844, 3014, 14847, 3000, 14847 }, hideLabel = true, reference = { index = 113, width = 6, points = { 3027, 14521, 3027, 14835, 3025, 14839, 3020, 14844, 3014, 14847, 3000, 14847 } } }
    -- #121 Main St
    ops[121] = { expectedWidth = 8, expectedPoints = { 7277, 8158, 7277, 8558 }, hideLabel = true, reference = { index = 114, width = 8, points = { 7277, 8158, 7277, 8558 } } }
    -- #126 Goose Lane
    ops[126] = { expectedWidth = 6, expectedPoints = { 7216, 8412, 7273, 8412 }, hideLabel = true, reference = { index = 119, width = 6, points = { 7216, 8412, 7273, 8412 } } }
    -- #127 Lakehead Dr
    ops[127] = { expectedWidth = 6, expectedPoints = { 7281, 8372, 7391, 8372, 7391, 8379 }, hideLabel = true, reference = { index = 120, width = 6, points = { 7281, 8372, 7391, 8372, 7391, 8379 } } }
    -- #129 Pony Trot Road
    ops[129] = { expectedWidth = 8, expectedPoints = { 7281, 8562, 8702, 8562, 8724, 8573, 8745, 8594, 8756, 8616, 8756, 9785 }, hideLabel = true, reference = { index = 122, width = 8, points = { 7281, 8562, 8702, 8562, 8724, 8573, 8745, 8594, 8756, 8616, 8756, 9785 } } }
    -- #136 Fairground Road
    ops[136] = { expectedWidth = 5, expectedPoints = { 1425, 6809.5, 917, 6809.5, 900.5, 6793, 900.5, 6300.5, 901.5, 6298.5, 901.5, 6056.5, 1469, 6056.5 }, hideLabel = true, reference = { index = 127, width = 5, points = { 1425, 6809.5, 917, 6809.5, 900.5, 6793, 900.5, 6300.5, 901.5, 6298.5, 901.5, 6056.5, 1469, 6056.5 } } }
    -- #137 Court Road
    ops[137] = { expectedWidth = 6, expectedPoints = { 1472, 5775, 1472, 6054 }, hideLabel = true, reference = { index = 128, width = 6, points = { 1472, 5775, 1472, 6054 } } }
    -- #138 River Loop Dr
    ops[138] = { expectedWidth = 4, expectedPoints = { 1546, 5683, 1546, 5591, 1549.5, 5583.5, 1551.5, 5582, 1559, 5578, 1573, 5578, 1583, 5583, 1598, 5598, 1602, 5605, 1602, 5697 }, hideLabel = true, reference = { index = 129, width = 4, points = { 1546, 5683, 1546, 5591, 1549.5, 5583.5, 1551.5, 5582, 1559, 5578, 1573, 5578, 1583, 5583, 1598, 5598, 1602, 5605, 1602, 5697 } } }
    -- #139 River Loop Dr
    ops[139] = { expectedWidth = 4, expectedPoints = { 1546, 5683, 1550, 5691, 1555, 5696, 1561, 5699, 1707, 5699 }, hideLabel = true, reference = { index = 130, width = 4, points = { 1546, 5683, 1550, 5691, 1555, 5696, 1561, 5699, 1707, 5699 } } }
    -- #140 N Brand St
    ops[140] = { expectedWidth = 6, expectedPoints = { 1643, 5598, 1643, 5769 }, hideLabel = true, reference = { index = 131, width = 6, points = { 1643, 5598, 1643, 5769 } } }
    -- #141 S Brand St
    ops[141] = { expectedWidth = 5, expectedPoints = { 1549, 5885.5, 1625.5, 5885.5, 1631, 5883, 1639, 5875, 1643, 5868 }, hideLabel = true, reference = { index = 132, width = 5, points = { 1549, 5885.5, 1625.5, 5885.5, 1631, 5883, 1639, 5875, 1643, 5868 } } }
    -- #142 N Fairway St
    ops[142] = { expectedWidth = 5, expectedPoints = { 1546.5, 5775, 1546.5, 5997 }, hideLabel = true, reference = { index = 133, width = 5, points = { 1546.5, 5775, 1546.5, 5997 } } }
    -- #143 S Fairway St
    ops[143] = { expectedWidth = 5, expectedPoints = { 1546.5, 6002, 1546.5, 6107.5, 1556, 6127, 1706, 6277, 1735.5, 6291.5, 1964, 6291.5 }, hideLabel = true, reference = { index = 134, width = 5, points = { 1546.5, 6002, 1546.5, 6107.5, 1556, 6127, 1706, 6277, 1735.5, 6291.5, 1964, 6291.5 } } }
    -- #144 Anvil St
    ops[144] = { expectedWidth = 6, expectedPoints = { 1750, 5775, 1750, 5997 }, hideLabel = true, reference = { index = 135, width = 6, points = { 1750, 5775, 1750, 5997 } } }
    -- #145 Anvil St
    ops[145] = { expectedWidth = 5, expectedPoints = { 1749.5, 6002, 1749.5, 6126 }, hideLabel = true, reference = { index = 136, width = 5, points = { 1749.5, 6002, 1749.5, 6126 } } }
    -- #146 Hammer St
    ops[146] = { expectedWidth = 5, expectedPoints = { 1659.5, 6002, 1659.5, 6126 }, hideLabel = true, reference = { index = 137, width = 5, points = { 1659.5, 6002, 1659.5, 6126 } } }
    -- #147 Nail St
    ops[147] = { expectedWidth = 5, expectedPoints = { 1841.5, 6002, 1841.5, 6126 }, hideLabel = true, reference = { index = 138, width = 5, points = { 1841.5, 6002, 1841.5, 6126 } } }
    -- #148 Meade Road
    ops[148] = { expectedWidth = 5, expectedPoints = { 1508, 5999.5, 1893.5, 5999.5, 1898, 5997, 1906, 5989, 1912.5, 5976, 1912.5, 5948, 1918, 5938, 1926, 5930, 1935, 5925.5, 1964, 5925.5, 1970, 5926 }, hideLabel = true, reference = { index = 139, width = 5, points = { 1508, 5999.5, 1893.5, 5999.5, 1898, 5997, 1906, 5989, 1912.5, 5976, 1912.5, 5948, 1918, 5938, 1926, 5930, 1935, 5925.5, 1964, 5925.5, 1970, 5926 } } }
    -- #149 Meade Road
    ops[149] = { expectedWidth = 6, expectedPoints = { 1970, 5926, 2153, 5926, 2162, 5931, 2169, 5938, 2171, 5943, 2171, 5977, 2176, 5987, 2185, 5996, 2192, 6000, 2554, 6000, 2563, 5995, 2574, 5984, 2581, 5970, 2581, 5828, 2581, 5827, 2581, 5783 }, hideLabel = true, reference = { index = 140, width = 6, points = { 1970, 5926, 2153, 5926, 2162, 5931, 2169, 5938, 2171, 5943, 2171, 5977, 2176, 5987, 2185, 5996, 2192, 6000, 2554, 6000, 2563, 5995, 2574, 5984, 2581, 5970, 2581, 5828, 2581, 5827, 2581, 5783 } } }
    -- #150 Lawrence St
    ops[150] = { expectedWidth = 6, expectedPoints = { 1508, 5772, 1804, 5772, 1867, 5803, 2248, 5803, 2310, 5834, 2480, 5834, 2498, 5825, 2579, 5825 }, hideLabel = true, reference = { index = 141, width = 6, points = { 1508, 5772, 1804, 5772, 1867, 5803, 2248, 5803, 2310, 5834, 2480, 5834, 2498, 5825, 2579, 5825 } } }
    -- #151 Howard Dr
    ops[151] = { expectedWidth = 5, expectedPoints = { 1593, 6162, 1622, 6133, 1631, 6128.5, 1964, 6128.5 }, hideLabel = true, reference = { index = 142, width = 5, points = { 1593, 6162, 1622, 6133, 1631, 6128.5, 1964, 6128.5 } } }
    -- #152 Howard Dr
    ops[152] = { expectedWidth = 6, expectedPoints = { 1970, 6128, 2096, 6128 }, hideLabel = true, reference = { index = 143, width = 6, points = { 1970, 6128, 2096, 6128 } } }
    -- #153 Saunder St
    ops[153] = { expectedWidth = 6, expectedPoints = { 1970, 6233, 2096, 6233 }, hideLabel = true, reference = { index = 144, width = 6, points = { 1970, 6233, 2096, 6233 } } }
    -- #156 Glen Way
    ops[156] = { expectedWidth = 6, expectedPoints = { 2102, 6491, 2315, 6491 }, hideLabel = true, reference = { index = 146, width = 6, points = { 2102, 6491, 2315, 6491 } } }
    -- #159 Cottontail Lane
    ops[159] = { expectedWidth = 6, expectedPoints = { 2293, 6108, 2293, 6037, 2297, 6030, 2302, 6026, 2306, 6024, 2402, 6024 }, hideLabel = true, reference = { index = 148, width = 6, points = { 2293, 6108, 2293, 6037, 2297, 6030, 2302, 6026, 2306, 6024, 2402, 6024 } } }
    -- #160 Greer Road
    ops[160] = { expectedWidth = 6, expectedPoints = { 2349, 6027, 2349, 6282 }, hideLabel = true, reference = { index = 149, width = 6, points = { 2349, 6027, 2349, 6282 } } }
    -- #161 Lafayette Dr
    ops[161] = { expectedWidth = 6, expectedPoints = { 2102, 6111, 2521, 6111 }, hideLabel = true, reference = { index = 150, width = 6, points = { 2102, 6111, 2521, 6111 } } }
    -- #162 Kilree St
    ops[162] = { expectedWidth = 4, expectedPoints = { 2118, 6070, 2274, 6070 }, hideLabel = true, reference = { index = 151, width = 4, points = { 2118, 6070, 2274, 6070 } } }
    -- #163 Monroe Dr
    ops[163] = { expectedWidth = 6, expectedPoints = { 2118, 6029, 2192, 6029 }, hideLabel = true, reference = { index = 152, width = 6, points = { 2118, 6029, 2192, 6029 } } }
    -- #164 Union Dr
    ops[164] = { expectedWidth = 4, expectedPoints = { 2107, 5887, 2274, 5887 }, hideLabel = true, reference = { index = 153, width = 4, points = { 2107, 5887, 2274, 5887 } } }
    -- #165 W Lawrence Lane
    ops[165] = { expectedWidth = 6, expectedPoints = { 2162, 5806, 2162, 5878 }, hideLabel = true, reference = { index = 154, width = 6, points = { 2162, 5806, 2162, 5878 } } }
    -- #166 E Lawrence Lane
    ops[166] = { expectedWidth = 6, expectedPoints = { 2228, 5806, 2228, 5878 }, hideLabel = true, reference = { index = 155, width = 6, points = { 2228, 5806, 2228, 5878 } } }
    -- #167 Wood Lane
    ops[167] = { expectedWidth = 4, expectedPoints = { 2236, 5889, 2236, 6068 }, hideLabel = true, reference = { index = 156, width = 4, points = { 2236, 5889, 2236, 6068 } } }
    -- #168 Ridge St
    ops[168] = { expectedWidth = 5, expectedPoints = { 2276.5, 5820, 2276.5, 5997 }, hideLabel = true, reference = { index = 157, width = 5, points = { 2276.5, 5820, 2276.5, 5997 } } }
    -- #169 Ridge St
    ops[169] = { expectedWidth = 6, expectedPoints = { 2277, 6003, 2277, 6124, 2320, 6210, 2320, 6466 }, hideLabel = true, reference = { index = 158, width = 6, points = { 2277, 6003, 2277, 6124, 2320, 6210, 2320, 6466 } } }
    -- #170 Woodrow St
    ops[170] = { expectedWidth = 5, expectedPoints = { 2523.5, 6002, 2523.5, 6466 }, hideLabel = true, reference = { index = 159, width = 5, points = { 2523.5, 6002, 2523.5, 6466 } } }
    -- #171 Shamrock Road
    ops[171] = { expectedWidth = 5, expectedPoints = { 2523.5, 6480, 2523.5, 7043.5, 2400.5, 7166.5, 2400.5, 7677, 2394, 7690, 2218.5, 7865.5, 2198, 7875.5, 1881, 7875.5 }, hideLabel = true, reference = { index = 160, width = 5, points = { 2523.5, 6480, 2523.5, 7043.5, 2400.5, 7166.5, 2400.5, 7677, 2394, 7690, 2218.5, 7865.5, 2198, 7875.5, 1881, 7875.5 } } }
    -- #172 Ferryman Road
    ops[172] = { expectedWidth = 5, expectedPoints = { 2526, 6899.5, 2945.5, 6899.5, 2973, 6886, 2985.5, 6873.5, 2999.5, 6845.5, 2999.5, 6600 }, hideLabel = true, reference = { index = 161, width = 5, points = { 2526, 6899.5, 2945.5, 6899.5, 2973, 6886, 2985.5, 6873.5, 2999.5, 6845.5, 2999.5, 6600 } } }
    -- #173 Ferryman Road
    ops[173] = { expectedWidth = 5, expectedPoints = { 2999.5, 6600, 2999.5, 6159 }, hideLabel = true, reference = { index = 162, width = 5, points = { 2999.5, 6600, 2999.5, 6159 } } }
    -- #174 Bud Road
    ops[174] = { expectedWidth = 5, expectedPoints = { 2735, 5828, 2735, 6143 }, hideLabel = true, reference = { index = 163, width = 5, points = { 2735, 5828, 2735, 6143 } } }
    -- #175 Wilson Road
    ops[175] = { expectedWidth = 5, expectedPoints = { 2999.5, 5858, 2999.5, 6143 }, hideLabel = true, reference = { index = 164, width = 5, points = { 2999.5, 5858, 2999.5, 6143 } } }
    -- #176 Christian Road
    ops[176] = { expectedWidth = 5, expectedPoints = { 2584, 5961.5, 3186, 5961.5, 3231, 5916.5, 3307, 5916.5, 3333, 5890.5, 3401, 5890.5, 3418.5, 5873, 3418.5, 5851, 3438, 5831.5 }, hideLabel = true, reference = { index = 165, width = 5, points = { 2584, 5961.5, 3186, 5961.5, 3231, 5916.5, 3307, 5916.5, 3333, 5890.5, 3401, 5890.5, 3418.5, 5873, 3418.5, 5851, 3438, 5831.5 } } }
    -- #177 Doe Run Road
    ops[177] = { expectedWidth = 6, expectedPoints = { 2584, 5825, 2775, 5825, 2835, 5855, 3222, 5855, 3274, 5829, 3698, 5829 }, hideLabel = true, reference = { index = 166, width = 6, points = { 2584, 5825, 2775, 5825, 2835, 5855, 3222, 5855, 3274, 5829, 3698, 5829 } } }
    -- #178 High St
    ops[178] = { expectedWidth = 6, expectedPoints = { 1967, 5806, 1967, 6230 }, hideLabel = true, reference = { index = 167, width = 6, points = { 1967, 5806, 1967, 6230 } } }
    -- #179 Main St
    ops[179] = { expectedWidth = 6, expectedPoints = { 1967, 6236, 1967, 6462 }, hideLabel = true, reference = { index = 168, width = 6, points = { 1967, 6236, 1967, 6462 } } }
    -- #180 Baptist Way
    ops[180] = { expectedWidth = 4, expectedPoints = { 2011, 5806, 2011, 5923 }, hideLabel = true, reference = { index = 169, width = 4, points = { 2011, 5806, 2011, 5923 } } }
    -- #181 Kelly Dr
    ops[181] = { expectedWidth = 4, expectedPoints = { 2064, 5848, 2093, 5848, 2098, 5851, 2102, 5856, 2105, 5862, 2105, 5923 }, hideLabel = true, reference = { index = 170, width = 4, points = { 2064, 5848, 2093, 5848, 2098, 5851, 2102, 5856, 2105, 5862, 2105, 5923 } } }
    -- #182 Ohio Dr
    ops[182] = { expectedWidth = 6, expectedPoints = { 2102, 6193, 2277, 6193, 2277, 6330, 2116, 6330 }, hideLabel = true, reference = { index = 171, width = 6, points = { 2102, 6193, 2277, 6193, 2277, 6330, 2116, 6330 } } }
    -- #183 Cross St
    ops[183] = { expectedWidth = 6, expectedPoints = { 2102, 6285, 2402, 6285 }, hideLabel = true, reference = { index = 172, width = 6, points = { 2102, 6285, 2402, 6285 } } }
    -- #184 Armory Road
    ops[184] = { expectedWidth = 6, expectedPoints = { 2113, 6196, 2113, 6406 }, hideLabel = true, reference = { index = 173, width = 6, points = { 2113, 6196, 2113, 6406 } } }
    -- #186 Lakeview Lane
    ops[186] = { expectedWidth = 5, expectedPoints = { 1799.5, 6131, 1799.5, 6143, 1807, 6158, 1836, 6187, 1847.5, 6210, 1847.5, 6320 }, hideLabel = true, reference = { index = 175, width = 5, points = { 1799.5, 6131, 1799.5, 6143, 1807, 6158, 1836, 6187, 1847.5, 6210, 1847.5, 6320 } } }
    -- #187 Kirch Road
    ops[187] = { expectedWidth = 5, expectedPoints = { 1714.5, 6517, 1714.5, 6580.5, 1721, 6587.5, 1792.5, 6587.5, 1792.5, 6889 }, hideLabel = true, reference = { index = 176, width = 5, points = { 1714.5, 6517, 1714.5, 6580.5, 1721, 6587.5, 1792.5, 6587.5, 1792.5, 6889 } } }
    -- #188 Windsor Dr
    ops[188] = { expectedWidth = 5, expectedPoints = { 1484.5, 6272, 1484.5, 6369, 1504, 6388.5, 1570, 6388.5 }, hideLabel = true, reference = { index = 177, width = 5, points = { 1484.5, 6272, 1484.5, 6369, 1504, 6388.5, 1570, 6388.5 } } }
    -- #189 Windsor Road
    ops[189] = { expectedWidth = 5, expectedPoints = { 1141, 6269.5, 1508.5, 6269.5, 1572.5, 6333.5, 1572.5, 6789.5, 1552.5, 6809.5, 1500, 6809.5 }, hideLabel = true, reference = { index = 178, width = 5, points = { 1141, 6269.5, 1508.5, 6269.5, 1572.5, 6333.5, 1572.5, 6789.5, 1552.5, 6809.5, 1500, 6809.5 } } }
    -- #190 Indiana St
    ops[190] = { expectedWidth = 6, expectedPoints = { 2115, 5929, 2115, 6108 }, hideLabel = true, reference = { index = 179, width = 6, points = { 2115, 5929, 2115, 6108 } } }
    -- #191 Trail Link Road
    ops[191] = { expectedWidth = 5, expectedPoints = { 1430, 6891.5, 1964, 6891.5 }, hideLabel = true, reference = { index = 180, width = 5, points = { 1430, 6891.5, 1964, 6891.5 } } }
    -- #192 Broad St
    ops[192] = { expectedWidth = 6, expectedPoints = { 70, 9441, 87, 9441, 307, 9551, 315, 9559, 322, 9574, 322, 9650, 328, 9662, 336, 9670, 349, 9677, 1052, 9677 }, hideLabel = true, reference = { index = 181, width = 6, points = { 70, 9441, 87, 9441, 307, 9551, 315, 9559, 322, 9574, 322, 9650, 328, 9662, 336, 9670, 349, 9677, 1052, 9677 } } }
    -- #193 West Alley St
    ops[193] = { expectedWidth = 6, expectedPoints = { 386, 9642, 386, 9891 }, hideLabel = true, reference = { index = 182, width = 6, points = { 386, 9642, 386, 9891 } } }
    -- #194 Cane St
    ops[194] = { expectedWidth = 6, expectedPoints = { 476, 9680, 476, 9806 }, hideLabel = true, reference = { index = 183, width = 6, points = { 476, 9680, 476, 9806 } } }
    -- #195 Old Ekron Road
    ops[195] = { expectedWidth = 6, expectedPoints = { 539, 9293.5, 539, 9674 }, hideLabel = true, reference = { index = 184, width = 6, points = { 539, 9293.5, 539, 9674 } } }
    -- #196 Chism Dr
    ops[196] = { expectedWidth = 6, expectedPoints = { 479, 9809, 527, 9809, 533, 9806, 536, 9803, 539, 9797, 539, 9680 }, hideLabel = true, reference = { index = 185, width = 6, points = { 479, 9809, 527, 9809, 533, 9806, 536, 9803, 539, 9797, 539, 9680 } } }
    -- #197 East Alley St
    ops[197] = { expectedWidth = 6, expectedPoints = { 453, 9812, 453, 9891 }, hideLabel = true, reference = { index = 186, width = 6, points = { 453, 9812, 453, 9891 } } }
    -- #198 Hutchins Dr
    ops[198] = { expectedWidth = 6, expectedPoints = { 305, 9891, 305, 9822, 308, 9815, 313, 9811, 318, 9809, 473, 9809 }, hideLabel = true, reference = { index = 187, width = 6, points = { 305, 9891, 305, 9822, 308, 9815, 313, 9811, 318, 9809, 473, 9809 } } }
    -- #199 Haysville Road
    ops[199] = { expectedWidth = 8, expectedPoints = { 0, 9895, 1520, 9895 }, hideLabel = true, reference = { index = 188, width = 8, points = { 0, 9895, 1520, 9895 } } }
    -- #200 Railway St
    ops[200] = { expectedWidth = 6, expectedPoints = { 596, 9680, 596, 9891 }, hideLabel = true, reference = { index = 189, width = 6, points = { 596, 9680, 596, 9891 } } }
    -- #201 Willie Dr
    ops[201] = { expectedWidth = 6, expectedPoints = { 647, 9581, 647, 9806 }, hideLabel = true, reference = { index = 190, width = 6, points = { 647, 9581, 647, 9806 } } }
    -- #202 Reese Ave
    ops[202] = { expectedWidth = 6, expectedPoints = { 707, 9558, 707, 9891 }, hideLabel = true, reference = { index = 191, width = 6, points = { 707, 9558, 707, 9891 } } }
    -- #203 Dry Alley
    ops[203] = { expectedWidth = 5, expectedPoints = { 650, 9736, 704, 9736 }, hideLabel = true, reference = { index = 192, width = 5, points = { 650, 9736, 704, 9736 } } }
    -- #204 Parkway Ave
    ops[204] = { expectedWidth = 6, expectedPoints = { 599, 9809, 837, 9809, 849, 9815, 856, 9822, 862, 9834, 862, 9891 }, hideLabel = true, reference = { index = 193, width = 6, points = { 599, 9809, 837, 9809, 849, 9815, 856, 9822, 862, 9834, 862, 9891 } } }
    -- #205 Berry Dr
    ops[205] = { expectedWidth = 6, expectedPoints = { 710, 9746, 795, 9746, 804, 9741, 809, 9736, 812, 9730, 812, 9680 }, hideLabel = true, reference = { index = 194, width = 6, points = { 710, 9746, 795, 9746, 804, 9741, 809, 9736, 812, 9730, 812, 9680 } } }
    -- #206 Smith Road
    ops[206] = { expectedWidth = 6, expectedPoints = { 1055, 9468, 1055, 9710, 1014, 9792, 1014, 9891 }, hideLabel = true, reference = { index = 195, width = 6, points = { 1055, 9468, 1055, 9710, 1014, 9792, 1014, 9891 } } }
    -- #207 Smith Road
    ops[207] = { expectedWidth = 4, expectedPoints = { 774, 9038, 906, 9170, 1056, 9469.5 }, hideLabel = true, reference = { index = 196, width = 4, points = { 774, 9038, 906, 9170, 1056, 9469.5 } } }
    -- #208 Larry Dr
    ops[208] = { expectedWidth = 6, expectedPoints = { 812, 9486, 812, 9674 }, hideLabel = true, reference = { index = 197, width = 6, points = { 812, 9486, 812, 9674 } } }
    -- #209 Stringtown Road
    ops[209] = { expectedWidth = 8, expectedPoints = { 911, 9899, 911, 10200 }, hideLabel = true, reference = { index = 198, width = 8, points = { 911, 9899, 911, 10200 } } }
    -- #211 Boone Road
    ops[211] = { expectedWidth = 6, expectedPoints = { 10064, 9793, 10064, 9993, 10079, 10023, 10091, 10035, 10123, 10051, 10521, 10051 }, hideLabel = true, reference = { index = 200, width = 6, points = { 10064, 9793, 10064, 9993, 10079, 10023, 10091, 10035, 10123, 10051, 10521, 10051 } } }
    -- #212 Old Mill Road
    ops[212] = { expectedWidth = 8, expectedPoints = { 9908, 9789, 10332, 9789, 10436, 9737, 10521, 9737 }, hideLabel = true, reference = { index = 201, width = 8, points = { 9908, 9789, 10332, 9789, 10436, 9737, 10521, 9737 } } }
    -- #213 McCoy Road
    ops[213] = { expectedWidth = 5, expectedPoints = { 10029.5, 9785, 10029.5, 9552, 10036, 9539, 10043, 9532, 10056, 9525.5, 10233, 9525.5, 10245, 9531, 10254, 9541, 10259.5, 9551.5, 10259.5, 9709, 10267.5, 9725, 10274, 9731, 10333, 9760.5, 10384.5, 9760.5 }, hideLabel = true, reference = { index = 202, width = 5, points = { 10029.5, 9785, 10029.5, 9552, 10036, 9539, 10043, 9532, 10056, 9525.5, 10233, 9525.5, 10245, 9531, 10254, 9541, 10259.5, 9551.5, 10259.5, 9709, 10267.5, 9725, 10274, 9731, 10333, 9760.5, 10384.5, 9760.5 } } }
    -- #214 Dixie Highway (Route 31W)
    ops[214] = { expectedWidth = 14, expectedPoints = { 10592, 8858, 10592, 11197, 10592, 14251 }, hideLabel = true, reference = { index = 203, width = 14, points = { 10592, 8858, 10592, 11197, 10592, 14251 } } }
    -- #215 Irma Dr
    ops[215] = { expectedWidth = 4, expectedPoints = { 11104, 9318, 11310, 9318 }, hideLabel = true, reference = { index = 217, width = 4, points = { 11104, 9318, 11310, 9318 } } }
    -- #218 Magazine Road
    ops[218] = { expectedWidth = 4, expectedPoints = { 11545, 9746, 11288, 9746, 11262, 9733, 11245, 9716, 11231, 9689, 11231, 9417, 11239, 9400, 11246, 9393, 11262, 9385, 11289, 9385, 11300, 9379.5, 11306.5, 9373, 11312, 9362, 11312, 9313, 11319, 9299, 11325, 9293, 11333, 9289, 11534, 9289, 11540, 9286, 11545, 9281, 11548, 9275, 11548, 9265, 11551, 9258.5, 11555, 9254.5, 11562, 9251, 11790, 9251, 11822, 9267, 11844, 9289, 11876, 9305, 12263, 9305 }, hideLabel = true, reference = { index = 253, width = 4, points = { 11545, 9746, 11288, 9746, 11262, 9733, 11245, 9716, 11231, 9689, 11231, 9417, 11239, 9400, 11246, 9393, 11262, 9385, 11289, 9385, 11300, 9379.5, 11306.5, 9373, 11312, 9362, 11312, 9313, 11319, 9299, 11325, 9293, 11333, 9289, 11534, 9289, 11540, 9286, 11545, 9281, 11548, 9275, 11548, 9265, 11551, 9258.5, 11555, 9254.5, 11562, 9251, 11790, 9251, 11822, 9267, 11844, 9289, 11876, 9305, 12263, 9305 } } }
    -- #219 Deerstalk Road
    ops[219] = { expectedWidth = 4, expectedPoints = { 11331, 9748, 11331, 9939, 11357, 9992, 11416, 10051, 11437, 10093, 11437, 10300, 11444.5, 10315, 11459.5, 10329.5, 11474, 10337, 11601, 10337 }, hideLabel = true, reference = { index = 254, width = 4, points = { 11331, 9748, 11331, 9939, 11357, 9992, 11416, 10051, 11437, 10093, 11437, 10300, 11444.5, 10315, 11459.5, 10329.5, 11474, 10337, 11601, 10337 } } }
    -- #220 Horselick Road
    ops[220] = { expectedWidth = 5, expectedPoints = { 6695, 11212, 6695, 11469, 6729, 11536, 7276, 12084, 7294, 12119, 7294, 13312, 7566, 13856, 8031, 14321 }, hideLabel = true, reference = { index = 255, width = 5, points = { 6695, 11212, 6695, 11469, 6729, 11536, 7276, 12084, 7294, 12119, 7294, 13312, 7566, 13856, 8031, 14321 } } }
    -- #221 Upturned Road
    ops[221] = { expectedWidth = 4, expectedPoints = { 7734, 14020, 8220.5, 14019.5, 8225.5, 14023.5, 8329.5, 14023, 8334, 14025, 8339, 14030, 8343, 14037, 8343.5, 14112 }, hideLabel = true, reference = { index = 256, width = 4, points = { 7734, 14020, 8220.5, 14019.5, 8225.5, 14023.5, 8329.5, 14023, 8334, 14025, 8339, 14030, 8343, 14037, 8343.5, 14112 } } }
    -- #222 Poppy's Peace Road
    ops[222] = { expectedWidth = 5, expectedPoints = { 5531, 14353, 5531, 14507, 5537, 14518, 5541, 14522, 5553, 14528, 5648, 14528, 5695, 14551, 5919, 14551, 5981, 14582, 6047, 14582, 6055, 14578, 6060, 14572, 6063, 14566, 6063, 14560 }, hideLabel = true, reference = { index = 257, width = 5, points = { 5531, 14353, 5531, 14507, 5537, 14518, 5541, 14522, 5553, 14528, 5648, 14528, 5695, 14551, 5919, 14551, 5981, 14582, 6047, 14582, 6055, 14578, 6060, 14572, 6063, 14566, 6063, 14560 } } }
    -- #226 Taffy Lane
    ops[226] = { expectedWidth = 6, expectedPoints = { 9122, 8700, 9297, 8700 }, hideLabel = true, reference = { index = 261, width = 6, points = { 9122, 8700, 9297, 8700 } } }
    -- #227 Egg Lane
    ops[227] = { expectedWidth = 6, expectedPoints = { 9300, 8482, 9300, 8997 }, hideLabel = true, reference = { index = 262, width = 6, points = { 9300, 8482, 9300, 8997 } } }
    -- #228 Apple Grove Road
    ops[228] = { expectedWidth = 6, expectedPoints = { 9122, 9000, 9417, 9000, 9417, 9333 }, hideLabel = true, reference = { index = 263, width = 6, points = { 9122, 9000, 9417, 9000, 9417, 9333 } } }
    -- #229 Buck Road
    ops[229] = { expectedWidth = 6, expectedPoints = { 9300, 8063, 9300, 8146, 9119, 8327, 9119, 9290, 9129, 9300, 9280, 9300, 9316, 9336, 9420, 9336, 9440, 9356, 9440, 9785 }, hideLabel = true, reference = { index = 264, width = 6, points = { 9300, 8063, 9300, 8146, 9119, 8327, 9119, 9290, 9129, 9300, 9280, 9300, 9316, 9336, 9420, 9336, 9440, 9356, 9440, 9785 } } }
    -- #230 Balsam Lane
    ops[230] = { expectedWidth = 4, expectedPoints = { 8860, 9214, 8989, 9214, 8989, 9139, 9116, 9139 }, hideLabel = true, reference = { index = 265, width = 4, points = { 8860, 9214, 8989, 9214, 8989, 9139, 9116, 9139 } } }
    -- #231 Ann's Kiss Lane
    ops[231] = { expectedWidth = 6, expectedPoints = { 8760, 8793, 9116, 8793 }, hideLabel = true, reference = { index = 266, width = 6, points = { 8760, 8793, 9116, 8793 } } }
    -- #232 Blue Sky Road
    ops[232] = { expectedWidth = 6, expectedPoints = { 8514, 9478, 8752, 9478 }, hideLabel = true, reference = { index = 267, width = 6, points = { 8514, 9478, 8752, 9478 } } }
    -- #233 Old Logging Road
    ops[233] = { expectedWidth = 7, expectedPoints = { 7871.5, 8566, 7871.5, 8883.5, 7679.5, 8883.5, 7679.5, 9297, 8038.5, 9297.5, 8038.5, 9508.5, 8271.5, 9508.5, 8285.5, 9516, 8293, 9523, 8299.5, 9536, 8299.5, 9785 }, hideLabel = true, reference = { index = 268, width = 7, points = { 7871.5, 8566, 7871.5, 8883.5, 7679.5, 8883.5, 7679.5, 9297, 8038.5, 9297.5, 8038.5, 9508.5, 8271.5, 9508.5, 8285.5, 9516, 8293, 9523, 8299.5, 9536, 8299.5, 9785 } } }
    -- #234 Otter Creek Road
    ops[234] = { expectedWidth = 8, expectedPoints = { 4362, 6110, 4362, 6685, 4381, 6723, 4412, 6754, 4442, 6769, 6733, 6769 }, hideLabel = true, reference = { index = 269, width = 8, points = { 4362, 6110, 4362, 6685, 4381, 6723, 4412, 6754, 4442, 6769, 6733, 6769 } } }
    -- #235 Ito Road
    ops[235] = { expectedWidth = 8, expectedPoints = { 3762, 6338, 4358, 6338 }, hideLabel = true, reference = { index = 270, width = 8, points = { 3762, 6338, 4358, 6338 } } }
    -- #236 Rabbit Lane
    ops[236] = { expectedWidth = 6, expectedPoints = { 3949, 6163, 3949, 6300 }, hideLabel = true, reference = { index = 271, width = 6, points = { 3949, 6163, 3949, 6300 } } }
    -- #237 Fox Road
    ops[237] = { expectedWidth = 6, expectedPoints = { 3904, 6205, 3961, 6148, 4206, 6148 }, hideLabel = true, reference = { index = 272, width = 6, points = { 3904, 6205, 3961, 6148, 4206, 6148 } } }
    -- #238 Sunderland Hills Road
    ops[238] = { expectedWidth = 6, expectedPoints = { 3963, 6546, 4206, 6546, 4232, 6520, 4232, 6342 }, hideLabel = true, reference = { index = 273, width = 6, points = { 3963, 6546, 4206, 6546, 4232, 6520, 4232, 6342 } } }
    -- #239 Pigtail Road
    ops[239] = { expectedWidth = 4, expectedPoints = { 4860, 6279, 4882, 6279, 4898, 6271, 4904, 6265, 4911, 6251, 4911, 6230, 4894, 6196, 4876, 6179, 4846, 6164, 4814, 6164, 4791, 6175, 4767, 6199, 4752, 6229, 4752, 6276, 4801, 6374, 4901, 6474, 4941, 6554, 4941, 6602, 4949, 6618, 4949, 6630, 4974, 6680, 5027, 6733, 5033, 6743, 5033, 6765 }, hideLabel = true, reference = { index = 274, width = 4, points = { 4860, 6279, 4882, 6279, 4898, 6271, 4904, 6265, 4911, 6251, 4911, 6230, 4894, 6196, 4876, 6179, 4846, 6164, 4814, 6164, 4791, 6175, 4767, 6199, 4752, 6229, 4752, 6276, 4801, 6374, 4901, 6474, 4941, 6554, 4941, 6602, 4949, 6618, 4949, 6630, 4974, 6680, 5027, 6733, 5033, 6743, 5033, 6765 } } }
    -- #240 Long Needle Road
    ops[240] = { expectedWidth = 8, expectedPoints = { 5458, 5840, 5458, 6152, 5340, 6388.5, 5340, 6501.5, 5223, 6735, 5223, 6765 }, hideLabel = true, reference = { index = 275, width = 8, points = { 5458, 5840, 5458, 6152, 5340, 6388.5, 5340, 6501.5, 5223, 6735, 5223, 6765 } } }
    -- #241 Coalfield Road
    ops[241] = { expectedWidth = 8, expectedPoints = { 2815, 8394, 3746, 8394 }, hideLabel = true, reference = { index = 276, width = 8, points = { 2815, 8394, 3746, 8394 } } }
    -- #242 Coalfield Road
    ops[242] = { expectedWidth = 7, expectedPoints = { 2674, 8297.5, 2725, 8323, 2776, 8374, 2818.5, 8395 }, hideLabel = true, reference = { index = 277, width = 7, points = { 2674, 8297.5, 2725, 8323, 2776, 8374, 2818.5, 8395 } } }
    -- #243 Coalfield Road
    ops[243] = { expectedWidth = 8, expectedPoints = { 2272, 8298, 2676, 8298 }, hideLabel = true, reference = { index = 278, width = 8, points = { 2272, 8298, 2676, 8298 } } }
    -- #244 Coalfield Road
    ops[244] = { expectedWidth = 7, expectedPoints = { 1976.5, 8104, 2034, 8133, 2126, 8225, 2273.5, 8299 }, hideLabel = true, reference = { index = 279, width = 7, points = { 1976.5, 8104, 2034, 8133, 2126, 8225, 2273.5, 8299 } } }
    -- #245 Coalfield Road
    ops[245] = { expectedWidth = 8, expectedPoints = { 1881, 8105, 1978, 8105 }, hideLabel = true, reference = { index = 280, width = 8, points = { 1881, 8105, 1978, 8105 } } }
    -- #246 Irvington Road
    ops[246] = { expectedWidth = 8, expectedPoints = { 2390, 8302, 2390, 8594, 2305, 8765, 2196, 8874, 1961, 8991, 1587, 9365, 1524, 9491, 1524, 9891 }, hideLabel = true, reference = { index = 281, width = 8, points = { 2390, 8302, 2390, 8594, 2305, 8765, 2196, 8874, 1961, 8991, 1587, 9365, 1524, 9491, 1524, 9891 } } }
    -- #247 Garcon Road
    ops[247] = { expectedWidth = 3, expectedPoints = { 836, 11921.5, 1313.5, 11921.5, 1388.5, 11996.5, 1653, 11996.5, 1798, 11851.5, 2564, 11851.5 }, hideLabel = true, reference = { index = 282, width = 3, points = { 836, 11921.5, 1313.5, 11921.5, 1388.5, 11996.5, 1653, 11996.5, 1798, 11851.5, 2564, 11851.5 } } }
    -- #248 Mount Merino Road
    ops[248] = { expectedWidth = 8, expectedPoints = { 836, 12565, 971, 12565, 1230, 12694, 1362, 12694, 1686, 12533, 2899, 12533 }, hideLabel = true, reference = { index = 283, width = 8, points = { 836, 12565, 971, 12565, 1230, 12694, 1362, 12694, 1686, 12533, 2899, 12533 } } }
    -- #249 Wadsworth Road
    ops[249] = { expectedWidth = 5, expectedPoints = { 2907, 12465, 3297, 12465 }, hideLabel = true, reference = { index = 284, width = 5, points = { 2907, 12465, 3297, 12465 } } }
    -- #250 Kitten Road
    ops[250] = { expectedWidth = 5, expectedPoints = { 3082, 12196, 3089, 12196, 3090, 12193, 3090, 12046, 3094, 12040, 3100, 12037, 3118, 12037 }, hideLabel = true, reference = { index = 285, width = 5, points = { 3082, 12196, 3089, 12196, 3090, 12193, 3090, 12046, 3094, 12040, 3100, 12037, 3118, 12037 } } }
    -- #251 Caban Road
    ops[251] = { expectedWidth = 5, expectedPoints = { 3093, 12095, 3179, 12095, 3184, 12097, 3188, 12101, 3190, 12106, 3190, 12243, 3190, 12244, 3193, 12249, 3196, 12252, 3202, 12255, 3297, 12255 }, hideLabel = true, reference = { index = 286, width = 5, points = { 3093, 12095, 3179, 12095, 3184, 12097, 3188, 12101, 3190, 12106, 3190, 12243, 3190, 12244, 3193, 12249, 3196, 12252, 3202, 12255, 3297, 12255 } } }
    -- #252 Echo Creek Road
    ops[252] = { expectedWidth = 5, expectedPoints = { 2621, 11902, 2637, 11886, 2673, 11868, 3105, 11868, 3188, 11826, 3592, 11422, 3599, 11409 }, hideLabel = true, reference = { index = 287, width = 5, points = { 2621, 11902, 2637, 11886, 2673, 11868, 3105, 11868, 3188, 11826, 3592, 11422, 3599, 11409 } } }
    -- #253 Main St
    ops[253] = { expectedWidth = 5, expectedPoints = { 3599.5, 10929, 3599.5, 11409 }, hideLabel = true, reference = { index = 288, width = 5, points = { 3599.5, 10929, 3599.5, 11409 } } }
    -- #254 Elder Road
    ops[254] = { expectedWidth = 5, expectedPoints = { 3602, 11399.5, 3898, 11399.5 }, hideLabel = true, reference = { index = 289, width = 5, points = { 3602, 11399.5, 3898, 11399.5 } } }
    -- #255 Hawthorne Creek Road
    ops[255] = { expectedWidth = 5, expectedPoints = { 3726, 11260.5, 4453, 11260.5 }, hideLabel = true, reference = { index = 290, width = 5, points = { 3726, 11260.5, 4453, 11260.5 } } }
    -- #256 Echo Close
    ops[256] = { expectedWidth = 5, expectedPoints = { 3662.5, 10929, 3662, 10963, 3666, 10971, 3671, 10974, 3675, 10976, 3766, 10975.5 }, hideLabel = true, reference = { index = 291, width = 5, points = { 3662.5, 10929, 3662, 10963, 3666, 10971, 3671, 10974, 3675, 10976, 3766, 10975.5 } } }
    -- #257 Frog Jump Road
    ops[257] = { expectedWidth = 6, expectedPoints = { 4200.5, 11062, 4207, 11049.5, 4403, 10853.5, 4410.5, 10849.5 }, hideLabel = true, reference = { index = 292, width = 6, points = { 4200.5, 11062, 4207, 11049.5, 4403, 10853.5, 4410.5, 10849.5 } } }
    -- #258 Frog Jump Road
    ops[258] = { expectedWidth = 5, expectedPoints = { 4021, 11978, 4191, 11808, 4200.5, 11789.5, 4200.5, 11060.5 }, hideLabel = true, reference = { index = 293, width = 5, points = { 4021, 11978, 4191, 11808, 4200.5, 11789.5, 4200.5, 11060.5 } } }
    -- #259 Hog Wallow Road
    ops[259] = { expectedWidth = 8, expectedPoints = { 4483, 10744, 4483, 10946, 4457, 10997, 4457, 11279, 4463, 11289, 4475, 11301, 4483, 11315, 4483, 11879, 4470, 11905, 4459, 11917, 4441, 11926, 4334, 11926, 4304, 11941, 4131, 12113, 4113, 12149, 4113, 12694, 4108, 12703, 4104, 12708, 4093, 12714, 4040, 12714, 4028, 12719, 4025, 12722, 4019, 12733, 4019, 13015, 3957, 13139, 3957, 13521, 3952, 13531.5, 3908.5, 13575 }, hideLabel = true, reference = { index = 294, width = 8, points = { 4483, 10744, 4483, 10946, 4457, 10997, 4457, 11279, 4463, 11289, 4475, 11301, 4483, 11315, 4483, 11879, 4470, 11905, 4459, 11917, 4441, 11926, 4334, 11926, 4304, 11941, 4131, 12113, 4113, 12149, 4113, 12694, 4108, 12703, 4104, 12708, 4093, 12714, 4040, 12714, 4028, 12719, 4025, 12722, 4019, 12733, 4019, 13015, 3957, 13139, 3957, 13521, 3952, 13531.5, 3908.5, 13575 } } }
    -- #260 Freedom Road
    ops[260] = { expectedWidth = 5, expectedPoints = { 3056, 9899, 3056, 10883, 3243, 11256, 3684, 11697, 3690, 11701, 3716, 11701, 3719, 11702, 3724, 11707, 3727, 11712, 3727, 11735, 3731, 11744, 3913, 11926, 4016, 11978, 4139, 12101 }, hideLabel = true, reference = { index = 295, width = 5, points = { 3056, 9899, 3056, 10883, 3243, 11256, 3684, 11697, 3690, 11701, 3716, 11701, 3719, 11702, 3724, 11707, 3727, 11712, 3727, 11735, 3731, 11744, 3913, 11926, 4016, 11978, 4139, 12101 } } }
    -- #261 Steelworks Road
    ops[261] = { expectedWidth = 6, expectedPoints = { 1752, 10850.5, 1785, 10834, 1824.5, 10794.5, 1857.5, 10778, 2007, 10778, 2032, 10765.5, 2049, 10748.5 }, hideLabel = true, reference = { index = 296, width = 6, points = { 1752, 10850.5, 1785, 10834, 1824.5, 10794.5, 1857.5, 10778, 2007, 10778, 2032, 10765.5, 2049, 10748.5 } } }
    -- #262 Smith Road
    ops[262] = { expectedWidth = 6, expectedPoints = { 1512, 10852, 3054, 10852 }, hideLabel = true, reference = { index = 297, width = 6, points = { 1512, 10852, 3054, 10852 } } }
    -- #263 Payne Road
    ops[263] = { expectedWidth = 8, expectedPoints = { 3059, 10852, 3292, 10852, 3320, 10866, 3363, 10909, 3395, 10925, 3823, 10925, 3840, 10917, 3890, 10866, 3927, 10848, 4479, 10848 }, hideLabel = true, reference = { index = 298, width = 8, points = { 3059, 10852, 3292, 10852, 3320, 10866, 3363, 10909, 3395, 10925, 3823, 10925, 3840, 10917, 3890, 10866, 3927, 10848, 4479, 10848 } } }
    -- #264 Creek Lane
    ops[264] = { expectedWidth = 5, expectedPoints = { 3563, 10893.5, 3416.5, 10893.5, 3414.5, 10895.5, 3414.5, 11065 }, hideLabel = true, reference = { index = 299, width = 5, points = { 3563, 10893.5, 3416.5, 10893.5, 3414.5, 10895.5, 3414.5, 11065 } } }
    -- #265 Peacekeeper Road
    ops[265] = { expectedWidth = 5, expectedPoints = { 3417, 10961.5, 3597, 10961.5 }, hideLabel = true, reference = { index = 300, width = 5, points = { 3417, 10961.5, 3597, 10961.5 } } }
    -- #266 Winter Dr
    ops[266] = { expectedWidth = 5, expectedPoints = { 3564.5, 10964, 3564.5, 11229, 3568, 11236, 3574, 11242, 3581, 11245.5, 3597, 11245.5 }, hideLabel = true, reference = { index = 301, width = 5, points = { 3564.5, 10964, 3564.5, 11229, 3568, 11236, 3574, 11242, 3581, 11245.5, 3597, 11245.5 } } }
    -- #267 Pipspit Road
    ops[267] = { expectedWidth = 5, expectedPoints = { 3895, 11107, 3977, 11025, 3982, 11016, 3982.5, 10852 }, hideLabel = true, reference = { index = 302, width = 5, points = { 3895, 11107, 3977, 11025, 3982, 11016, 3982.5, 10852 } } }
    -- #268 Wilde Road
    ops[268] = { expectedWidth = 5, expectedPoints = { 3768.5, 10929, 3768.5, 11084.5, 3772, 11092, 3778, 11098, 3784, 11100.5, 3880, 11100.5, 3890, 11105, 3897, 11112, 3900.5, 11119.5, 3900.5, 11258 }, hideLabel = true, reference = { index = 303, width = 5, points = { 3768.5, 10929, 3768.5, 11084.5, 3772, 11092, 3778, 11098, 3784, 11100.5, 3880, 11100.5, 3890, 11105, 3897, 11112, 3900.5, 11119.5, 3900.5, 11258 } } }
    -- #269 Johannes Road
    ops[269] = { expectedWidth = 5, expectedPoints = { 3900.5, 11263, 3900.5, 11599 }, hideLabel = true, reference = { index = 304, width = 5, points = { 3900.5, 11263, 3900.5, 11599 } } }
    -- #270 Lakeview Road
    ops[270] = { expectedWidth = 5, expectedPoints = { 3195, 11823, 3291, 11919, 3299, 11935, 3299, 12713, 3303, 12720, 3309, 12726, 3311, 12728, 3318, 12732, 3734, 12732, 3776, 12753, 4015, 12753 }, hideLabel = true, reference = { index = 305, width = 5, points = { 3195, 11823, 3291, 11919, 3299, 11935, 3299, 12713, 3303, 12720, 3309, 12726, 3311, 12728, 3318, 12732, 3734, 12732, 3776, 12753, 4015, 12753 } } }
    -- #273 Poverty Lane
    ops[273] = { expectedWidth = 6, expectedPoints = { 9300, 7800, 9300, 7710, 9380, 7630, 9509, 7630 }, hideLabel = true, reference = { index = 308, width = 6, points = { 9300, 7800, 9300, 7710, 9380, 7630, 9509, 7630 } } }
    -- #274 River Sight Road
    ops[274] = { expectedWidth = 7, expectedPoints = { 9358, 7435.5, 9486, 7435.5, 9499, 7442, 9507, 7450, 9513.5, 7463, 9513.5, 7625, 9513, 7628, 9513, 7769, 9521, 7786, 9525, 7791 }, hideLabel = true, reference = { index = 309, width = 7, points = { 9358, 7435.5, 9486, 7435.5, 9499, 7442, 9507, 7450, 9513.5, 7463, 9513.5, 7625, 9513, 7628, 9513, 7769, 9521, 7786, 9525, 7791 } } }
    -- #276 Lipstick Road
    ops[276] = { expectedWidth = 4, expectedPoints = { 10364, 6675, 10364, 6654, 10368, 6646, 10375.5, 6642, 10716, 6642 }, hideLabel = true, reference = { index = 311, width = 4, points = { 10364, 6675, 10364, 6654, 10368, 6646, 10375.5, 6642, 10716, 6642 } } }
    -- #277 Lipstick Road
    ops[277] = { expectedWidth = 6, expectedPoints = { 10308, 7446, 10308, 7161, 10363, 7106, 10363, 6675 }, hideLabel = true, reference = { index = 312, width = 6, points = { 10308, 7446, 10308, 7161, 10363, 7106, 10363, 6675 } } }
    -- #278 West Hold Road
    ops[278] = { expectedWidth = 6, expectedPoints = { 10620, 6644, 10620, 6925 }, hideLabel = true, reference = { index = 313, width = 6, points = { 10620, 6644, 10620, 6925 } } }
    -- #279 River Walk Road
    ops[279] = { expectedWidth = 6, expectedPoints = { 10366, 6928, 10860, 6928 }, hideLabel = true, reference = { index = 314, width = 6, points = { 10366, 6928, 10860, 6928 } } }
    -- #280 Raccoon Road
    ops[280] = { expectedWidth = 10, expectedPoints = { 9511, 8055, 9511, 7822, 9521, 7802, 9532, 7791, 9552, 7781, 9912, 7781, 9926, 7774, 9934, 7766, 9941, 7752, 9941, 7496, 9951, 7476, 9967, 7460, 9985, 7451, 10673, 7451, 10687.5, 7443, 10695.5, 7435.5, 10703, 7421, 10703, 7075.5, 10710, 7062, 10719, 7054, 10730.5, 7048, 10732, 7048 }, hideLabel = true, reference = { index = 315, width = 10, points = { 9511, 8055, 9511, 7822, 9521, 7802, 9532, 7791, 9552, 7781, 9912, 7781, 9926, 7774, 9934, 7766, 9941, 7752, 9941, 7496, 9951, 7476, 9967, 7460, 9985, 7451, 10673, 7451, 10687.5, 7443, 10695.5, 7435.5, 10703, 7421, 10703, 7075.5, 10710, 7062, 10719, 7054, 10730.5, 7048, 10732, 7048 } } }
    -- #281 Riverside Road
    ops[281] = { expectedWidth = 8, expectedPoints = { 7007, 7585, 7451, 7585, 7472, 7596, 7485, 7609, 7495, 7629, 7495, 7757, 7514, 7794, 7538, 7818, 7567, 7833, 8312, 7833, 8343, 7849, 8368, 7874, 8384, 7906, 8384, 8062, 8397, 8088, 8420, 8111, 8454, 8128, 8642, 8128 }, hideLabel = true, reference = { index = 316, width = 8, points = { 7007, 7585, 7451, 7585, 7472, 7596, 7485, 7609, 7495, 7629, 7495, 7757, 7514, 7794, 7538, 7818, 7567, 7833, 8312, 7833, 8343, 7849, 8368, 7874, 8384, 7906, 8384, 8062, 8397, 8088, 8420, 8111, 8454, 8128, 8642, 8128 } } }
    -- #282 Riverside Road
    ops[282] = { expectedWidth = 8, expectedPoints = { 8646, 8132, 8646, 8095, 8655, 8077, 8664, 8068, 8682, 8059, 10742, 8059, 10759, 8068, 10773, 8081, 10781, 8098, 10781, 8285, 10791, 8305, 10805, 8319, 10823, 8328, 11637, 8328 }, hideLabel = true, reference = { index = 317, width = 8, points = { 8646, 8132, 8646, 8095, 8655, 8077, 8664, 8068, 8682, 8059, 10742, 8059, 10759, 8068, 10773, 8081, 10781, 8098, 10781, 8285, 10791, 8305, 10805, 8319, 10823, 8328, 11637, 8328 } } }
    -- #283 Skullcrack Road
    ops[283] = { expectedWidth = 4, expectedPoints = { 9849, 8055, 9849, 8001, 9856, 7988, 9863, 7981, 9876, 7974, 9989, 7974, 10005, 7967, 10194, 7777, 10500, 7777 }, hideLabel = true, reference = { index = 318, width = 4, points = { 9849, 8055, 9849, 8001, 9856, 7988, 9863, 7981, 9876, 7974, 9989, 7974, 10005, 7967, 10194, 7777, 10500, 7777 } } }
    -- #284 Brandy Lane
    ops[284] = { expectedWidth = 4, expectedPoints = { 10204, 7456, 10204, 7646, 10277, 7719, 10277, 7775 }, hideLabel = true, reference = { index = 319, width = 4, points = { 10204, 7456, 10204, 7646, 10277, 7719, 10277, 7775 } } }
    -- #285 Tioga Road
    ops[285] = { expectedWidth = 4, expectedPoints = { 11931.5, 10337, 11609, 10337 }, hideLabel = true, reference = { index = 320, width = 4, points = { 11931.5, 10337, 11609, 10337 } } }
    -- #286 Tioga Road
    ops[286] = { expectedWidth = 5, expectedPoints = { 12237.5, 9608.5, 11977, 9608.5, 11954, 9620, 11940, 9634, 11927.5, 9659, 11927.5, 9815, 11918, 9834, 11903.5, 9848.5, 11890.5, 9874, 11890.5, 10059, 11913.5, 10105, 11945.5, 10137, 11968.5, 10183, 11968.5, 10299.5, 11958, 10320.5, 11952, 10326.5, 11931, 10337 }, hideLabel = true, reference = { index = 321, width = 5, points = { 12237.5, 9608.5, 11977, 9608.5, 11954, 9620, 11940, 9634, 11927.5, 9659, 11927.5, 9815, 11918, 9834, 11903.5, 9848.5, 11890.5, 9874, 11890.5, 10059, 11913.5, 10105, 11945.5, 10137, 11968.5, 10183, 11968.5, 10299.5, 11958, 10320.5, 11952, 10326.5, 11931, 10337 } } }
    -- #287 Tioga Road
    ops[287] = { expectedWidth = 7, expectedPoints = { 12266.5, 9300.5, 12266.5, 9581.5, 12260.5, 9593, 12252, 9601.5, 12237, 9609 }, hideLabel = true, reference = { index = 322, width = 7, points = { 12266.5, 9300.5, 12266.5, 9581.5, 12260.5, 9593, 12252, 9601.5, 12237, 9609 } } }
    -- #288 Tioga Road
    ops[288] = { expectedWidth = 6, expectedPoints = { 12266, 9000, 12266.5, 9264.5, 12266.5, 9300.5 }, hideLabel = true, reference = { index = 323, width = 6, points = { 12266, 9000, 12266.5, 9264.5, 12266.5, 9300.5 } } }
    -- #289 Tioga Road
    ops[289] = { expectedWidth = 7, expectedPoints = { 12208, 8327, 12237.5, 8341.5, 12254, 8358, 12266.5, 8383.5, 12266.5, 9000 }, hideLabel = true, reference = { index = 324, width = 7, points = { 12208, 8327, 12237.5, 8341.5, 12254, 8358, 12266.5, 8383.5, 12266.5, 9000 } } }
    -- #290 Tioga Road
    ops[290] = { expectedWidth = 8, expectedPoints = { 11651, 8328, 12209.5, 8328 }, hideLabel = true, reference = { index = 325, width = 8, points = { 11651, 8328, 12209.5, 8328 } } }
    -- #291 Knox Road
    ops[291] = { expectedWidth = 8, expectedPoints = { 11605, 10199, 11605, 10519, 11602, 10525.5, 11595, 10532.5, 11588, 10536, 11530, 10536, 11521.5, 10539, 11518.5, 10542.5, 11513, 10553, 11513, 11197 }, hideLabel = true, reference = { index = 326, width = 8, points = { 11605, 10199, 11605, 10519, 11602, 10525.5, 11595, 10532.5, 11588, 10536, 11530, 10536, 11521.5, 10539, 11518.5, 10542.5, 11513, 10553, 11513, 11197 } } }
    -- #292 Haulage Road
    ops[292] = { expectedWidth = 6, expectedPoints = { 11707, 9606.5, 11512, 9606.5, 11512, 9690.5, 11548, 9690.5, 11548, 10196, 11609, 10196 }, hideLabel = true, reference = { index = 327, width = 6, points = { 11707, 9606.5, 11512, 9606.5, 11512, 9690.5, 11548, 9690.5, 11548, 10196, 11609, 10196 } } }
    -- #293 Minions Lane
    ops[293] = { expectedWidth = 4, expectedPoints = { 8703, 11645, 9095, 11645 }, hideLabel = true, reference = { index = 329, width = 4, points = { 8703, 11645, 9095, 11645 } } }
    -- #294 Cowcall Road
    ops[294] = { expectedWidth = 5, expectedPoints = { 8779, 11867.5, 9358, 11867.5 }, hideLabel = true, reference = { index = 330, width = 5, points = { 8779, 11867.5, 9358, 11867.5 } } }
    -- #295 Wicklow Lane
    ops[295] = { expectedWidth = 4, expectedPoints = { 9097, 11455, 9097, 11865 }, hideLabel = true, reference = { index = 331, width = 4, points = { 9097, 11455, 9097, 11865 } } }
    -- #296 Bantam Road
    ops[296] = { expectedWidth = 5, expectedPoints = { 9024.5, 11870, 9024.5, 12194 }, hideLabel = true, reference = { index = 332, width = 5, points = { 9024.5, 11870, 9024.5, 12194 } } }
    -- #297 Darkwallow Dr
    ops[297] = { expectedWidth = 5, expectedPoints = { 8470, 14400.5, 8547, 14400.5, 8554, 14396.5, 8579, 14371.5, 8585, 14359.5, 8602.5, 14342, 8620, 14333.5, 8727, 14333.5 }, hideLabel = true, reference = { index = 333, width = 5, points = { 8470, 14400.5, 8547, 14400.5, 8554, 14396.5, 8579, 14371.5, 8585, 14359.5, 8602.5, 14342, 8620, 14333.5, 8727, 14333.5 } } }
    -- #298 Dark Wallow Road
    ops[298] = { expectedWidth = 6, expectedPoints = { 8730, 14121, 8730, 14471, 8733, 14477, 8810.5, 14554, 8815.5, 14557, 8884, 14557, 8890.5, 14560, 8969, 14639, 8972, 14642, 8974, 14646, 8974, 14779, 8971, 14785, 8955.5, 14801, 8953, 14806, 8953, 14897, 8950, 14904, 8906.5, 14948, 8906, 14949, 8906, 14991, 8903, 14998, 8898, 15003, 8892, 15007, 8875, 15007, 8869, 15010, 8850, 15029, 8847, 15032, 8845, 15036, 8845, 15063, 8848, 15069, 8869.5, 15090.5, 8873, 15097.5, 8873, 15241, 8869.5, 15248.5, 8853, 15265, 8846, 15269, 8806.5, 15269, 8801.5, 15271.5, 8784, 15289, 8780, 15296, 8780, 15330, 8777, 15336, 8768, 15345, 8761, 15350, 8675, 15350, 8669.5, 15352.5, 8628.5, 15394, 8621, 15398, 8534, 15398, 8528, 15401, 8475, 15454, 8468, 15458, 8420, 15458, 8414, 15461, 8406, 15468, 8402, 15470, 8389, 15470, 8384, 15472, 8356, 15500, 8349.5, 15503, 8001, 15503, 7994, 15500, 7922, 15429, 7918, 15421, 7918, 14949, 7921.5, 14942, 7959.5, 14903.5 }, hideLabel = true, reference = { index = 334, width = 6, points = { 8730, 14121, 8730, 14471, 8733, 14477, 8810.5, 14554, 8815.5, 14557, 8884, 14557, 8890.5, 14560, 8969, 14639, 8972, 14642, 8974, 14646, 8974, 14779, 8971, 14785, 8955.5, 14801, 8953, 14806, 8953, 14897, 8950, 14904, 8906.5, 14948, 8906, 14949, 8906, 14991, 8903, 14998, 8898, 15003, 8892, 15007, 8875, 15007, 8869, 15010, 8850, 15029, 8847, 15032, 8845, 15036, 8845, 15063, 8848, 15069, 8869.5, 15090.5, 8873, 15097.5, 8873, 15241, 8869.5, 15248.5, 8853, 15265, 8846, 15269, 8806.5, 15269, 8801.5, 15271.5, 8784, 15289, 8780, 15296, 8780, 15330, 8777, 15336, 8768, 15345, 8761, 15350, 8675, 15350, 8669.5, 15352.5, 8628.5, 15394, 8621, 15398, 8534, 15398, 8528, 15401, 8475, 15454, 8468, 15458, 8420, 15458, 8414, 15461, 8406, 15468, 8402, 15470, 8389, 15470, 8384, 15472, 8356, 15500, 8349.5, 15503, 8001, 15503, 7994, 15500, 7922, 15429, 7918, 15421, 7918, 14949, 7921.5, 14942, 7959.5, 14903.5 } } }
    -- #299 Camp Arthur Road
    ops[299] = { expectedWidth = 6, expectedPoints = { 7833.5, 14767, 7942, 14767, 7948, 14764, 7959, 14754, 7964, 14746, 7964, 14674.5, 7965.5, 14672, 7972, 14665.5, 7975, 14664, 8222, 14664, 8278, 14608, 8304, 14608 }, hideLabel = true, reference = { index = 335, width = 6, points = { 7833.5, 14767, 7942, 14767, 7948, 14764, 7959, 14754, 7964, 14746, 7964, 14674.5, 7965.5, 14672, 7972, 14665.5, 7975, 14664, 8222, 14664, 8278, 14608, 8304, 14608 } } }
    -- #300 Camp Arthur Road
    ops[300] = { expectedWidth = 8, expectedPoints = { 7752, 14505, 7752, 14752, 7758.5, 14762, 7768, 14768, 7833.5, 14768 }, hideLabel = true, reference = { index = 336, width = 8, points = { 7752, 14505, 7752, 14752, 7758.5, 14762, 7768, 14768, 7833.5, 14768 } } }
    -- #301 Water Treatment Plant Road
    ops[301] = { expectedWidth = 8, expectedPoints = { 8030, 14970.5, 8033, 14975.5, 8035, 14980, 8035, 15247 }, hideLabel = true, reference = { index = 337, width = 8, points = { 8030, 14970.5, 8033, 14975.5, 8035, 14980, 8035, 15247 } } }
    -- #302 Water Treatment Plant Road
    ops[302] = { expectedWidth = 6, expectedPoints = { 7829, 14769.5, 8030, 14970.5 }, hideLabel = true, reference = { index = 338, width = 6, points = { 7829, 14769.5, 8030, 14970.5 } } }
    -- #303 Trinca Road
    ops[303] = { expectedWidth = 8, expectedPoints = { 7007, 8154, 6557, 8154, 6535, 8165, 6519, 8181, 6508, 8203, 6508, 8473, 6518.5, 8493.5, 6534, 8508, 6552, 8517, 6657, 8517, 6677, 8527, 6689, 8539, 6699, 8559, 6699, 8914, 6708, 8931, 6722, 8945, 6740, 8955, 7273, 8955 }, hideLabel = true, reference = { index = 339, width = 8, points = { 7007, 8154, 6557, 8154, 6535, 8165, 6519, 8181, 6508, 8203, 6508, 8473, 6518.5, 8493.5, 6534, 8508, 6552, 8517, 6657, 8517, 6677, 8527, 6689, 8539, 6699, 8559, 6699, 8914, 6708, 8931, 6722, 8945, 6740, 8955, 7273, 8955 } } }
    -- #304 Jasper Road
    ops[304] = { expectedWidth = 4, expectedPoints = { 6440, 9000, 6440, 9102 }, hideLabel = true, reference = { index = 340, width = 4, points = { 6440, 9000, 6440, 9102 } } }
    -- #305 Jasper Road
    ops[305] = { expectedWidth = 5, expectedPoints = { 6518, 8497, 6506.5, 8520.5, 6506.5, 8569, 6440.5, 8635, 6440.5, 9000 }, hideLabel = true, reference = { index = 341, width = 5, points = { 6518, 8497, 6506.5, 8520.5, 6506.5, 8569, 6440.5, 8635, 6440.5, 9000 } } }
    -- #306 Lickskillet Lane
    ops[306] = { expectedWidth = 5, expectedPoints = { 6096.5, 9469, 6096.5, 9381.5, 6161.5, 9316.5, 6161.5, 9104.5, 7053, 9104.5 }, hideLabel = true, reference = { index = 342, width = 5, points = { 6096.5, 9469, 6096.5, 9381.5, 6161.5, 9316.5, 6161.5, 9104.5, 7053, 9104.5 } } }
    -- #307 Emerald Road
    ops[307] = { expectedWidth = 5, expectedPoints = { 6530.5, 9107, 6530.5, 9305.5, 6560.5, 9338 }, hideLabel = true, reference = { index = 343, width = 5, points = { 6530.5, 9107, 6530.5, 9305.5, 6560.5, 9338 } } }
    -- #308 Fallas Back Road
    ops[308] = { expectedWidth = 8, expectedPoints = { 5218, 11100, 5218, 10041, 5225, 10027, 5231, 10021, 5245, 10014, 5400, 10014, 5410, 10009, 5414, 10005, 5418, 9996, 5418, 9650, 5423, 9640, 5425, 9638, 5436, 9633, 5638, 9633, 5680, 9613, 5789, 9503, 5849, 9473, 7273, 9473 }, hideLabel = true, reference = { index = 344, width = 8, points = { 5218, 11100, 5218, 10041, 5225, 10027, 5231, 10021, 5245, 10014, 5400, 10014, 5410, 10009, 5414, 10005, 5418, 9996, 5418, 9650, 5423, 9640, 5425, 9638, 5436, 9633, 5638, 9633, 5680, 9613, 5789, 9503, 5849, 9473, 7273, 9473 } } }
    -- #309 Fallas Back Road
    ops[309] = { expectedWidth = 7, expectedPoints = { 5249.5, 11167, 5230, 11147.5, 5217.5, 11122.5, 5217.5, 11100 }, hideLabel = true, reference = { index = 345, width = 7, points = { 5249.5, 11167, 5230, 11147.5, 5217.5, 11122.5, 5217.5, 11100 } } }
    -- #310 Darling Lane
    ops[310] = { expectedWidth = 8, expectedPoints = { 6786, 10066, 6880, 9972, 7009, 9972, 7028, 9962, 7039, 9951, 7048, 9933, 7048, 9477 }, hideLabel = true, reference = { index = 346, width = 8, points = { 6786, 10066, 6880, 9972, 7009, 9972, 7028, 9962, 7039, 9951, 7048, 9933, 7048, 9477 } } }
    -- #311 Taffin Road
    ops[311] = { expectedWidth = 5, expectedPoints = { 6381, 9477, 6381, 9925, 6558.5, 10103.5, 6558, 10492 }, hideLabel = true, reference = { index = 347, width = 5, points = { 6381, 9477, 6381, 9925, 6558.5, 10103.5, 6558, 10492 } } }
    -- #312 Leaffall Road
    ops[312] = { expectedWidth = 6, expectedPoints = { 4215, 9142, 4640, 9142, 4717, 9219, 4736, 9229, 4754, 9229, 4772, 9220, 4783, 9209, 4798, 9202, 4837, 9202, 4851, 9209, 4928, 9286, 4935, 9299, 4935, 9444, 4941, 9457, 5020, 9536, 5414, 9536 }, hideLabel = true, reference = { index = 348, width = 6, points = { 4215, 9142, 4640, 9142, 4717, 9219, 4736, 9229, 4754, 9229, 4772, 9220, 4783, 9209, 4798, 9202, 4837, 9202, 4851, 9209, 4928, 9286, 4935, 9299, 4935, 9444, 4941, 9457, 5020, 9536, 5414, 9536 } } }
    -- #313 Twin Sisters Close
    ops[313] = { expectedWidth = 8, expectedPoints = { 5513, 9637, 5513, 9689, 5516, 9694, 5516, 9743, 5616, 9743, 5624, 9735, 5624, 9637 }, hideLabel = true, reference = { index = 349, width = 8, points = { 5513, 9637, 5513, 9689, 5516, 9694, 5516, 9743, 5616, 9743, 5624, 9735, 5624, 9637 } } }
    -- #314 Rabbit Haven Road
    ops[314] = { expectedWidth = 5, expectedPoints = { 7055.5, 8959, 7055.5, 9173, 7138, 9255.5, 7273, 9255.5 }, hideLabel = true, reference = { index = 350, width = 5, points = { 7055.5, 8959, 7055.5, 9173, 7138, 9255.5, 7273, 9255.5 } } }
    -- #315 Railview Road
    ops[315] = { expectedWidth = 8, expectedPoints = { 7007, 8154, 7684, 8154, 7698, 8147, 7709, 8136, 7715, 8122, 7715, 8093, 7733, 8058, 7758, 8033, 7792, 8016, 7854, 8016, 7874, 8006, 7883, 7997, 7893, 7977, 7893, 7837 }, hideLabel = true, reference = { index = 351, width = 8, points = { 7007, 8154, 7684, 8154, 7698, 8147, 7709, 8136, 7715, 8122, 7715, 8093, 7733, 8058, 7758, 8033, 7792, 8016, 7854, 8016, 7874, 8006, 7883, 7997, 7893, 7977, 7893, 7837 } } }
    -- #319 Brenford Ave
    ops[319] = { expectedWidth = 4, expectedPoints = { 1285, 7382, 1425, 7382 }, hideLabel = true, reference = { index = 353, width = 4, points = { 1285, 7382, 1425, 7382 } } }
    -- #320 Stone Road
    ops[320] = { expectedWidth = 5, expectedPoints = { 1430, 7381.5, 2398, 7381.5 }, hideLabel = true, reference = { index = 354, width = 5, points = { 1430, 7381.5, 2398, 7381.5 } } }
    -- #321 Cavalry Road
    ops[321] = { expectedWidth = 4, expectedPoints = { 988, 9094, 1050, 9094, 1063, 9089, 1067, 9084, 1072, 9073, 1072, 8993, 1079, 8980, 1087, 8972, 1098, 8967, 1564, 8967, 1600, 8985, 1936, 8985, 1949, 8997 }, hideLabel = true, reference = { index = 355, width = 4, points = { 988, 9094, 1050, 9094, 1063, 9089, 1067, 9084, 1072, 9073, 1072, 8993, 1079, 8980, 1087, 8972, 1098, 8967, 1564, 8967, 1600, 8985, 1936, 8985, 1949, 8997 } } }
    -- #322 Adam Road
    ops[322] = { expectedWidth = 4, expectedPoints = { 1344, 8613, 1344, 8965 }, hideLabel = true, reference = { index = 356, width = 4, points = { 1344, 8613, 1344, 8965 } } }
    -- #323 Buffalo Lane
    ops[323] = { expectedWidth = 5, expectedPoints = { 2483, 9461, 2479, 9463, 2474, 9469, 2468, 9474, 2451, 9509, 2434, 9526, 2417, 9559, 2418, 9569, 2403, 9599, 2403, 9878, 2406, 9884, 2411, 9889, 2414, 9891 }, hideLabel = true, reference = { index = 357, width = 5, points = { 2483, 9461, 2479, 9463, 2474, 9469, 2468, 9474, 2451, 9509, 2434, 9526, 2417, 9559, 2418, 9569, 2403, 9599, 2403, 9878, 2406, 9884, 2411, 9889, 2414, 9891 } } }
    -- #324 Irvington Road
    ops[324] = { expectedWidth = 8, expectedPoints = { 1524, 9891, 1524, 10307, 1534, 10327, 1547, 10340, 1568, 10351, 1613, 10351, 1629, 10359, 1639, 10369, 1648, 10387, 1648, 10567, 1631, 10601, 1549, 10683, 1508, 10766, 1508, 11305, 1538, 11365, 1582, 11409, 1660, 11448, 1922, 11448, 2405, 11689, 2653, 11938, 2903, 12439.5, 2903, 12869, 2749, 13177, 2528, 13398, 2400, 13651.5, 2400, 13880 }, hideLabel = true, reference = { index = 358, width = 8, points = { 1524, 9891, 1524, 10307, 1534, 10327, 1547, 10340, 1568, 10351, 1613, 10351, 1629, 10359, 1639, 10369, 1648, 10387, 1648, 10567, 1631, 10601, 1549, 10683, 1508, 10766, 1508, 11305, 1538, 11365, 1582, 11409, 1660, 11448, 1922, 11448, 2405, 11689, 2653, 11938, 2903, 12439.5, 2903, 12869, 2749, 13177, 2528, 13398, 2400, 13651.5, 2400, 13880 } } }
    -- #325 Boywhistle Road
    ops[325] = { expectedWidth = 6, expectedPoints = { 2825, 13033, 2877, 13059, 2936, 13118, 2947, 13140, 2947, 13430 }, hideLabel = true, reference = { index = 359, width = 6, points = { 2825, 13033, 2877, 13059, 2936, 13118, 2947, 13140, 2947, 13430 } } }
    -- #326 Hook Lane
    ops[326] = { expectedWidth = 5, expectedPoints = { 1341, 13468, 1341, 13629, 1333, 13647, 1306, 13674, 1293, 13681, 1284, 13690, 1276, 13706, 1276, 13737, 1285, 13755, 1295, 13765, 1310, 13773, 1335, 13773 }, hideLabel = true, reference = { index = 360, width = 5, points = { 1341, 13468, 1341, 13629, 1333, 13647, 1306, 13674, 1293, 13681, 1284, 13690, 1276, 13706, 1276, 13737, 1285, 13755, 1295, 13765, 1310, 13773, 1335, 13773 } } }
    -- #327 Irvington Heights Road
    ops[327] = { expectedWidth = 6, expectedPoints = { 2212.5, 13462.5, 2386.5, 13549.5, 2427.5, 13590.5 }, hideLabel = true, reference = { index = 361, width = 6, points = { 2212.5, 13462.5, 2386.5, 13549.5, 2427.5, 13590.5 } } }
    -- #328 Irvington Heights Road
    ops[328] = { expectedWidth = 8, expectedPoints = { 1102, 13464, 2215, 13464 }, hideLabel = true, reference = { index = 362, width = 8, points = { 1102, 13464, 2215, 13464 } } }
    -- #329 South Park Road
    ops[329] = { expectedWidth = 8, expectedPoints = { 13427, 4084, 14226, 4084, 14241, 4069, 14241, 4046, 14259, 4028, 15185, 4028, 15288, 3976, 15576, 3976, 15588, 3970, 15596, 3962, 15600, 3952, 15600, 3338 }, hideLabel = true, reference = { index = 363, width = 8, points = { 13427, 4084, 14226, 4084, 14241, 4069, 14241, 4046, 14259, 4028, 15185, 4028, 15288, 3976, 15576, 3976, 15588, 3970, 15596, 3962, 15600, 3952, 15600, 3338 } } }
    -- #330 One Horse Road
    ops[330] = { expectedWidth = 4, expectedPoints = { 14246.5, 3466, 15596, 3466 }, hideLabel = true, reference = { index = 364, width = 4, points = { 14246.5, 3466, 15596, 3466 } } }
    -- #331 One Horse Road
    ops[331] = { expectedWidth = 3, expectedPoints = { 13956, 3757.5, 14248, 3465.5 }, hideLabel = true, reference = { index = 365, width = 3, points = { 13956, 3757.5, 14248, 3465.5 } } }
    -- #332 One Horse Road
    ops[332] = { expectedWidth = 4, expectedPoints = { 13642, 3748, 13659, 3757, 13957, 3757 }, hideLabel = true, reference = { index = 366, width = 4, points = { 13642, 3748, 13659, 3757, 13957, 3757 } } }
    -- #333 Old Ashville Road
    ops[333] = { expectedWidth = 5, expectedPoints = { 15604, 3676, 15900, 3676 }, hideLabel = true, reference = { index = 367, width = 5, points = { 15604, 3676, 15900, 3676 } } }
    -- #334 Luthers Road
    ops[334] = { expectedWidth = 5, expectedPoints = { 15679, 3678, 15679, 3896 }, hideLabel = true, reference = { index = 368, width = 5, points = { 15679, 3678, 15679, 3896 } } }
    -- #335 Ashville Road
    ops[335] = { expectedWidth = 5, expectedPoints = { 15604, 3900, 15900, 3900 }, hideLabel = true, reference = { index = 369, width = 5, points = { 15604, 3900, 15900, 3900 } } }
    -- #336 Holly Road
    ops[336] = { expectedWidth = 4, expectedPoints = { 15302, 3760, 15353, 3760, 15359, 3763, 15492, 3896, 15500, 3900, 15596, 3900 }, hideLabel = true, reference = { index = 370, width = 4, points = { 15302, 3760, 15353, 3760, 15359, 3763, 15492, 3896, 15500, 3900, 15596, 3900 } } }
    -- #337 Alberta Dr
    ops[337] = { expectedWidth = 4, expectedPoints = { 15144, 3825, 15144, 3879, 15147, 3885, 15159, 3897, 15163, 3899, 15298, 3899 }, hideLabel = true, reference = { index = 371, width = 4, points = { 15144, 3825, 15144, 3879, 15147, 3885, 15159, 3897, 15163, 3899, 15298, 3899 } } }
    -- #338 Masons Lane
    ops[338] = { expectedWidth = 4, expectedPoints = { 15000, 3459, 15000, 3679 }, hideLabel = true, reference = { index = 372, width = 4, points = { 15000, 3459, 15000, 3679 } } }
    -- #339 Fairdale Road
    ops[339] = { expectedWidth = 4, expectedPoints = { 15002, 3600, 15298, 3600 }, hideLabel = true, reference = { index = 373, width = 4, points = { 15002, 3600, 15298, 3600 } } }
    -- #340 Shawnee Road
    ops[340] = { expectedWidth = 4, expectedPoints = { 15300, 3468, 15300, 3900, 15300, 3972 }, hideLabel = true, reference = { index = 374, width = 4, points = { 15300, 3468, 15300, 3900, 15300, 3972 } } }
    -- #341 Fair Road
    ops[341] = { expectedWidth = 4, expectedPoints = { 13939, 3537, 13915.5, 3537, 13911, 3542, 13911, 3594, 13778, 3594, 13778, 3755 }, hideLabel = true, reference = { index = 375, width = 4, points = { 13939, 3537, 13915.5, 3537, 13911, 3542, 13911, 3594, 13778, 3594, 13778, 3755 } } }
    -- #342 Ash Lane
    ops[342] = { expectedWidth = 4, expectedPoints = { 13795, 3759, 13795, 3866, 13644, 3866 }, hideLabel = true, reference = { index = 376, width = 4, points = { 13795, 3759, 13795, 3866, 13644, 3866 } } }
    -- #343 Corn Road
    ops[343] = { expectedWidth = 7, expectedPoints = { 13652.5, 3458, 13652.5, 3724, 13643.5, 3742.5, 13638, 3748, 13618.5, 3757.5, 13427, 3757.5 }, hideLabel = true, reference = { index = 377, width = 7, points = { 13652.5, 3458, 13652.5, 3724, 13643.5, 3742.5, 13638, 3748, 13618.5, 3757.5, 13427, 3757.5 } } }
    -- #344 Louisville Road
    ops[344] = { expectedWidth = 6, expectedPoints = { 13272, 3458, 13272, 3608, 13424, 3760, 13424, 4382, 13522, 4578, 13522, 4897 }, hideLabel = true, reference = { index = 378, width = 6, points = { 13272, 3458, 13272, 3608, 13424, 3760, 13424, 4382, 13522, 4578, 13522, 4897 } } }
    -- #345 Blueberry Dr
    ops[345] = { expectedWidth = 6, expectedPoints = { 13330, 4904, 13330, 5014 }, hideLabel = true, reference = { index = 379, width = 6, points = { 13330, 4904, 13330, 5014 } } }
    -- #346 Bearcamp Road
    ops[346] = { expectedWidth = 7, expectedPoints = { 12790.5, 5231.5, 12790.5, 5041, 12803, 5016, 12807, 5012, 12832, 4999.5, 12990, 4999.5, 13188, 4900.5, 13925, 4900.5, 13946, 4911, 13960, 4925, 13973.5, 4952, 13973.5, 5549, 13968, 5558.5, 13960.5, 5562.5, 13824, 5562.5, 13802, 5573.5, 13795, 5580, 13786, 5598, 13785.5, 5719.5, 13513.5, 5719.5, 13513.5, 5985.5, 14177, 5986, 14177, 5951, 14177, 5930.5, 14398, 5930 }, hideLabel = true, reference = { index = 380, width = 7, points = { 12790.5, 5231.5, 12790.5, 5041, 12803, 5016, 12807, 5012, 12832, 4999.5, 12990, 4999.5, 13188, 4900.5, 13925, 4900.5, 13946, 4911, 13960, 4925, 13973.5, 4952, 13973.5, 5549, 13968, 5558.5, 13960.5, 5562.5, 13824, 5562.5, 13802, 5573.5, 13795, 5580, 13786, 5598, 13785.5, 5719.5, 13513.5, 5719.5, 13513.5, 5985.5, 14177, 5986, 14177, 5951, 14177, 5930.5, 14398, 5930 } } }
    -- #347 Bearcamp Road
    ops[347] = { expectedWidth = 5, expectedPoints = { 12931, 5479.5, 12915, 5471.5, 12906, 5462.5, 12789.5, 5229 }, hideLabel = true, reference = { index = 381, width = 5, points = { 12931, 5479.5, 12915, 5471.5, 12906, 5462.5, 12789.5, 5229 } } }
    -- #348 Bearcamp Road
    ops[348] = { expectedWidth = 7, expectedPoints = { 13199.5, 6463, 13199.5, 5506, 13193, 5493, 13185, 5485, 13171.5, 5478.5, 12929, 5478.5 }, hideLabel = true, reference = { index = 382, width = 7, points = { 13199.5, 6463, 13199.5, 5506, 13193, 5493, 13185, 5485, 13171.5, 5478.5, 12929, 5478.5 } } }
    -- #349 Fruitwood Road
    ops[349] = { expectedWidth = 7, expectedPoints = { 13879, 5498.5, 14101, 5498.5 }, hideLabel = true, reference = { index = 383, width = 7, points = { 13879, 5498.5, 14101, 5498.5 } } }
    -- #350 Flower Road
    ops[350] = { expectedWidth = 6, expectedPoints = { 14104, 5422, 14104, 5694.5, 14392.5, 5697.5 }, hideLabel = true, reference = { index = 384, width = 6, points = { 14104, 5422, 14104, 5694.5, 14392.5, 5697.5 } } }
    -- #351 Cedar Dr
    ops[351] = { expectedWidth = 5, expectedPoints = { 14392, 5066, 14362.5, 5095, 14362.5, 5228.5, 14374.5, 5241, 14374.5, 5324, 14392, 5341.5 }, hideLabel = true, reference = { index = 385, width = 5, points = { 14392, 5066, 14362.5, 5095, 14362.5, 5228.5, 14374.5, 5241, 14374.5, 5324, 14392, 5341.5 } } }
    -- #352 Washington Road
    ops[352] = { expectedWidth = 6, expectedPoints = { 13977, 4982, 14124, 4982, 14146, 5004, 14607, 5004 }, hideLabel = true, reference = { index = 386, width = 6, points = { 13977, 4982, 14124, 4982, 14146, 5004, 14607, 5004 } } }
    -- #353 Damon Road
    ops[353] = { expectedWidth = 5, expectedPoints = { 14394.5, 5007, 14395, 5926.5 }, hideLabel = true, reference = { index = 387, width = 5, points = { 14394.5, 5007, 14395, 5926.5 } } }
    -- #354 Ernest Cooper Road
    ops[354] = { expectedWidth = 4, expectedPoints = { 14277, 4855.5, 14277, 5001 }, hideLabel = true, reference = { index = 388, width = 4, points = { 14277, 4855.5, 14277, 5001 } } }
    -- #355 Ernest Cooper Road
    ops[355] = { expectedWidth = 5, expectedPoints = { 14366, 4768.5, 14277, 4857 }, hideLabel = true, reference = { index = 389, width = 5, points = { 14366, 4768.5, 14277, 4857 } } }
    -- #356 Ernest Cooper Road
    ops[356] = { expectedWidth = 4, expectedPoints = { 14535, 4032, 14535, 4071, 14366, 4240, 14366, 4770 }, hideLabel = true, reference = { index = 390, width = 4, points = { 14535, 4032, 14535, 4071, 14366, 4240, 14366, 4770 } } }
    -- #357 Smuggler's Road
    ops[357] = { expectedWidth = 4, expectedPoints = { 14535, 3468, 14535, 4024 }, hideLabel = true, reference = { index = 391, width = 4, points = { 14535, 3468, 14535, 4024 } } }
    -- #358 Moonshine Lane
    ops[358] = { expectedWidth = 4, expectedPoints = { 14537, 3754, 14807, 3754, 14815, 3746, 14815, 3720 }, hideLabel = true, reference = { index = 392, width = 4, points = { 14537, 3754, 14807, 3754, 14815, 3746, 14815, 3720 } } }
    -- #359 Lower River Road
    ops[359] = { expectedWidth = 6, expectedPoints = { 12282, 3458, 12282, 3680, 12288, 3692.5, 12296.5, 3701, 12311, 3708, 12330, 3708, 12330, 3840, 12344, 3868, 12358, 3883, 12390, 3899, 12506, 3899 }, hideLabel = true, reference = { index = 393, width = 6, points = { 12282, 3458, 12282, 3680, 12288, 3692.5, 12296.5, 3701, 12311, 3708, 12330, 3708, 12330, 3840, 12344, 3868, 12358, 3883, 12390, 3899, 12506, 3899 } } }
    -- #360 Farnly Road
    ops[360] = { expectedWidth = 5, expectedPoints = { 12520, 3899.5, 12533, 3899.5, 12540, 3903, 12545, 3908, 12549.5, 3918, 12549.5, 3933, 12571.5, 3977, 12571.5, 4058.5, 12575, 4065, 12578, 4068, 12585, 4071.5, 12681, 4071.5, 12709, 4043.5, 12742, 4043.5, 12763, 4022.5, 12870, 4022.5, 12902, 3990.5, 13421, 3990.5 }, hideLabel = true, reference = { index = 394, width = 5, points = { 12520, 3899.5, 12533, 3899.5, 12540, 3903, 12545, 3908, 12549.5, 3918, 12549.5, 3933, 12571.5, 3977, 12571.5, 4058.5, 12575, 4065, 12578, 4068, 12585, 4071.5, 12681, 4071.5, 12709, 4043.5, 12742, 4043.5, 12763, 4022.5, 12870, 4022.5, 12902, 3990.5, 13421, 3990.5 } } }
    -- #361 Moormen Road
    ops[361] = { expectedWidth = 5, expectedPoints = { 12897, 3674.5, 12916, 3674.5, 12927, 3680, 12933.5, 3686.5, 12938.5, 3697, 12938.5, 3810, 12900.5, 3886, 12900.5, 3988 }, hideLabel = true, reference = { index = 395, width = 5, points = { 12897, 3674.5, 12916, 3674.5, 12927, 3680, 12933.5, 3686.5, 12938.5, 3697, 12938.5, 3810, 12900.5, 3886, 12900.5, 3988 } } }
    -- #362 North Dr
    ops[362] = { expectedWidth = 5, expectedPoints = { 12693, 3919.5, 12771, 3919.5 }, hideLabel = true, reference = { index = 396, width = 5, points = { 12693, 3919.5, 12771, 3919.5 } } }
    -- #363 South Dr
    ops[363] = { expectedWidth = 6, expectedPoints = { 12693, 3960, 12771, 3960 }, hideLabel = true, reference = { index = 397, width = 6, points = { 12693, 3960, 12771, 3960 } } }
    -- #364 Turkey Ave
    ops[364] = { expectedWidth = 5, expectedPoints = { 12773.5, 3922, 12773.5, 4020 }, hideLabel = true, reference = { index = 398, width = 5, points = { 12773.5, 3922, 12773.5, 4020 } } }
    -- #365 Duckling Ave
    ops[365] = { expectedWidth = 5, expectedPoints = { 12690.5, 3922, 12690.5, 4036 }, hideLabel = true, reference = { index = 399, width = 5, points = { 12690.5, 3922, 12690.5, 4036 } } }
    -- #366 Jay St
    ops[366] = { expectedWidth = 5, expectedPoints = { 12690, 3496.5, 12850, 3496.5 }, hideLabel = true, reference = { index = 400, width = 5, points = { 12690, 3496.5, 12850, 3496.5 } } }
    -- #367 Dove St
    ops[367] = { expectedWidth = 8, expectedPoints = { 12936, 3458, 12936, 3528 }, hideLabel = true, reference = { index = 401, width = 8, points = { 12936, 3458, 12936, 3528 } } }
    -- #368 Robin St
    ops[368] = { expectedWidth = 5, expectedPoints = { 12687.5, 3573, 12687.5, 3818.5, 12760, 3818.5 }, hideLabel = true, reference = { index = 402, width = 5, points = { 12687.5, 3573, 12687.5, 3818.5, 12760, 3818.5 } } }
    -- #369 Finch St
    ops[369] = { expectedWidth = 6, expectedPoints = { 12690, 3693, 12891, 3693 }, hideLabel = true, reference = { index = 403, width = 6, points = { 12690, 3693, 12891, 3693 } } }
    -- #370 Cardinal Dr
    ops[370] = { expectedWidth = 5, expectedPoints = { 12757.5, 3573, 12757.5, 3816 }, hideLabel = true, reference = { index = 404, width = 5, points = { 12757.5, 3573, 12757.5, 3816 } } }
    -- #371 Starling St
    ops[371] = { expectedWidth = 6, expectedPoints = { 12685, 3570, 12823, 3570, 12823, 3690 }, hideLabel = true, reference = { index = 405, width = 6, points = { 12685, 3570, 12823, 3570, 12823, 3690 } } }
    -- #372 Bluebird St
    ops[372] = { expectedWidth = 6, expectedPoints = { 12894, 3534, 12894, 3691 }, hideLabel = true, reference = { index = 406, width = 6, points = { 12894, 3534, 12894, 3691 } } }
    -- #373 Crow Court
    ops[373] = { expectedWidth = 6, expectedPoints = { 12898, 3604, 13020, 3604 }, hideLabel = true, reference = { index = 407, width = 6, points = { 12898, 3604, 13020, 3604 } } }
    -- #374 Sparrow St
    ops[374] = { expectedWidth = 6, expectedPoints = { 12793, 3531, 13027, 3531 }, hideLabel = true, reference = { index = 408, width = 6, points = { 12793, 3531, 13027, 3531 } } }
    -- #375 Wren Way
    ops[375] = { expectedWidth = 6, expectedPoints = { 12894, 3471, 12894, 3528 }, hideLabel = true, reference = { index = 409, width = 6, points = { 12894, 3471, 12894, 3528 } } }
    -- #376 Station Road
    ops[376] = { expectedWidth = 7, expectedPoints = { 12520, 4358.5, 12827.5, 4358.5, 12838, 4364, 12844, 4370, 12848, 4380, 12848, 4417 }, hideLabel = true, reference = { index = 410, width = 7, points = { 12520, 4358.5, 12827.5, 4358.5, 12838, 4364, 12844, 4370, 12848, 4380, 12848, 4417 } } }
    -- #377 Tinsley Road
    ops[377] = { expectedWidth = 6, expectedPoints = { 12557, 4637, 12775, 4637, 12840.5, 4669, 12868, 4696, 12900, 4760, 12900, 4996 }, hideLabel = true, reference = { index = 411, width = 6, points = { 12557, 4637, 12775, 4637, 12840.5, 4669, 12868, 4696, 12900, 4760, 12900, 4996 } } }
    -- #378 Oliver Road
    ops[378] = { expectedWidth = 6, expectedPoints = { 12592, 4362, 12586, 4365, 12582, 4369, 12575, 4382, 12575, 4447, 12569, 4458, 12568, 4460, 12560, 4468, 12554, 4480, 12554, 4734 }, hideLabel = true, reference = { index = 412, width = 6, points = { 12592, 4362, 12586, 4365, 12582, 4369, 12575, 4382, 12575, 4447, 12569, 4458, 12568, 4460, 12560, 4468, 12554, 4480, 12554, 4734 } } }
    -- #379 Appletree Lane
    ops[379] = { expectedWidth = 6, expectedPoints = { 12689, 5140, 12699, 5120, 12707, 5112, 12733, 5099, 12787, 5099 }, hideLabel = true, reference = { index = 413, width = 6, points = { 12689, 5140, 12699, 5120, 12707, 5112, 12733, 5099, 12787, 5099 } } }
    -- #380 Knob Creek Road
    ops[380] = { expectedWidth = 6, expectedPoints = { 12978, 5003, 12978, 5101, 13033, 5101, 13033, 5354, 13043, 5364, 13255, 5364, 13265, 5374.5, 13265, 5413.5, 13248, 5430.5 }, hideLabel = true, reference = { index = 414, width = 6, points = { 12978, 5003, 12978, 5101, 13033, 5101, 13033, 5354, 13043, 5364, 13255, 5364, 13265, 5374.5, 13265, 5413.5, 13248, 5430.5 } } }
    -- #381 Ray Road
    ops[381] = { expectedWidth = 6, expectedPoints = { 12837, 5319, 12856, 5300, 12860, 5292, 12860, 5255, 12864, 5247, 12872, 5243, 12921, 5243, 12937, 5227, 12937, 5207, 12948, 5196, 13030, 5196 }, hideLabel = true, reference = { index = 415, width = 6, points = { 12837, 5319, 12856, 5300, 12860, 5292, 12860, 5255, 12864, 5247, 12872, 5243, 12921, 5243, 12937, 5227, 12937, 5207, 12948, 5196, 13030, 5196 } } }
    -- #382 Wagon Road
    ops[382] = { expectedWidth = 7, expectedPoints = { 13203, 5559.5, 13335, 5559.5, 13362, 5573, 13378, 5589, 13390.5, 5616, 13390.5, 5701, 13395, 5710, 13399, 5714, 13410, 5719.5, 13510, 5719.5 }, hideLabel = true, reference = { index = 416, width = 7, points = { 13203, 5559.5, 13335, 5559.5, 13362, 5573, 13378, 5589, 13390.5, 5616, 13390.5, 5701, 13395, 5710, 13399, 5714, 13410, 5719.5, 13510, 5719.5 } } }
    -- #383 Cub Road
    ops[383] = { expectedWidth = 7, expectedPoints = { 13203, 5985.5, 13510, 5985.5 }, hideLabel = true, reference = { index = 417, width = 7, points = { 13203, 5985.5, 13510, 5985.5 } } }
    -- #384 Mullins Road
    ops[384] = { expectedWidth = 6, expectedPoints = { 13125, 5367, 13125, 5475 }, hideLabel = true, reference = { index = 418, width = 6, points = { 13125, 5367, 13125, 5475 } } }
    -- #386 Mill Road
    ops[386] = { expectedWidth = 4, expectedPoints = { 12594, 5766, 12594, 6367, 12602, 6375, 12628, 6375 }, hideLabel = true, reference = { index = 420, width = 4, points = { 12594, 5766, 12594, 6367, 12602, 6375, 12628, 6375 } } }
    -- #387 Valley Station Road
    ops[387] = { expectedWidth = 9, expectedPoints = { 12642, 6375.5, 12791, 6375.5 }, hideLabel = true, reference = { index = 421, width = 9, points = { 12642, 6375.5, 12791, 6375.5 } } }
    -- #389 Salt River Road
    ops[389] = { expectedWidth = 6, expectedPoints = { 12878.5, 6900, 13200, 6900, 13200, 6469 }, hideLabel = true, reference = { index = 423, width = 6, points = { 12878.5, 6900, 13200, 6900, 13200, 6469 } } }
    -- #391 Rockford Lane
    ops[391] = { expectedWidth = 6, expectedPoints = { 12285, 3510, 12477, 3510, 12477, 3621 }, hideLabel = true, reference = { index = 425, width = 6, points = { 12285, 3510, 12477, 3510, 12477, 3621 } } }
    -- #392 W River Road
    ops[392] = { expectedWidth = 8, expectedPoints = { 12258, 1237, 12592, 1237 }, hideLabel = true, reference = { index = 426, width = 8, points = { 12258, 1237, 12592, 1237 } } }
    -- #393 5th St
    ops[393] = { expectedWidth = 10, expectedPoints = { 12157, 1243, 12157, 1721 }, hideLabel = true, reference = { index = 427, width = 10, points = { 12157, 1243, 12157, 1721 } } }
    -- #394 W Liberty St
    ops[394] = { expectedWidth = 10, expectedPoints = { 12162, 1655, 12295, 1655, 12305, 1656, 12592, 1656 }, hideLabel = true, reference = { index = 428, width = 10, points = { 12162, 1655, 12295, 1655, 12305, 1656, 12592, 1656 } } }
    -- #395 Bourbon Way
    ops[395] = { expectedWidth = 10, expectedPoints = { 12295, 1726, 12067, 1726, 12067, 3173 }, hideLabel = true, reference = { index = 429, width = 10, points = { 12295, 1726, 12067, 1726, 12067, 3173 } } }
    -- #396 Waverly St
    ops[396] = { expectedWidth = 6, expectedPoints = { 12072, 3000, 12468, 3000 }, hideLabel = true, reference = { index = 430, width = 6, points = { 12072, 3000, 12468, 3000 } } }
    -- #397 Nelson St
    ops[397] = { expectedWidth = 6, expectedPoints = { 12257, 3003, 12257, 3232, 12282, 3232, 12282, 3442 }, hideLabel = true, reference = { index = 431, width = 6, points = { 12257, 3003, 12257, 3232, 12282, 3232, 12282, 3442 } } }
    -- #398 Oakdale Crescent
    ops[398] = { expectedWidth = 5, expectedPoints = { 12279, 3295.5, 12212.5, 3295.5, 12212.5, 3403.5, 12279, 3403.5 }, hideLabel = true, reference = { index = 432, width = 5, points = { 12279, 3295.5, 12212.5, 3295.5, 12212.5, 3403.5, 12279, 3403.5 } } }
    -- #399 Leafhill Heights
    ops[399] = { expectedWidth = 6, expectedPoints = { 12285, 3324, 12481, 3324 }, hideLabel = true, reference = { index = 433, width = 6, points = { 12285, 3324, 12481, 3324 } } }
    -- #400 Stable Road
    ops[400] = { expectedWidth = 6, expectedPoints = { 12444, 2701.5, 12444, 2719, 12471, 2746, 12471, 3089 }, hideLabel = true, reference = { index = 434, width = 6, points = { 12444, 2701.5, 12444, 2719, 12471, 2746, 12471, 3089 } } }
    -- #401 Chapelmount Downs
    ops[401] = { expectedWidth = 9, expectedPoints = { 12072, 2571.5, 12458, 2571.5, 12458, 2696 }, hideLabel = true, reference = { index = 435, width = 9, points = { 12072, 2571.5, 12458, 2571.5, 12458, 2696 } } }
    -- #402 3rd St
    ops[402] = { expectedWidth = 10, expectedPoints = { 12300, 1357, 12300, 2514, 12506, 2514 }, hideLabel = true, reference = { index = 436, width = 10, points = { 12300, 1357, 12300, 2514, 12506, 2514 } } }
    -- #403 2nd St
    ops[403] = { expectedWidth = 10, expectedPoints = { 12393, 1357, 12393, 2031 }, hideLabel = true, reference = { index = 437, width = 10, points = { 12393, 1357, 12393, 2031 } } }
    -- #404 Broadway Close
    ops[404] = { expectedWidth = 7, expectedPoints = { 12155, 1800.5, 12295, 1800.5 }, hideLabel = true, reference = { index = 438, width = 7, points = { 12155, 1800.5, 12295, 1800.5 } } }
    -- #405 W Broadway St
    ops[405] = { expectedWidth = 10, expectedPoints = { 12305, 1800, 12592, 1800 }, hideLabel = true, reference = { index = 439, width = 10, points = { 12305, 1800, 12592, 1800 } } }
    -- #406 E Broadway St
    ops[406] = { expectedWidth = 10, expectedPoints = { 12607, 1800, 13195, 1800 }, hideLabel = true, reference = { index = 440, width = 10, points = { 12607, 1800, 13195, 1800 } } }
    -- #407 Kilkenny St
    ops[407] = { expectedWidth = 5, expectedPoints = { 12955.5, 1857, 12955.5, 1932.5, 13034.5, 1932.5, 13034.5, 1857 }, hideLabel = true, reference = { index = 441, width = 5, points = { 12955.5, 1857, 12955.5, 1932.5, 13034.5, 1932.5, 13034.5, 1857 } } }
    -- #408 Chicasaw St
    ops[408] = { expectedWidth = 8, expectedPoints = { 12072, 2069, 12295, 2069 }, hideLabel = true, reference = { index = 442, width = 8, points = { 12072, 2069, 12295, 2069 } } }
    -- #409 Wolfe Tone St
    ops[409] = { expectedWidth = 10, expectedPoints = { 12305, 1955, 12500, 1955 }, hideLabel = true, reference = { index = 443, width = 10, points = { 12305, 1955, 12500, 1955 } } }
    -- #410 N 1st St
    ops[410] = { expectedWidth = 15, expectedPoints = { 12599.5, 1241, 12599.5, 2150 }, hideLabel = true, reference = { index = 444, width = 15, points = { 12599.5, 1241, 12599.5, 2150 } } }
    -- #411 Grady St
    ops[411] = { expectedWidth = 5, expectedPoints = { 12607.5, 2100.5, 12898, 2100.5 }, hideLabel = true, reference = { index = 445, width = 5, points = { 12607.5, 2100.5, 12898, 2100.5 } } }
    -- #413 Industry Road
    ops[413] = { expectedWidth = 10, expectedPoints = { 12398, 1574, 12592, 1574 }, hideLabel = true, reference = { index = 447, width = 10, points = { 12398, 1574, 12592, 1574 } } }
    -- #414 Jefferson St
    ops[414] = { expectedWidth = 10, expectedPoints = { 12305, 1500, 12592, 1500 }, hideLabel = true, reference = { index = 448, width = 10, points = { 12305, 1500, 12592, 1500 } } }
    -- #415 Smoky St
    ops[415] = { expectedWidth = 7, expectedPoints = { 12162, 1499.5, 12295, 1499.5 }, hideLabel = true, reference = { index = 449, width = 7, points = { 12162, 1499.5, 12295, 1499.5 } } }
    -- #416 Park Ave
    ops[416] = { expectedWidth = 5, expectedPoints = { 12218, 1537.5, 12258, 1537.5 }, hideLabel = true, reference = { index = 450, width = 5, points = { 12218, 1537.5, 12258, 1537.5 } } }
    -- #417 4th St
    ops[417] = { expectedWidth = 6, expectedPoints = { 12255, 1243, 12255, 1399 }, hideLabel = true, reference = { index = 451, width = 6, points = { 12255, 1243, 12255, 1399 } } }
    -- #418 Jackson St
    ops[418] = { expectedWidth = 10, expectedPoints = { 12295, 1352, 13195, 1352 }, hideLabel = true, reference = { index = 452, width = 10, points = { 12295, 1352, 13195, 1352 } } }
    -- #419 W Main St
    ops[419] = { expectedWidth = 10, expectedPoints = { 12607, 1500, 12897, 1500 }, hideLabel = true, reference = { index = 453, width = 10, points = { 12607, 1500, 12897, 1500 } } }
    -- #420 E Main St
    ops[420] = { expectedWidth = 10, expectedPoints = { 12903, 1500, 13195, 1500 }, hideLabel = true, reference = { index = 454, width = 10, points = { 12903, 1500, 13195, 1500 } } }
    -- #421 E Liberty St
    ops[421] = { expectedWidth = 10, expectedPoints = { 12607, 1656, 13195, 1656 }, hideLabel = true, reference = { index = 455, width = 10, points = { 12607, 1656, 13195, 1656 } } }
    -- #422 E River Road
    ops[422] = { expectedWidth = 8, expectedPoints = { 12607, 1237, 13048, 1237 }, hideLabel = true, reference = { index = 456, width = 8, points = { 12607, 1237, 13048, 1237 } } }
    -- #423 Bruiser Ave
    ops[423] = { expectedWidth = 8, expectedPoints = { 13202, 1265, 13495, 1265 }, hideLabel = true, reference = { index = 457, width = 8, points = { 13202, 1265, 13495, 1265 } } }
    -- #424 Butcher St
    ops[424] = { expectedWidth = 10, expectedPoints = { 13287, 1385, 13495, 1385 }, hideLabel = true, reference = { index = 458, width = 10, points = { 13287, 1385, 13495, 1385 } } }
    -- #425 W Market St
    ops[425] = { expectedWidth = 6, expectedPoints = { 13205, 1904, 13361, 1904, 13361, 1501.5, 13495, 1501.5 }, hideLabel = true, reference = { index = 459, width = 6, points = { 13205, 1904, 13361, 1904, 13361, 1501.5, 13495, 1501.5 } } }
    -- #426 E Market St
    ops[426] = { expectedWidth = 10, expectedPoints = { 13505, 1500, 13646, 1500, 13646, 1797, 13644, 1803, 13644, 1844 }, hideLabel = true, reference = { index = 460, width = 10, points = { 13505, 1500, 13646, 1500, 13646, 1797, 13644, 1803, 13644, 1844 } } }
    -- #427 Goat Race Alley
    ops[427] = { expectedWidth = 6, expectedPoints = { 13364, 1552, 13641, 1552 }, hideLabel = true, reference = { index = 461, width = 6, points = { 13364, 1552, 13641, 1552 } } }
    -- #428 Germantown Road
    ops[428] = { expectedWidth = 6, expectedPoints = { 13483, 1847, 13846, 1847, 13857, 1853, 13860, 1856, 13864, 1865, 13864, 2041, 13879, 2071, 13892, 2084, 13923, 2100, 13992, 2100, 14002, 2105, 14009, 2112, 14013, 2121, 14013, 2260 }, hideLabel = true, reference = { index = 462, width = 6, points = { 13483, 1847, 13846, 1847, 13857, 1853, 13860, 1856, 13864, 1865, 13864, 2041, 13879, 2071, 13892, 2084, 13923, 2100, 13992, 2100, 14002, 2105, 14009, 2112, 14013, 2121, 14013, 2260 } } }
    -- #429 William St
    ops[429] = { expectedWidth = 10, expectedPoints = { 12511, 1955, 13195, 1955 }, hideLabel = true, reference = { index = 463, width = 10, points = { 12511, 1955, 13195, 1955 } } }
    -- #430 St Michael St
    ops[430] = { expectedWidth = 10, expectedPoints = { 13205, 1955, 13506, 1955 }, hideLabel = true, reference = { index = 464, width = 10, points = { 13205, 1955, 13506, 1955 } } }
    -- #431 S Shelby Road
    ops[431] = { expectedWidth = 10, expectedPoints = { 13501, 1960, 13501, 2405 }, hideLabel = true, reference = { index = 465, width = 10, points = { 13501, 1960, 13501, 2405 } } }
    -- #432 N Rogers St
    ops[432] = { expectedWidth = 6, expectedPoints = { 13504, 2864, 13629, 2864 }, hideLabel = true, reference = { index = 466, width = 6, points = { 13504, 2864, 13629, 2864 } } }
    -- #433 S Rogers St
    ops[433] = { expectedWidth = 6, expectedPoints = { 13504, 2951, 13629, 2951 }, hideLabel = true, reference = { index = 467, width = 6, points = { 13504, 2951, 13629, 2951 } } }
    -- #434 Evergreen St
    ops[434] = { expectedWidth = 8, expectedPoints = { 13633, 2706, 13633, 3067 }, hideLabel = true, reference = { index = 468, width = 8, points = { 13633, 2706, 13633, 3067 } } }
    -- #435 Kenwood St
    ops[435] = { expectedWidth = 10, expectedPoints = { 13504, 2701, 13976, 2701 }, hideLabel = true, reference = { index = 469, width = 10, points = { 13504, 2701, 13976, 2701 } } }
    -- #436 McKinley Ave
    ops[436] = { expectedWidth = 6, expectedPoints = { 13636, 2610, 13929, 2610, 13929, 2666 }, hideLabel = true, reference = { index = 470, width = 6, points = { 13636, 2610, 13929, 2610, 13929, 2666 } } }
    -- #437 Southside Dr
    ops[437] = { expectedWidth = 10, expectedPoints = { 13506, 2400, 13959, 2400, 13969, 2405, 13977, 2413, 13981, 2422, 13981, 3442 }, hideLabel = true, reference = { index = 471, width = 10, points = { 13506, 2400, 13959, 2400, 13969, 2405, 13977, 2413, 13981, 2422, 13981, 3442 } } }
    -- #438 Audubon St
    ops[438] = { expectedWidth = 6, expectedPoints = { 13800, 2405, 13800, 2964 }, hideLabel = true, reference = { index = 472, width = 6, points = { 13800, 2405, 13800, 2964 } } }
    -- #439 Eastern Church St
    ops[439] = { expectedWidth = 4, expectedPoints = { 13636, 2570, 13715, 2570, 13715, 2530 }, hideLabel = true, reference = { index = 473, width = 4, points = { 13636, 2570, 13715, 2570, 13715, 2530 } } }
    -- #440 Edgewood Court
    ops[440] = { expectedWidth = 5, expectedPoints = { 14103, 2629.5, 14144, 2629.5 }, hideLabel = true, reference = { index = 474, width = 5, points = { 14103, 2629.5, 14144, 2629.5 } } }
    -- #441 Rosebush Court
    ops[441] = { expectedWidth = 6, expectedPoints = { 14135, 2370, 14192, 2370 }, hideLabel = true, reference = { index = 475, width = 6, points = { 14135, 2370, 14192, 2370 } } }
    -- #442 Scholars Lane
    ops[442] = { expectedWidth = 6, expectedPoints = { 12506, 1357, 12506, 1495 }, hideLabel = true, reference = { index = 476, width = 6, points = { 12506, 1357, 12506, 1495 } } }
    -- #443 Horse St
    ops[443] = { expectedWidth = 10, expectedPoints = { 12506, 1241, 12506, 1347 }, hideLabel = true, reference = { index = 477, width = 10, points = { 12506, 1241, 12506, 1347 } } }
    -- #444 S 1st St
    ops[444] = { expectedWidth = 14, expectedPoints = { 12513, 2509, 12513, 3442 }, hideLabel = true, reference = { index = 478, width = 14, points = { 12513, 2509, 12513, 3442 } } }
    -- #445 W River Road
    ops[445] = { expectedWidth = 10, expectedPoints = { 12152, 1238, 12258, 1238 }, hideLabel = true, reference = { index = 479, width = 10, points = { 12152, 1238, 12258, 1238 } } }
    -- #446 Waverly St
    ops[446] = { expectedWidth = 7, expectedPoints = { 12795, 3000.5, 12474, 3000.5 }, hideLabel = true, reference = { index = 481, width = 7, points = { 12795, 3000.5, 12474, 3000.5 } } }
    -- #447 Waverly St
    ops[447] = { expectedWidth = 8, expectedPoints = { 13410, 3000, 12795, 3000 }, hideLabel = true, reference = { index = 482, width = 8, points = { 13410, 3000, 12795, 3000 } } }
    -- #448 S Shelby Road
    ops[448] = { expectedWidth = 8, expectedPoints = { 13500, 2954, 13500, 2405 }, hideLabel = true, reference = { index = 483, width = 8, points = { 13500, 2954, 13500, 2405 } } }
    -- #449 N Brand St
    ops[449] = { expectedWidth = 5, expectedPoints = { 1642.5, 5775, 1642.5, 5867.5 }, hideLabel = true, reference = { index = 484, width = 5, points = { 1642.5, 5775, 1642.5, 5867.5 } } }
    -- #450 Brandenburg Bypass
    ops[450] = { expectedWidth = 16, expectedPoints = { 2997, 6151, 2727, 6151 }, hideLabel = true, reference = { index = 485, width = 16, points = { 2997, 6151, 2727, 6151 } } }
    -- #451 Brandenburg Bypass
    ops[451] = { expectedWidth = 14, expectedPoints = { 2727, 6151, 2687, 6151, 2663.5, 6161.5, 2647, 6176.5, 2632, 6206.5, 2632, 6417.5, 2619.5, 6444, 2604.5, 6459.5, 2577, 6473, 1874.5, 6473 }, hideLabel = true, reference = { index = 486, width = 14, points = { 2727, 6151, 2687, 6151, 2663.5, 6161.5, 2647, 6176.5, 2632, 6206.5, 2632, 6417.5, 2619.5, 6444, 2604.5, 6459.5, 2577, 6473, 1874.5, 6473 } } }
    -- #452 KY-60
    ops[452] = { expectedWidth = 16, expectedPoints = { 2997, 6151, 3460.5, 6151, 3495.5, 6134, 3507.5, 6122, 3524, 6089, 3524, 6047, 3537, 6021.5, 3547, 6011.5, 3570, 6000, 3699, 6000, 3720.5, 6010.5, 3741.5, 6032, 3755, 6058.5 }, hideLabel = true, reference = { index = 487, width = 16, points = { 2997, 6151, 3460.5, 6151, 3495.5, 6134, 3507.5, 6122, 3524, 6089, 3524, 6047, 3537, 6021.5, 3547, 6011.5, 3570, 6000, 3699, 6000, 3720.5, 6010.5, 3741.5, 6032, 3755, 6058.5 } } }
    -- #453 KY-60
    ops[453] = { expectedWidth = 17, expectedPoints = { 3753.5, 8717, 3829, 8868, 4206, 9245, 4338.5, 9510 }, hideLabel = true, reference = { index = 488, width = 17, points = { 3753.5, 8717, 3829, 8868, 4206, 9245, 4338.5, 9510 } } }
    -- #454 KY-60
    ops[454] = { expectedWidth = 16, expectedPoints = { 3754, 6055, 3754, 8721 }, hideLabel = true, reference = { index = 489, width = 16, points = { 3754, 6055, 3754, 8721 } } }
    -- #457 Brandenburg Bypass
    ops[457] = { expectedWidth = 10, expectedPoints = { 1501, 6080, 1502.5, 6085, 1540.5, 6161.5, 1827, 6448, 1874.5, 6473 }, hideLabel = true, reference = { index = 491, width = 10, points = { 1501, 6080, 1502.5, 6085, 1540.5, 6161.5, 1827, 6448, 1874.5, 6473 } } }
    -- #458 KY-144
    ops[458] = { expectedWidth = 9, expectedPoints = { 4200, 9895.5, 4330, 9895.5 }, hideLabel = true, reference = { index = 492, width = 9, points = { 4200, 9895.5, 4330, 9895.5 } } }
    -- #459 KY-144
    ops[459] = { expectedWidth = 8, expectedPoints = { 1528, 9895, 4200, 9895 }, hideLabel = true, reference = { index = 493, width = 8, points = { 1528, 9895, 4200, 9895 } } }
    -- #460 KY-60
    ops[460] = { expectedWidth = 15, expectedPoints = { 6000, 11204.5, 12900, 11204.5 }, hideLabel = true, reference = { index = 494, width = 15, points = { 6000, 11204.5, 12900, 11204.5 } } }
    -- #461 KY-60
    ops[461] = { expectedWidth = 16, expectedPoints = { 5296.5, 11204, 6000, 11204 }, hideLabel = true, reference = { index = 495, width = 16, points = { 5296.5, 11204, 6000, 11204 } } }
    -- #462 KY-60
    ops[462] = { expectedWidth = 17, expectedPoints = { 4960, 11034.5, 5300, 11204.5 }, hideLabel = true, reference = { index = 496, width = 17, points = { 4960, 11034.5, 5300, 11204.5 } } }
    -- #463 KY-60
    ops[463] = { expectedWidth = 16, expectedPoints = { 4569.5, 10644, 4962, 11036.5 }, hideLabel = true, reference = { index = 497, width = 16, points = { 4569.5, 10644, 4962, 11036.5 } } }
    -- #464 KY-60
    ops[464] = { expectedWidth = 17, expectedPoints = { 4338, 10179, 4571.5, 10646 }, hideLabel = true, reference = { index = 498, width = 17, points = { 4338, 10179, 4571.5, 10646 } } }
    -- #465 KY-60
    ops[465] = { expectedWidth = 16, expectedPoints = { 4338, 9506, 4338, 10183 }, hideLabel = true, reference = { index = 499, width = 16, points = { 4338, 9506, 4338, 10183 } } }
    -- #466 KY-163
    ops[466] = { expectedWidth = 15, expectedPoints = { 10599, 12324.5, 11221.5, 12324.5, 11221.5, 11776.5, 11671.5, 11776.5, 11671.5, 11496.5, 12021.5, 11496.5, 12021.5, 11386.5, 12591.5, 11386.5, 12591.5, 11212 }, hideLabel = true, reference = { index = 500, width = 15, points = { 10599, 12324.5, 11221.5, 12324.5, 11221.5, 11776.5, 11671.5, 11776.5, 11671.5, 11496.5, 12021.5, 11496.5, 12021.5, 11386.5, 12591.5, 11386.5, 12591.5, 11212 } } }
    -- #467 KY-79
    ops[467] = { expectedWidth = 8, expectedPoints = { 832, 10691, 832, 13305.5 }, hideLabel = true, reference = { index = 501, width = 8, points = { 832, 10691, 832, 13305.5 } } }
    -- #468 KY-79
    ops[468] = { expectedWidth = 6, expectedPoints = { 950, 13446, 988, 13465 }, hideLabel = true, reference = { index = 502, width = 6, points = { 950, 13446, 988, 13465 } } }
    -- #469 KY-79
    ops[469] = { expectedWidth = 5, expectedPoints = { 852.5, 13348.5, 950.5, 13446.5 }, hideLabel = true, reference = { index = 503, width = 5, points = { 852.5, 13348.5, 950.5, 13446.5 } } }
    -- #470 KY-79
    ops[470] = { expectedWidth = 6, expectedPoints = { 831, 13304, 853.5, 13349 }, hideLabel = true, reference = { index = 504, width = 6, points = { 831, 13304, 853.5, 13349 } } }
    -- #471 KY-79
    ops[471] = { expectedWidth = 8, expectedPoints = { 987, 13464, 1099, 13464 }, hideLabel = true, reference = { index = 505, width = 8, points = { 987, 13464, 1099, 13464 } } }
    -- #472 KY-79
    ops[472] = { expectedWidth = 8, expectedPoints = { 1902, 14838.5, 1920, 14829.5, 2250.5, 14499 }, hideLabel = true, reference = { index = 506, width = 8, points = { 1902, 14838.5, 1920, 14829.5, 2250.5, 14499 } } }
    -- #473 KY-79
    ops[473] = { expectedWidth = 6, expectedPoints = { 1500, 14838, 1903.5, 14838 }, hideLabel = true, reference = { index = 507, width = 6, points = { 1500, 14838, 1903.5, 14838 } } }
    -- #474 KY-79
    ops[474] = { expectedWidth = 6, expectedPoints = { 1099, 13460, 1099, 13654, 1091.5, 13669, 952.5, 13808, 943, 13827, 943, 14807.5, 947, 14816, 965, 14834, 976, 14839, 1500, 14839 }, hideLabel = true, reference = { index = 508, width = 6, points = { 1099, 13460, 1099, 13654, 1091.5, 13669, 952.5, 13808, 943, 13827, 943, 14807.5, 947, 14816, 965, 14834, 976, 14839, 1500, 14839 } } }
    -- #475 KY-79
    ops[475] = { expectedWidth = 8, expectedPoints = { 8268, 14116, 10585, 14116 }, hideLabel = true, reference = { index = 509, width = 8, points = { 8268, 14116, 10585, 14116 } } }
    -- #476 KY-79
    ops[476] = { expectedWidth = 7, expectedPoints = { 8217.5, 14141, 8269, 14115 }, hideLabel = true, reference = { index = 510, width = 7, points = { 8217.5, 14141, 8269, 14115 } } }
    -- #477 KY-79
    ops[477] = { expectedWidth = 8, expectedPoints = { 2593, 14501, 5309, 14501, 5387, 14462, 5484.5, 14364.5, 5514.5, 14349, 6259, 14349, 6307.5, 14373.5, 6493, 14558.5, 6592, 14607, 6988, 14607, 7003.5, 14599.5, 7091.5, 14511.5, 7112.5, 14501, 7834, 14501, 7881, 14477.5, 8217.5, 14141 }, hideLabel = true, reference = { index = 511, width = 8, points = { 2593, 14501, 5309, 14501, 5387, 14462, 5484.5, 14364.5, 5514.5, 14349, 6259, 14349, 6307.5, 14373.5, 6493, 14558.5, 6592, 14607, 6988, 14607, 7003.5, 14599.5, 7091.5, 14511.5, 7112.5, 14501, 7834, 14501, 7881, 14477.5, 8217.5, 14141 } } }
    -- #478 KY-79
    ops[478] = { expectedWidth = 10, expectedPoints = { 2248.5, 14501, 2593, 14501 }, hideLabel = true, reference = { index = 512, width = 10, points = { 2248.5, 14501, 2593, 14501 } } }
    -- #479 KY-79
    ops[479] = { expectedWidth = 7, expectedPoints = { 539, 9295, 566, 9241, 1054, 8753, 1630, 8465, 1810.5, 8284.5, 1874, 8158, 1874, 8134.5 }, hideLabel = true, reference = { index = 513, width = 7, points = { 539, 9295, 566, 9241, 1054, 8753, 1630, 8465, 1810.5, 8284.5, 1874, 8158, 1874, 8134.5 } } }
    -- #480 KY-163
    ops[480] = { expectedWidth = 8, expectedPoints = { 4274, 6106, 4388, 6106, 4472, 6064, 4907, 6064, 4931, 6052, 4942, 6041, 4955, 6014.5, 4955, 5876, 4965.5, 5856.5, 4974.5, 5847.5, 4997, 5836, 5454, 5836 }, hideLabel = true, reference = { index = 514, width = 8, points = { 4274, 6106, 4388, 6106, 4472, 6064, 4907, 6064, 4931, 6052, 4942, 6041, 4955, 6014.5, 4955, 5876, 4965.5, 5856.5, 4974.5, 5847.5, 4997, 5836, 5454, 5836 } } }
    -- #481 KY-163
    ops[481] = { expectedWidth = 7, expectedPoints = { 4147, 5999, 4184.5, 6017.5, 4201, 6034, 4219, 6070, 4236, 6087, 4275, 6106.5 }, hideLabel = true, reference = { index = 515, width = 7, points = { 4147, 5999, 4184.5, 6017.5, 4201, 6034, 4219, 6070, 4236, 6087, 4275, 6106.5 } } }
    -- #482 KY-163
    ops[482] = { expectedWidth = 8, expectedPoints = { 3763, 6086, 3784.5, 6044, 3804, 6025, 3855, 6000, 4149, 6000 }, hideLabel = true, reference = { index = 516, width = 8, points = { 3763, 6086, 3784.5, 6044, 3804, 6025, 3855, 6000, 4149, 6000 } } }
    -- #487 Dixie Highway (Route 31W)
    ops[487] = { expectedWidth = 13, expectedPoints = { 10590.5, 8861, 10618, 8806, 10638, 8786, 10684, 8763 }, hideLabel = true, reference = { index = 520, width = 13, points = { 10590.5, 8861, 10618, 8806, 10638, 8786, 10684, 8763 } } }
    -- #490 Dixie Highway (Route 31W)
    ops[490] = { expectedWidth = 14, expectedPoints = { 12681.5, 4862.5, 12666, 4831, 12650, 4815, 12620.5, 4800, 12566, 4800, 12546, 4790, 12524.5, 4768.5, 12513, 4746, 12513, 3458 }, hideLabel = true, reference = { index = 522, width = 14, points = { 12681.5, 4862.5, 12666, 4831, 12650, 4815, 12620.5, 4800, 12566, 4800, 12546, 4790, 12524.5, 4768.5, 12513, 4746, 12513, 3458 } } }
    -- #493 Stringtown Road
    ops[493] = { expectedWidth = 7, expectedPoints = { 910, 10198, 962.5, 10303 }, hideLabel = true, reference = { index = 524, width = 7, points = { 910, 10198, 962.5, 10303 } } }
    -- #494 Broadway St
    ops[494] = { expectedWidth = 5, expectedPoints = { 2404.5, 6288, 2404.5, 6343, 2430.5, 6396, 2430.5, 6437 }, hideLabel = true, reference = { index = 525, width = 5, points = { 2404.5, 6288, 2404.5, 6343, 2430.5, 6396, 2430.5, 6437 } } }
    -- #495 Broadway St
    ops[495] = { expectedWidth = 6, expectedPoints = { 2405, 6002, 2405, 6288 }, hideLabel = true, reference = { index = 526, width = 6, points = { 2405, 6002, 2405, 6288 } } }
    -- #496 Old State Road
    ops[496] = { expectedWidth = 6, expectedPoints = { 1967, 6480, 1967, 6888.5 }, hideLabel = true, reference = { index = 527, width = 6, points = { 1967, 6480, 1967, 6888.5 } } }
    -- #497 Old State Road
    ops[497] = { expectedWidth = 6, expectedPoints = { 1975, 6480, 1975, 6888.5 }, hideLabel = true, reference = { index = 528, width = 6, points = { 1975, 6480, 1975, 6888.5 } } }
    -- #498 KY-79
    ops[498] = { expectedWidth = 6, expectedPoints = { 1967, 6888.5, 1967, 7420.5, 1870, 7614, 1870, 8125, 1874, 8135 }, hideLabel = true, reference = { index = 529, width = 6, points = { 1967, 6888.5, 1967, 7420.5, 1870, 7614, 1870, 8125, 1874, 8135 } } }
    -- #499 KY-79
    ops[499] = { expectedWidth = 6, expectedPoints = { 1975, 6888, 1975, 7425.5, 1878, 7619, 1878, 8126, 1874, 8135 }, hideLabel = true, reference = { index = 530, width = 6, points = { 1975, 6888, 1975, 7425.5, 1878, 7619, 1878, 8126, 1874, 8135 } } }
    -- #500 Mainslick Road
    ops[500] = { expectedWidth = 8, expectedPoints = { 12936, 3004, 12936, 3442 }, hideLabel = true, reference = { index = 531, width = 8, points = { 12936, 3004, 12936, 3442 } } }
    -- #501 KY-1394
    ops[501] = { expectedWidth = 6, expectedPoints = { 12067, 3173, 12072, 3180, 12072, 3302, 12104, 3365.5, 12143, 3404.5, 12224, 3445, 12932, 3445 }, hideLabel = true, reference = { index = 532, width = 6, points = { 12067, 3173, 12072, 3180, 12072, 3302, 12104, 3365.5, 12143, 3404.5, 12224, 3445, 12932, 3445 } } }
    -- #502 KY-1394
    ops[502] = { expectedWidth = 6, expectedPoints = { 12067, 3173, 12062, 3180, 12062, 3301, 12095.5, 3368, 12141, 3413.5, 12224, 3455, 12932, 3455 }, hideLabel = true, reference = { index = 533, width = 6, points = { 12067, 3173, 12062, 3180, 12062, 3301, 12095.5, 3368, 12141, 3413.5, 12224, 3455, 12932, 3455 } } }
    -- #503 KY-841
    ops[503] = { expectedWidth = 6, expectedPoints = { 12940, 3445, 15144.5, 3445, 15162, 3436, 15241, 3357, 15304.5, 3325, 15898, 3325 }, hideLabel = true, reference = { index = 534, width = 6, points = { 12940, 3445, 15144.5, 3445, 15162, 3436, 15241, 3357, 15304.5, 3325, 15898, 3325 } } }
    -- #504 KY-841
    ops[504] = { expectedWidth = 6, expectedPoints = { 12940.5, 3455, 15137, 3455, 15140.5, 3455, 15152.5, 3455, 15170, 3446, 15247.5, 3367.5, 15313, 3335, 15898, 3335 }, hideLabel = true, reference = { index = 535, width = 6, points = { 12940.5, 3455, 15137, 3455, 15140.5, 3455, 15152.5, 3455, 15170, 3446, 15247.5, 3367.5, 15313, 3335, 15898, 3335 } } }
    -- #505 Flower Road
    ops[505] = { expectedWidth = 5, expectedPoints = { 14145.5, 5005.5, 14145.5, 5383.5, 14104, 5383.5, 14104, 5422 }, hideLabel = true, reference = { index = 536, width = 5, points = { 14145.5, 5005.5, 14145.5, 5383.5, 14104, 5383.5, 14104, 5422 } } }
    -- #507 Harley Chase Road
    ops[507] = { expectedWidth = 8, expectedPoints = { 7800, 9793, 7800, 10609, 7805, 10619.5, 7810.5, 10625, 7821, 10630, 8096, 10630 }, hideLabel = true, reference = { index = 538, width = 8, points = { 7800, 9793, 7800, 10609, 7805, 10619.5, 7810.5, 10625, 7821, 10630, 8096, 10630 } } }
    -- #508 Flaherty Road
    ops[508] = { expectedWidth = 5, expectedPoints = { 8313.5, 10063, 8313.5, 10213.5, 8231.5, 10295.5, 8231.5, 10471.5, 8226, 10483, 8222, 10487, 8211, 10492.5, 8123.5, 10492.5, 8112.5, 10497.5, 8108.5, 10501.5, 8100, 10517.5 }, hideLabel = true, reference = { index = 539, width = 5, points = { 8313.5, 10063, 8313.5, 10213.5, 8231.5, 10295.5, 8231.5, 10471.5, 8226, 10483, 8222, 10487, 8211, 10492.5, 8123.5, 10492.5, 8112.5, 10497.5, 8108.5, 10501.5, 8100, 10517.5 } } }
    -- #509 Flaherty Road
    ops[509] = { expectedWidth = 8, expectedPoints = { 8100, 10494, 8100, 11118, 8106, 11124.5, 8106, 11197 }, hideLabel = true, reference = { index = 540, width = 8, points = { 8100, 10494, 8100, 11118, 8106, 11124.5, 8106, 11197 } } }
    -- #510 Shack Lane
    ops[510] = { expectedWidth = 5, expectedPoints = { 7804, 10421.5, 7977.5, 10421.5, 7994, 10418, 8002, 10410, 8004, 10402.5, 8004, 10260.5 }, hideLabel = true, reference = { index = 541, width = 5, points = { 7804, 10421.5, 7977.5, 10421.5, 7994, 10418, 8002, 10410, 8004, 10402.5, 8004, 10260.5 } } }
    -- #511 Crooked Eye Road
    ops[511] = { expectedWidth = 5, expectedPoints = { 7796, 10400.5, 7570.5, 10400.5, 7528.5, 10442.5, 7397.5, 10442.5, 7397.5, 10846.5 }, hideLabel = true, reference = { index = 542, width = 5, points = { 7796, 10400.5, 7570.5, 10400.5, 7528.5, 10442.5, 7397.5, 10442.5, 7397.5, 10846.5 } } }
    -- #512 Deer Trail Road
    ops[512] = { expectedWidth = 5, expectedPoints = { 6295.5, 11197, 6295.5, 10594, 6394.5, 10494.5, 7395, 10494.5 }, hideLabel = true, reference = { index = 543, width = 5, points = { 6295.5, 11197, 6295.5, 10594, 6394.5, 10494.5, 7395, 10494.5 } } }
    -- #513 Hill St
    ops[513] = { expectedWidth = 6, expectedPoints = { 2195, 6003, 2195, 6437 }, hideLabel = true, reference = { index = 544, width = 6, points = { 2195, 6003, 2195, 6437 } } }
    -- #514 Forrest Ave
    ops[514] = { expectedWidth = 5, expectedPoints = { 3417, 11026.5, 3562, 11026.5 }, hideLabel = true, reference = { index = 545, width = 5, points = { 3417, 11026.5, 3562, 11026.5 } } }
    -- #515 Farmhouse Lane
    ops[515] = { expectedWidth = 5, expectedPoints = { 3674, 8556.5, 3726, 8556.5 }, hideLabel = true, reference = { index = 546, width = 5, points = { 3674, 8556.5, 3726, 8556.5 } } }
    -- #516 Deerhead Road
    ops[516] = { expectedWidth = 6, expectedPoints = { 3762, 8451, 3827.5, 8451, 3878, 8501, 3885, 8516, 3885, 8598, 3892, 8611, 3920, 8639, 3935, 8646, 3966, 8646, 3981, 8654, 3993, 8666, 4000, 8680, 4000, 8828.5, 4065, 8893, 4212, 8893, 4212, 9193.5, 4189.5, 9216 }, hideLabel = true, reference = { index = 547, width = 6, points = { 3762, 8451, 3827.5, 8451, 3878, 8501, 3885, 8516, 3885, 8598, 3892, 8611, 3920, 8639, 3935, 8646, 3966, 8646, 3981, 8654, 3993, 8666, 4000, 8680, 4000, 8828.5, 4065, 8893, 4212, 8893, 4212, 9193.5, 4189.5, 9216 } } }
    -- #517 Dutch Lane
    ops[517] = { expectedWidth = 5, expectedPoints = { 4229.5, 9738, 4209.5, 9748.5, 4198, 9759.5, 4192, 9767, 4174.5, 9799, 4174.5, 9891 }, hideLabel = true, reference = { index = 548, width = 5, points = { 4229.5, 9738, 4209.5, 9748.5, 4198, 9759.5, 4192, 9767, 4174.5, 9799, 4174.5, 9891 } } }
    -- #518 Piers Av
    ops[518] = { expectedWidth = 8, expectedPoints = { 10093, 12769, 10171, 12769, 10171, 12829 }, hideLabel = true, reference = { index = 549, width = 8, points = { 10093, 12769, 10171, 12769, 10171, 12829 } } }
    -- #519 Folger St
    ops[519] = { expectedWidth = 8, expectedPoints = { 9870, 12697, 10155, 12697, 10155, 12600 }, hideLabel = true, reference = { index = 550, width = 8, points = { 9870, 12697, 10155, 12697, 10155, 12600 } } }
    -- #520 Adams Road
    ops[520] = { expectedWidth = 7, expectedPoints = { 9866.5, 12612, 9866.5, 12891 }, hideLabel = true, reference = { index = 551, width = 7, points = { 9866.5, 12612, 9866.5, 12891 } } }
    -- #521 Patton St
    ops[521] = { expectedWidth = 8, expectedPoints = { 10364, 12332, 10364, 12829 }, hideLabel = true, reference = { index = 552, width = 8, points = { 10364, 12332, 10364, 12829 } } }
    -- #522 MacArthur St
    ops[522] = { expectedWidth = 7, expectedPoints = { 9804.5, 12614, 9804.5, 13137 }, hideLabel = true, reference = { index = 553, width = 7, points = { 9804.5, 12614, 9804.5, 13137 } } }
    -- #523 Westmoore St
    ops[523] = { expectedWidth = 8, expectedPoints = { 9801, 13141, 10057, 13141 }, hideLabel = true, reference = { index = 554, width = 8, points = { 9801, 13141, 10057, 13141 } } }
    -- #524 Eisenhower St
    ops[524] = { expectedWidth = 8, expectedPoints = { 10049, 12833, 10368, 12833 }, hideLabel = true, reference = { index = 555, width = 8, points = { 10049, 12833, 10368, 12833 } } }
    -- #525 Lafayette St
    ops[525] = { expectedWidth = 7, expectedPoints = { 10368, 12681.5, 10470, 12681.5 }, hideLabel = true, reference = { index = 556, width = 7, points = { 10368, 12681.5, 10470, 12681.5 } } }
    -- #526 Putnam St
    ops[526] = { expectedWidth = 8, expectedPoints = { 10368, 12743, 10491, 12743 }, hideLabel = true, reference = { index = 557, width = 8, points = { 10368, 12743, 10491, 12743 } } }
    -- #527 Montgomery Dr
    ops[527] = { expectedWidth = 7, expectedPoints = { 10368, 12804.5, 10500, 12804.5 }, hideLabel = true, reference = { index = 558, width = 7, points = { 10368, 12804.5, 10500, 12804.5 } } }
    -- #528 Greene St
    ops[528] = { expectedWidth = 8, expectedPoints = { 10237, 12624, 10237, 12829 }, hideLabel = true, reference = { index = 559, width = 8, points = { 10237, 12624, 10237, 12829 } } }
    -- #529 Lincoln Av
    ops[529] = { expectedWidth = 8, expectedPoints = { 10053, 12837, 10053, 13137 }, hideLabel = true, reference = { index = 560, width = 8, points = { 10053, 12837, 10053, 13137 } } }
    -- #530 Grant St
    ops[530] = { expectedWidth = 7, expectedPoints = { 10241, 12681.5, 10360, 12681.5 }, hideLabel = true, reference = { index = 561, width = 7, points = { 10241, 12681.5, 10360, 12681.5 } } }
    -- #531 Gettysburg Dr
    ops[531] = { expectedWidth = 8, expectedPoints = { 10241, 12743, 10360, 12743 }, hideLabel = true, reference = { index = 562, width = 8, points = { 10241, 12743, 10360, 12743 } } }
    -- #532 Yorktown St
    ops[532] = { expectedWidth = 8, expectedPoints = { 9808, 12895, 10049, 12895 }, hideLabel = true, reference = { index = 563, width = 8, points = { 9808, 12895, 10049, 12895 } } }
    -- #533 Knox St
    ops[533] = { expectedWidth = 8, expectedPoints = { 10159, 12620, 10360, 12620 }, hideLabel = true, reference = { index = 564, width = 8, points = { 10159, 12620, 10360, 12620 } } }
    -- #534 Nelson Dr
    ops[534] = { expectedWidth = 8, expectedPoints = { 10089, 12701, 10089, 12829 }, hideLabel = true, reference = { index = 565, width = 8, points = { 10089, 12701, 10089, 12829 } } }
    -- #535 Sherman St
    ops[535] = { expectedWidth = 8, expectedPoints = { 9991, 12701, 9991, 13137 }, hideLabel = true, reference = { index = 566, width = 8, points = { 9991, 12701, 9991, 13137 } } }
    -- #536 Bradley St
    ops[536] = { expectedWidth = 7, expectedPoints = { 9928.5, 12979, 9928.5, 13002.5, 9928.5, 13137 }, hideLabel = true, reference = { index = 567, width = 7, points = { 9928.5, 12979, 9928.5, 13002.5, 9928.5, 13137 } } }
    -- #537 Runner St
    ops[537] = { expectedWidth = 7, expectedPoints = { 9864.5, 12948, 9864.5, 13137 }, hideLabel = true, reference = { index = 568, width = 7, points = { 9864.5, 12948, 9864.5, 13137 } } }
    -- #538 Churchill St
    ops[538] = { expectedWidth = 7, expectedPoints = { 9868, 12975.5, 9987, 12975.5 }, hideLabel = true, reference = { index = 569, width = 7, points = { 9868, 12975.5, 9987, 12975.5 } } }
    -- #539 Saratoga Way
    ops[539] = { expectedWidth = 6, expectedPoints = { 9836.5, 12618, 9836, 12849 }, hideLabel = true, reference = { index = 570, width = 6, points = { 9836.5, 12618, 9836, 12849 } } }
    -- #540 Potomac Way
    ops[540] = { expectedWidth = 5, expectedPoints = { 9835.5, 12949, 9835.5, 13123 }, hideLabel = true, reference = { index = 571, width = 5, points = { 9835.5, 12949, 9835.5, 13123 } } }
    -- #541 Bugle St
    ops[541] = { expectedWidth = 6, expectedPoints = { 9808, 12663, 9863, 12663 }, hideLabel = true, reference = { index = 572, width = 6, points = { 9808, 12663, 9863, 12663 } } }
    -- #542 Gates St
    ops[542] = { expectedWidth = 6, expectedPoints = { 9808, 12760, 9826.5, 12760, 9863, 12760 }, hideLabel = true, reference = { index = 573, width = 6, points = { 9808, 12760, 9826.5, 12760, 9863, 12760 } } }
    -- #543 Old Lane
    ops[543] = { expectedWidth = 7, expectedPoints = { 9808, 13038.5, 9861, 13038.5 }, hideLabel = true, reference = { index = 574, width = 7, points = { 9808, 13038.5, 9861, 13038.5 } } }
    -- #544 March Ridge Way
    ops[544] = { expectedWidth = 7, expectedPoints = { 9928.5, 12701, 9928.5, 12891 }, hideLabel = true, reference = { index = 575, width = 7, points = { 9928.5, 12701, 9928.5, 12891 } } }
    -- #545 Frank Road
    ops[545] = { expectedWidth = 9, expectedPoints = { 11531.5, 8771, 11531.5, 8864, 11531.5, 8877.5, 11522.5, 8887.5 }, hideLabel = true, reference = { index = 576, width = 9, points = { 11531.5, 8771, 11531.5, 8864, 11531.5, 8877.5, 11522.5, 8887.5 } } }
    -- #546 Frank Road
    ops[546] = { expectedWidth = 6, expectedPoints = { 11525, 8884.5, 11525, 8965 }, hideLabel = true, reference = { index = 577, width = 6, points = { 11525, 8884.5, 11525, 8965 } } }
    -- #547 Summer Rest Lane
    ops[547] = { expectedWidth = 6, expectedPoints = { 11523, 8882, 11466, 8882, 11466, 8943, 11522, 8943 }, hideLabel = true, reference = { index = 578, width = 6, points = { 11523, 8882, 11466, 8882, 11466, 8943, 11522, 8943 } } }
    -- #548 Dixie Lane
    ops[548] = { expectedWidth = 6, expectedPoints = { 11528, 8905, 11761, 8905, 11761, 8852 }, hideLabel = true, reference = { index = 579, width = 6, points = { 11528, 8905, 11761, 8905, 11761, 8852 } } }
    -- #549 Forest View Lane
    ops[549] = { expectedWidth = 5, expectedPoints = { 11626.5, 8743.5, 11650.5, 8766.5, 11676, 8766.5, 11680.5, 8771.5, 11681, 8808.5, 11739, 8808.5 }, hideLabel = true, reference = { index = 580, width = 5, points = { 11626.5, 8743.5, 11650.5, 8766.5, 11676, 8766.5, 11680.5, 8771.5, 11681, 8808.5, 11739, 8808.5 } } }
    -- #550 Dixie Loop S St
    ops[550] = { expectedWidth = 5, expectedPoints = { 11741.5, 8797, 11741.5, 8847 }, hideLabel = true, reference = { index = 581, width = 5, points = { 11741.5, 8797, 11741.5, 8847 } } }
    -- #551 Dixie Loop S St
    ops[551] = { expectedWidth = 5, expectedPoints = { 11739, 8849.5, 11854, 8849.5 }, hideLabel = true, reference = { index = 582, width = 5, points = { 11739, 8849.5, 11854, 8849.5 } } }
    -- #552 Dixie Loop S St
    ops[552] = { expectedWidth = 6, expectedPoints = { 11851, 8847, 11851, 8812.5, 11851, 8797 }, hideLabel = true, reference = { index = 583, width = 6, points = { 11851, 8847, 11851, 8812.5, 11851, 8797 } } }
    -- #553 Dixie Loop N St
    ops[553] = { expectedWidth = 6, expectedPoints = { 11854, 8794, 11748, 8794, 11739, 8794 }, hideLabel = true, reference = { index = 584, width = 6, points = { 11854, 8794, 11748, 8794, 11739, 8794 } } }
    -- #554 Saltlick Lane
    ops[554] = { expectedWidth = 6, expectedPoints = { 8449, 8566, 8449.5, 8620, 8569, 8620 }, hideLabel = true, reference = { index = 585, width = 6, points = { 8449, 8566, 8449.5, 8620, 8569, 8620 } } }
    -- #555 Vernon Road
    ops[555] = { expectedWidth = 7, expectedPoints = { 8038.5, 9294, 8038.5, 9242.5, 8038.5, 9170, 8044.5, 9156.5, 8050.5, 9151.5, 8062.5, 9145.5, 8194, 9145.5 }, hideLabel = true, reference = { index = 586, width = 7, points = { 8038.5, 9294, 8038.5, 9242.5, 8038.5, 9170, 8044.5, 9156.5, 8050.5, 9151.5, 8062.5, 9145.5, 8194, 9145.5 } } }
    -- #556 Lumber Lane
    ops[556] = { expectedWidth = 4, expectedPoints = { 7875, 8715, 7972, 8715 }, hideLabel = true, reference = { index = 587, width = 4, points = { 7875, 8715, 7972, 8715 } } }
    -- #557 Riverside Link Road
    ops[557] = { expectedWidth = 8, expectedPoints = { 8644.5, 8557.5, 8644, 8388.5, 8646, 8386.5, 8646, 8338, 8646, 8132 }, hideLabel = true, reference = { index = 588, width = 8, points = { 8644.5, 8557.5, 8644, 8388.5, 8646, 8386.5, 8646, 8338, 8646, 8132 } } }
    -- #558 Stanley Road
    ops[558] = { expectedWidth = 6, expectedPoints = { 6862, 7544, 6862, 7800 }, hideLabel = true, reference = { index = 589, width = 6, points = { 6862, 7544, 6862, 7800 } } }
    -- #559 Merryman Road
    ops[559] = { expectedWidth = 6, expectedPoints = { 6741, 7260, 6839.5, 7260, 6928, 7260 }, hideLabel = true, reference = { index = 590, width = 6, points = { 6741, 7260, 6839.5, 7260, 6928, 7260 } } }
    -- #560 Lakeshore Parkway
    ops[560] = { expectedWidth = 8, expectedPoints = { 5659.5, 6764.5, 5659, 6742.5, 5665.5, 6730, 5673, 6722, 5687.5, 6714.5, 5793.5, 6714.5, 5806.5, 6708.5, 5814, 6694, 5814.5, 6553, 5804.5, 6533.5, 5793.5, 6521.5, 5770.5, 6510, 5683, 6510, 5666, 6502.5, 5654, 6490, 5646, 6474.5, 5646, 6385, 5739.5, 6385, 5745, 6389.5, 5745, 6393 }, hideLabel = true, reference = { index = 591, width = 8, points = { 5659.5, 6764.5, 5659, 6742.5, 5665.5, 6730, 5673, 6722, 5687.5, 6714.5, 5793.5, 6714.5, 5806.5, 6708.5, 5814, 6694, 5814.5, 6553, 5804.5, 6533.5, 5793.5, 6521.5, 5770.5, 6510, 5683, 6510, 5666, 6502.5, 5654, 6490, 5646, 6474.5, 5646, 6385, 5739.5, 6385, 5745, 6389.5, 5745, 6393 } } }
    -- #561 Tim Cain Road
    ops[561] = { expectedWidth = 6, expectedPoints = { 5779, 5832, 5779, 5713 }, hideLabel = true, reference = { index = 592, width = 6, points = { 5779, 5832, 5779, 5713 } } }
    -- #562 Sawyer Lane
    ops[562] = { expectedWidth = 6, expectedPoints = { 5687, 5745, 5776, 5745 }, hideLabel = true, reference = { index = 593, width = 6, points = { 5687, 5745, 5776, 5745 } } }
    -- #569 Doe Valley Dr
    ops[569] = { expectedWidth = 6, expectedPoints = { 5810, 6658, 5539.5, 6658, 5515.5, 6646.5, 5508, 6641, 5502, 6630.5, 5502, 6621, 5505.5, 6615.5, 5506.5, 6613, 5511.5, 6608, 5521, 6603, 5616.5, 6603, 5646.5, 6617, 5674, 6645.5, 5688, 6652 }, hideLabel = true, reference = { index = 600, width = 6, points = { 5810, 6658, 5539.5, 6658, 5515.5, 6646.5, 5508, 6641, 5502, 6630.5, 5502, 6621, 5505.5, 6615.5, 5506.5, 6613, 5511.5, 6608, 5521, 6603, 5616.5, 6603, 5646.5, 6617, 5674, 6645.5, 5688, 6652 } } }
    -- #570 West Maple St
    ops[570] = { expectedWidth = 4, expectedPoints = { 5818, 6638, 6014, 6638, 6014, 6698, 6256.5, 6698.5, 6270, 6704 }, hideLabel = true, reference = { index = 601, width = 4, points = { 5818, 6638, 6014, 6638, 6014, 6698, 6256.5, 6698.5, 6270, 6704 } } }
    -- #571 Doe Valley Ct
    ops[571] = { expectedWidth = 5, expectedPoints = { 6088.5, 6695, 6088.5, 6662.5, 6135.5, 6662.5, 6152.5, 6676.5, 6236.5, 6676.5, 6236.5, 6696.5 }, hideLabel = true, reference = { index = 602, width = 5, points = { 6088.5, 6695, 6088.5, 6662.5, 6135.5, 6662.5, 6152.5, 6676.5, 6236.5, 6676.5, 6236.5, 6696.5 } } }
    -- #573 Wilson Road
    ops[573] = { expectedWidth = 6, expectedPoints = { 4223.5, 6079.5, 4219.5, 6083, 4209, 6103, 4209, 6240, 4232, 6264.5, 4232, 6334 }, hideLabel = true, reference = { index = 604, width = 6, points = { 4223.5, 6079.5, 4219.5, 6083, 4209, 6103, 4209, 6240, 4232, 6264.5, 4232, 6334 } } }
    -- #574 Veronica Road
    ops[574] = { expectedWidth = 6, expectedPoints = { 4235, 6265, 4280, 6265 }, hideLabel = true, reference = { index = 605, width = 6, points = { 4235, 6265, 4280, 6265 } } }
    -- #575 Bright Valley Road
    ops[575] = { expectedWidth = 6, expectedPoints = { 2736, 6159, 2736, 6184.5, 2731, 6189.5, 2727.5, 6192, 2703.5, 6192, 2694, 6201, 2694, 6234.5, 2694, 6398, 2639, 6398 }, hideLabel = true, reference = { index = 606, width = 6, points = { 2736, 6159, 2736, 6184.5, 2731, 6189.5, 2727.5, 6192, 2703.5, 6192, 2694, 6201, 2694, 6234.5, 2694, 6398, 2639, 6398 } } }
    -- #576 Bright Valley Upper Lane
    ops[576] = { expectedWidth = 6, expectedPoints = { 2700, 6216, 2795, 6216, 2795, 6273, 2700, 6273 }, hideLabel = true, reference = { index = 607, width = 6, points = { 2700, 6216, 2795, 6216, 2795, 6273, 2700, 6273 } } }
    -- #577 Bright Valley Lower Lane
    ops[577] = { expectedWidth = 6, expectedPoints = { 2751, 6276, 2751, 6345.5, 2724.5, 6373, 2700, 6373 }, hideLabel = true, reference = { index = 608, width = 6, points = { 2751, 6276, 2751, 6345.5, 2724.5, 6373, 2700, 6373 } } }
    -- #579 Quarter Moon Lane
    ops[579] = { expectedWidth = 4, expectedPoints = { 6870, 7200, 6870, 7257 }, hideLabel = true, reference = { index = 610, width = 4, points = { 6870, 7200, 6870, 7257 } } }
    -- #580 Scenic Grove Road
    ops[580] = { expectedWidth = 5, expectedPoints = { 5454, 6059.5, 5442.5, 6059.5, 5429, 6073.5, 5332.5, 6074, 5310, 6053, 5310, 5913.5, 5327, 5913.5, 5347, 5933.5, 5382.5, 5933.5, 5382.5, 5981, 5389, 5987, 5388.5, 6016, 5421, 6050, 5421, 6070.5 }, hideLabel = true, reference = { index = 611, width = 5, points = { 5454, 6059.5, 5442.5, 6059.5, 5429, 6073.5, 5332.5, 6074, 5310, 6053, 5310, 5913.5, 5327, 5913.5, 5347, 5933.5, 5382.5, 5933.5, 5382.5, 5981, 5389, 5987, 5388.5, 6016, 5421, 6050, 5421, 6070.5 } } }
    -- #581 Grove St
    ops[581] = { expectedWidth = 5, expectedPoints = { 5346.5, 5936, 5346.5, 5982 }, hideLabel = true, reference = { index = 612, width = 5, points = { 5346.5, 5936, 5346.5, 5982 } } }
    -- #582 Sweet St
    ops[582] = { expectedWidth = 5, expectedPoints = { 5312.5, 5984.5, 5380.5, 5984 }, hideLabel = true, reference = { index = 613, width = 5, points = { 5312.5, 5984.5, 5380.5, 5984 } } }
    -- #583 Lemonscent Lane
    ops[583] = { expectedWidth = 4, expectedPoints = { 5357, 5986.5, 5357, 6071.5 }, hideLabel = true, reference = { index = 614, width = 4, points = { 5357, 5986.5, 5357, 6071.5 } } }
    -- #584 Kavanagh St
    ops[584] = { expectedWidth = 4, expectedPoints = { 5340, 6076.5, 5340, 6119, 5393, 6119, 5397, 6115.5, 5397, 6087.5, 5399.5, 6085.5 }, hideLabel = true, reference = { index = 615, width = 4, points = { 5340, 6076.5, 5340, 6119, 5393, 6119, 5397, 6115.5, 5397, 6087.5, 5399.5, 6085.5 } } }
    -- #585 Hennings Knob Lane
    ops[585] = { expectedWidth = 3, expectedPoints = { 5422, 5505, 5424.5, 5511, 5424.5, 5563 }, hideLabel = true, reference = { index = 616, width = 3, points = { 5422, 5505, 5424.5, 5511, 5424.5, 5563 } } }
    -- #586 Driver Road
    ops[586] = { expectedWidth = 3, expectedPoints = { 5393.5, 5442, 5393.5, 5500.5 }, hideLabel = true, reference = { index = 617, width = 3, points = { 5393.5, 5442, 5393.5, 5500.5 } } }
    -- #587 Beehive Hill Road
    ops[587] = { expectedWidth = 3, expectedPoints = { 5222, 5559.5, 5195.5, 5559.5, 5172.5, 5536.5, 5172.5, 5510.5, 5189, 5494.5, 5207, 5494.5 }, hideLabel = true, reference = { index = 618, width = 3, points = { 5222, 5559.5, 5195.5, 5559.5, 5172.5, 5536.5, 5172.5, 5510.5, 5189, 5494.5, 5207, 5494.5 } } }
    -- #588 Last Hunt Road
    ops[588] = { expectedWidth = 5, expectedPoints = { 4951, 5640, 4951, 5596, 4940, 5584 }, hideLabel = true, reference = { index = 619, width = 5, points = { 4951, 5640, 4951, 5596, 4940, 5584 } } }
    -- #589 Seven Bells Lane
    ops[589] = { expectedWidth = 3, expectedPoints = { 4808.5, 5716.5, 4808.5, 5749.5, 4850.5, 5749.5, 4859, 5757.5, 4879, 5757.5 }, hideLabel = true, reference = { index = 620, width = 3, points = { 4808.5, 5716.5, 4808.5, 5749.5, 4850.5, 5749.5, 4859, 5757.5, 4879, 5757.5 } } }
    -- #590 Abraham Lane
    ops[590] = { expectedWidth = 3, expectedPoints = { 4511.5, 5813.5, 4511.5, 5742.5, 4517, 5737.5, 4561, 5737.5 }, hideLabel = true, reference = { index = 621, width = 3, points = { 4511.5, 5813.5, 4511.5, 5742.5, 4517, 5737.5, 4561, 5737.5 } } }
    -- #591 Long Branch Link Road
    ops[591] = { expectedWidth = 5, expectedPoints = { 4292, 5833.5, 4411.5, 5953, 4501, 5954, 4501.5, 6060 }, hideLabel = true, reference = { index = 622, width = 5, points = { 4292, 5833.5, 4411.5, 5953, 4501, 5954, 4501.5, 6060 } } }
    -- #592 Berger Road
    ops[592] = { expectedWidth = 5, expectedPoints = { 4503.5, 5953, 4521.5, 5953, 4524, 5951, 4524, 5922, 4524, 5871, 4533, 5862.5, 4612, 5862, 4639, 5834.5, 4639.5, 5822, 4630.5, 5813, 4628, 5809 }, hideLabel = true, reference = { index = 623, width = 5, points = { 4503.5, 5953, 4521.5, 5953, 4524, 5951, 4524, 5922, 4524, 5871, 4533, 5862.5, 4612, 5862, 4639, 5834.5, 4639.5, 5822, 4630.5, 5813, 4628, 5809 } } }
    -- #593 Stepdown Road
    ops[593] = { expectedWidth = 5, expectedPoints = { 3806, 5715, 3818, 5703, 3959, 5702, 3984.5, 5728, 4045, 5728, 4081, 5764, 4100.5, 5764, 4125, 5787, 4190.5, 5786.5, 4233.5, 5829 }, hideLabel = true, reference = { index = 624, width = 5, points = { 3806, 5715, 3818, 5703, 3959, 5702, 3984.5, 5728, 4045, 5728, 4081, 5764, 4100.5, 5764, 4125, 5787, 4190.5, 5786.5, 4233.5, 5829 } } }
    -- #594 Flood Road
    ops[594] = { expectedWidth = 5, expectedPoints = { 4055, 5732.5, 4185, 5732 }, hideLabel = true, reference = { index = 625, width = 5, points = { 4055, 5732.5, 4185, 5732 } } }
    -- #595 Trout Lane
    ops[595] = { expectedWidth = 3, expectedPoints = { 4293.5, 5800.5, 4285.5, 5793.5, 4272.5, 5793.5, 4252.5, 5773, 4253, 5759.5, 4258.5, 5754, 4258.5, 5742 }, hideLabel = true, reference = { index = 626, width = 3, points = { 4293.5, 5800.5, 4285.5, 5793.5, 4272.5, 5793.5, 4252.5, 5773, 4253, 5759.5, 4258.5, 5754, 4258.5, 5742 } } }
    -- #596 Rainy St
    ops[596] = { expectedWidth = 4, expectedPoints = { 1676, 5701, 1676, 5744 }, hideLabel = true, reference = { index = 627, width = 4, points = { 1676, 5701, 1676, 5744 } } }
    -- #597 Esther Kinsella Memorial Bridge
    ops[597] = { expectedWidth = 15, expectedPoints = { 1501.5, 5517, 1501.5, 5400 }, hideLabel = true, reference = { index = 628, width = 15, points = { 1501.5, 5517, 1501.5, 5400 } } }
    -- #599 Lakehook Road
    ops[599] = { expectedWidth = 5, expectedPoints = { 2025, 10855.5, 2041.5, 10864, 2064, 10886, 2078, 10915.5, 2078, 10944.5, 2066, 10967.5, 2053, 10981, 2032.5, 10992.5, 1997, 10992, 1955.5, 10972, 1897.5, 10972, 1889.5, 10968.5, 1884, 10960, 1884, 10953, 1886.5, 10947.5, 1890.5, 10944.5, 1897, 10942, 1906, 10942 }, hideLabel = true, reference = { index = 630, width = 5, points = { 2025, 10855.5, 2041.5, 10864, 2064, 10886, 2078, 10915.5, 2078, 10944.5, 2066, 10967.5, 2053, 10981, 2032.5, 10992.5, 1997, 10992, 1955.5, 10972, 1897.5, 10972, 1889.5, 10968.5, 1884, 10960, 1884, 10953, 1886.5, 10947.5, 1890.5, 10944.5, 1897, 10942, 1906, 10942 } } }
    -- #600 Simon Lane
    ops[600] = { expectedWidth = 4, expectedPoints = { 1338, 8969, 1338, 9072, 1345.5, 9086.5, 1354, 9095.5, 1371.5, 9105, 1405, 9105 }, hideLabel = true, reference = { index = 631, width = 4, points = { 1338, 8969, 1338, 9072, 1345.5, 9086.5, 1354, 9095.5, 1371.5, 9105, 1405, 9105 } } }
    -- #601 Painter Road
    ops[601] = { expectedWidth = 5, expectedPoints = { 1431.5, 7857, 1539, 7965.5, 1580, 8007, 1597, 8016, 1633, 8016.5, 1639, 8014, 1643.5, 8010.5, 1647.5, 8003, 1647.5, 7955 }, hideLabel = true, reference = { index = 632, width = 5, points = { 1431.5, 7857, 1539, 7965.5, 1580, 8007, 1597, 8016, 1633, 8016.5, 1639, 8014, 1643.5, 8010.5, 1647.5, 8003, 1647.5, 7955 } } }
    -- #602 Camp Access Road
    ops[602] = { expectedWidth = 3, expectedPoints = { 2281, 10848, 2280.5, 10587.5, 2229, 10587.5 }, hideLabel = true, reference = { index = 633, width = 3, points = { 2281, 10848, 2280.5, 10587.5, 2229, 10587.5 } } }
    -- #603 Beaver Log Lane
    ops[603] = { expectedWidth = 4, expectedPoints = { 4090, 5820, 4090, 5871 }, hideLabel = true, reference = { index = 634, width = 4, points = { 4090, 5820, 4090, 5871 } } }
    -- #604 Barley Road
    ops[604] = { expectedWidth = 4, expectedPoints = { 1935, 8983, 1935, 8865 }, hideLabel = true, reference = { index = 635, width = 4, points = { 1935, 8983, 1935, 8865 } } }
    -- #605 Offshot Road
    ops[605] = { expectedWidth = 3, expectedPoints = { 2020.5, 11850, 2020.5, 11690.5, 2026.5, 11679.5, 2040, 11672.5, 2055, 11672.5 }, hideLabel = true, reference = { index = 636, width = 3, points = { 2020.5, 11850, 2020.5, 11690.5, 2026.5, 11679.5, 2040, 11672.5, 2055, 11672.5 } } }
    -- #606 Pointer Road
    ops[606] = { expectedWidth = 3, expectedPoints = { 1645.5, 11995, 1645.5, 11928 }, hideLabel = true, reference = { index = 637, width = 3, points = { 1645.5, 11995, 1645.5, 11928 } } }
    -- #607 Browntree Road
    ops[607] = { expectedWidth = 5, expectedPoints = { 1798.5, 14841, 1798.5, 14964.5, 1807, 14982, 1821.5, 14997.5, 1829.5, 15013.5, 1829.5, 15124.5 }, hideLabel = true, reference = { index = 638, width = 5, points = { 1798.5, 14841, 1798.5, 14964.5, 1807, 14982, 1821.5, 14997.5, 1829.5, 15013.5, 1829.5, 15124.5 } } }
    -- #608 Terrier Road
    ops[608] = { expectedWidth = 5, expectedPoints = { 1832, 15040.5, 2004.5, 15040.5 }, hideLabel = true, reference = { index = 639, width = 5, points = { 1832, 15040.5, 2004.5, 15040.5 } } }
    -- #609 Straight Road
    ops[609] = { expectedWidth = 5, expectedPoints = { 1567.5, 14474, 1567.5, 14835 }, hideLabel = true, reference = { index = 640, width = 5, points = { 1567.5, 14474, 1567.5, 14835 } } }
    -- #610 Cornwell Road
    ops[610] = { expectedWidth = 5, expectedPoints = { 1351, 14666.5, 1565, 14666.5 }, hideLabel = true, reference = { index = 641, width = 5, points = { 1351, 14666.5, 1565, 14666.5 } } }
    -- #611 S Carl St
    ops[611] = { expectedWidth = 6, expectedPoints = { 1899, 14502, 1899, 14598 }, hideLabel = true, reference = { index = 642, width = 6, points = { 1899, 14502, 1899, 14598 } } }
    -- #612 Arkansas Av
    ops[612] = { expectedWidth = 6, expectedPoints = { 1801, 14601, 1999, 14601 }, hideLabel = true, reference = { index = 643, width = 6, points = { 1801, 14601, 1999, 14601 } } }
    -- #613 Tree Branch Road
    ops[613] = { expectedWidth = 7, expectedPoints = { 8038.5, 9512, 8038.5, 9564.5, 7835, 9564.5 }, hideLabel = true, reference = { index = 644, width = 7, points = { 8038.5, 9512, 8038.5, 9564.5, 7835, 9564.5 } } }
    -- #614 Angler Road
    ops[614] = { expectedWidth = 6, expectedPoints = { 8335.5, 9793, 8335.5, 9819.5, 8304.5, 9851, 8237, 9851 }, hideLabel = true, reference = { index = 645, width = 6, points = { 8335.5, 9793, 8335.5, 9819.5, 8304.5, 9851, 8237, 9851 } } }
    -- #615 Manifold Road
    ops[615] = { expectedWidth = 5, expectedPoints = { 7796, 10161.5, 7684, 10161.5 }, hideLabel = true, reference = { index = 646, width = 5, points = { 7796, 10161.5, 7684, 10161.5 } } }
    -- #616 Barn Row Road
    ops[616] = { expectedWidth = 8, expectedPoints = { 6846.5, 10003, 6765.5, 10003, 6747, 9987, 6720.5, 9987, 6709, 9998.5, 6708.5, 10052 }, hideLabel = true, reference = { index = 647, width = 8, points = { 6846.5, 10003, 6765.5, 10003, 6747, 9987, 6720.5, 9987, 6709, 9998.5, 6708.5, 10052 } } }
    -- #617 Field Lane
    ops[617] = { expectedWidth = 5, expectedPoints = { 6742.5, 9983, 6742.5, 9750 }, hideLabel = true, reference = { index = 648, width = 5, points = { 6742.5, 9983, 6742.5, 9750 } } }
    -- #618 Farmhand Road
    ops[618] = { expectedWidth = 6, expectedPoints = { 6561, 10105.5, 6795, 10105, 6795, 10285 }, hideLabel = true, reference = { index = 649, width = 6, points = { 6561, 10105.5, 6795, 10105, 6795, 10285 } } }
    -- #619 Faralong Road
    ops[619] = { expectedWidth = 4, expectedPoints = { 7509, 10440, 7509, 10345, 7539.5, 10315, 7539, 10265 }, hideLabel = true, reference = { index = 650, width = 4, points = { 7509, 10440, 7509, 10345, 7539.5, 10315, 7539, 10265 } } }
    -- #620 Nailcut Road
    ops[620] = { expectedWidth = 6, expectedPoints = { 8525.5, 9793, 8525.5, 9839.5, 8492, 9873.5, 8492, 10005, 8488, 10014, 8480, 10018, 8209, 10018 }, hideLabel = true, reference = { index = 651, width = 6, points = { 8525.5, 9793, 8525.5, 9839.5, 8492, 9873.5, 8492, 10005, 8488, 10014, 8480, 10018, 8209, 10018 } } }
    -- #621 Cartoss Road
    ops[621] = { expectedWidth = 4, expectedPoints = { 7804, 10228, 8008, 10228, 8008, 10179 }, hideLabel = true, reference = { index = 652, width = 4, points = { 7804, 10228, 8008, 10228, 8008, 10179 } } }
    -- #622 Twin Lane
    ops[622] = { expectedWidth = 5, expectedPoints = { 7804, 10187, 7847, 10187, 7870, 10209, 7922, 10209 }, hideLabel = true, reference = { index = 653, width = 5, points = { 7804, 10187, 7847, 10187, 7870, 10209, 7922, 10209 } } }
    -- #623 Wander Road
    ops[623] = { expectedWidth = 5, expectedPoints = { 7273, 9640.5, 7192, 9640.5 }, hideLabel = true, reference = { index = 654, width = 5, points = { 7273, 9640.5, 7192, 9640.5 } } }
    -- #624 Carter Road
    ops[624] = { expectedWidth = 5, expectedPoints = { 7190.5, 9732, 7190, 9614.5, 7167, 9614.5 }, hideLabel = true, reference = { index = 655, width = 5, points = { 7190.5, 9732, 7190, 9614.5, 7167, 9614.5 } } }
    -- #625 West Pass Road
    ops[625] = { expectedWidth = 4, expectedPoints = { 6499, 9469, 6499, 9344 }, hideLabel = true, reference = { index = 656, width = 4, points = { 6499, 9469, 6499, 9344 } } }
    -- #626 East Pass Road
    ops[626] = { expectedWidth = 5, expectedPoints = { 6550, 9468.5, 6550.5, 9450.5, 6563, 9437.5, 6563.5, 9352.5 }, hideLabel = true, reference = { index = 657, width = 5, points = { 6550, 9468.5, 6550.5, 9450.5, 6563, 9437.5, 6563.5, 9352.5 } } }
    -- #627 Pass Link Road
    ops[627] = { expectedWidth = 3, expectedPoints = { 6501, 9443.5, 6512, 9443.5, 6528, 9427.5, 6560.5, 9427.5 }, hideLabel = true, reference = { index = 658, width = 3, points = { 6501, 9443.5, 6512, 9443.5, 6528, 9427.5, 6560.5, 9427.5 } } }
    -- #628 Nash Road
    ops[628] = { expectedWidth = 5, expectedPoints = { 6153.5, 9477, 6153.5, 9562, 6153.5, 9575, 6098, 9575 }, hideLabel = true, reference = { index = 659, width = 5, points = { 6153.5, 9477, 6153.5, 9562, 6153.5, 9575, 6098, 9575 } } }
    -- #629 Ghost Loop Road
    ops[629] = { expectedWidth = 6, expectedPoints = { 5628, 9724, 5724.5, 9724, 5733, 9716, 5733.5, 9698.5, 5723, 9688.5, 5687.5, 9688.5, 5680.5, 9695, 5680.5, 9720.5 }, hideLabel = true, reference = { index = 660, width = 6, points = { 5628, 9724, 5724.5, 9724, 5733, 9716, 5733.5, 9698.5, 5723, 9688.5, 5687.5, 9688.5, 5680.5, 9695, 5680.5, 9720.5 } } }
    -- #631 Daft Road
    ops[631] = { expectedWidth = 5, expectedPoints = { 8705.5, 12332, 8705.5, 12412, 8785, 12412, 8808.5, 12435, 8808, 12445 }, hideLabel = true, reference = { index = 662, width = 5, points = { 8705.5, 12332, 8705.5, 12412, 8785, 12412, 8808.5, 12435, 8808, 12445 } } }
    -- #632 Cave Lane
    ops[632] = { expectedWidth = 4, expectedPoints = { 8705, 12414.5, 8705, 12455 }, hideLabel = true, reference = { index = 663, width = 4, points = { 8705, 12414.5, 8705, 12455 } } }
    -- #633 Bowstring Road
    ops[633] = { expectedWidth = 4, expectedPoints = { 9043, 12332, 9043, 12449 }, hideLabel = true, reference = { index = 664, width = 4, points = { 9043, 12332, 9043, 12449 } } }
    -- #634 Sixoaks Road
    ops[634] = { expectedWidth = 5, expectedPoints = { 9022, 12098.5, 8911, 12098.5 }, hideLabel = true, reference = { index = 665, width = 5, points = { 9022, 12098.5, 8911, 12098.5 } } }
    -- #635 Handler Road
    ops[635] = { expectedWidth = 8, expectedPoints = { 9046, 12198, 9026, 12198, 9026, 12317 }, hideLabel = true, reference = { index = 666, width = 8, points = { 9046, 12198, 9026, 12198, 9026, 12317 } } }
    -- #636 Laydown Road
    ops[636] = { expectedWidth = 5, expectedPoints = { 9027, 12135.5, 9156, 12135.5 }, hideLabel = true, reference = { index = 667, width = 5, points = { 9027, 12135.5, 9156, 12135.5 } } }
    -- #637 Yew Road
    ops[637] = { expectedWidth = 4, expectedPoints = { 8833, 11643, 8833, 11596.5, 8846.5, 11596.5, 8846.5, 11643 }, hideLabel = true, reference = { index = 668, width = 4, points = { 8833, 11643, 8833, 11596.5, 8846.5, 11596.5, 8846.5, 11643 } } }
    -- #639 Poorpath Road
    ops[639] = { expectedWidth = 5, expectedPoints = { 14181, 5927, 14158.5, 5904, 14159, 5698.5 }, hideLabel = true, reference = { index = 670, width = 5, points = { 14181, 5927, 14158.5, 5904, 14159, 5698.5 } } }
    -- #640 Jeff Road
    ops[640] = { expectedWidth = 7, expectedPoints = { 14161, 5854, 14185, 5847, 14210.5, 5840, 14215, 5834, 14226.5, 5831.5, 14237.5, 5820, 14237.5, 5699 }, hideLabel = true, reference = { index = 671, width = 7, points = { 14161, 5854, 14185, 5847, 14210.5, 5840, 14215, 5834, 14226.5, 5831.5, 14237.5, 5820, 14237.5, 5699 } } }
    -- #641 Fur Trapper Road
    ops[641] = { expectedWidth = 5, expectedPoints = { 13884.5, 4897, 13884.5, 4639 }, hideLabel = true, reference = { index = 672, width = 5, points = { 13884.5, 4897, 13884.5, 4639 } } }
    -- #642 West St
    ops[642] = { expectedWidth = 6, expectedPoints = { 13502, 4041, 13502, 4129 }, hideLabel = true, reference = { index = 673, width = 6, points = { 13502, 4041, 13502, 4129 } } }
    -- #643 May St
    ops[643] = { expectedWidth = 6, expectedPoints = { 13565, 4041, 13565, 4178 }, hideLabel = true, reference = { index = 674, width = 6, points = { 13565, 4041, 13565, 4178 } } }
    -- #644 Scarlet Road
    ops[644] = { expectedWidth = 6, expectedPoints = { 13562, 4181, 13615, 4181 }, hideLabel = true, reference = { index = 675, width = 6, points = { 13562, 4181, 13615, 4181 } } }
    -- #645 Dixie St
    ops[645] = { expectedWidth = 6, expectedPoints = { 13568, 4118, 13593.5, 4118, 13609, 4118 }, hideLabel = true, reference = { index = 676, width = 6, points = { 13568, 4118, 13593.5, 4118, 13609, 4118 } } }
    -- #646 Rose Dr
    ops[646] = { expectedWidth = 6, expectedPoints = { 13612, 4088, 13612, 4178 }, hideLabel = true, reference = { index = 677, width = 6, points = { 13612, 4088, 13612, 4178 } } }
    -- #647 Garden Dr
    ops[647] = { expectedWidth = 6, expectedPoints = { 13622, 4041, 13622, 4080 }, hideLabel = true, reference = { index = 678, width = 6, points = { 13622, 4041, 13622, 4080 } } }
    -- #648 Noctural Dr
    ops[648] = { expectedWidth = 6, expectedPoints = { 13499, 4038, 13749, 4038 }, hideLabel = true, reference = { index = 679, width = 6, points = { 13499, 4038, 13749, 4038 } } }
    -- #649 East St
    ops[649] = { expectedWidth = 6, expectedPoints = { 13746, 4041, 13746, 4115, 13742, 4123.5, 13738.5, 4127, 13728.5, 4132, 13615, 4132 }, hideLabel = true, reference = { index = 680, width = 6, points = { 13746, 4041, 13746, 4115, 13742, 4123.5, 13738.5, 4127, 13728.5, 4132, 13615, 4132 } } }
    -- #650 Skeeter St
    ops[650] = { expectedWidth = 6, expectedPoints = { 13499, 4132, 13562, 4132 }, hideLabel = true, reference = { index = 681, width = 6, points = { 13499, 4132, 13562, 4132 } } }
    -- #651 Olive Close
    ops[651] = { expectedWidth = 5, expectedPoints = { 13822.5, 4080, 13822.5, 4012, 13824.5, 4009.5, 13888, 4009.5, 13889.5, 4011, 13889.5, 4062.5, 13887, 4064.5, 13825.5, 4064.5 }, hideLabel = true, reference = { index = 682, width = 5, points = { 13822.5, 4080, 13822.5, 4012, 13824.5, 4009.5, 13888, 4009.5, 13889.5, 4011, 13889.5, 4062.5, 13887, 4064.5, 13825.5, 4064.5 } } }
    -- #652 Cobbler Road
    ops[652] = { expectedWidth = 4, expectedPoints = { 13528, 3754, 13528, 3666 }, hideLabel = true, reference = { index = 683, width = 4, points = { 13528, 3754, 13528, 3666 } } }
    -- #653 Cob Road
    ops[653] = { expectedWidth = 4, expectedPoints = { 13466, 3681, 13466, 3699, 13481, 3714, 13562, 3714 }, hideLabel = true, reference = { index = 684, width = 4, points = { 13466, 3681, 13466, 3699, 13481, 3714, 13562, 3714 } } }
    -- #654 Husk Lane
    ops[654] = { expectedWidth = 4, expectedPoints = { 13649, 3640, 13615, 3640, 13594, 3660.5, 13594, 3699 }, hideLabel = true, reference = { index = 685, width = 4, points = { 13649, 3640, 13615, 3640, 13594, 3660.5, 13594, 3699 } } }
    -- #655 Terminal Dr
    ops[655] = { expectedWidth = 8, expectedPoints = { 15600, 3322, 15600, 3155.5, 15606, 3143, 15616.5, 3132, 15620, 3125.5, 15620, 2495, 15615, 2483.5, 15600, 2468.5 }, hideLabel = true, reference = { index = 686, width = 8, points = { 15600, 3322, 15600, 3155.5, 15606, 3143, 15616.5, 3132, 15620, 3125.5, 15620, 2495, 15615, 2483.5, 15600, 2468.5 } } }
    -- #656 Pigeon Road
    ops[656] = { expectedWidth = 4, expectedPoints = { 7693, 11197, 7693, 11112, 7680, 11099.5 }, hideLabel = true, reference = { index = 687, width = 4, points = { 7693, 11197, 7693, 11112, 7680, 11099.5 } } }
    -- #657 Wheel Road
    ops[657] = { expectedWidth = 5, expectedPoints = { 6962.5, 10497, 6962.5, 10635 }, hideLabel = true, reference = { index = 688, width = 5, points = { 6962.5, 10497, 6962.5, 10635 } } }
    -- #658 Ram Road
    ops[658] = { expectedWidth = 5, expectedPoints = { 7395, 10734.5, 7320, 10734.5, 7303.5, 10718.5, 7273, 10718 }, hideLabel = true, reference = { index = 689, width = 5, points = { 7395, 10734.5, 7320, 10734.5, 7303.5, 10718.5, 7273, 10718 } } }
    -- #659 Locust Road
    ops[659] = { expectedWidth = 5, expectedPoints = { 10698, 7221.5, 10557, 7221.5, 10556.5, 7190, 10500, 7190.5 }, hideLabel = true, reference = { index = 690, width = 5, points = { 10698, 7221.5, 10557, 7221.5, 10556.5, 7190, 10500, 7190.5 } } }
    -- #660 Ladies Lane
    ops[660] = { expectedWidth = 5, expectedPoints = { 10756.5, 7044, 10756.5, 6991.5 }, hideLabel = true, reference = { index = 691, width = 5, points = { 10756.5, 7044, 10756.5, 6991.5 } } }
    -- #661 Carlow Road
    ops[661] = { expectedWidth = 5, expectedPoints = { 10708, 7097, 10768, 7097, 10797.5, 7126.5, 10900, 7127 }, hideLabel = true, reference = { index = 692, width = 5, points = { 10708, 7097, 10768, 7097, 10797.5, 7126.5, 10900, 7127 } } }
    -- #662 Derry Close
    ops[662] = { expectedWidth = 8, expectedPoints = { 11878, 7048, 11917, 7048 }, hideLabel = true, reference = { index = 693, width = 8, points = { 11878, 7048, 11917, 7048 } } }
    -- #663 Marston Road
    ops[663] = { expectedWidth = 4, expectedPoints = { 10600, 7219, 10600, 7143 }, hideLabel = true, reference = { index = 694, width = 4, points = { 10600, 7219, 10600, 7143 } } }
    -- #664 Salt St
    ops[664] = { expectedWidth = 5, expectedPoints = { 11235.5, 6755, 11235.5, 6878 }, hideLabel = true, reference = { index = 695, width = 5, points = { 11235.5, 6755, 11235.5, 6878 } } }
    -- #665 Lacey Lane
    ops[665] = { expectedWidth = 8, expectedPoints = { 11626, 6904, 11626, 6945 }, hideLabel = true, reference = { index = 696, width = 8, points = { 11626, 6904, 11626, 6945 } } }
    -- #667 Esther Road
    ops[667] = { expectedWidth = 8, expectedPoints = { 12564, 5163, 12564, 5353, 12674, 5353 }, hideLabel = true, reference = { index = 698, width = 8, points = { 12564, 5163, 12564, 5353, 12674, 5353 } } }
    -- #668 Cupcake Road
    ops[668] = { expectedWidth = 6, expectedPoints = { 12568, 5231, 12627, 5231 }, hideLabel = true, reference = { index = 699, width = 6, points = { 12568, 5231, 12627, 5231 } } }
    -- #669 Brown Bread Road
    ops[669] = { expectedWidth = 6, expectedPoints = { 12503, 5160, 12612, 5160 }, hideLabel = true, reference = { index = 700, width = 6, points = { 12503, 5160, 12612, 5160 } } }
    -- #670 Vincent Road
    ops[670] = { expectedWidth = 6, expectedPoints = { 12750, 6463, 12750, 6380 }, hideLabel = true, reference = { index = 701, width = 6, points = { 12750, 6463, 12750, 6380 } } }
    -- #671 Blossom Lane
    ops[671] = { expectedWidth = 6, expectedPoints = { 14102.5, 5381, 14102.5, 5357.5, 14042.5, 5357.5 }, hideLabel = true, reference = { index = 702, width = 6, points = { 14102.5, 5381, 14102.5, 5357.5, 14042.5, 5357.5 } } }
    -- #672 Albany Close
    ops[672] = { expectedWidth = 6, expectedPoints = { 14392, 5434.5, 14335, 5434.5, 14333, 5390, 14316.5, 5375, 14351, 5375, 14369.5, 5396, 14370, 5430.5 }, hideLabel = true, reference = { index = 703, width = 6, points = { 14392, 5434.5, 14335, 5434.5, 14333, 5390, 14316.5, 5375, 14351, 5375, 14369.5, 5396, 14370, 5430.5 } } }
    -- #673 Cloth Road
    ops[673] = { expectedWidth = 4, expectedPoints = { 13829, 3592, 13829, 3549 }, hideLabel = true, reference = { index = 704, width = 4, points = { 13829, 3592, 13829, 3549 } } }
    -- #674 Dixie Highway (Route 31 W)
    ops[674] = { expectedWidth = 15, expectedPoints = { 12599.5, 1241, 12599.5, 1119 }, hideLabel = true, reference = { index = 705, width = 15, points = { 12599.5, 1241, 12599.5, 1119 } } }
    -- #675 Clark Memorial Bridge
    ops[675] = { expectedWidth = 15, expectedPoints = { 12599.5, 1119, 12599.5, 900 }, hideLabel = true, reference = { index = 706, width = 15, points = { 12599.5, 1119, 12599.5, 900 } } }
    -- #676 Bathtub Road
    ops[676] = { expectedWidth = 6, expectedPoints = { 7690.5, 13984.5, 7657, 14017.5, 7657, 14240, 7615, 14282, 7615, 14497 }, hideLabel = true, reference = { index = 707, width = 6, points = { 7690.5, 13984.5, 7657, 14017.5, 7657, 14240, 7615, 14282, 7615, 14497 } } }
    -- #677 Gartip Road
    ops[677] = { expectedWidth = 4, expectedPoints = { 7612, 14326, 7541, 14326, 7525, 14341.5, 7519.5, 14341.5 }, hideLabel = true, reference = { index = 708, width = 4, points = { 7612, 14326, 7541, 14326, 7525, 14341.5, 7519.5, 14341.5 } } }
    -- #678 Parsnip Road
    ops[678] = { expectedWidth = 5, expectedPoints = { 7660.5, 14214, 7688, 14242, 7722, 14242, 7744.5, 14262.5, 7743.5, 14310, 7706.5, 14310 }, hideLabel = true, reference = { index = 709, width = 5, points = { 7660.5, 14214, 7688, 14242, 7722, 14242, 7744.5, 14262.5, 7743.5, 14310, 7706.5, 14310 } } }
    -- #679 Peapod Road
    ops[679] = { expectedWidth = 5, expectedPoints = { 7736, 14251.5, 7755, 14232.5, 7839, 14232.5, 7877, 14269.5, 7876, 14322, 7864, 14322 }, hideLabel = true, reference = { index = 710, width = 5, points = { 7736, 14251.5, 7755, 14232.5, 7839, 14232.5, 7877, 14269.5, 7876, 14322, 7864, 14322 } } }
    -- #680 Edam Road
    ops[680] = { expectedWidth = 5, expectedPoints = { 13525.5, 4836.5, 13543, 4818.5, 13542.5, 4633, 13525.5, 4615.5 }, hideLabel = true, reference = { index = 711, width = 5, points = { 13525.5, 4836.5, 13543, 4818.5, 13542.5, 4633, 13525.5, 4615.5 } } }
    -- #681 Patch Road
    ops[681] = { expectedWidth = 4, expectedPoints = { 8345, 14055, 8355, 14055, 8379, 14030.5, 8379, 13929, 8391, 13917, 8416, 13917 }, hideLabel = true, reference = { index = 712, width = 4, points = { 8345, 14055, 8355, 14055, 8379, 14030.5, 8379, 13929, 8391, 13917, 8416, 13917 } } }
    -- #682 Dempsey St
    ops[682] = { expectedWidth = 8, expectedPoints = { 2253, 14496, 2496.5, 14253.5 }, hideLabel = true, reference = { index = 713, width = 8, points = { 2253, 14496, 2496.5, 14253.5 } } }
    -- #683 Ed St
    ops[683] = { expectedWidth = 6, expectedPoints = { 2203.5, 14010.5, 2301.5, 13961.5, 2401, 13961, 2412, 13937.5, 2417.5, 13932.5 }, hideLabel = true, reference = { index = 714, width = 6, points = { 2203.5, 14010.5, 2301.5, 13961.5, 2401, 13961, 2412, 13937.5, 2417.5, 13932.5 } } }
    -- #684 Calfrun Road
    ops[684] = { expectedWidth = 5, expectedPoints = { 3198.5, 13520, 3198.5, 13789 }, hideLabel = true, reference = { index = 715, width = 5, points = { 3198.5, 13520, 3198.5, 13789 } } }
    -- #685 Edward S. Jonas Lane
    ops[685] = { expectedWidth = 4, expectedPoints = { 4205, 5835.5, 4205, 5850, 4217, 5862, 4251, 5862 }, hideLabel = true, reference = { index = 716, width = 4, points = { 4205, 5835.5, 4205, 5850, 4217, 5862, 4251, 5862 } } }
    -- #686 Three Clouds Road
    ops[686] = { expectedWidth = 5, expectedPoints = { 8538.5, 9475, 8538.5, 9391 }, hideLabel = true, reference = { index = 717, width = 5, points = { 8538.5, 9475, 8538.5, 9391 } } }
    -- #687 Lakepoint Road
    ops[687] = { expectedWidth = 4, expectedPoints = { 1347.5, 8695.5, 1424, 8695.5, 1444.5, 8686.5, 1500.5, 8631.5, 1518, 8623, 1709, 8623 }, hideLabel = true, reference = { index = 718, width = 4, points = { 1347.5, 8695.5, 1424, 8695.5, 1444.5, 8686.5, 1500.5, 8631.5, 1518, 8623, 1709, 8623 } } }
    -- #688 Birdsong Road
    ops[688] = { expectedWidth = 4, expectedPoints = { 14535, 3442, 14535, 3000, 13986, 3000 }, hideLabel = true, reference = { index = 719, width = 4, points = { 14535, 3442, 14535, 3000, 13986, 3000 } } }
    -- #689 Chuckle St
    ops[689] = { expectedWidth = 4, expectedPoints = { 14537, 3161, 14574, 3161, 14574, 3116 }, hideLabel = true, reference = { index = 720, width = 4, points = { 14537, 3161, 14574, 3161, 14574, 3116 } } }
    -- #690 Last Smile Lane
    ops[690] = { expectedWidth = 4, expectedPoints = { 14537, 3055, 14580, 3055 }, hideLabel = true, reference = { index = 721, width = 4, points = { 14537, 3055, 14580, 3055 } } }
    -- #691 Freddy Stapleton St
    ops[691] = { expectedWidth = 6, expectedPoints = { 14227, 2997.5, 14227, 2853 }, hideLabel = true, reference = { index = 722, width = 6, points = { 14227, 2997.5, 14227, 2853 } } }
    -- #692 Lilliput Road
    ops[692] = { expectedWidth = 6, expectedPoints = { 9785, 7786, 9785, 7820, 9790.5, 7825, 9895, 7825 }, hideLabel = true, reference = { index = 723, width = 6, points = { 9785, 7786, 9785, 7820, 9790.5, 7825, 9895, 7825 } } }
    -- #694 Try Hard Road
    ops[694] = { expectedWidth = 5, expectedPoints = { 1519.5, 10292, 1410.5, 10291 }, hideLabel = true, reference = { index = 725, width = 5, points = { 1519.5, 10292, 1410.5, 10291 } } }
    -- #695 Wagon Rest St
    ops[695] = { expectedWidth = 5, expectedPoints = { 934.5, 9674, 934.5, 9579 }, hideLabel = true, reference = { index = 726, width = 5, points = { 934.5, 9674, 934.5, 9579 } } }
    -- #696 Woodhaul Road
    ops[696] = { expectedWidth = 3, expectedPoints = { 10229.5, 9523, 10229.5, 9507, 10232.5, 9500.5, 10239.5, 9496.5, 10336, 9496.5, 10438, 9496.5, 10453.5, 9488.5, 10460, 9473.5, 10460.5, 9410.5, 10465, 9401, 10468.5, 9398, 10477.5, 9393.5, 10521, 9393.5 }, hideLabel = true, reference = { index = 727, width = 3, points = { 10229.5, 9523, 10229.5, 9507, 10232.5, 9500.5, 10239.5, 9496.5, 10336, 9496.5, 10438, 9496.5, 10453.5, 9488.5, 10460, 9473.5, 10460.5, 9410.5, 10465, 9401, 10468.5, 9398, 10477.5, 9393.5, 10521, 9393.5 } } }
    -- #697 Axhead Road
    ops[697] = { expectedWidth = 3, expectedPoints = { 10402.5, 9499.5, 10402.5, 9625, 10406, 9632, 10410.5, 9636.5, 10447, 9636.5, 10521, 9636.5 }, hideLabel = true, reference = { index = 728, width = 3, points = { 10402.5, 9499.5, 10402.5, 9625, 10406, 9632, 10410.5, 9636.5, 10447, 9636.5, 10521, 9636.5 } } }
    -- #698 Bobby Road
    ops[698] = { expectedWidth = 6, expectedPoints = { 6697, 8917, 6649, 8917, 6616, 8952, 6585, 8952 }, hideLabel = true, reference = { index = 729, width = 6, points = { 6697, 8917, 6649, 8917, 6616, 8952, 6585, 8952 } } }
    -- #699 Neils Road
    ops[699] = { expectedWidth = 4, expectedPoints = { 5990, 9469, 5990, 9369 }, hideLabel = true, reference = { index = 730, width = 4, points = { 5990, 9469, 5990, 9369 } } }
    -- #700 Twist Road
    ops[700] = { expectedWidth = 5, expectedPoints = { 5422, 9942.5, 5549.5, 9942.5, 5549.5, 9935, 5614.5, 9935, 5655, 9895, 5751, 9895, 5769, 9877, 5846, 9877, 5924.5, 9877.5, 5924.5, 9618.5, 5933, 9609, 5933, 9600 }, hideLabel = true, reference = { index = 731, width = 5, points = { 5422, 9942.5, 5549.5, 9942.5, 5549.5, 9935, 5614.5, 9935, 5655, 9895, 5751, 9895, 5769, 9877, 5846, 9877, 5924.5, 9877.5, 5924.5, 9618.5, 5933, 9609, 5933, 9600 } } }
    -- #701 Broken Spear Road
    ops[701] = { expectedWidth = 6, expectedPoints = { 7691, 11137, 7490, 11137, 7490, 11103 }, hideLabel = true, reference = { index = 732, width = 6, points = { 7691, 11137, 7490, 11137, 7490, 11103 } } }
    -- #702 Haulier Road
    ops[702] = { expectedWidth = 5, expectedPoints = { 6798, 10205.5, 7043, 10205.5 }, hideLabel = true, reference = { index = 733, width = 5, points = { 6798, 10205.5, 7043, 10205.5 } } }
    -- #703 Keane Lane
    ops[703] = { expectedWidth = 5, expectedPoints = { 5824, 9634.5, 5922, 9634.5 }, hideLabel = true, reference = { index = 734, width = 5, points = { 5824, 9634.5, 5922, 9634.5 } } }
    -- #704 Rabbit Hutch Road
    ops[704] = { expectedWidth = 5, expectedPoints = { 5222, 10259.5, 5272.5, 10259.5, 5378, 10259.5 }, hideLabel = true, reference = { index = 735, width = 5, points = { 5222, 10259.5, 5272.5, 10259.5, 5378, 10259.5 } } }
    -- #705 Old Mans Walk Road
    ops[705] = { expectedWidth = 5, expectedPoints = { 5222.5, 10508, 5322, 10508.5 }, hideLabel = true, reference = { index = 736, width = 5, points = { 5222.5, 10508, 5322, 10508.5 } } }
    -- #706 Spirit Road
    ops[706] = { expectedWidth = 4, expectedPoints = { 14700, 3756, 14700, 3916 }, hideLabel = true, reference = { index = 737, width = 4, points = { 14700, 3756, 14700, 3916 } } }
    -- #707 Midfield Access Road
    ops[707] = { expectedWidth = 8, expectedPoints = { 15325, 3322, 15325, 3113, 15616, 3113 }, hideLabel = true, reference = { index = 738, width = 8, points = { 15325, 3322, 15325, 3113, 15616, 3113 } } }
    -- #708 Great Road
    ops[708] = { expectedWidth = 5, expectedPoints = { 13892, 4047.5, 13954.5, 4047.5, 13971.5, 4065, 13971.5, 4080 }, hideLabel = true, reference = { index = 739, width = 5, points = { 13892, 4047.5, 13954.5, 4047.5, 13971.5, 4065, 13971.5, 4080 } } }
    -- #709 N Shelby Road
    ops[709] = { expectedWidth = 10, expectedPoints = { 13500, 1261, 13500, 1549 }, hideLabel = true, reference = { index = 740, width = 10, points = { 13500, 1261, 13500, 1549 } } }
    -- #710 Wellington Hts
    ops[710] = { expectedWidth = 10, expectedPoints = { 12900, 2258, 12900, 2197, 13351, 2197, 13351, 2307, 13496, 2307 }, hideLabel = true, reference = { index = 741, width = 10, points = { 12900, 2258, 12900, 2197, 13351, 2197, 13351, 2307, 13496, 2307 } } }
    -- #711 Horseman St
    ops[711] = { expectedWidth = 6, expectedPoints = { 13539, 2867, 13539, 2948 }, hideLabel = true, reference = { index = 742, width = 6, points = { 13539, 2867, 13539, 2948 } } }
    -- #712 Woodsedge St
    ops[712] = { expectedWidth = 6, expectedPoints = { 13826, 2395, 13826, 2349, 13933, 2348.5, 13933, 2263, 14101.5, 2263, 14114, 2269, 14126, 2280, 14132, 2291.5, 14132, 2402, 14127.5, 2411.5, 14119.5, 2420, 14108, 2426, 13986, 2426 }, hideLabel = true, reference = { index = 743, width = 6, points = { 13826, 2395, 13826, 2349, 13933, 2348.5, 13933, 2263, 14101.5, 2263, 14114, 2269, 14126, 2280, 14132, 2291.5, 14132, 2402, 14127.5, 2411.5, 14119.5, 2420, 14108, 2426, 13986, 2426 } } }
    -- #713 Maybloom Dr
    ops[713] = { expectedWidth = 6, expectedPoints = { 13930, 2308, 13889, 2308, 13889, 2245 }, hideLabel = true, reference = { index = 744, width = 6, points = { 13930, 2308, 13889, 2308, 13889, 2245 } } }
    -- #714 Hans Ct
    ops[714] = { expectedWidth = 6, expectedPoints = { 13936, 2320, 13985, 2320 }, hideLabel = true, reference = { index = 745, width = 6, points = { 13936, 2320, 13985, 2320 } } }
    -- #715 Washboard St
    ops[715] = { expectedWidth = 6, expectedPoints = { 13972, 2260, 13972, 2234 }, hideLabel = true, reference = { index = 746, width = 6, points = { 13972, 2260, 13972, 2234 } } }
    -- #716 Parrot St
    ops[716] = { expectedWidth = 6, expectedPoints = { 14016, 2171, 14077, 2171 }, hideLabel = true, reference = { index = 747, width = 6, points = { 14016, 2171, 14077, 2171 } } }
    -- #717 Patriots St
    ops[717] = { expectedWidth = 6, expectedPoints = { 14043, 2429, 14043, 2578, 14100, 2578, 14100, 2700, 14052, 2700, 14032, 2690.5, 14011, 2669.5, 13992.5, 2661, 13986, 2661 }, hideLabel = true, reference = { index = 748, width = 6, points = { 14043, 2429, 14043, 2578, 14100, 2578, 14100, 2700, 14052, 2700, 14032, 2690.5, 14011, 2669.5, 13992.5, 2661, 13986, 2661 } } }
    -- #718 Liberty St
    ops[718] = { expectedWidth = 6, expectedPoints = { 14268, 2715, 14268, 2850, 14103, 2850 }, hideLabel = true, reference = { index = 749, width = 6, points = { 14268, 2715, 14268, 2850, 14103, 2850 } } }
    -- #719 Blue St
    ops[719] = { expectedWidth = 6, expectedPoints = { 14265, 2787, 14188, 2787 }, hideLabel = true, reference = { index = 750, width = 6, points = { 14265, 2787, 14188, 2787 } } }
    -- #720 Senior St
    ops[720] = { expectedWidth = 6, expectedPoints = { 14271, 2823, 14315, 2823 }, hideLabel = true, reference = { index = 751, width = 6, points = { 14271, 2823, 14315, 2823 } } }
    -- #721 Wilson St
    ops[721] = { expectedWidth = 6, expectedPoints = { 14072, 2742, 14185, 2742, 14185, 2811, 13986, 2811 }, hideLabel = true, reference = { index = 752, width = 6, points = { 14072, 2742, 14185, 2742, 14185, 2811, 13986, 2811 } } }
    -- #722 Carrot St
    ops[722] = { expectedWidth = 6, expectedPoints = { 14230, 2964, 14319, 2964 }, hideLabel = true, reference = { index = 753, width = 6, points = { 14230, 2964, 14319, 2964 } } }
    -- #723 Nuremberg Dr
    ops[723] = { expectedWidth = 6, expectedPoints = { 14290, 2961, 14290, 2913 }, hideLabel = true, reference = { index = 754, width = 6, points = { 14290, 2961, 14290, 2913 } } }
    -- #724 Hamburg Close
    ops[724] = { expectedWidth = 6, expectedPoints = { 14259, 2910, 14321, 2910 }, hideLabel = true, reference = { index = 755, width = 6, points = { 14259, 2910, 14321, 2910 } } }
    -- #725 Mulefear St
    ops[725] = { expectedWidth = 6, expectedPoints = { 14103, 2924, 14224, 2924 }, hideLabel = true, reference = { index = 756, width = 6, points = { 14103, 2924, 14224, 2924 } } }
    -- #726 Soup St
    ops[726] = { expectedWidth = 6, expectedPoints = { 14156, 2927, 14156, 2981 }, hideLabel = true, reference = { index = 757, width = 6, points = { 14156, 2927, 14156, 2981 } } }
    -- #727 Tramp St
    ops[727] = { expectedWidth = 6, expectedPoints = { 14100, 2814, 14100, 2981 }, hideLabel = true, reference = { index = 758, width = 6, points = { 14100, 2814, 14100, 2981 } } }
    -- #728 Hundred Steps St
    ops[728] = { expectedWidth = 6, expectedPoints = { 14027, 2877, 14097, 2877 }, hideLabel = true, reference = { index = 759, width = 6, points = { 14027, 2877, 14097, 2877 } } }
    -- #729 Marzipan Close
    ops[729] = { expectedWidth = 4, expectedPoints = { 14053, 2874, 14053, 2836 }, hideLabel = true, reference = { index = 760, width = 4, points = { 14053, 2874, 14053, 2836 } } }
    -- #730 Beggars St
    ops[730] = { expectedWidth = 6, expectedPoints = { 14024, 2846, 14024, 2953 }, hideLabel = true, reference = { index = 761, width = 6, points = { 14024, 2846, 14024, 2953 } } }
    -- #731 Noluck Lane
    ops[731] = { expectedWidth = 4, expectedPoints = { 14027, 2931, 14065, 2931 }, hideLabel = true, reference = { index = 762, width = 4, points = { 14027, 2931, 14065, 2931 } } }
    -- #732 American St
    ops[732] = { expectedWidth = 6, expectedPoints = { 14069, 2808, 14069, 2703 }, hideLabel = true, reference = { index = 763, width = 6, points = { 14069, 2808, 14069, 2703 } } }
    -- #733 Dresden Dr
    ops[733] = { expectedWidth = 6, expectedPoints = { 13992, 2756, 14066, 2756 }, hideLabel = true, reference = { index = 764, width = 6, points = { 13992, 2756, 14066, 2756 } } }
    -- #734 Black Forest St
    ops[734] = { expectedWidth = 4, expectedPoints = { 14015, 2753, 14015, 2709 }, hideLabel = true, reference = { index = 765, width = 4, points = { 14015, 2753, 14015, 2709 } } }
    -- #735 Army St
    ops[735] = { expectedWidth = 6, expectedPoints = { 13428, 2103, 13428, 2302 }, hideLabel = true, reference = { index = 766, width = 6, points = { 13428, 2103, 13428, 2302 } } }
    -- #736 Store Row
    ops[736] = { expectedWidth = 4, expectedPoints = { 14013, 2407, 14100, 2407 }, hideLabel = true, reference = { index = 767, width = 4, points = { 14013, 2407, 14100, 2407 } } }
    -- #737 Doorstop St
    ops[737] = { expectedWidth = 6, expectedPoints = { 13598, 2154, 13598, 2023, 13631, 2023 }, hideLabel = true, reference = { index = 768, width = 6, points = { 13598, 2154, 13598, 2023, 13631, 2023 } } }
    -- #738 Errant St
    ops[738] = { expectedWidth = 6, expectedPoints = { 13558, 2122, 13558, 2071, 13662, 2071 }, hideLabel = true, reference = { index = 769, width = 6, points = { 13558, 2122, 13558, 2071, 13662, 2071 } } }
    -- #739 Nick St
    ops[739] = { expectedWidth = 6, expectedPoints = { 13643, 2148, 13643, 2104, 13697, 2104 }, hideLabel = true, reference = { index = 770, width = 6, points = { 13643, 2148, 13643, 2104, 13697, 2104 } } }
    -- #740 Swill St
    ops[740] = { expectedWidth = 6, expectedPoints = { 13506, 2157, 13630, 2157 }, hideLabel = true, reference = { index = 771, width = 6, points = { 13506, 2157, 13630, 2157 } } }
    -- #741 Hatshop St
    ops[741] = { expectedWidth = 6, expectedPoints = { 13558, 2160, 13558, 2230 }, hideLabel = true, reference = { index = 772, width = 6, points = { 13558, 2160, 13558, 2230 } } }
    -- #742 Right Hook St
    ops[742] = { expectedWidth = 6, expectedPoints = { 13633, 2230, 13633, 2151, 13718, 2151 }, hideLabel = true, reference = { index = 773, width = 6, points = { 13633, 2230, 13633, 2151, 13718, 2151 } } }
    -- #743 Cousin Clash St
    ops[743] = { expectedWidth = 6, expectedPoints = { 13739, 2196, 13739, 2252 }, hideLabel = true, reference = { index = 774, width = 6, points = { 13739, 2196, 13739, 2252 } } }
    -- #744 Bavaria St
    ops[744] = { expectedWidth = 6, expectedPoints = { 13561, 2193, 13742, 2193 }, hideLabel = true, reference = { index = 775, width = 6, points = { 13561, 2193, 13742, 2193 } } }
    -- #745 Victory St
    ops[745] = { expectedWidth = 6, expectedPoints = { 13555, 2233, 13736, 2233 }, hideLabel = true, reference = { index = 776, width = 6, points = { 13555, 2233, 13736, 2233 } } }
    -- #746 German St
    ops[746] = { expectedWidth = 6, expectedPoints = { 13597, 2236, 13597, 2289 }, hideLabel = true, reference = { index = 777, width = 6, points = { 13597, 2236, 13597, 2289 } } }
    -- #747 Boniface St
    ops[747] = { expectedWidth = 6, expectedPoints = { 13679, 2236, 13679, 2292, 13534, 2292 }, hideLabel = true, reference = { index = 778, width = 6, points = { 13679, 2236, 13679, 2292, 13534, 2292 } } }
    -- #748 Kleiner Cl
    ops[748] = { expectedWidth = 6, expectedPoints = { 13666, 2295, 13666, 2321 }, hideLabel = true, reference = { index = 779, width = 6, points = { 13666, 2295, 13666, 2321 } } }
    -- #749 Lerman St
    ops[749] = { expectedWidth = 6, expectedPoints = { 13608, 2295, 13608, 2395 }, hideLabel = true, reference = { index = 780, width = 6, points = { 13608, 2295, 13608, 2395 } } }
    -- #750 Bratwurst Lane
    ops[750] = { expectedWidth = 6, expectedPoints = { 13561, 2295, 13561, 2363 }, hideLabel = true, reference = { index = 781, width = 6, points = { 13561, 2295, 13561, 2363 } } }
    -- #751 Congress St
    ops[751] = { expectedWidth = 6, expectedPoints = { 13745, 2613, 13745, 2682 }, hideLabel = true, reference = { index = 782, width = 6, points = { 13745, 2613, 13745, 2682 } } }
    -- #752 Washington St
    ops[752] = { expectedWidth = 6, expectedPoints = { 13504, 2499, 13633, 2499, 13633, 2696 }, hideLabel = true, reference = { index = 783, width = 6, points = { 13504, 2499, 13633, 2499, 13633, 2696 } } }
    -- #753 Senate Dr
    ops[753] = { expectedWidth = 4, expectedPoints = { 13687, 2613, 13687, 2652 }, hideLabel = true, reference = { index = 784, width = 4, points = { 13687, 2613, 13687, 2652 } } }
    -- #754 Democrat St
    ops[754] = { expectedWidth = 5, expectedPoints = { 13644, 2684.5, 13797, 2684.5 }, hideLabel = true, reference = { index = 785, width = 5, points = { 13644, 2684.5, 13797, 2684.5 } } }
    -- #755 Beethoven St
    ops[755] = { expectedWidth = 6, expectedPoints = { 13861, 2613, 13861, 2682 }, hideLabel = true, reference = { index = 786, width = 6, points = { 13861, 2613, 13861, 2682 } } }
    -- #756 Pill St
    ops[756] = { expectedWidth = 6, expectedPoints = { 13545, 2496, 13545, 2405 }, hideLabel = true, reference = { index = 787, width = 6, points = { 13545, 2496, 13545, 2405 } } }
    -- #757 Fourth of July St
    ops[757] = { expectedWidth = 6, expectedPoints = { 13714, 2405.5, 13714, 2524 }, hideLabel = true, reference = { index = 788, width = 6, points = { 13714, 2405.5, 13714, 2524 } } }
    -- #758 Lincoln St
    ops[758] = { expectedWidth = 6, expectedPoints = { 13636, 2527, 13797, 2527 }, hideLabel = true, reference = { index = 789, width = 6, points = { 13636, 2527, 13797, 2527 } } }
    -- #759 Panama St
    ops[759] = { expectedWidth = 6, expectedPoints = { 13803, 2526, 13894, 2526, 13894, 2607 }, hideLabel = true, reference = { index = 790, width = 6, points = { 13803, 2526, 13894, 2526, 13894, 2607 } } }
    -- #760 Frankfurt St
    ops[760] = { expectedWidth = 6, expectedPoints = { 13897, 2570, 13976, 2570 }, hideLabel = true, reference = { index = 791, width = 6, points = { 13897, 2570, 13976, 2570 } } }
    -- #761 Independence St
    ops[761] = { expectedWidth = 5, expectedPoints = { 13756.5, 2524, 13756.5, 2405 }, hideLabel = true, reference = { index = 792, width = 5, points = { 13756.5, 2524, 13756.5, 2405 } } }
    -- #762 Oriole St
    ops[762] = { expectedWidth = 5, expectedPoints = { 13587.5, 2496, 13587.5, 2449.5, 13670.5, 2449.5, 13670.5, 2524 }, hideLabel = true, reference = { index = 793, width = 5, points = { 13587.5, 2496, 13587.5, 2449.5, 13670.5, 2449.5, 13670.5, 2524 } } }
    -- #763 Roosevelt St
    ops[763] = { expectedWidth = 6, expectedPoints = { 13803, 2467, 13873, 2467, 13873, 2523 }, hideLabel = true, reference = { index = 794, width = 6, points = { 13803, 2467, 13873, 2467, 13873, 2523 } } }
    -- #764 Headless Dr
    ops[764] = { expectedWidth = 4, expectedPoints = { 13555, 2188, 13514, 2188 }, hideLabel = true, reference = { index = 795, width = 4, points = { 13555, 2188, 13514, 2188 } } }
    -- #765 Keep St
    ops[765] = { expectedWidth = 4, expectedPoints = { 13521, 2190, 13521, 2240 }, hideLabel = true, reference = { index = 796, width = 4, points = { 13521, 2190, 13521, 2240 } } }
    -- #766 Fountain View Sq
    ops[766] = { expectedWidth = 6, expectedPoints = { 13400, 1877.5, 13400, 1840, 13441, 1840, 13441, 1881, 13397, 1881 }, hideLabel = true, reference = { index = 797, width = 6, points = { 13400, 1877.5, 13400, 1840, 13441, 1840, 13441, 1881, 13397, 1881 } } }
    -- #767 Woodpecker St
    ops[767] = { expectedWidth = 6, expectedPoints = { 13637, 2864, 13760, 2864, 13760, 2955, 13751, 2955, 13751, 2997 }, hideLabel = true, reference = { index = 798, width = 6, points = { 13637, 2864, 13760, 2864, 13760, 2955, 13751, 2955, 13751, 2997 } } }
    -- #768 Piano St
    ops[768] = { expectedWidth = 6, expectedPoints = { 13851, 2529, 13851, 2578 }, hideLabel = true, reference = { index = 799, width = 6, points = { 13851, 2529, 13851, 2578 } } }
    -- #769 Pillow Dr
    ops[769] = { expectedWidth = 6, expectedPoints = { 13562, 2696, 13562, 2664 }, hideLabel = true, reference = { index = 800, width = 6, points = { 13562, 2696, 13562, 2664 } } }
    -- #770 Scrap Av
    ops[770] = { expectedWidth = 6, expectedPoints = { 13504, 2629, 13630, 2629 }, hideLabel = true, reference = { index = 801, width = 6, points = { 13504, 2629, 13630, 2629 } } }
    -- #771 Crow St
    ops[771] = { expectedWidth = 6, expectedPoints = { 13504, 2575, 13630, 2575 }, hideLabel = true, reference = { index = 802, width = 6, points = { 13504, 2575, 13630, 2575 } } }
    -- #772 Wetterau Dr
    ops[772] = { expectedWidth = 4, expectedPoints = { 13567, 2572, 13567, 2526 }, hideLabel = true, reference = { index = 803, width = 4, points = { 13567, 2572, 13567, 2526 } } }
    -- #773 Cheeky Chap Lane
    ops[773] = { expectedWidth = 6, expectedPoints = { 13458, 2585, 13496, 2585 }, hideLabel = true, reference = { index = 804, width = 6, points = { 13458, 2585, 13496, 2585 } } }
    -- #774 Forgotten St
    ops[774] = { expectedWidth = 6, expectedPoints = { 13410, 2849, 13455, 2849, 13455, 2792, 13496, 2792 }, hideLabel = true, reference = { index = 805, width = 6, points = { 13410, 2849, 13455, 2849, 13455, 2792, 13496, 2792 } } }
    -- #775 Old Market St
    ops[775] = { expectedWidth = 8, expectedPoints = { 13652, 3442, 13652, 3071, 13613, 3071 }, hideLabel = true, reference = { index = 806, width = 8, points = { 13652, 3442, 13652, 3071, 13613, 3071 } } }
    -- #776 Hog Squeal Lane
    ops[776] = { expectedWidth = 6, expectedPoints = { 13390, 1269, 13390, 1380 }, hideLabel = true, reference = { index = 807, width = 6, points = { 13390, 1269, 13390, 1380 } } }
    -- #777 Trotter St
    ops[777] = { expectedWidth = 10, expectedPoints = { 13205, 1425, 13282, 1425, 13282, 1269 }, hideLabel = true, reference = { index = 808, width = 10, points = { 13205, 1425, 13282, 1425, 13282, 1269 } } }
    -- #778 Muldraugh Cl
    ops[778] = { expectedWidth = 4, expectedPoints = { 13895, 2725, 13895, 2706 }, hideLabel = true, reference = { index = 809, width = 4, points = { 13895, 2725, 13895, 2706 } } }
    -- #779 Cuckoo St
    ops[779] = { expectedWidth = 6, expectedPoints = { 13758, 2717, 13758, 2846 }, hideLabel = true, reference = { index = 810, width = 6, points = { 13758, 2717, 13758, 2846 } } }
    -- #780 Duck St
    ops[780] = { expectedWidth = 6, expectedPoints = { 13761, 2794, 13797, 2794 }, hideLabel = true, reference = { index = 811, width = 6, points = { 13761, 2794, 13797, 2794 } } }
    -- #781 Egghatch St
    ops[781] = { expectedWidth = 6, expectedPoints = { 13803, 2794, 13873, 2794 }, hideLabel = true, reference = { index = 812, width = 6, points = { 13803, 2794, 13873, 2794 } } }
    -- #782 Falcon St
    ops[782] = { expectedWidth = 6, expectedPoints = { 13496, 2466, 13455, 2466, 13455, 2704, 13461, 2704, 13461, 2789 }, hideLabel = true, reference = { index = 813, width = 6, points = { 13496, 2466, 13455, 2466, 13455, 2704, 13461, 2704, 13461, 2789 } } }
    -- #783 N Fountain Av
    ops[783] = { expectedWidth = 6, expectedPoints = { 13421, 1803, 13421, 1837 }, hideLabel = true, reference = { index = 814, width = 6, points = { 13421, 1803, 13421, 1837 } } }
    -- #784 S Fountain Av
    ops[784] = { expectedWidth = 6, expectedPoints = { 13421, 1884, 13421, 1950 }, hideLabel = true, reference = { index = 815, width = 6, points = { 13421, 1884, 13421, 1950 } } }
    -- #785 Clay St
    ops[785] = { expectedWidth = 3, expectedPoints = { 13364, 1801.5, 13490, 1801.5 }, hideLabel = true, reference = { index = 816, width = 3, points = { 13364, 1801.5, 13490, 1801.5 } } }
    -- #786 Terrace St
    ops[786] = { expectedWidth = 6, expectedPoints = { 13493, 1803, 13493, 1666 }, hideLabel = true, reference = { index = 817, width = 6, points = { 13493, 1803, 13493, 1666 } } }
    -- #787 Derek Auton St
    ops[787] = { expectedWidth = 6, expectedPoints = { 13364, 1663, 13496, 1663 }, hideLabel = true, reference = { index = 818, width = 6, points = { 13364, 1663, 13496, 1663 } } }
    -- #788 Rathunt St
    ops[788] = { expectedWidth = 6, expectedPoints = { 13286, 1663, 13358, 1663 }, hideLabel = true, reference = { index = 819, width = 6, points = { 13286, 1663, 13358, 1663 } } }
    -- #789 Dancer St
    ops[789] = { expectedWidth = 6, expectedPoints = { 13496, 1731, 13641, 1731 }, hideLabel = true, reference = { index = 820, width = 6, points = { 13496, 1731, 13641, 1731 } } }
    -- #790 New Hunter St
    ops[790] = { expectedWidth = 6, expectedPoints = { 13541, 1728, 13541, 1555 }, hideLabel = true, reference = { index = 821, width = 6, points = { 13541, 1728, 13541, 1555 } } }
    -- #791 Old Hunter St
    ops[791] = { expectedWidth = 6, expectedPoints = { 13593, 1555, 13593, 1646, 13641, 1646 }, hideLabel = true, reference = { index = 822, width = 6, points = { 13593, 1555, 13593, 1646, 13641, 1646 } } }
    -- #792 Greengrass Lane
    ops[792] = { expectedWidth = 6, expectedPoints = { 13651, 1552, 13735, 1552 }, hideLabel = true, reference = { index = 823, width = 6, points = { 13651, 1552, 13735, 1552 } } }
    -- #793 Bass Road
    ops[793] = { expectedWidth = 6, expectedPoints = { 13651, 1498, 13782, 1498, 13782, 1248 }, hideLabel = true, reference = { index = 824, width = 6, points = { 13651, 1498, 13782, 1498, 13782, 1248 } } }
    -- #794 Hummingbird St
    ops[794] = { expectedWidth = 6, expectedPoints = { 13689, 2867, 13689, 2997 }, hideLabel = true, reference = { index = 825, width = 6, points = { 13689, 2867, 13689, 2997 } } }
    -- #795 Phoenix St
    ops[795] = { expectedWidth = 6, expectedPoints = { 13637, 3000, 13800, 3000 }, hideLabel = true, reference = { index = 826, width = 6, points = { 13637, 3000, 13800, 3000 } } }
    -- #796 Owl St
    ops[796] = { expectedWidth = 6, expectedPoints = { 13800, 3000, 13800, 3061 }, hideLabel = true, reference = { index = 827, width = 6, points = { 13800, 3000, 13800, 3061 } } }
    -- #797 Opal St
    ops[797] = { expectedWidth = 6, expectedPoints = { 13797, 3064, 13976, 3064 }, hideLabel = true, reference = { index = 828, width = 6, points = { 13797, 3064, 13976, 3064 } } }
    -- #798 Backside St
    ops[798] = { expectedWidth = 6, expectedPoints = { 13886, 3067, 13886, 3209, 13941, 3209, 13941, 3297 }, hideLabel = true, reference = { index = 829, width = 6, points = { 13886, 3067, 13886, 3209, 13941, 3209, 13941, 3297 } } }
    -- #799 Sapphire St
    ops[799] = { expectedWidth = 6, expectedPoints = { 13803, 2918, 13923.5, 2918, 13925, 2919.5, 13925, 3061 }, hideLabel = true, reference = { index = 830, width = 6, points = { 13803, 2918, 13923.5, 2918, 13925, 2919.5, 13925, 3061 } } }
    -- #800 Rice St
    ops[800] = { expectedWidth = 6, expectedPoints = { 13874, 3300, 13976, 3300 }, hideLabel = true, reference = { index = 831, width = 6, points = { 13874, 3300, 13976, 3300 } } }
    -- #801 Mosey Lane
    ops[801] = { expectedWidth = 6, expectedPoints = { 13922, 3303, 13922, 3354 }, hideLabel = true, reference = { index = 832, width = 6, points = { 13922, 3303, 13922, 3354 } } }
    -- #802 Diamond St
    ops[802] = { expectedWidth = 6, expectedPoints = { 13850, 2706, 13850, 2758, 13962, 2758, 13962, 3023 }, hideLabel = true, reference = { index = 833, width = 6, points = { 13850, 2706, 13850, 2758, 13962, 2758, 13962, 3023 } } }
    -- #803 Emerald St
    ops[803] = { expectedWidth = 6, expectedPoints = { 13803, 3026, 13965, 3026 }, hideLabel = true, reference = { index = 834, width = 6, points = { 13803, 3026, 13965, 3026 } } }
    -- #804 Jeweler St
    ops[804] = { expectedWidth = 6, expectedPoints = { 13840, 3023, 13840, 2921 }, hideLabel = true, reference = { index = 835, width = 6, points = { 13840, 3023, 13840, 2921 } } }
    -- #805 Quartz Cl
    ops[805] = { expectedWidth = 6, expectedPoints = { 13881, 2948, 13881, 3023 }, hideLabel = true, reference = { index = 836, width = 6, points = { 13881, 2948, 13881, 3023 } } }
    -- #806 Gem Lane
    ops[806] = { expectedWidth = 6, expectedPoints = { 13928, 2949, 13959, 2949 }, hideLabel = true, reference = { index = 837, width = 6, points = { 13928, 2949, 13959, 2949 } } }
    -- #807 Copper St
    ops[807] = { expectedWidth = 6, expectedPoints = { 13922, 2915, 13922, 2868 }, hideLabel = true, reference = { index = 838, width = 6, points = { 13922, 2915, 13922, 2868 } } }
    -- #808 Ruby St
    ops[808] = { expectedWidth = 6, expectedPoints = { 13803, 2865, 13959, 2865 }, hideLabel = true, reference = { index = 839, width = 6, points = { 13803, 2865, 13959, 2865 } } }
    -- #809 Gold St
    ops[809] = { expectedWidth = 6, expectedPoints = { 13876, 2761, 13876, 2826 }, hideLabel = true, reference = { index = 840, width = 6, points = { 13876, 2761, 13876, 2826 } } }
    -- #810 Silver St
    ops[810] = { expectedWidth = 6, expectedPoints = { 13852, 2862, 13852, 2829, 13959, 2829 }, hideLabel = true, reference = { index = 841, width = 6, points = { 13852, 2862, 13852, 2829, 13959, 2829 } } }
    -- #811 Henrietta Dr
    ops[811] = { expectedWidth = 5, expectedPoints = { 13656, 3071, 13722.5, 3071, 13722.5, 3132.5, 13656, 3132.5 }, hideLabel = true, reference = { index = 842, width = 5, points = { 13656, 3071, 13722.5, 3071, 13722.5, 3132.5, 13656, 3132.5 } } }
    -- #812 Captain Franks St
    ops[812] = { expectedWidth = 5, expectedPoints = { 13712.5, 3135, 13712.5, 3203 }, hideLabel = true, reference = { index = 843, width = 5, points = { 13712.5, 3135, 13712.5, 3203 } } }
    -- #813 Walnut Wood St
    ops[813] = { expectedWidth = 5, expectedPoints = { 13656, 3205.5, 13722.5, 3205.5, 13722.5, 3262 }, hideLabel = true, reference = { index = 844, width = 5, points = { 13656, 3205.5, 13722.5, 3205.5, 13722.5, 3262 } } }
    -- #814 Fishmonger Row
    ops[814] = { expectedWidth = 5, expectedPoints = { 13656, 3264.5, 13771.5, 3264.5, 13771.5, 3333.5, 13656, 3333.5 }, hideLabel = true, reference = { index = 845, width = 5, points = { 13656, 3264.5, 13771.5, 3264.5, 13771.5, 3333.5, 13656, 3333.5 } } }
    -- #815 Bluegill St
    ops[815] = { expectedWidth = 5, expectedPoints = { 13712.5, 3267, 13712.5, 3331 }, hideLabel = true, reference = { index = 846, width = 5, points = { 13712.5, 3267, 13712.5, 3331 } } }
    -- #816 Tanner St
    ops[816] = { expectedWidth = 6, expectedPoints = { 13277, 1306, 13168, 1306 }, hideLabel = true, reference = { index = 847, width = 6, points = { 13277, 1306, 13168, 1306 } } }
    -- #817 Leatherwork St
    ops[817] = { expectedWidth = 5, expectedPoints = { 13199.5, 1303, 13199.5, 1226.5, 13166.5, 1226.5, 13166.5, 1248 }, hideLabel = true, reference = { index = 848, width = 5, points = { 13199.5, 1303, 13199.5, 1226.5, 13166.5, 1226.5, 13166.5, 1248 } } }
    -- #818 Bone St
    ops[818] = { expectedWidth = 10, expectedPoints = { 13163, 1347, 13163, 1253 }, hideLabel = true, reference = { index = 849, width = 10, points = { 13163, 1347, 13163, 1253 } } }
    -- #819 Cows Lament St
    ops[819] = { expectedWidth = 5, expectedPoints = { 13168, 1250.5, 13111.5, 1250.5, 13111.5, 1262.5, 13058, 1262.5 }, hideLabel = true, reference = { index = 850, width = 5, points = { 13168, 1250.5, 13111.5, 1250.5, 13111.5, 1262.5, 13058, 1262.5 } } }
    -- #820 Louisville Expo St
    ops[820] = { expectedWidth = 10, expectedPoints = { 13053, 1233, 13053, 1347 }, hideLabel = true, reference = { index = 851, width = 10, points = { 13053, 1233, 13053, 1347 } } }
    -- #821 New York St
    ops[821] = { expectedWidth = 6, expectedPoints = { 12740, 1241, 12740, 1288, 12800, 1288, 12800, 1347 }, hideLabel = true, reference = { index = 852, width = 6, points = { 12740, 1241, 12740, 1288, 12800, 1288, 12800, 1347 } } }
    -- #822 Load Haul St
    ops[822] = { expectedWidth = 5, expectedPoints = { 12341.5, 1241, 12341.5, 1347 }, hideLabel = true, reference = { index = 853, width = 5, points = { 12341.5, 1241, 12341.5, 1347 } } }
    -- #823 Coughers St
    ops[823] = { expectedWidth = 7, expectedPoints = { 12162, 1298.5, 12252, 1298.5 }, hideLabel = true, reference = { index = 854, width = 7, points = { 12162, 1298.5, 12252, 1298.5 } } }
    -- #824 Old Sulphur St
    ops[824] = { expectedWidth = 5, expectedPoints = { 12258, 1298.5, 12339, 1298.5 }, hideLabel = true, reference = { index = 855, width = 5, points = { 12258, 1298.5, 12339, 1298.5 } } }
    -- #825 Hardhead Lane
    ops[825] = { expectedWidth = 4, expectedPoints = { 12300, 1296, 12300, 1256 }, hideLabel = true, reference = { index = 856, width = 4, points = { 12300, 1296, 12300, 1256 } } }
    -- #826 Gnarled Stump Lane
    ops[826] = { expectedWidth = 6, expectedPoints = { 12252, 1402, 12295, 1402 }, hideLabel = true, reference = { index = 857, width = 6, points = { 12252, 1402, 12295, 1402 } } }
    -- #827 Baseball St
    ops[827] = { expectedWidth = 6, expectedPoints = { 13099, 1505, 13099, 1651 }, hideLabel = true, reference = { index = 858, width = 6, points = { 13099, 1505, 13099, 1651 } } }
    -- #828 Outfield St
    ops[828] = { expectedWidth = 6, expectedPoints = { 13102, 1551, 13155, 1551, 13155, 1651 }, hideLabel = true, reference = { index = 859, width = 6, points = { 13102, 1551, 13155, 1551, 13155, 1651 } } }
    -- #829 Cartwheel St
    ops[829] = { expectedWidth = 6, expectedPoints = { 13280, 1500, 13280, 1855, 13205, 1855 }, hideLabel = true, reference = { index = 860, width = 6, points = { 13280, 1500, 13280, 1855, 13205, 1855 } } }
    -- #830 Tristan St
    ops[830] = { expectedWidth = 6, expectedPoints = { 13283, 1538, 13358, 1538 }, hideLabel = true, reference = { index = 861, width = 6, points = { 13283, 1538, 13358, 1538 } } }
    -- #831 Wagon Block Way
    ops[831] = { expectedWidth = 6, expectedPoints = { 13205, 1601, 13477, 1601 }, hideLabel = true, reference = { index = 862, width = 6, points = { 13205, 1601, 13477, 1601 } } }
    -- #832 Tin Pan Alley
    ops[832] = { expectedWidth = 6, expectedPoints = { 13400, 1555, 13400, 1660 }, hideLabel = true, reference = { index = 863, width = 6, points = { 13400, 1555, 13400, 1660 } } }
    -- #833 Wonder St
    ops[833] = { expectedWidth = 6, expectedPoints = { 13480, 1555, 13480, 1660 }, hideLabel = true, reference = { index = 864, width = 6, points = { 13480, 1555, 13480, 1660 } } }
    -- #834 Folks Lane
    ops[834] = { expectedWidth = 4, expectedPoints = { 13446, 1604, 13446, 1634, 13477, 1634 }, hideLabel = true, reference = { index = 865, width = 4, points = { 13446, 1604, 13446, 1634, 13477, 1634 } } }
    -- #835 Backway St
    ops[835] = { expectedWidth = 6, expectedPoints = { 13738, 1501, 13738, 1646, 13651, 1646 }, hideLabel = true, reference = { index = 866, width = 6, points = { 13738, 1501, 13738, 1646, 13651, 1646 } } }
    -- #836 Blackberry Lane
    ops[836] = { expectedWidth = 5, expectedPoints = { 13199.5, 2996, 13199.5, 2965 }, hideLabel = true, reference = { index = 867, width = 5, points = { 13199.5, 2996, 13199.5, 2965 } } }
    -- #837 Wisteria St
    ops[837] = { expectedWidth = 6, expectedPoints = { 13200, 3004, 13200, 3196 }, hideLabel = true, reference = { index = 868, width = 6, points = { 13200, 3004, 13200, 3196 } } }
    -- #838 Goldenrod St
    ops[838] = { expectedWidth = 6, expectedPoints = { 13197, 3199, 13501, 3199 }, hideLabel = true, reference = { index = 869, width = 6, points = { 13197, 3199, 13501, 3199 } } }
    -- #839 Fuchsia St
    ops[839] = { expectedWidth = 5, expectedPoints = { 13232.5, 3202, 13232.5, 3300.5, 13197, 3300.5 }, hideLabel = true, reference = { index = 870, width = 5, points = { 13232.5, 3202, 13232.5, 3300.5, 13197, 3300.5 } } }
    -- #840 Bluebell Dr
    ops[840] = { expectedWidth = 5, expectedPoints = { 13203, 3154.5, 13501, 3154.5 }, hideLabel = true, reference = { index = 871, width = 5, points = { 13203, 3154.5, 13501, 3154.5 } } }
    -- #841 Daffodil St
    ops[841] = { expectedWidth = 8, expectedPoints = { 13203, 3109, 13648, 3109 }, hideLabel = true, reference = { index = 872, width = 8, points = { 13203, 3109, 13648, 3109 } } }
    -- #842 Rose St
    ops[842] = { expectedWidth = 5, expectedPoints = { 13503.5, 3113, 13503.5, 3298 }, hideLabel = true, reference = { index = 873, width = 5, points = { 13503.5, 3113, 13503.5, 3298 } } }
    -- #843 Tulip St
    ops[843] = { expectedWidth = 5, expectedPoints = { 13235, 3241.5, 13648, 3241.5 }, hideLabel = true, reference = { index = 874, width = 5, points = { 13235, 3241.5, 13648, 3241.5 } } }
    -- #844 Marigold Dr
    ops[844] = { expectedWidth = 5, expectedPoints = { 13506, 3182.5, 13570, 3182.5 }, hideLabel = true, reference = { index = 875, width = 5, points = { 13506, 3182.5, 13570, 3182.5 } } }
    -- #845 Lavender Av
    ops[845] = { expectedWidth = 5, expectedPoints = { 13572.5, 3180, 13572.5, 3378 }, hideLabel = true, reference = { index = 876, width = 5, points = { 13572.5, 3180, 13572.5, 3378 } } }
    -- #846 Crabapple Cl
    ops[846] = { expectedWidth = 5, expectedPoints = { 13548.5, 3180, 13548.5, 3128 }, hideLabel = true, reference = { index = 877, width = 5, points = { 13548.5, 3180, 13548.5, 3128 } } }
    -- #847 Lilac St
    ops[847] = { expectedWidth = 5, expectedPoints = { 13551, 3145.5, 13605, 3145.5 }, hideLabel = true, reference = { index = 878, width = 5, points = { 13551, 3145.5, 13605, 3145.5 } } }
    -- #848 Ivy St
    ops[848] = { expectedWidth = 5, expectedPoints = { 13607.5, 3128, 13607.5, 3239 }, hideLabel = true, reference = { index = 879, width = 5, points = { 13607.5, 3128, 13607.5, 3239 } } }
    -- #849 Hazel Row
    ops[849] = { expectedWidth = 5, expectedPoints = { 13501, 3300.5, 13648, 3300.5 }, hideLabel = true, reference = { index = 880, width = 5, points = { 13501, 3300.5, 13648, 3300.5 } } }
    -- #850 Clover St
    ops[850] = { expectedWidth = 5, expectedPoints = { 13500, 3345.5, 13648, 3345.5 }, hideLabel = true, reference = { index = 881, width = 5, points = { 13500, 3345.5, 13648, 3345.5 } } }
    -- #851 Posey St
    ops[851] = { expectedWidth = 5, expectedPoints = { 13361, 3380.5, 13579, 3380.5 }, hideLabel = true, reference = { index = 882, width = 5, points = { 13361, 3380.5, 13579, 3380.5 } } }
    -- #852 Greenleaf St
    ops[852] = { expectedWidth = 5, expectedPoints = { 13412.5, 3300, 13412.5, 3378 }, hideLabel = true, reference = { index = 883, width = 5, points = { 13412.5, 3300, 13412.5, 3378 } } }
    -- #853 Petal Fall Dr
    ops[853] = { expectedWidth = 5, expectedPoints = { 13367.5, 3300, 13367.5, 3336.5, 13457.5, 3336.5, 13457.5, 3300 }, hideLabel = true, reference = { index = 884, width = 5, points = { 13367.5, 3300, 13367.5, 3336.5, 13457.5, 3336.5, 13457.5, 3300 } } }
    -- #854 Jasmine St
    ops[854] = { expectedWidth = 5, expectedPoints = { 13286.5, 3113, 13286.5, 3196 }, hideLabel = true, reference = { index = 885, width = 5, points = { 13286.5, 3113, 13286.5, 3196 } } }
    -- #855 Sweetblossom Lane
    ops[855] = { expectedWidth = 6, expectedPoints = { 13265, 3105, 13265, 3042 }, hideLabel = true, reference = { index = 886, width = 6, points = { 13265, 3105, 13265, 3042 } } }
    -- #856 Summer Cl
    ops[856] = { expectedWidth = 5, expectedPoints = { 13277.5, 3244, 13277.5, 3298 }, hideLabel = true, reference = { index = 887, width = 5, points = { 13277.5, 3244, 13277.5, 3298 } } }
    -- #857 Spring Cl
    ops[857] = { expectedWidth = 5, expectedPoints = { 13322.5, 3244, 13322.5, 3298 }, hideLabel = true, reference = { index = 888, width = 5, points = { 13322.5, 3244, 13322.5, 3298 } } }
    -- #858 Gray St
    ops[858] = { expectedWidth = 6, expectedPoints = { 12940, 3129, 13197, 3129 }, hideLabel = true, reference = { index = 889, width = 6, points = { 12940, 3129, 13197, 3129 } } }
    -- #859 Hyacinth St
    ops[859] = { expectedWidth = 8, expectedPoints = { 13496, 2894, 13414, 2894, 13414, 3105 }, hideLabel = true, reference = { index = 890, width = 8, points = { 13496, 2894, 13414, 2894, 13414, 3105 } } }
    -- #860 Northside Lane
    ops[860] = { expectedWidth = 6, expectedPoints = { 13353, 2150, 13353, 2192 }, hideLabel = true, reference = { index = 891, width = 6, points = { 13353, 2150, 13353, 2192 } } }
    -- #861 Tall Fence St
    ops[861] = { expectedWidth = 6, expectedPoints = { 13310, 2049, 13310, 2147, 13425, 2147 }, hideLabel = true, reference = { index = 892, width = 6, points = { 13310, 2049, 13310, 2147, 13425, 2147 } } }
    -- #862 Rest St
    ops[862] = { expectedWidth = 4, expectedPoints = { 13254, 2049, 13254, 2098 }, hideLabel = true, reference = { index = 893, width = 4, points = { 13254, 2049, 13254, 2098 } } }
    -- #863 Peaceful Haven St
    ops[863] = { expectedWidth = 6, expectedPoints = { 13205, 2046, 13351, 2046 }, hideLabel = true, reference = { index = 894, width = 6, points = { 13205, 2046, 13351, 2046 } } }
    -- #864 Euphoria St
    ops[864] = { expectedWidth = 6, expectedPoints = { 13354, 1960, 13354, 2070 }, hideLabel = true, reference = { index = 895, width = 6, points = { 13354, 1960, 13354, 2070 } } }
    -- #865 Heaven's Door St
    ops[865] = { expectedWidth = 6, expectedPoints = { 13205, 2002, 13351, 2002 }, hideLabel = true, reference = { index = 896, width = 6, points = { 13205, 2002, 13351, 2002 } } }
    -- #866 Ladykiss St
    ops[866] = { expectedWidth = 8, expectedPoints = { 13035, 1960, 13035, 2192 }, hideLabel = true, reference = { index = 897, width = 8, points = { 13035, 1960, 13035, 2192 } } }
    -- #867 Virginia Av
    ops[867] = { expectedWidth = 5, expectedPoints = { 12900.5, 2103, 12900.5, 1505 }, hideLabel = true, reference = { index = 898, width = 5, points = { 12900.5, 2103, 12900.5, 1505 } } }
    -- #868 Danson St
    ops[868] = { expectedWidth = 6, expectedPoints = { 12900, 1505, 12900, 1357 }, hideLabel = true, reference = { index = 899, width = 6, points = { 12900, 1505, 12900, 1357 } } }
    -- #869 Gear St
    ops[869] = { expectedWidth = 6, expectedPoints = { 13548, 1850, 13548, 1904 }, hideLabel = true, reference = { index = 900, width = 6, points = { 13548, 1850, 13548, 1904 } } }
    -- #870 Hammersong St
    ops[870] = { expectedWidth = 4, expectedPoints = { 13522, 1925, 13522, 1893, 13506, 1893 }, hideLabel = true, reference = { index = 901, width = 4, points = { 13522, 1925, 13522, 1893, 13506, 1893 } } }
    -- #871 Potter St
    ops[871] = { expectedWidth = 6, expectedPoints = { 13524, 1907, 13577, 1907 }, hideLabel = true, reference = { index = 902, width = 6, points = { 13524, 1907, 13577, 1907 } } }
    -- #872 Bricklayer St
    ops[872] = { expectedWidth = 4, expectedPoints = { 13575, 1910, 13575, 1957, 13544, 1957 }, hideLabel = true, reference = { index = 903, width = 4, points = { 13575, 1910, 13575, 1957, 13544, 1957 } } }
    -- #873 Heisenberg St
    ops[873] = { expectedWidth = 4, expectedPoints = { 13577, 1943, 13622, 1943 }, hideLabel = true, reference = { index = 904, width = 4, points = { 13577, 1943, 13622, 1943 } } }
    -- #874 Ray St
    ops[874] = { expectedWidth = 6, expectedPoints = { 13205, 1731, 13277, 1731 }, hideLabel = true, reference = { index = 905, width = 6, points = { 13205, 1731, 13277, 1731 } } }
    -- #875 Whistle Boy Lane
    ops[875] = { expectedWidth = 4, expectedPoints = { 13251, 1734, 13251, 1795, 13229, 1795 }, hideLabel = true, reference = { index = 906, width = 4, points = { 13251, 1734, 13251, 1795, 13229, 1795 } } }
    -- #876 Feast Dr
    ops[876] = { expectedWidth = 6, expectedPoints = { 13358, 1723, 13329, 1723, 13329, 1874 }, hideLabel = true, reference = { index = 907, width = 6, points = { 13358, 1723, 13329, 1723, 13329, 1874 } } }
    -- #877 Banquet Lane
    ops[877] = { expectedWidth = 3, expectedPoints = { 13283, 1801.5, 13326, 1801.5 }, hideLabel = true, reference = { index = 908, width = 3, points = { 13283, 1801.5, 13326, 1801.5 } } }
    -- #878 Hikes Lane
    ops[878] = { expectedWidth = 6, expectedPoints = { 13649.5, 1800, 13739, 1800, 13739, 1844 }, hideLabel = true, reference = { index = 909, width = 6, points = { 13649.5, 1800, 13739, 1800, 13739, 1844 } } }
    -- #879 Old Wall St
    ops[879] = { expectedWidth = 5, expectedPoints = { 13029.5, 3004, 13029.5, 3102 }, hideLabel = true, reference = { index = 910, width = 5, points = { 13029.5, 3004, 13029.5, 3102 } } }
    -- #880 Window St
    ops[880] = { expectedWidth = 5, expectedPoints = { 13032, 3071.5, 13118, 3071.5 }, hideLabel = true, reference = { index = 911, width = 5, points = { 13032, 3071.5, 13118, 3071.5 } } }
    -- #881 Bucket St
    ops[881] = { expectedWidth = 6, expectedPoints = { 13072, 3074, 13072, 3126 }, hideLabel = true, reference = { index = 912, width = 6, points = { 13072, 3074, 13072, 3126 } } }
    -- #882 Sweater St
    ops[882] = { expectedWidth = 5, expectedPoints = { 12984.5, 3004, 12984.5, 3126 }, hideLabel = true, reference = { index = 913, width = 5, points = { 12984.5, 3004, 12984.5, 3126 } } }
    -- #883 Christmas Row St
    ops[883] = { expectedWidth = 7, expectedPoints = { 12871.5, 3004, 12871.5, 3230 }, hideLabel = true, reference = { index = 914, width = 7, points = { 12871.5, 3004, 12871.5, 3230 } } }
    -- #884 Lantern St
    ops[884] = { expectedWidth = 7, expectedPoints = { 12704.5, 3004, 12704.5, 3397 }, hideLabel = true, reference = { index = 915, width = 7, points = { 12704.5, 3004, 12704.5, 3397 } } }
    -- #885 Angel St
    ops[885] = { expectedWidth = 8, expectedPoints = { 12936, 2706, 12936, 2996 }, hideLabel = true, reference = { index = 916, width = 8, points = { 12936, 2706, 12936, 2996 } } }
    -- #886 Luther St
    ops[886] = { expectedWidth = 8, expectedPoints = { 12753, 2702, 12940, 2702 }, hideLabel = true, reference = { index = 917, width = 8, points = { 12753, 2702, 12940, 2702 } } }
    -- #887 Worship St
    ops[887] = { expectedWidth = 5, expectedPoints = { 12750.5, 2698, 12750.5, 2919 }, hideLabel = true, reference = { index = 918, width = 5, points = { 12750.5, 2698, 12750.5, 2919 } } }
    -- #888 Sinner St
    ops[888] = { expectedWidth = 5, expectedPoints = { 12748, 2760.5, 12703.5, 2760.5, 12703.5, 2921.5, 12753, 2921.5 }, hideLabel = true, reference = { index = 919, width = 5, points = { 12748, 2760.5, 12703.5, 2760.5, 12703.5, 2921.5, 12753, 2921.5 } } }
    -- #889 Witchhunt St
    ops[889] = { expectedWidth = 5, expectedPoints = { 12798.5, 2706, 12798.5, 2827.5, 12753, 2827.5 }, hideLabel = true, reference = { index = 920, width = 5, points = { 12798.5, 2706, 12798.5, 2827.5, 12753, 2827.5 } } }
    -- #890 Burners St
    ops[890] = { expectedWidth = 6, expectedPoints = { 12842, 2706, 12842, 2865 }, hideLabel = true, reference = { index = 921, width = 6, points = { 12842, 2706, 12842, 2865 } } }
    -- #891 Remorse St
    ops[891] = { expectedWidth = 5, expectedPoints = { 12753, 2867.5, 12845, 2867.5 }, hideLabel = true, reference = { index = 922, width = 5, points = { 12753, 2867.5, 12845, 2867.5 } } }
    -- #892 Stonepress St
    ops[892] = { expectedWidth = 5, expectedPoints = { 12878.5, 2706, 12878.5, 2799.5, 12845, 2799.5 }, hideLabel = true, reference = { index = 923, width = 5, points = { 12878.5, 2706, 12878.5, 2799.5, 12845, 2799.5 } } }
    -- #893 Confessor St
    ops[893] = { expectedWidth = 5, expectedPoints = { 12797.5, 2870, 12797.5, 2996 }, hideLabel = true, reference = { index = 924, width = 5, points = { 12797.5, 2870, 12797.5, 2996 } } }
    -- #894 Penance Road
    ops[894] = { expectedWidth = 5, expectedPoints = { 12800, 2920.5, 12932, 2920.5 }, hideLabel = true, reference = { index = 925, width = 5, points = { 12800, 2920.5, 12932, 2920.5 } } }
    -- #895 Absolution St
    ops[895] = { expectedWidth = 5, expectedPoints = { 12899.5, 2923, 12899.5, 2960.5, 12800, 2960.5 }, hideLabel = true, reference = { index = 926, width = 5, points = { 12899.5, 2923, 12899.5, 2960.5, 12800, 2960.5 } } }
    -- #896 Cumberland Gap St
    ops[896] = { expectedWidth = 6, expectedPoints = { 12940, 2888, 13063, 2888, 13063, 2996 }, hideLabel = true, reference = { index = 927, width = 6, points = { 12940, 2888, 13063, 2888, 13063, 2996 } } }
    -- #897 Tennessee St
    ops[897] = { expectedWidth = 6, expectedPoints = { 12940, 2928, 13180, 2928 }, hideLabel = true, reference = { index = 928, width = 6, points = { 12940, 2928, 13180, 2928 } } }
    -- #898 Stuffing St
    ops[898] = { expectedWidth = 8, expectedPoints = { 12708, 3113, 12814, 3113 }, hideLabel = true, reference = { index = 929, width = 8, points = { 12708, 3113, 12814, 3113 } } }
    -- #899 Candle St
    ops[899] = { expectedWidth = 7, expectedPoints = { 12708, 3196.5, 12760, 3196.5 }, hideLabel = true, reference = { index = 930, width = 7, points = { 12708, 3196.5, 12760, 3196.5 } } }
    -- #900 Bethelehem St
    ops[900] = { expectedWidth = 8, expectedPoints = { 12701, 3401, 12899, 3401 }, hideLabel = true, reference = { index = 931, width = 8, points = { 12701, 3401, 12899, 3401 } } }
    -- #901 Star St
    ops[901] = { expectedWidth = 7, expectedPoints = { 12708, 3270.5, 12771.5, 3270.5, 12771.5, 3442 }, hideLabel = true, reference = { index = 932, width = 7, points = { 12708, 3270.5, 12771.5, 3270.5, 12771.5, 3442 } } }
    -- #902 Nazareth St
    ops[902] = { expectedWidth = 7, expectedPoints = { 12857.5, 3397, 12857.5, 3316 }, hideLabel = true, reference = { index = 933, width = 7, points = { 12857.5, 3397, 12857.5, 3316 } } }
    -- #903 Inn St
    ops[903] = { expectedWidth = 7, expectedPoints = { 12854, 3331.5, 12797, 3331.5 }, hideLabel = true, reference = { index = 934, width = 7, points = { 12854, 3331.5, 12797, 3331.5 } } }
    -- #904 Darker St
    ops[904] = { expectedWidth = 7, expectedPoints = { 12932, 3233.5, 12821.5, 3233.5, 12821.5, 3312.5, 12898, 3312.5 }, hideLabel = true, reference = { index = 935, width = 7, points = { 12932, 3233.5, 12821.5, 3233.5, 12821.5, 3312.5, 12898, 3312.5 } } }
    -- #905 New Oak St
    ops[905] = { expectedWidth = 5, expectedPoints = { 12940, 3258.5, 13044, 3258.5 }, hideLabel = true, reference = { index = 936, width = 5, points = { 12940, 3258.5, 13044, 3258.5 } } }
    -- #906 Yellow St
    ops[906] = { expectedWidth = 5, expectedPoints = { 13046.5, 3132.5, 13046.5, 3316.5 }, hideLabel = true, reference = { index = 937, width = 5, points = { 13046.5, 3132.5, 13046.5, 3316.5 } } }
    -- #907 Red Dr
    ops[907] = { expectedWidth = 5, expectedPoints = { 13049, 3172.5, 13107, 3172.5 }, hideLabel = true, reference = { index = 938, width = 5, points = { 13049, 3172.5, 13107, 3172.5 } } }
    -- #908 Clancy Cl
    ops[908] = { expectedWidth = 5, expectedPoints = { 12993.5, 3261, 12993.5, 3300 }, hideLabel = true, reference = { index = 939, width = 5, points = { 12993.5, 3261, 12993.5, 3300 } } }
    -- #909 Manger St
    ops[909] = { expectedWidth = 5, expectedPoints = { 12965.5, 3300, 12965.5, 3327 }, hideLabel = true, reference = { index = 940, width = 5, points = { 12965.5, 3300, 12965.5, 3327 } } }
    -- #910 Sheriff St
    ops[910] = { expectedWidth = 9, expectedPoints = { 12940, 3331.5, 13031, 3331.5 }, hideLabel = true, reference = { index = 941, width = 9, points = { 12940, 3331.5, 13031, 3331.5 } } }
    -- #911 Sycamore Court Loop
    ops[911] = { expectedWidth = 5, expectedPoints = { 13034, 3336, 13034, 3328, 13042.5, 3320, 13051, 3320, 13058.5, 3327.5, 13058.5, 3336.5, 13051, 3344.5, 13043.5, 3344.5, 13036.5, 3337.5 }, hideLabel = true, reference = { index = 942, width = 5, points = { 13034, 3336, 13034, 3328, 13042.5, 3320, 13051, 3320, 13058.5, 3327.5, 13058.5, 3336.5, 13051, 3344.5, 13043.5, 3344.5, 13036.5, 3337.5 } } }
    -- #912 Sheriff St
    ops[912] = { expectedWidth = 8, expectedPoints = { 13061.5, 3331.5, 13106.5, 3331.5, 13106, 3223.5 }, hideLabel = true, reference = { index = 943, width = 8, points = { 13061.5, 3331.5, 13106.5, 3331.5, 13106, 3223.5 } } }
    -- #913 S Sycamore Ct
    ops[913] = { expectedWidth = 4, expectedPoints = { 12976, 3370, 12976, 3402, 13047, 3402, 13047, 3370 }, hideLabel = true, reference = { index = 944, width = 4, points = { 12976, 3370, 12976, 3402, 13047, 3402, 13047, 3370 } } }
    -- #914 N Sycamore Ct
    ops[914] = { expectedWidth = 4, expectedPoints = { 12976, 3336, 12976, 3368, 13047, 3368, 13047, 3347 }, hideLabel = true, reference = { index = 945, width = 4, points = { 12976, 3336, 12976, 3368, 13047, 3368, 13047, 3347 } } }
    -- #915 Grenadiers Row
    ops[915] = { expectedWidth = 5, expectedPoints = { 13276, 2242.5, 13346, 2242.5 }, hideLabel = true, reference = { index = 946, width = 5, points = { 13276, 2242.5, 13346, 2242.5 } } }
    -- #916 First Class St
    ops[916] = { expectedWidth = 4, expectedPoints = { 13392, 2150, 13392, 2302 }, hideLabel = true, reference = { index = 947, width = 4, points = { 13392, 2150, 13392, 2302 } } }
    -- #917 Cobbler St
    ops[917] = { expectedWidth = 4, expectedPoints = { 13394, 2270, 13425, 2270 }, hideLabel = true, reference = { index = 948, width = 4, points = { 13394, 2270, 13425, 2270 } } }
    -- #918 Goodboot St
    ops[918] = { expectedWidth = 4, expectedPoints = { 13431, 2270, 13496, 2270 }, hideLabel = true, reference = { index = 949, width = 4, points = { 13431, 2270, 13496, 2270 } } }
    -- #919 March Ridge St
    ops[919] = { expectedWidth = 4, expectedPoints = { 13431, 2191, 13465, 2191 }, hideLabel = true, reference = { index = 950, width = 4, points = { 13431, 2191, 13465, 2191 } } }
    -- #920 Recruiter Dr
    ops[920] = { expectedWidth = 4, expectedPoints = { 13467, 2103, 13467, 2268 }, hideLabel = true, reference = { index = 951, width = 4, points = { 13467, 2103, 13467, 2268 } } }
    -- #921 Miracle St
    ops[921] = { expectedWidth = 6, expectedPoints = { 13457, 1960, 13457, 2097 }, hideLabel = true, reference = { index = 952, width = 6, points = { 13457, 1960, 13457, 2097 } } }
    -- #922 Purple Cove St
    ops[922] = { expectedWidth = 5, expectedPoints = { 13454, 1993.5, 13388.5, 1993.5, 13388.5, 2096.5 }, hideLabel = true, reference = { index = 953, width = 5, points = { 13454, 1993.5, 13388.5, 1993.5, 13388.5, 2096.5 } } }
    -- #923 Jobs Lament St
    ops[923] = { expectedWidth = 4, expectedPoints = { 13454, 2032, 13391, 2032 }, hideLabel = true, reference = { index = 954, width = 4, points = { 13454, 2032, 13391, 2032 } } }
    -- #924 Ponderosa St
    ops[924] = { expectedWidth = 6, expectedPoints = { 12800, 1505, 12800, 1651 }, hideLabel = true, reference = { index = 955, width = 6, points = { 12800, 1505, 12800, 1651 } } }
    -- #925 Pigeon St
    ops[925] = { expectedWidth = 7, expectedPoints = { 12755, 3566.5, 12789.5, 3532, 12789.5, 3499 }, hideLabel = true, reference = { index = 956, width = 7, points = { 12755, 3566.5, 12789.5, 3532, 12789.5, 3499 } } }
    -- #926 Cutpurse St
    ops[926] = { expectedWidth = 6, expectedPoints = { 13195, 2099, 13099, 2099, 13099, 2192 }, hideLabel = true, reference = { index = 957, width = 6, points = { 13195, 2099, 13099, 2099, 13099, 2192 } } }
    -- #927 Mens St
    ops[927] = { expectedWidth = 6, expectedPoints = { 13099, 1661, 13099, 1795 }, hideLabel = true, reference = { index = 958, width = 6, points = { 13099, 1661, 13099, 1795 } } }
    -- #928 Womens St
    ops[928] = { expectedWidth = 6, expectedPoints = { 13155, 1661, 13155, 1795 }, hideLabel = true, reference = { index = 959, width = 6, points = { 13155, 1661, 13155, 1795 } } }
    -- #929 Fresno St
    ops[929] = { expectedWidth = 10, expectedPoints = { 12685, 1505, 12685, 1651 }, hideLabel = true, reference = { index = 960, width = 10, points = { 12685, 1505, 12685, 1651 } } }
    -- #930 San Francisco St
    ops[930] = { expectedWidth = 10, expectedPoints = { 12685, 1357, 12685, 1495 }, hideLabel = true, reference = { index = 961, width = 10, points = { 12685, 1357, 12685, 1495 } } }
    -- #931 California St
    ops[931] = { expectedWidth = 5, expectedPoints = { 12800.5, 1357, 12800.5, 1495 }, hideLabel = true, reference = { index = 962, width = 5, points = { 12800.5, 1357, 12800.5, 1495 } } }
    -- #932 Gods Mercy St
    ops[932] = { expectedWidth = 6, expectedPoints = { 13167, 1805, 13167, 1950 }, hideLabel = true, reference = { index = 963, width = 6, points = { 13167, 1805, 13167, 1950 } } }
    -- #933 Destiny St
    ops[933] = { expectedWidth = 5, expectedPoints = { 13164, 1852.5, 13126, 1852.5 }, hideLabel = true, reference = { index = 964, width = 5, points = { 13164, 1852.5, 13126, 1852.5 } } }
    -- #934 Eve St
    ops[934] = { expectedWidth = 5, expectedPoints = { 13164, 1900.5, 13126, 1900.5 }, hideLabel = true, reference = { index = 965, width = 5, points = { 13164, 1900.5, 13126, 1900.5 } } }
    -- #935 United States St
    ops[935] = { expectedWidth = 5, expectedPoints = { 13098.5, 1805, 13098.5, 1950 }, hideLabel = true, reference = { index = 966, width = 5, points = { 13098.5, 1805, 13098.5, 1950 } } }
    -- #936 Surrender St
    ops[936] = { expectedWidth = 5, expectedPoints = { 13096, 1900.5, 13037, 1900.5 }, hideLabel = true, reference = { index = 967, width = 5, points = { 13096, 1900.5, 13037, 1900.5 } } }
    -- #937 Stonewall St
    ops[937] = { expectedWidth = 5, expectedPoints = { 12953, 1854.5, 13037, 1854.5 }, hideLabel = true, reference = { index = 968, width = 5, points = { 12953, 1854.5, 13037, 1854.5 } } }
    -- #938 Lee St
    ops[938] = { expectedWidth = 5, expectedPoints = { 12955.5, 1805, 12955.5, 1852 }, hideLabel = true, reference = { index = 969, width = 5, points = { 12955.5, 1805, 12955.5, 1852 } } }
    -- #939 Davis St
    ops[939] = { expectedWidth = 5, expectedPoints = { 13034.5, 1805, 13034.5, 1852 }, hideLabel = true, reference = { index = 970, width = 5, points = { 13034.5, 1805, 13034.5, 1852 } } }
    -- #940 New Venture St
    ops[940] = { expectedWidth = 6, expectedPoints = { 13480, 1803, 13480, 1919 }, hideLabel = true, reference = { index = 971, width = 6, points = { 13480, 1803, 13480, 1919 } } }
    -- #941 Fountain View Dr
    ops[941] = { expectedWidth = 6, expectedPoints = { 13477, 1860, 13444, 1860 }, hideLabel = true, reference = { index = 972, width = 6, points = { 13477, 1860, 13444, 1860 } } }
    -- #942 Old Mule St
    ops[942] = { expectedWidth = 5, expectedPoints = { 13361, 1907, 13361, 1919.5, 13418, 1919.5 }, hideLabel = true, reference = { index = 973, width = 5, points = { 13361, 1907, 13361, 1919.5, 13418, 1919.5 } } }
    -- #943 Robbers Hide St
    ops[943] = { expectedWidth = 4, expectedPoints = { 13277, 1551, 13233, 1551, 13233, 1500 }, hideLabel = true, reference = { index = 974, width = 4, points = { 13277, 1551, 13233, 1551, 13233, 1500 } } }
    -- #944 Music Hall St
    ops[944] = { expectedWidth = 10, expectedPoints = { 12506, 1661, 12506, 1795 }, hideLabel = true, reference = { index = 975, width = 10, points = { 12506, 1661, 12506, 1795 } } }
    -- #945 Romero St
    ops[945] = { expectedWidth = 11, expectedPoints = { 12505.5, 1805, 12505.5, 1960 }, hideLabel = true, reference = { index = 976, width = 11, points = { 12505.5, 1805, 12505.5, 1960 } } }
    -- #946 Savini St
    ops[946] = { expectedWidth = 4, expectedPoints = { 12551, 1805, 12551, 1950 }, hideLabel = true, reference = { index = 977, width = 4, points = { 12551, 1805, 12551, 1950 } } }
    -- #947 Boyle St
    ops[947] = { expectedWidth = 5, expectedPoints = { 12592, 1855.5, 12512, 1855.5 }, hideLabel = true, reference = { index = 978, width = 5, points = { 12592, 1855.5, 12512, 1855.5 } } }
    -- #948 Coyote St
    ops[948] = { expectedWidth = 5, expectedPoints = { 12530.5, 1810, 12530.5, 1946 }, hideLabel = true, reference = { index = 979, width = 5, points = { 12530.5, 1810, 12530.5, 1946 } } }
    -- #949 Spark St
    ops[949] = { expectedWidth = 7, expectedPoints = { 12214.5, 1503, 12214.5, 1561.5 }, hideLabel = true, reference = { index = 980, width = 7, points = { 12214.5, 1503, 12214.5, 1561.5 } } }
    -- #950 Tang St
    ops[950] = { expectedWidth = 5, expectedPoints = { 12260.5, 1503, 12260.5, 1540 }, hideLabel = true, reference = { index = 981, width = 5, points = { 12260.5, 1503, 12260.5, 1540 } } }
    -- #951 Doffcap St
    ops[951] = { expectedWidth = 10, expectedPoints = { 12607, 2263, 12905.5, 2263 }, hideLabel = true, reference = { index = 982, width = 10, points = { 12607, 2263, 12905.5, 2263 } } }
    -- #952 Lace Curtain St
    ops[952] = { expectedWidth = 7, expectedPoints = { 12295, 1872.5, 12185, 1872.5 }, hideLabel = true, reference = { index = 983, width = 7, points = { 12295, 1872.5, 12185, 1872.5 } } }
    -- #953 Kenmare St
    ops[953] = { expectedWidth = 7, expectedPoints = { 12181.5, 1857, 12181.5, 2064.5 }, hideLabel = true, reference = { index = 984, width = 7, points = { 12181.5, 1857, 12181.5, 2064.5 } } }
    -- #954 Limerick St
    ops[954] = { expectedWidth = 7, expectedPoints = { 12254.5, 1876, 12254.5, 2013 }, hideLabel = true, reference = { index = 985, width = 7, points = { 12254.5, 1876, 12254.5, 2013 } } }
    -- #955 Golden Vale St
    ops[955] = { expectedWidth = 7, expectedPoints = { 12185, 2016.5, 12280, 2016.5 }, hideLabel = true, reference = { index = 986, width = 7, points = { 12185, 2016.5, 12280, 2016.5 } } }
    -- #956 Brigid St
    ops[956] = { expectedWidth = 5, expectedPoints = { 12128.5, 2073, 12128.5, 2169 }, hideLabel = true, reference = { index = 987, width = 5, points = { 12128.5, 2073, 12128.5, 2169 } } }
    -- #957 Francis St
    ops[957] = { expectedWidth = 5, expectedPoints = { 12117, 2171.5, 12239.5, 2171.5, 12239.5, 2073 }, hideLabel = true, reference = { index = 988, width = 5, points = { 12117, 2171.5, 12239.5, 2171.5, 12239.5, 2073 } } }
    -- #958 Mary St
    ops[958] = { expectedWidth = 5, expectedPoints = { 12198.5, 2100, 12198.5, 2304 }, hideLabel = true, reference = { index = 989, width = 5, points = { 12198.5, 2100, 12198.5, 2304 } } }
    -- #959 Cross St
    ops[959] = { expectedWidth = 5, expectedPoints = { 12262.5, 2154, 12262.5, 2346 }, hideLabel = true, reference = { index = 990, width = 5, points = { 12262.5, 2154, 12262.5, 2346 } } }
    -- #960 Joseph St
    ops[960] = { expectedWidth = 5, expectedPoints = { 12201, 2216.5, 12295, 2216.5 }, hideLabel = true, reference = { index = 991, width = 5, points = { 12201, 2216.5, 12295, 2216.5 } } }
    -- #961 Boru St
    ops[961] = { expectedWidth = 5, expectedPoints = { 12236, 2348.5, 12284, 2348.5 }, hideLabel = true, reference = { index = 992, width = 5, points = { 12236, 2348.5, 12284, 2348.5 } } }
    -- #962 Shawnee St
    ops[962] = { expectedWidth = 5, expectedPoints = { 12072, 2471.5, 12295, 2471.5 }, hideLabel = true, reference = { index = 993, width = 5, points = { 12072, 2471.5, 12295, 2471.5 } } }
    -- #963 Dublin St
    ops[963] = { expectedWidth = 5, expectedPoints = { 12166, 2306.5, 12233.5, 2306.5, 12233.5, 2400 }, hideLabel = true, reference = { index = 994, width = 5, points = { 12166, 2306.5, 12233.5, 2306.5, 12233.5, 2400 } } }
    -- #964 De Valera St
    ops[964] = { expectedWidth = 5, expectedPoints = { 12163.5, 2304, 12163.5, 2547 }, hideLabel = true, reference = { index = 995, width = 5, points = { 12163.5, 2304, 12163.5, 2547 } } }
    -- #965 Kerry Lane
    ops[965] = { expectedWidth = 3, expectedPoints = { 12088, 2401.5, 12161, 2401.5 }, hideLabel = true, reference = { index = 996, width = 3, points = { 12088, 2401.5, 12161, 2401.5 } } }
    -- #966 Central Lane
    ops[966] = { expectedWidth = 5, expectedPoints = { 12520, 2700.5, 12555, 2700.5 }, hideLabel = true, reference = { index = 997, width = 5, points = { 12520, 2700.5, 12555, 2700.5 } } }
    -- #967 Widow Johnson St
    ops[967] = { expectedWidth = 5, expectedPoints = { 12639, 2635.5, 12557.5, 2635.5, 12557.5, 2754 }, hideLabel = true, reference = { index = 998, width = 5, points = { 12639, 2635.5, 12557.5, 2635.5, 12557.5, 2754 } } }
    -- #968 Bulls Anger St
    ops[968] = { expectedWidth = 5, expectedPoints = { 12606.5, 2638, 12606.5, 2659, 12626.5, 2679, 12626.5, 2756.5, 12555, 2756.5 }, hideLabel = true, reference = { index = 999, width = 5, points = { 12606.5, 2638, 12606.5, 2659, 12626.5, 2679, 12626.5, 2756.5, 12555, 2756.5 } } }
    -- #969 Early Riser St
    ops[969] = { expectedWidth = 5, expectedPoints = { 12595.5, 2759, 12595.5, 2836.5 }, hideLabel = true, reference = { index = 1000, width = 5, points = { 12595.5, 2759, 12595.5, 2836.5 } } }
    -- #970 Ulster St
    ops[970] = { expectedWidth = 6, expectedPoints = { 12900, 2268, 12900, 2698 }, hideLabel = true, reference = { index = 1001, width = 6, points = { 12900, 2268, 12900, 2698 } } }
    -- #971 Scots St
    ops[971] = { expectedWidth = 6, expectedPoints = { 12687, 1805, 12687, 1950 }, hideLabel = true, reference = { index = 1002, width = 6, points = { 12687, 1805, 12687, 1950 } } }
    -- #972 Leitrim St
    ops[972] = { expectedWidth = 6, expectedPoints = { 12388, 1857, 12309, 1857 }, hideLabel = true, reference = { index = 1003, width = 6, points = { 12388, 1857, 12309, 1857 } } }
    -- #973 Mayo St
    ops[973] = { expectedWidth = 7, expectedPoints = { 12388, 1829.5, 12313, 1829.5 }, hideLabel = true, reference = { index = 1004, width = 7, points = { 12388, 1829.5, 12313, 1829.5 } } }
    -- #974 Spinster St
    ops[974] = { expectedWidth = 5, expectedPoints = { 12398, 1827.5, 12490, 1827.5 }, hideLabel = true, reference = { index = 1005, width = 5, points = { 12398, 1827.5, 12490, 1827.5 } } }
    -- #975 Cherokee St
    ops[975] = { expectedWidth = 5, expectedPoints = { 12305, 2033.5, 12501, 2033.5 }, hideLabel = true, reference = { index = 1006, width = 5, points = { 12305, 2033.5, 12501, 2033.5 } } }
    -- #976 Creek St
    ops[976] = { expectedWidth = 9, expectedPoints = { 12305, 2098.5, 12501, 2098.5 }, hideLabel = true, reference = { index = 1007, width = 9, points = { 12305, 2098.5, 12501, 2098.5 } } }
    -- #977 Hatbox St
    ops[977] = { expectedWidth = 8, expectedPoints = { 12351, 2519, 12351, 2567 }, hideLabel = true, reference = { index = 1008, width = 8, points = { 12351, 2519, 12351, 2567 } } }
    -- #978 Pike St
    ops[978] = { expectedWidth = 10, expectedPoints = { 12506, 1960, 12506, 2388 }, hideLabel = true, reference = { index = 1009, width = 10, points = { 12506, 1960, 12506, 2388 } } }
    -- #979 Old Seminary Road
    ops[979] = { expectedWidth = 7, expectedPoints = { 12321, 2191.5, 12501, 2191.5 }, hideLabel = true, reference = { index = 1010, width = 7, points = { 12321, 2191.5, 12501, 2191.5 } } }
    -- #980 Graduate St
    ops[980] = { expectedWidth = 7, expectedPoints = { 12317.5, 2103, 12317.5, 2323 }, hideLabel = true, reference = { index = 1011, width = 7, points = { 12317.5, 2103, 12317.5, 2323 } } }
    -- #981 Geoffrey R. Rogers St
    ops[981] = { expectedWidth = 11, expectedPoints = { 12305, 2327.5, 12501, 2327.5 }, hideLabel = true, reference = { index = 1012, width = 11, points = { 12305, 2327.5, 12501, 2327.5 } } }
    -- #982 University St
    ops[982] = { expectedWidth = 9, expectedPoints = { 12481.5, 2195, 12481.5, 2322 }, hideLabel = true, reference = { index = 1013, width = 9, points = { 12481.5, 2195, 12481.5, 2322 } } }
    -- #983 Vinegar Hill
    ops[983] = { expectedWidth = 5, expectedPoints = { 12361, 2031, 12361, 2005.5, 12309, 2005.5 }, hideLabel = true, reference = { index = 1014, width = 5, points = { 12361, 2031, 12361, 2005.5, 12309, 2005.5 } } }
    -- #984 Seventh Seal St
    ops[984] = { expectedWidth = 10, expectedPoints = { 12511, 2155, 12607, 2155 }, hideLabel = true, reference = { index = 1015, width = 10, points = { 12511, 2155, 12607, 2155 } } }
    -- #985 Merciful St
    ops[985] = { expectedWidth = 11, expectedPoints = { 12601.5, 2160, 12601.5, 2314 }, hideLabel = true, reference = { index = 1016, width = 11, points = { 12601.5, 2160, 12601.5, 2314 } } }
    -- #986 Back Rail Lane
    ops[986] = { expectedWidth = 5, expectedPoints = { 12598.5, 2314, 12598.5, 2388 }, hideLabel = true, reference = { index = 1017, width = 5, points = { 12598.5, 2314, 12598.5, 2388 } } }
    -- #987 Station Road
    ops[987] = { expectedWidth = 10, expectedPoints = { 12607, 2309, 12654, 2309, 12654, 2393, 12580, 2393, 12501, 2393 }, hideLabel = true, reference = { index = 1018, width = 10, points = { 12607, 2309, 12654, 2309, 12654, 2393, 12580, 2393, 12501, 2393 } } }
    -- #988 Daniel Boone St
    ops[988] = { expectedWidth = 10, expectedPoints = { 12685, 1960, 12685, 2258 }, hideLabel = true, reference = { index = 1019, width = 10, points = { 12685, 1960, 12685, 2258 } } }
    -- #989 Quarantine Lane
    ops[989] = { expectedWidth = 6, expectedPoints = { 12903, 2439, 13009, 2439 }, hideLabel = true, reference = { index = 1020, width = 6, points = { 12903, 2439, 13009, 2439 } } }
    -- #990 Pit St
    ops[990] = { expectedWidth = 6, expectedPoints = { 12934, 2442, 12934, 2638 }, hideLabel = true, reference = { index = 1021, width = 6, points = { 12934, 2442, 12934, 2638 } } }
    -- #991 Coffin St
    ops[991] = { expectedWidth = 6, expectedPoints = { 12970, 2442, 12970, 2638 }, hideLabel = true, reference = { index = 1022, width = 6, points = { 12970, 2442, 12970, 2638 } } }
    -- #992 Blackcloak St
    ops[992] = { expectedWidth = 6, expectedPoints = { 12903, 2641, 12973, 2641 }, hideLabel = true, reference = { index = 1023, width = 6, points = { 12903, 2641, 12973, 2641 } } }
    -- #993 Mourners Lane
    ops[993] = { expectedWidth = 5, expectedPoints = { 12903, 2540.5, 12931, 2540.5 }, hideLabel = true, reference = { index = 1024, width = 5, points = { 12903, 2540.5, 12931, 2540.5 } } }
    -- #994 Mourners Lane
    ops[994] = { expectedWidth = 5, expectedPoints = { 12937, 2540.5, 12967, 2540.5 }, hideLabel = true, reference = { index = 1025, width = 5, points = { 12937, 2540.5, 12967, 2540.5 } } }
    -- #995 Last Up St
    ops[995] = { expectedWidth = 6, expectedPoints = { 12612, 2633, 12612, 2580 }, hideLabel = true, reference = { index = 1026, width = 6, points = { 12612, 2633, 12612, 2580 } } }
    -- #996 San Jose St
    ops[996] = { expectedWidth = 6, expectedPoints = { 12683, 1661, 12683, 1727, 12850, 1727, 12850, 1778 }, hideLabel = true, reference = { index = 1027, width = 6, points = { 12683, 1661, 12683, 1727, 12850, 1727, 12850, 1778 } } }
    -- #997 Bakersfield Road
    ops[997] = { expectedWidth = 4, expectedPoints = { 12903, 1719, 12956, 1719, 12956, 1795 }, hideLabel = true, reference = { index = 1028, width = 4, points = { 12903, 1719, 12956, 1719, 12956, 1795 } } }
    -- #998 Sacramento St
    ops[998] = { expectedWidth = 5, expectedPoints = { 12800.5, 1661, 12800.5, 1795 }, hideLabel = true, reference = { index = 1029, width = 5, points = { 12800.5, 1661, 12800.5, 1795 } } }
    -- #999 Legiron St
    ops[999] = { expectedWidth = 10, expectedPoints = { 12506, 1651, 12506, 1579 }, hideLabel = true, reference = { index = 1030, width = 10, points = { 12506, 1651, 12506, 1579 } } }
    -- #1000 Courthouse St
    ops[1000] = { expectedWidth = 10, expectedPoints = { 12506, 1505, 12506, 1569 }, hideLabel = true, reference = { index = 1031, width = 10, points = { 12506, 1505, 12506, 1569 } } }
    -- #1001 Lincoln St
    ops[1001] = { expectedWidth = 6, expectedPoints = { 12818, 1805, 12818, 1837, 12898, 1837 }, hideLabel = true, reference = { index = 1032, width = 6, points = { 12818, 1805, 12818, 1837, 12898, 1837 } } }
    -- #1002 Bull Run St
    ops[1002] = { expectedWidth = 5, expectedPoints = { 12903, 1877.5, 12953, 1877.5 }, hideLabel = true, reference = { index = 1033, width = 5, points = { 12903, 1877.5, 12953, 1877.5 } } }
    -- #1003 Chickasaw Road
    ops[1003] = { expectedWidth = 5, expectedPoints = { 12744.5, 1960, 12744.5, 2098 }, hideLabel = true, reference = { index = 1034, width = 5, points = { 12744.5, 1960, 12744.5, 2098 } } }
    -- #1004 James Harrod St
    ops[1004] = { expectedWidth = 7, expectedPoints = { 12747.5, 2013.5, 12898.5, 2013.5 }, hideLabel = true, reference = { index = 1035, width = 7, points = { 12747.5, 2013.5, 12898.5, 2013.5 } } }
    -- #1005 Dunmore St
    ops[1005] = { expectedWidth = 5, expectedPoints = { 12822.5, 2103, 12822.5, 2219.5, 12895, 2219.5 }, hideLabel = true, reference = { index = 1036, width = 5, points = { 12822.5, 2103, 12822.5, 2219.5, 12895, 2219.5 } } }
    -- #1006 Highland St
    ops[1006] = { expectedWidth = 5, expectedPoints = { 12820, 2153.5, 12779, 2153.5 }, hideLabel = true, reference = { index = 1037, width = 5, points = { 12820, 2153.5, 12779, 2153.5 } } }
    -- #1007 Lewis and Clark St
    ops[1007] = { expectedWidth = 10, expectedPoints = { 12999, 1495, 12999, 1357 }, hideLabel = true, reference = { index = 1038, width = 10, points = { 12999, 1495, 12999, 1357 } } }
    -- #1008 Chapelmount Access Road
    ops[1008] = { expectedWidth = 5, expectedPoints = { 12506, 2699, 12431, 2699, 12416, 2683.5, 12407, 2683.5, 12403.5, 2687, 12403.5, 2721.5, 12410.5, 2728.5, 12421.5, 2728, 12430.5, 2719.5, 12430.5, 2702 }, hideLabel = true, reference = { index = 1039, width = 5, points = { 12506, 2699, 12431, 2699, 12416, 2683.5, 12407, 2683.5, 12403.5, 2687, 12403.5, 2721.5, 12410.5, 2728.5, 12421.5, 2728, 12430.5, 2719.5, 12430.5, 2702 } } }
    -- #1009 Manfall St
    ops[1009] = { expectedWidth = 8, expectedPoints = { 12208.5, 2997, 12208.5, 2941, 12174, 2941 }, hideLabel = true, reference = { index = 1040, width = 8, points = { 12208.5, 2997, 12208.5, 2941, 12174, 2941 } } }
    -- #1010 W Maple Court St
    ops[1010] = { expectedWidth = 13, expectedPoints = { 12256.5, 2997, 12256.5, 2866 }, hideLabel = true, reference = { index = 1041, width = 13, points = { 12256.5, 2997, 12256.5, 2866 } } }
    -- #1011 N Maple Court St
    ops[1011] = { expectedWidth = 15, expectedPoints = { 12263, 2912.5, 12468, 2912.5 }, hideLabel = true, reference = { index = 1042, width = 15, points = { 12263, 2912.5, 12468, 2912.5 } } }
    -- #1012 Garibaldi St
    ops[1012] = { expectedWidth = 6, expectedPoints = { 12398, 3003, 12398, 3089 }, hideLabel = true, reference = { index = 1043, width = 6, points = { 12398, 3003, 12398, 3089 } } }
    -- #1013 River St
    ops[1013] = { expectedWidth = 5, expectedPoints = { 12182, 3146.5, 12254, 3146.5 }, hideLabel = true, reference = { index = 1044, width = 5, points = { 12182, 3146.5, 12254, 3146.5 } } }
    -- #1014 Beech Row
    ops[1014] = { expectedWidth = 5, expectedPoints = { 12209.5, 3149, 12209.5, 3188 }, hideLabel = true, reference = { index = 1045, width = 5, points = { 12209.5, 3149, 12209.5, 3188 } } }
    -- #1015 Sandra Mallard St
    ops[1015] = { expectedWidth = 7, expectedPoints = { 12311.5, 3092, 12420, 3092, 12420, 3244.5, 12506, 3244.5 }, hideLabel = true, reference = { index = 1046, width = 7, points = { 12311.5, 3092, 12420, 3092, 12420, 3244.5, 12506, 3244.5 } } }
    -- #1016 Hyena St
    ops[1016] = { expectedWidth = 6, expectedPoints = { 12423.5, 3177, 12489, 3177 }, hideLabel = true, reference = { index = 1047, width = 6, points = { 12423.5, 3177, 12489, 3177 } } }
    -- #1017 Carson St
    ops[1017] = { expectedWidth = 6, expectedPoints = { 12339, 3095.5, 12339, 3216 }, hideLabel = true, reference = { index = 1048, width = 6, points = { 12339, 3095.5, 12339, 3216 } } }
    -- #1018 Tincture Lane
    ops[1018] = { expectedWidth = 5, expectedPoints = { 12337.5, 3327, 12337.5, 3413.5 }, hideLabel = true, reference = { index = 1049, width = 5, points = { 12337.5, 3327, 12337.5, 3413.5 } } }
    -- #1019 Chemist St
    ops[1019] = { expectedWidth = 5, expectedPoints = { 12340, 3391.5, 12430.5, 3391.5, 12430.5, 3327 }, hideLabel = true, reference = { index = 1050, width = 5, points = { 12340, 3391.5, 12430.5, 3391.5, 12430.5, 3327 } } }
    -- #1020 Kneeslap Lane
    ops[1020] = { expectedWidth = 6, expectedPoints = { 12484, 3248, 12484, 3403 }, hideLabel = true, reference = { index = 1051, width = 6, points = { 12484, 3248, 12484, 3403 } } }
    -- #1021 St Peregrine St
    ops[1021] = { expectedWidth = 6, expectedPoints = { 12349, 3513, 12349, 3600 }, hideLabel = true, reference = { index = 1052, width = 6, points = { 12349, 3513, 12349, 3600 } } }
    -- #1022 Chapelmount Downs Back Road
    ops[1022] = { expectedWidth = 7, expectedPoints = { 12072, 2819.5, 12095.5, 2819.5, 12095.5, 2892, 12102, 2892 }, hideLabel = true, reference = { index = 1053, width = 7, points = { 12072, 2819.5, 12095.5, 2819.5, 12095.5, 2892, 12102, 2892 } } }
    -- #1023 Station Link Road
    ops[1023] = { expectedWidth = 7, expectedPoints = { 12517.5, 2509, 12517.5, 2398 }, hideLabel = true, reference = { index = 1054, width = 7, points = { 12517.5, 2509, 12517.5, 2398 } } }
    -- #1024 Train Station Access Road
    ops[1024] = { expectedWidth = 7, expectedPoints = { 12520, 2512.5, 12710, 2512.5, 12710, 2405 }, hideLabel = true, reference = { index = 1055, width = 7, points = { 12520, 2512.5, 12710, 2512.5, 12710, 2405 } } }
    -- #1025 Old Factory Road
    ops[1025] = { expectedWidth = 8, expectedPoints = { 15329, 3219, 15445, 3219 }, hideLabel = true, reference = { index = 1056, width = 8, points = { 15329, 3219, 15445, 3219 } } }
    -- #1026 Standiford Road
    ops[1026] = { expectedWidth = 8, expectedPoints = { 15329, 3306, 15430.5, 3306, 15439.5, 3301, 15444, 3296.5, 15449, 3287.5, 15449, 3117 }, hideLabel = true, reference = { index = 1057, width = 8, points = { 15329, 3306, 15430.5, 3306, 15439.5, 3301, 15444, 3296.5, 15449, 3287.5, 15449, 3117 } } }
    -- #1027 Holy Haven Road
    ops[1027] = { expectedWidth = 6, expectedPoints = { 12520, 3263, 12537, 3263, 12537, 3374, 12559.5, 3396, 12583, 3396 }, hideLabel = true, reference = { index = 1058, width = 6, points = { 12520, 3263, 12537, 3263, 12537, 3374, 12559.5, 3396, 12583, 3396 } } }
    -- #1028 Louisville Railroad (Doe Valley - Louisville)
    ops[1028] = { expectedWidth = 3, expectedPoints = { 12698, 2661.5, 12646.5, 2713, 12646.5, 3019.5, 12668.5, 3041.5, 12668.5, 3494, 12664.5, 3498, 12664.5, 4220.5 }, hideLabel = true, reference = { index = 1059, width = 3, points = { 12698, 2661.5, 12646.5, 2713, 12646.5, 3019.5, 12668.5, 3041.5, 12668.5, 3494, 12664.5, 3498, 12664.5, 4220.5 } } }
    -- #1029 Northern Railroad (Muldraugh - Doe Valley)
    ops[1029] = { expectedWidth = 4, expectedPoints = { 12664.5, 4476.5, 12664.5, 5819, 12620.5, 5862.5, 12620.5, 6564, 12576, 6608.5, 12306, 6608.5, 12294.5, 6620, 12294.5, 6775, 12252.5, 6817, 12197, 6817.5, 12178.5, 6836, 12178.5, 7688, 12106.5, 7759.5, 12106.5, 9391, 12034, 9463.5, 11930, 9463.5, 11869, 9524.5, 11671, 9524.5, 11644.5, 9551, 11644.5, 9618.5 }, hideLabel = true, reference = { index = 1060, width = 4, points = { 12664.5, 4476.5, 12664.5, 5819, 12620.5, 5862.5, 12620.5, 6564, 12576, 6608.5, 12306, 6608.5, 12294.5, 6620, 12294.5, 6775, 12252.5, 6817, 12197, 6817.5, 12178.5, 6836, 12178.5, 7688, 12106.5, 7759.5, 12106.5, 9391, 12034, 9463.5, 11930, 9463.5, 11869, 9524.5, 11671, 9524.5, 11644.5, 9551, 11644.5, 9618.5 } } }
    -- #1030 Southern Railroad (Muldraugh - Fort Knox)
    ops[1030] = { expectedWidth = 4, expectedPoints = { 11736, 10196, 11901.5, 10361.5, 11901.5, 12154, 11185.5, 12870, 11185.5, 13800 }, hideLabel = true, reference = { index = 1061, width = 4, points = { 11736, 10196, 11901.5, 10361.5, 11901.5, 12154, 11185.5, 12870, 11185.5, 13800 } } }
    -- #1031 Southern Railroad (Muldraugh - Fort Knox)
    ops[1031] = { expectedWidth = 5, expectedPoints = { 11185.5, 13800, 11185.5, 14084, 11139, 14130.5, 10142, 14130.5 }, hideLabel = true, reference = { index = 1062, width = 5, points = { 11185.5, 13800, 11185.5, 14084, 11139, 14130.5, 10142, 14130.5 } } }
    -- #1032 Southwestern Railroad (Fort Knox - Irvington)
    ops[1032] = { expectedWidth = 5, expectedPoints = { 10142, 14130.5, 8287.5, 14131, 7903, 14516.5, 7113.5, 14517, 7006.5, 14625.5, 6527.5, 14625, 6268.5, 14367, 5507.5, 14365, 5354.5, 14518.5, 4884.5, 14517.5, 4682, 14314, 4505.5, 14138.5, 3488.5, 14138.5, 3430.5, 14080.5, 2619, 14080.5 }, hideLabel = true, reference = { index = 1063, width = 5, points = { 10142, 14130.5, 8287.5, 14131, 7903, 14516.5, 7113.5, 14517, 7006.5, 14625.5, 6527.5, 14625, 6268.5, 14367, 5507.5, 14365, 5354.5, 14518.5, 4884.5, 14517.5, 4682, 14314, 4505.5, 14138.5, 3488.5, 14138.5, 3430.5, 14080.5, 2619, 14080.5 } } }
    -- #1037 Northwestern Railroad (Muldraugh - Brandenburg)
    ops[1037] = { expectedWidth = 5, expectedPoints = { 2238, 6695.5, 2574.5, 6695.5, 2646.5, 6623.5, 2646.5, 6210.5, 2691.5, 6165.5, 3138.5, 6165.5, 3197.5, 6224.5, 3603.5, 6224.5, 3729, 6350.5, 4331.5, 6350.5, 4350.5, 6369.5, 4350.5, 6706.5, 4424.5, 6780.5, 5222.5, 6780.5, 5323.5, 6881.5, 6607, 6881.5, 6724.5, 6998.5, 6724.5, 7514.5, 6762.5, 7552.5, 6949.5, 7552.5, 6994.5, 7597.5, 7453.5, 7597.5, 7482.5, 7626.5, 7482.5, 7778.5, 7549.5, 7845.5, 8298.5, 7845.5, 8421.5, 7968.5, 8421.5, 8080.5, 8456.5, 8115.5, 8655.5, 8115.5, 8699.5, 8071.5, 10724.5, 8071.5, 10761.5, 8108.5, 12104, 8108.5 }, hideLabel = true, reference = { index = 1068, width = 5, points = { 2238, 6695.5, 2574.5, 6695.5, 2646.5, 6623.5, 2646.5, 6210.5, 2691.5, 6165.5, 3138.5, 6165.5, 3197.5, 6224.5, 3603.5, 6224.5, 3729, 6350.5, 4331.5, 6350.5, 4350.5, 6369.5, 4350.5, 6706.5, 4424.5, 6780.5, 5222.5, 6780.5, 5323.5, 6881.5, 6607, 6881.5, 6724.5, 6998.5, 6724.5, 7514.5, 6762.5, 7552.5, 6949.5, 7552.5, 6994.5, 7597.5, 7453.5, 7597.5, 7482.5, 7626.5, 7482.5, 7778.5, 7549.5, 7845.5, 8298.5, 7845.5, 8421.5, 7968.5, 8421.5, 8080.5, 8456.5, 8115.5, 8655.5, 8115.5, 8699.5, 8071.5, 10724.5, 8071.5, 10761.5, 8108.5, 12104, 8108.5 } } }
    Repairs["muldraugh-1993"] = { schemaVersion = 1, mapMod = "muldraugh1993b42", mapDir = "Muldraugh 1993 B42", operations = ops }
end
