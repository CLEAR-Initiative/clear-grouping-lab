# CLEAR Sudan alert review — week of 20–27 Oct 2026

Source: `dev-api.clearinitiative.io` via the clear MCP, all published alerts whose event sits under the Sudan location, primary timestamp 2026-10-20 00:00Z to 2026-10-27 ~14:00Z. 325 alerts (336 globally; the other 11 are Afghanistan/Venezuela). Day = the event's first-signal day (what `clear_count` groups by); 'alerted' shows the alert's own creation day when it differs.

Source attribution: an event whose first signal has a whole-second timestamp (`…:14.000Z`) is an X post ingested by BetaMinr as `sudan-war-x`; millisecond timestamps are Dataminr / ACLED / IDMC / NASA FIRMS. Verified on 7 events with `clear_get_event`.

## Rubric (total /10)

| Dim | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **R** Relevance to NRC/BetaMinr priorities | out of scope (politics, diplomacy, satellite noise) | marginal: military-on-military, macro-economics | secondary: health, prices, services, local security, famine warnings | primary: displacement, aid access, protection of civilians with humanitarian consequence |
| **I** Humanitarian impact | none / unknown | minor, no casualties | several killed or district-level disruption | mass casualties, ≥10k displaced, area-wide service loss |
| **S** Specificity / actionability | vague or country-level roundup | place or figure, not both | named place + figures + date | — |
| **N** Novelty | duplicate, stale (>3 days) or recirculation | meaningful update (new toll/detail) | first report this week | — |

Verdict: **Alert** ≥7, **Digest** 5–6, **Suppress** ≤4; anything that is a duplicate of an earlier alert this week is **Merge/suppress** regardless of score.

## Summary

| | Count | Share |
|---|---|---|
| BetaMinr sudan-war-x | 302 | 92% |
| Dataminr/ACLED/IDMC | 16 | 4% |
| NASA FIRMS (via Dataminr) | 7 | 2% |

| Verdict | Count | /day |
|---|---|---|
| Alert | 96 | 12.0 |
| Digest | 55 | 6.9 |
| Suppress | 53 | 6.6 |
| Merge/suppress | 121 | 15.1 |

| Day | Alerts | BetaMinr | Other | Alert (≥7, new) | Digest | Suppress | Merge/dup | Mean /10 |
|---|---|---|---|---|---|---|---|---|
| 2026-10-20 | 78 | 75 | 3 | 27 | 14 | 16 | 21 | 5.7 |
| 2026-10-21 | 72 | 67 | 5 | 19 | 10 | 14 | 29 | 5.7 |
| 2026-10-22 | 49 | 44 | 5 | 15 | 8 | 4 | 22 | 5.8 |
| 2026-10-23 | 28 | 27 | 1 | 5 | 6 | 3 | 14 | 5.2 |
| 2026-10-24 | 19 | 19 | 0 | 4 | 3 | 4 | 8 | 5.5 |
| 2026-10-25 | 22 | 22 | 0 | 7 | 2 | 3 | 10 | 5.3 |
| 2026-10-26 | 41 | 35 | 6 | 12 | 10 | 5 | 14 | 5.9 |
| 2026-10-27 | 16 | 13 | 3 | 7 | 2 | 4 | 3 | 6.0 |
| **Week** | 325 | 302 | 23 | 96 | 55 | 53 | 121 | 5.7 |

Alerts by the day they were actually **created** (what lands in an inbox):

| Created | Count |
|---|---|
| 2026-10-20 | 74 |
| 2026-10-21 | 66 |
| 2026-10-22 | 27 |
| 2026-10-23 | 53 |
| 2026-10-24 | 11 |
| 2026-10-26 | 74 |
| 2026-10-27 | 20 |

17 alerts were created 2+ days after their first signal (weekend backlog fired Mon 26 Oct; single stragglers 4–6 days late: #132, #133, #192).

## Biggest duplicate clusters

| Cluster | Alerts | Ideal |
|---|---|---|
| West Kordofan Al-Mujlad/Al-Dibab market strike (19–20 Oct) | 11 (#1, #3, #17, #18, #33, #36, #52, #64, #85, #86, #114) | 1 + updates |
| Abyei / Amiet market strike | 5 (#7, #27, #28, #90, #204) | 1 + updates |
| Blue Nile Sali/Baraka battle, 4th Brigade | 6 (#11, #13, #14, #23, #29, #48) | 1 + updates |
| Bamina/Bamna, Chad drone strike on refugees | 12 (#69, #70, #71, #74, #87, #98, #107, #112, #115, #123, #128, #152) | 1 + updates |
| 'Economic crisis in Sudan/Khartoum' currency + bread + fuel | 39 (#2, #9, #19, #20, #24, #25, #30, #40, #47, #62, #76, #77, #89, #97, #99, #104, #108, #109, #118, #119, #120, #136, #154, #166, #168, #170, #171, #181, #203, #209, #249, #252, #254, #257, #258, #259, #261, #304, #318) | 1 + updates |
| UNICEF 12 children killed | 5 (#38, #60, #82, #143, #184) | 1 + updates |
| Al-Udhayyah/Al-Daima (WK) strike 16 killed | 3 (#94, #101, #111) | 1 + updates |
| River Nile drone on vehicle, 3 killed | 5 (#146, #149, #150, #153, #179) | 1 + updates |
| Sennar/Gedaref/Al Jazirah power-station wave (26 Oct) | 14 (#269, #270, #271, #273, #275, #276, #277, #279, #280, #283, #284, #287, #294, #305) | 1 + updates |
| WFP cuts | 4 (#138, #160, #172, #194) | 1 + updates |
| Omdurman Joint Forces vehicle, 8 killed | 4 (#237, #240, #246, #248) | 1 + updates |
| Tigrayan fighters killed, Blue Nile | 3 (#211, #212, #227) | 1 + updates |
| Nyala market strike 27 Oct | 3 (#311, #314, #325) | 1 + updates |

These 13 clusters alone account for 114 of 325 alerts.

## Geolocation errors flagged (20)

| # | Alert location | Title | Note |
|---|---|---|---|
| 13 | Janub Al Jazirah | Battles in Sali and Baraka, Blue Nile | Dup of #11, mislocated to Al Jazirah |
| 16 | North Darfur | Airstrikes on El Daein incl. Al-Jalabi prison, mass escape | El Daein is East Darfur (mislocated) |
| 52 | West Kordofan | Army drone hits livestock market, 87 killed | Dup of #17; date garbled as Sep 19 |
| 53 | Sudan | Drone strike on Al-Daein military sites, 5 killed 20 injured | Update of #16, mislocated to country |
| 65 | West Kordofan | Drone hits displacement camp east of Snakit, 9 children killed | Snakit is West Darfur (mislocated) |
| 69 | Sudan | Militia raids on Bamena, Chad | Cross-border, mislocated to Sudan |
| 87 | North Darfur | Airstrike on displacement camps at Bamina | Dup of Chad cluster, mislocated |
| 100 | West Kordofan | Akinci drone strikes 'El Fasher and Abu Zabad' | Garbled geography |
| 112 | As Salam - WK | Volunteers and displaced killed by drone in Al-Tayna | Dup of Chad/Tina cluster, mislocated |
| 130 | White Nile | CBS: 28.29% y/y inflation in September | Mislocated statistic |
| 139 | Delgo | Artillery shelling of 'Delingo' (Dilling) | Dup of #135, mislocated to Northern state |
| 165 | Sudan | Drone strike on Ali Dinar mosque during prayers, dozens killed | Toll update of #162, mislocated to country |
| 188 | East Darfur | Drones on RSF positions 'around Ad-Damazin in East Darfur' | Garbled geography |
| 189 | East Darfur | Airstrike on main market of Zalingei | Zalingei is Central Darfur (mislocated) |
| 214 | East Darfur | Airstrike on marketplace in 'El Geneina, East Darfur' | Dup of #189, garbled |
| 215 | Sudan | Al-Jalabi prison toll 26; 5 killed at travel hub | Toll update of #137, garbled location |
| 264 | North Darfur | Dokki camp (Chad): starvation, aid halted 4 months, 4 deaths | Mislocated (Chad) |
| 281 | Central Darfur | Drone on restaurant in 'Ed Daein, Central Darfur', 19 killed | Dup of #67 (19 Oct), mislocated |
| 285 | North Darfur | El Fasher displaced in camps near Port Sudan lack food/medicine | Mislocated |
| 307 | Khartoum | 40,000 fled; trapped at Kakuma camp (Kenya) | Mislocated (Kenya) |

## All alerts, by day

### 2026-10-20 — 78 alerts

| # | UTC | Alerted | Src | Sev | Location | Alert | R | I | S | N | **/10** | Verdict | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 03:00 |  | X | 5 | West Kordofan | Drone strike on Al-Mujlad / Al-Dibab market, dozens dead | 3 | 3 | 2 | 2 | **10** | Alert | First report of the WK market strike |
| 2 | 03:35 |  | X | 4 | Sudan | Economic crisis: pound slide pushes gold prices up | 1 | 1 | 0 | 1 | **3** | Suppress | Gold price, not a humanitarian indicator |
| 3 | 05:20 |  | X | 5 | West Kordofan | Drone strikes at transport hub, ~110 killed | 3 | 3 | 2 | 1 | **9** | Alert | Toll update of #1 |
| 4 | 05:45 |  | X | 4 | Kadugli | Drone attacks on Kafa site + market, 2 women 1 child killed | 3 | 2 | 2 | 2 | **9** | Alert |  |
| 5 | 07:27 |  | X | 4 | Sudan | OCHA: drone strikes in Khartoum, Darfur, Kordofan | 2 | 2 | 0 | 0 | **4** | Suppress | Country-level roundup |
| 6 | 07:37 |  | X | 4 | West Kordofan | RSF arrest 25 civilians in Um Marahik, execution ultimatum | 3 | 2 | 2 | 2 | **9** | Alert | Protection |
| 7 | 07:48 |  | X | 5 | Abyei | Army strike on Abyei market, 53 dead | 3 | 3 | 2 | 2 | **10** | Alert | First Abyei market report |
| 8 | 07:49 |  | X | 4 | Sudan | OCHA: ~20 dead Darfur/Kordofan, Khartoum airport flights cancelled | 2 | 2 | 0 | 0 | **4** | Suppress | Roundup |
| 9 | 07:57 |  | X | 4 | Sudan | Bread price increase after flour/oil/yeast rises | 2 | 1 | 1 | 1 | **5** | Digest |  |
| 10 | 07:58 |  | X | 4 | South Kordofan | Hostile drones over Dilling after Kadugli attacks | 2 | 1 | 1 | 0 | **4** | Suppress | Restates #4 |
| 11 | 08:11 |  | X | 4 | Blue Nile | Army repels RSF attack at Khawr al-Burri | 1 | 1 | 1 | 2 | **5** | Digest | Military-on-military; first Sali/Baraka report |
| 12 | 08:14 |  | X | 4 | Sudan | Wave of drone attacks Monday, civilian casualties | 2 | 2 | 0 | 0 | **4** | Suppress | Roundup |
| 13 | 08:33 |  | DM | 4 | Janub Al Jazirah | Battles in Sali and Baraka, Blue Nile | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #11, mislocated to Al Jazirah |
| 14 | 08:43 |  | X | 4 | Blue Nile | 4th Brigade repels attack, 15 vehicles captured | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #11 |
| 15 | 08:46 |  | X | 4 | Tendalti | RSF drones destroy Tandalti power station, outages in Kordofan/White Nile | 3 | 3 | 2 | 2 | **10** | Alert | Services cut |
| 16 | 08:54 |  | X | 4 | North Darfur | Airstrikes on El Daein incl. Al-Jalabi prison, mass escape | 2 | 2 | 2 | 2 | **8** | Alert | El Daein is East Darfur (mislocated) |
| 17 | 09:09 |  | X | 5 | West Kordofan | Drone airstrike kills 80 (medical source) | 3 | 3 | 1 | 1 | **8** | Alert | Toll update of #1/#3 |
| 18 | 09:09 |  | X | 5 | West Kordofan | Drone strike, 80 killed (medical source) | 3 | 3 | 1 | 0 | **7** | Merge/suppress | Exact dup of #17, same signal time |
| 19 | 09:29 |  | X | 5 | Sudan | Official rate hits 10,000 SDG/USD | 2 | 2 | 1 | 2 | **7** | Alert | Market-stress milestone |
| 20 | 09:29 |  | X | 5 | Sudan | Pound reaches 10,000/USD | 2 | 2 | 1 | 0 | **5** | Merge/suppress | Exact dup of #19 |
| 21 | 09:43 |  | X | 4 | Sudan | ~4M affected by drought-like conditions | 2 | 2 | 0 | 1 | **5** | Digest | Humanitarian update, vague |
| 22 | 09:43 |  | X | 4 | Sudan | ~4M affected by drought-like conditions | 2 | 2 | 0 | 0 | **4** | Merge/suppress | Exact dup of #21 |
| 23 | 09:50 |  | X | 4 | Blue Nile | 4th Brigade thwarts penetration at Sali, 15 vehicles seized | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #11 |
| 24 | 09:54 |  | X | 4 | Sudan | Citizen: lentil meal costs 21,000 SDG | 1 | 1 | 0 | 0 | **2** | Suppress | Anecdote |
| 25 | 09:54 |  | X | 4 | Sudan | Citizen: lentil meal costs 21,000 SDG | 1 | 1 | 0 | 0 | **2** | Merge/suppress | Exact dup of #24 |
| 26 | 10:03 |  | X | 4 | Port Sudan | Food and housing costs surge | 2 | 1 | 1 | 1 | **5** | Digest |  |
| 27 | 10:04 |  | X | 5 | Abyei PCA | Drone strike on market, 73 killed 19 injured | 3 | 3 | 2 | 1 | **9** | Alert | Toll update of #7 |
| 28 | 10:04 |  | X | 5 | Abyei PCA | Drone attack on marketplace, 73 killed 19 injured | 3 | 3 | 2 | 0 | **8** | Merge/suppress | Exact dup of #27 |
| 29 | 10:10 |  | X | 4 | Blue Nile | 4th Brigade repels RSF/Tuka attack at Sali | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #11 |
| 30 | 10:41 |  | X | 4 | Sudan | Customs dollar rate increase disrupts markets | 1 | 1 | 0 | 1 | **3** | Suppress |  |
| 31 | 10:47 |  | X | 5 | Sudan | 659,000 Sudanese refugees in South Sudan (as of 30 Sep) | 3 | 1 | 1 | 1 | **6** | Digest | Cumulative statistic, not an incident |
| 32 | 10:47 |  | X | 5 | Sudan | 659,000 Sudanese refugees in South Sudan | 3 | 1 | 1 | 0 | **5** | Merge/suppress | Exact dup of #31 |
| 33 | 10:50 |  | X | 5 | West Kordofan | Drone hits civilian transport, 80+ killed | 3 | 3 | 2 | 0 | **8** | Merge/suppress | Dup of #17 |
| 34 | 11:05 |  | X | 4 | Sudan | UN delegation visits Al-Kufrah | 0 | 0 | 0 | 1 | **1** | Suppress | Noise |
| 35 | 11:12 |  | X | 4 | East Darfur | Explosion in Daein, 40 killed/injured | 2 | 2 | 1 | 1 | **6** | Digest | Update of #16 |
| 36 | 11:18 |  | X | 5 | West Kordofan | Strike at strategic market, 80+ dead, market destroyed | 3 | 3 | 1 | 0 | **7** | Merge/suppress | Dup of #17 |
| 37 | 11:24 |  | X | 4 | Al Fasher | Ongoing violence, families displaced and missing | 2 | 2 | 0 | 0 | **4** | Suppress | Background, no new incident |
| 38 | 11:28 |  | X | 4 | Sudan | Drone strikes over 3 days killed 13 children (UNICEF) | 2 | 2 | 0 | 1 | **5** | Digest | Roundup |
| 39 | 11:48 |  | X | 4 | Sudan | Drone attacks near Khartoum airport, flights cancelled | 2 | 2 | 1 | 1 | **6** | Digest |  |
| 40 | 12:14 |  | X | 4 | Sudan | Dollar at 10,100 SDG | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #19 |
| 41 | 12:27 |  | X | 4 | White Nile | Polio outbreak reported, campaign prepared | 3 | 2 | 1 | 2 | **8** | Alert | Health, first report |
| 42 | 12:32 |  | X | 4 | Khartoum | Drone attacks + outages, fuel shortage, currency collapse | 2 | 2 | 0 | 0 | **4** | Suppress | Roundup |
| 43 | 12:50 |  | X | 5 | Sudan | 100+ killed in drone attacks across WK, S Darfur, Khartoum | 2 | 3 | 0 | 0 | **5** | Digest | Roundup |
| 44 | 12:59 |  | X | 4 | Sudan | 5 trillion SDG of goods stranded at Ethiopia border | 2 | 1 | 1 | 2 | **6** | Digest | Trade/access |
| 45 | 13:01 |  | X | 5 | North Kordofan | Families wiped out in massacre, waves of displaced | 3 | 3 | 0 | 1 | **7** | Alert | Vague place |
| 46 | 13:06 |  | X | 4 | South Darfur | Drones destroy cargo plane at Nyala airport, troop vehicles | 1 | 1 | 2 | 2 | **6** | Digest | Military target |
| 47 | 13:06 |  | X | 4 | Khartoum | Severe fuel crisis in the capital | 2 | 1 | 1 | 1 | **5** | Digest |  |
| 48 | 13:07 |  | X | 4 | Blue Nile | 4th Brigade repels RSF/Tuka attack at Sali | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #11 (4th copy) |
| 49 | 14:02 |  | FIRMS | 4 | Al Dibab | Wild fire hotspots in West Kordofan | 0 | 0 | 1 | 2 | **3** | Suppress | Satellite hotspots in a strike zone |
| 50 | 14:02 |  | X | 4 | Sudan | Thousands displaced in Beli Serif, East Jebel Marra, lack food/water/health | 3 | 2 | 1 | 2 | **8** | Alert |  |
| 51 | 14:08 |  | X | 4 | Sudan | Deadly drone strikes hit five states | 2 | 2 | 0 | 0 | **4** | Suppress | Roundup |
| 52 | 14:10 |  | X | 5 | West Kordofan | Army drone hits livestock market, 87 killed | 3 | 3 | 1 | 0 | **7** | Merge/suppress | Dup of #17; date garbled as Sep 19 |
| 53 | 14:22 |  | X | 4 | Sudan | Drone strike on Al-Daein military sites, 5 killed 20 injured | 2 | 2 | 2 | 1 | **7** | Alert | Update of #16, mislocated to country |
| 54 | 14:34 |  | X | 4 | Al Fasher | Cash shortage and prices prompt renewed displacement | 3 | 2 | 1 | 1 | **7** | Alert |  |
| 55 | 14:37 | 10-22 | X | 4 | Port Sudan | Riots: students demand IDPs leave their school | 2 | 1 | 2 | 2 | **7** | Alert | Alerted 2 days late |
| 56 | 14:44 |  | X | 4 | As Serief | Displaced face severe food and medicine shortages | 3 | 2 | 1 | 2 | **8** | Alert |  |
| 57 | 15:23 |  | X | 4 | Khartoum | Drones target multiple regions incl. Khartoum | 2 | 1 | 0 | 0 | **3** | Suppress | Roundup |
| 58 | 15:25 |  | X | 4 | Sudan | Gorom camp (South Sudan): water, medicine, security shortages | 2 | 2 | 1 | 2 | **7** | Alert | Cross-border |
| 59 | 15:29 |  | X | 4 | North Darfur | Deadly drone strikes, UN condemnation | 2 | 1 | 0 | 0 | **3** | Suppress | No new content |
| 60 | 15:30 |  | X | 4 | Sudan | At least 12 children killed | 2 | 2 | 0 | 0 | **4** | Merge/suppress | Dup of #38 |
| 61 | 15:31 |  | X | 4 | West Darfur | RSF UAV strike on Jar Snakid village, El Geneina (17 Oct) | 3 | 2 | 2 | 1 | **8** | Alert | New incident but 3 days old |
| 62 | 15:32 |  | X | 4 | Khartoum | Severe bread shortages, flour dwindling | 2 | 1 | 1 | 1 | **5** | Digest |  |
| 63 | 15:37 |  | X | 4 | River Nile | Polio response campaign from 26 Oct | 2 | 1 | 1 | 1 | **5** | Digest |  |
| 64 | 15:41 |  | X | 5 | West Kordofan | Drones hit vehicle carrying mourners, 150 killed | 3 | 3 | 1 | 1 | **8** | Alert | Toll variant of WK strike |
| 65 | 15:48 |  | X | 4 | West Kordofan | Drone hits displacement camp east of Snakit, 9 children killed | 3 | 3 | 2 | 2 | **10** | Alert | Snakit is West Darfur (mislocated) |
| 66 | 16:02 |  | FIRMS | 4 | Al Lagowa | Wild fire hotspots West Kordofan | 0 | 0 | 1 | 1 | **2** | Merge/suppress | Dup of #49 |
| 67 | 16:25 |  | X | 4 | East Darfur | Drone strike on restaurant in Al Daein, 19 civilians killed (19 Oct) | 3 | 3 | 2 | 1 | **9** | Alert | New detail on Daein |
| 68 | 16:30 |  | X | 4 | Blue Nile | Fighting near Ethiopian border, tens of thousands fleeing | 3 | 3 | 1 | 2 | **9** | Alert | Displacement |
| 69 | 17:02 |  | X | 4 | Sudan | Militia raids on Bamena, Chad | 2 | 2 | 1 | 2 | **7** | Alert | Cross-border, mislocated to Sudan |
| 70 | 17:08 |  | X | 4 | Sudan | Attacks on Bamina, Chad | 2 | 2 | 1 | 0 | **5** | Merge/suppress | Dup of #69 |
| 71 | 17:32 |  | X | 4 | Sudan | Drone airstrike on Bamina, Chad | 2 | 2 | 1 | 0 | **5** | Merge/suppress | Dup of #69 |
| 72 | 17:34 |  | X | 4 | Sudan | Armed group attacks Umm Smin, 4 killed, livestock looted, abductions | 3 | 2 | 2 | 2 | **9** | Alert | Local security |
| 73 | 17:42 |  | X | 4 | South Kordofan | Displaced from Kordofan/Darfur addressed in Al-Qadarif | 1 | 0 | 0 | 1 | **2** | Suppress | Noise |
| 74 | 17:43 |  | X | 4 | Sudan | RSF drones hit Amineh market, Wadi Fira, Chad | 2 | 2 | 1 | 0 | **5** | Merge/suppress | Dup of Chad cluster |
| 75 | 17:52 |  | X | 4 | South Kordofan | Aid convoy (WFP-contracted trucks) attacked | 3 | 2 | 1 | 2 | **8** | Alert | Aid access |
| 76 | 20:04 | 10-21 | X | 5 | Sudan | Dollar exceeds 10,000 SDG | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #19 |
| 77 | 21:42 | 10-21 | X | 4 | Sudan | Sharp price increases across states | 1 | 1 | 0 | 0 | **2** | Suppress | Roundup |
| 78 | 23:05 | 10-21 | X | 4 | Sudan | ~3,000/week arriving in Renk; 1M in S Sudan lose food aid | 3 | 2 | 1 | 2 | **8** | Alert |  |

### 2026-10-21 — 72 alerts

| # | UTC | Alerted | Src | Sev | Location | Alert | R | I | S | N | **/10** | Verdict | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 79 | 05:40 | 10-22 | X | 4 | Nyala Janoub | RSF violence in Nyala 14-27 Oct incl. Tangonjong market massacre (188 killed) | 3 | 3 | 2 | 1 | **9** | Alert | Multi-signal event window |
| 80 | 06:12 |  | DM | 3 | Abyei PCA area | Communal violence 17-21 Sep, 3,400 displaced | 3 | 2 | 2 | 0 | **7** | Merge/suppress | Stale (September); severity 3 still alerted |
| 81 | 06:23 |  | X | 4 | South Darfur | Government of Peace delegation visits Kulma camp | 1 | 0 | 1 | 2 | **4** | Suppress | Politics |
| 82 | 07:03 |  | X | 4 | Sudan | UNICEF: 12 children killed in Khartoum and WK | 2 | 2 | 0 | 0 | **4** | Merge/suppress | Dup of #38 |
| 83 | 07:06 |  | X | 4 | North Kordofan | Airstrike on Um Badir Hospital + Tandalti power station | 3 | 3 | 1 | 1 | **8** | Alert | Hospital hit is new; Tandalti dup |
| 84 | 07:19 |  | X | 4 | Sudan | Displaced persons with disabilities lack care in Tawila/Korma | 2 | 1 | 1 | 1 | **5** | Digest |  |
| 85 | 07:20 |  | X | 4 | West Kordofan | Strikes on An-Na'am / Ad-Dabb markets, injured without care | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #1 |
| 86 | 07:38 |  | X | 5 | West Kordofan | Transport hub double-tap, 80 dead, 50 buried on site | 3 | 3 | 2 | 0 | **8** | Merge/suppress | Dup of #17 with new detail |
| 87 | 07:39 |  | X | 4 | North Darfur | Airstrike on displacement camps at Bamina | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of Chad cluster, mislocated |
| 88 | 07:41 |  | X | 4 | Sudan | UN condemns drone attacks on Abyei and WK markets | 2 | 2 | 0 | 0 | **4** | Suppress | Roundup |
| 89 | 07:45 |  | X | 4 | Khartoum | Fuel shortages, bread rises, power cuts | 2 | 1 | 0 | 0 | **3** | Suppress | Roundup |
| 90 | 07:50 |  | X | 5 | Abyei PCA | Amiet market attack: 220+ killed, 8,000 flee | 3 | 3 | 2 | 1 | **9** | Alert | Displacement update on #7 |
| 91 | 07:55 |  | X | 4 | Blue Nile | RSF casualties overwhelm Assosa hospital (Ethiopia) | 1 | 1 | 1 | 1 | **4** | Suppress |  |
| 92 | 07:58 |  | X | 4 | Sudan | Egypt border closure drives shortages; trucks return | 2 | 2 | 1 | 2 | **7** | Alert | Access |
| 93 | 08:04 |  | X | 4 | North Kordofan | Airstrike destroys Um Badir Hospital | 3 | 3 | 1 | 0 | **7** | Merge/suppress | Dup of #83 |
| 94 | 08:05 |  | X | 4 | West Kordofan | Drone strike on Al-Udhayyah (Al-Odaya), 16 killed | 3 | 3 | 2 | 2 | **10** | Alert | New incident |
| 95 | 08:09 |  | X | 4 | South Darfur | SAF strike on Nyala livestock market, 30 killed | 3 | 3 | 2 | 2 | **10** | Alert | New incident |
| 96 | 08:40 |  | X | 4 | Blue Nile | 67 Misseriya fighters killed at Sali; forced recruitment | 1 | 1 | 1 | 1 | **4** | Suppress |  |
| 97 | 08:45 |  | X | 4 | Sudan | 30% customs dollar rise, price hikes | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #30 |
| 98 | 08:48 |  | X | 4 | Sudan | RSF drone kills 5 incl. 2 volunteers at Bamna, Taqanda | 2 | 2 | 2 | 1 | **7** | Alert | Chad cluster, new detail |
| 99 | 09:13 |  | X | 4 | Khartoum | Currency collapse, bread, fuel, transport | 1 | 1 | 0 | 0 | **2** | Suppress | Roundup |
| 100 | 09:25 |  | X | 4 | West Kordofan | Akinci drone strikes 'El Fasher and Abu Zabad' | 2 | 2 | 0 | 0 | **4** | Suppress | Garbled geography |
| 101 | 09:30 |  | X | 4 | West Kordofan | Akinci drone strike on Al-Daima, 16 killed | 3 | 3 | 2 | 0 | **8** | Merge/suppress | Dup of #94 |
| 102 | 09:32 |  | X | 4 | Blue Nile | Clashes at Al-Burqa, 2,700 killed or captured | 1 | 1 | 1 | 1 | **4** | Suppress | Implausible figure |
| 103 | 09:47 |  | X | 4 | Khartoum | Civilians fleeing, seeking care in Krandongo | 2 | 1 | 0 | 1 | **4** | Suppress |  |
| 104 | 09:53 |  | X | 4 | Sudan | Pound over 8,000 on parallel market | 1 | 1 | 0 | 0 | **2** | Merge/suppress | Dup/inconsistent with #19 |
| 105 | 09:54 |  | X | 4 | Dongola | Doctor assaulted by security forces; activist disappeared | 1 | 1 | 2 | 2 | **6** | Digest | Human rights, not NRC core |
| 106 | 10:07 |  | X | 4 | Blue Nile | Intensified fighting in Blue Nile, Kordofan, Darfur | 1 | 1 | 0 | 0 | **2** | Suppress | Roundup |
| 107 | 10:12 |  | X | 4 | North Darfur | Drone strike on Sudanese refugees in Chad, 5 killed | 2 | 2 | 1 | 0 | **5** | Merge/suppress | Dup of Chad cluster |
| 108 | 10:37 |  | X | 4 | Sudan | Food prices up 35%, flour 170,000 SDG | 2 | 1 | 1 | 1 | **5** | Digest |  |
| 109 | 10:38 |  | X | 4 | Khartoum | Dollar 9,500 on black market | 1 | 1 | 0 | 0 | **2** | Merge/suppress | Dup of #19 |
| 110 | 10:43 |  | X | 4 | Sudan | UNICEF/WASH: 67% of households water insecure | 2 | 2 | 1 | 2 | **7** | Alert | Report, not event |
| 111 | 10:46 |  | X | 4 | West Kordofan | 16 killed Al-Adiya, 5 in Abu Zabad | 3 | 3 | 2 | 0 | **8** | Merge/suppress | Dup of #94 |
| 112 | 10:48 |  | X | 4 | As Salam - WK | Volunteers and displaced killed by drone in Al-Tayna | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of Chad/Tina cluster, mislocated |
| 113 | 10:57 |  | X | 4 | Khartoum | Woman protests bread price at Burhan appearance | 0 | 0 | 1 | 1 | **2** | Suppress | Politics |
| 114 | 11:01 |  | X | 4 | West Kordofan | Drones hit Al-Majlad / Al-Dabab markets | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #1 |
| 115 | 11:02 |  | X | 4 | Sudan | Drone strike on refugee shelter in Bami, Chad, 5 killed | 2 | 2 | 2 | 0 | **6** | Merge/suppress | Dup of Chad cluster |
| 116 | 11:20 |  | X | 4 | South Darfur | RSF abducting children for forced recruitment | 3 | 2 | 1 | 2 | **8** | Alert | Protection |
| 117 | 11:52 |  | X | 4 | Sudan | Dengue spreading, hundreds of deaths | 3 | 3 | 0 | 2 | **8** | Alert | Vague location |
| 118 | 12:11 |  | X | 4 | Khartoum | Bakeries halt over flour price | 2 | 2 | 1 | 1 | **6** | Digest |  |
| 119 | 12:24 |  | X | 4 | Khartoum | Flour sack 87,000 to 180,000 SDG | 2 | 1 | 1 | 0 | **4** | Merge/suppress | Dup of #118 |
| 120 | 12:48 |  | X | 4 | Khartoum | Fuel shortage, public transport breakdown | 2 | 1 | 0 | 0 | **3** | Merge/suppress | Dup of #47 |
| 121 | 13:00 |  | X | 4 | Sudan | Sugar 420,000 SDG/50kg at Al Mailiq, Al Jazirah | 2 | 1 | 2 | 1 | **6** | Digest |  |
| 122 | 13:01 |  | X | 4 | Sawakin | Protests at Suakin port over passengers/cars | 1 | 1 | 2 | 2 | **6** | Digest |  |
| 123 | 13:01 |  | X | 4 | North Darfur | Drone at Bamna kills 5, comms severed | 2 | 2 | 1 | 0 | **5** | Merge/suppress | Dup of Chad cluster |
| 124 | 13:24 |  | X | 4 | Sudan | Gorom camp shortages | 2 | 2 | 1 | 0 | **5** | Merge/suppress | Dup of #58 |
| 125 | 13:45 |  | X | 4 | Bara | 600 decomposed bodies found, total displacement, disease | 3 | 3 | 1 | 1 | **8** | Alert | Bara follow-up |
| 126 | 14:02 |  | FIRMS | 4 | Abu Jubayhah | Wild fire hotspots South Kordofan | 0 | 0 | 1 | 1 | **2** | Suppress |  |
| 127 | 14:02 |  | FIRMS | 4 | Delami | Wild fire hotspots South Kordofan | 0 | 0 | 1 | 0 | **1** | Merge/suppress | Dup of #126 |
| 128 | 14:10 |  | X | 4 | Sudan | Drone strike on refugee site in Bamna, Chad, 5 killed | 2 | 2 | 2 | 0 | **6** | Merge/suppress | Dup of Chad cluster |
| 129 | 14:24 |  | X | 4 | Ar Rusayris | Cash assistance to conflict-affected families | 1 | 0 | 1 | 1 | **3** | Suppress | Aid delivery news |
| 130 | 14:53 |  | X | 4 | White Nile | CBS: 28.29% y/y inflation in September | 1 | 1 | 1 | 2 | **5** | Digest | Mislocated statistic |
| 131 | 15:06 |  | X | 4 | Blue Nile | Dengue outbreak in Damazin, shortages | 3 | 2 | 1 | 2 | **8** | Alert |  |
| 132 | 15:13 | 10-26 | DM | 4 | Janub Al Jazirah | RSF drones on power stations east of Al Jazirah | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Alerted 5 days late |
| 133 | 15:34 | 10-27 | X | 4 | Um Durman | Drones hit Omdurman facility + Murkhiyat power station, outages | 3 | 3 | 2 | 0 | **8** | Merge/suppress | Alerted 6 days late |
| 134 | 15:36 |  | X | 4 | South Darfur | Food crisis from crop failure and prices | 2 | 2 | 0 | 1 | **5** | Digest |  |
| 135 | 15:40 |  | X | 4 | South Kordofan | Artillery shelling of Dilling | 3 | 2 | 1 | 2 | **8** | Alert |  |
| 136 | 15:46 |  | X | 4 | Sudan | 30% customs dollar rise | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #30 |
| 137 | 16:00 |  | X | 4 | East Darfur | Drones hit Al-Jalabi prison, 34 killed/injured, 400 escape | 2 | 2 | 2 | 1 | **7** | Alert | Update of #16 |
| 138 | 16:09 |  | X | 4 | Sudan | WFP to cut food aid from November, 900,000 affected | 3 | 3 | 1 | 2 | **9** | Alert | Aid pipeline break |
| 139 | 16:13 |  | X | 4 | Delgo | Artillery shelling of 'Delingo' (Dilling) | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #135, mislocated to Northern state |
| 140 | 16:19 |  | X | 4 | West Kordofan | 21 civilians killed in two drone attacks | 3 | 3 | 1 | 1 | **8** | Alert |  |
| 141 | 17:26 | 10-23 | X | 4 | Aj Jabalain | Bread up to 1,000 SDG/loaf, market stagnation | 2 | 1 | 1 | 1 | **5** | Digest | Alerted 2 days late |
| 142 | 17:44 |  | X | 4 | Sudan | 400 containers stranded 5 months by import restrictions | 2 | 1 | 1 | 1 | **5** | Digest |  |
| 143 | 18:13 |  | X | 4 | Sudan | UNICEF condemns killing of 12 children | 2 | 2 | 0 | 0 | **4** | Merge/suppress | Dup of #38 |
| 144 | 18:16 |  | X | 4 | West Kordofan | Tasees: 21 civilians killed in airstrikes | 3 | 3 | 0 | 0 | **6** | Merge/suppress | Dup of #140 |
| 145 | 20:23 | 10-22 | X | 4 | East Darfur | Explosion outside El Daein, ~40 fighters killed | 1 | 1 | 1 | 0 | **3** | Suppress | Military |
| 146 | 20:26 | 10-22 | X | 4 | Reifi Nahr Atbara | Attack on gathering, 3 killed 3 injured | 3 | 2 | 2 | 2 | **9** | Alert | New: River Nile drone on civilians |
| 147 | 20:33 | 10-22 | X | 4 | Sennar | Dengue: 5 deaths, 1,400+ infections | 3 | 2 | 2 | 2 | **9** | Alert |  |
| 148 | 22:06 | 10-22 | X | 4 | North Kordofan | RSF raids: rape, looting, water infra destroyed, civilians flee 40km | 3 | 3 | 1 | 2 | **9** | Alert |  |
| 149 | 22:10 | 10-22 | X | 4 | River Nile | Drone on vehicle, 3 civilians killed | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #146 |
| 150 | 22:27 |  | DM | 4 | Atbara | Drone on vehicle in Al-Tabia, 3 killed 1 injured | 3 | 2 | 2 | 0 | **7** | Merge/suppress | Dup of #146 |

### 2026-10-22 — 49 alerts

| # | UTC | Alerted | Src | Sev | Location | Alert | R | I | S | N | **/10** | Verdict | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 151 | 04:42 |  | X | 4 | North Darfur | Displaced person in Tine camp describes hardship | 2 | 1 | 1 | 1 | **5** | Digest | Anecdote |
| 152 | 05:10 |  | DM | 4 | At Tina | Drone strike in Bamina, Chad (20 Oct), 4 dead 14 injured | 2 | 2 | 2 | 0 | **6** | Merge/suppress | Dup of Chad cluster |
| 153 | 05:26 |  | X | 4 | River Nile | Drone on Sidun village, 3 killed | 3 | 2 | 2 | 0 | **7** | Merge/suppress | Dup of #146 |
| 154 | 06:03 |  | X | 4 | Khartoum | Bread 500 SDG, flour 155,000 | 2 | 1 | 1 | 0 | **4** | Merge/suppress | Dup of #118 |
| 155 | 06:15 |  | X | 4 | West Kordofan | RSF abduct 6 civilians incl. sheikh in Nahud | 3 | 2 | 2 | 2 | **9** | Alert |  |
| 156 | 06:25 |  | DM | 4 | Ar Rahad | RSF drone strike on El Rahad, 2 civilians killed | 3 | 2 | 2 | 2 | **9** | Alert |  |
| 157 | 07:00 |  | X | 4 | Atbara | RSF convoy attacks eastern Atbara | 2 | 2 | 1 | 2 | **7** | Alert | New front, needs verification |
| 158 | 07:19 |  | DM | 4 | Geisan | SAF retakes Bikori, Blue Nile | 1 | 1 | 2 | 2 | **6** | Digest |  |
| 159 | 07:23 |  | X | 4 | Blue Nile | SAF recaptures Bakouri and Oakleyli | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #158 |
| 160 | 07:26 |  | X | 5 | Sudan | WFP reduces food assistance | 3 | 3 | 0 | 0 | **6** | Merge/suppress | Dup of #138 |
| 161 | 08:05 |  | X | 4 | Kutum | Displacement with little support, long walks for water | 3 | 2 | 1 | 2 | **8** | Alert |  |
| 162 | 08:37 |  | X | 4 | Al Fasher | SAF drones hit Ali Dinar mosque, market, airport in El Fasher | 3 | 3 | 2 | 2 | **10** | Alert | First El Fasher mosque strike |
| 163 | 09:22 |  | X | 4 | Khartoum | Dengue + hepatitis/TB/meningitis after floods (1,645 households) | 3 | 2 | 1 | 2 | **8** | Alert |  |
| 164 | 10:11 |  | X | 4 | Sudan | Army destroys Mesiria force | 1 | 1 | 0 | 1 | **3** | Suppress | Military |
| 165 | 10:19 |  | X | 5 | Sudan | Drone strike on Ali Dinar mosque during prayers, dozens killed | 3 | 3 | 2 | 1 | **9** | Alert | Toll update of #162, mislocated to country |
| 166 | 10:30 |  | X | 4 | Sudan | Pound record low 10,000/USD | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #19 |
| 167 | 10:41 |  | X | 4 | North Darfur | Cooked meals for 2,800 displaced at Al-Tayna camp | 1 | 1 | 2 | 1 | **5** | Digest | Aid delivery news |
| 168 | 10:49 |  | X | 4 | Khartoum | Bread input costs rising | 2 | 1 | 0 | 0 | **3** | Merge/suppress | Dup of #118 |
| 169 | 11:19 |  | X | 4 | East Darfur | Food crisis in Shairia from agricultural failure | 2 | 2 | 1 | 2 | **7** | Alert |  |
| 170 | 12:04 |  | X | 4 | Khartoum | Bread expected to reach 1,000 SDG | 2 | 1 | 0 | 0 | **3** | Merge/suppress | Dup of #118 |
| 171 | 12:11 | 10-23 | X | 4 | Sudan | Dollar 11,000, flour 130k to 180k | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #19 |
| 172 | 12:16 | 10-23 | X | 4 | Sudan | Drought worsening crisis, WFP cuts | 2 | 2 | 0 | 0 | **4** | Merge/suppress | Dup of #138/#21 |
| 173 | 12:23 | 10-23 | X | 4 | Wad Al Mahi | Security deterioration blocks health access for displaced | 3 | 2 | 1 | 2 | **8** | Alert |  |
| 174 | 12:44 | 10-23 | DM | 4 | Geisan | Drone from Ethiopia shot down over Bakuri | 1 | 1 | 2 | 1 | **5** | Digest |  |
| 175 | 12:50 | 10-23 | X | 4 | Sudan | Sudanese refugees beaten in Uganda | 1 | 1 | 1 | 2 | **5** | Digest | Outside Sudan ops |
| 176 | 13:00 | 10-23 | X | 5 | Sudan | Airborne attacks kill at least 18 children | 2 | 3 | 0 | 0 | **5** | Digest | Roundup |
| 177 | 13:09 | 10-23 | X | 4 | North Darfur | Dengue in Tallaga, hundreds of cases | 3 | 2 | 2 | 2 | **9** | Alert |  |
| 178 | 13:17 | 10-23 | X | 4 | Sudan | 6 civilians incl. sheikh killed, 'Nyala, West Kordofan' | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #155 |
| 179 | 13:58 | 10-23 | X | 4 | River Nile | Civilian vehicle attacked, 3 dead | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #146 |
| 180 | 13:59 | 10-23 | X | 4 | West Kordofan | Drone kills 21, dozens injured | 3 | 3 | 1 | 0 | **7** | Merge/suppress | Dup of #140 |
| 181 | 14:22 | 10-23 | X | 4 | Sudan | Dollar 10,200 black market, import restrictions lifted | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #19 |
| 182 | 14:25 | 10-23 | X | 4 | Sudan | Inflation 28.29% in September | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #130 |
| 183 | 14:37 | 10-23 | X | 4 | Northern | Gold trading disrupted in mining markets | 1 | 1 | 1 | 1 | **4** | Suppress |  |
| 184 | 15:17 | 10-23 | X | 4 | Sudan | UNICEF: 12 children killed | 2 | 2 | 0 | 0 | **4** | Merge/suppress | Dup of #38 |
| 185 | 15:34 | 10-23 | X | 4 | Al Fasher | El Fasher population down 90%, ongoing crisis | 2 | 2 | 0 | 0 | **4** | Suppress | Background |
| 186 | 15:47 | 10-23 | X | 4 | South Kordofan | 4 civilians killed at Rajul Al-Marafieen after looting | 3 | 2 | 2 | 2 | **9** | Alert |  |
| 187 | 15:51 | 10-23 | X | 4 | Blue Nile | RSF/SPLM-N repel attacks at Al-Burqa | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #102 |
| 188 | 16:14 | 10-23 | X | 4 | East Darfur | Drones on RSF positions 'around Ad-Damazin in East Darfur' | 1 | 1 | 0 | 0 | **2** | Suppress | Garbled geography |
| 189 | 16:18 | 10-23 | X | 4 | East Darfur | Airstrike on main market of Zalingei | 3 | 2 | 1 | 2 | **8** | Alert | Zalingei is Central Darfur (mislocated) |
| 190 | 16:38 | 10-23 | X | 4 | West Kordofan | Army drones bomb homes in Babanusa | 3 | 2 | 1 | 2 | **8** | Alert |  |
| 191 | 16:55 | 10-23 | X | 4 | Blue Nile | WFP warns of food/shelter shortages for displaced before winter | 3 | 2 | 0 | 1 | **6** | Digest |  |
| 192 | 17:00 | 10-26 | DM | 4 | Ar Rahad | Drones hit fuel pumps and power stations in Ar Rahad, Gedaref | 3 | 2 | 2 | 0 | **7** | Merge/suppress | Alerted 4 days late |
| 193 | 17:05 | 10-23 | X | 4 | North Darfur | ~100 women held in secret RSF facility in El Fasher | 3 | 2 | 1 | 2 | **8** | Alert | Protection |
| 194 | 17:18 | 10-23 | X | 4 | North Darfur | Camps coordination warns WFP cuts threaten thousands | 3 | 2 | 0 | 0 | **5** | Merge/suppress | Dup of #138 |
| 195 | 17:45 | 10-23 | X | 4 | North Kordofan | Village completely looted, only mosque standing | 2 | 2 | 0 | 1 | **5** | Digest | No place named |
| 196 | 17:54 | 10-23 | X | 4 | Sudan | Inflation 28.29%, food +36.81% | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #130 |
| 197 | 17:57 | 10-23 | X | 4 | South Kordofan | Drone on Tagoula mine, Tlowdi, 4 civilians killed | 3 | 2 | 2 | 2 | **9** | Alert |  |
| 198 | 18:19 | 10-23 | X | 4 | South Kordofan | 4 livestock traders killed on road, livestock looted | 3 | 2 | 2 | 0 | **7** | Merge/suppress | Dup of #186 |
| 199 | 19:44 | 10-23 | X | 4 | Sudan | Two drone attacks in Kordofan kill 4 civilians | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #197 |

### 2026-10-23 — 28 alerts

| # | UTC | Alerted | Src | Sev | Location | Alert | R | I | S | N | **/10** | Verdict | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 200 | 07:11 |  | X | 4 | Um Rawaba | RSF drones destroy 5 empty buses at gas station, no casualties | 2 | 1 | 2 | 2 | **7** | Alert |  |
| 201 | 07:12 |  | X | 4 | Um Rawaba | RSF drone strike on gas station with empty buses | 2 | 1 | 2 | 0 | **5** | Merge/suppress | Dup of #200 |
| 202 | 07:33 |  | X | 4 | Tawila | Dengue in Tawila, 927 cases Sep to 16 Oct | 3 | 2 | 2 | 1 | **8** | Alert | Update on N Darfur dengue |
| 203 | 07:36 |  | X | 4 | Khartoum | Bakeries warn of 1,000 SDG bread | 2 | 1 | 0 | 0 | **3** | Merge/suppress | Dup of #118 |
| 204 | 08:10 |  | X | 5 | Sudan | Amiet market bombardment: 153 killed, 220 missing | 3 | 3 | 1 | 1 | **8** | Alert | Toll update of #7 |
| 205 | 09:25 |  | X | 4 | East Darfur | Attack on Abu Jabir market | 3 | 2 | 1 | 2 | **8** | Alert |  |
| 206 | 09:30 |  | X | 4 | Sudan | Farmers face famine conditions, weather | 2 | 2 | 0 | 0 | **4** | Suppress | Roundup |
| 207 | 09:56 |  | X | 5 | Sudan | Aerial attacks on residential areas, markets, IDP sites in recent weeks | 2 | 2 | 0 | 0 | **4** | Suppress | Roundup |
| 208 | 10:05 |  | X | 4 | East Darfur | Militia shell Abu Jabra market, casualties | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #205 |
| 209 | 10:25 |  | X | 4 | Sudan | Bread boycott as flour hits 195,000 | 2 | 1 | 1 | 1 | **5** | Digest |  |
| 210 | 10:31 |  | X | 4 | Sudan | Drones hit RSF depots in El Fasher, El Daein, Nyala | 1 | 1 | 1 | 1 | **4** | Suppress | Military targets |
| 211 | 11:34 |  | X | 4 | Blue Nile | 30+ Tigrayan fighters killed | 1 | 1 | 1 | 2 | **5** | Digest |  |
| 212 | 11:37 |  | X | 4 | Blue Nile | 30+ Tigrayan fighters killed in ambush near Al-Burka | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #211 |
| 213 | 11:45 |  | X | 4 | Sudan | Intensive drone strikes on El Fasher | 2 | 2 | 0 | 0 | **4** | Merge/suppress | Dup of #162 |
| 214 | 12:07 |  | X | 4 | East Darfur | Airstrike on marketplace in 'El Geneina, East Darfur' | 3 | 2 | 0 | 0 | **5** | Merge/suppress | Dup of #189, garbled |
| 215 | 12:52 |  | X | 4 | Sudan | Al-Jalabi prison toll 26; 5 killed at travel hub | 2 | 2 | 1 | 1 | **6** | Digest | Toll update of #137, garbled location |
| 216 | 14:03 |  | X | 4 | North Darfur | Lowest rainfall since 1984 (USGS), crop failure risk | 3 | 2 | 1 | 2 | **8** | Alert | Early warning |
| 217 | 14:31 |  | X | 5 | Sudan | UN documents 300 drone deaths in one month | 2 | 2 | 0 | 1 | **5** | Digest | Roundup |
| 218 | 15:05 |  | X | 5 | Sudan | UN HR: 306 killed by drones in 3 weeks of October | 2 | 2 | 0 | 0 | **4** | Merge/suppress | Dup of #217 |
| 219 | 15:55 |  | X | 4 | Sudan | War, drought and famine; lowest rainfall in 30 years | 2 | 2 | 0 | 0 | **4** | Merge/suppress | Dup of #216 |
| 220 | 16:34 |  | X | 4 | North Darfur | Drought: crop failure, livestock deaths, farmer-herder tension | 3 | 2 | 0 | 0 | **5** | Merge/suppress | Dup of #216 |
| 221 | 16:53 |  | X | 4 | West Kordofan | 4 livestock traders killed in armed robbery (22 Oct) | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #186 |
| 222 | 17:10 |  | X | 4 | Sudan | Assosa hospitals overwhelmed with RSF wounded | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #91 |
| 223 | 17:11 |  | DM | 4 | Khartoum | Polio campaign for 11M children in 12 states | 2 | 1 | 2 | 1 | **6** | Digest |  |
| 224 | 17:57 | 10-24 | X | 4 | Red Sea | Protests in eastern Sudan over prices | 2 | 1 | 1 | 2 | **6** | Digest |  |
| 225 | 18:11 | 10-24 | X | 4 | Sudan | Polio confirmed, campaign 26-29 Oct | 2 | 1 | 1 | 0 | **4** | Merge/suppress | Dup of #223 |
| 226 | 20:24 | 10-24 | X | 5 | West Kordofan | UN report: drones on IDP shelters El Ghbash/Nyala 6-10 Oct, 25 killed | 3 | 3 | 2 | 0 | **8** | Merge/suppress | Stale (6-10 Oct) |
| 227 | 22:53 | 10-24 | X | 4 | Blue Nile | 30+ Tigrayan fighters killed near Al-Burka | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of #211 |

### 2026-10-24 — 19 alerts

| # | UTC | Alerted | Src | Sev | Location | Alert | R | I | S | N | **/10** | Verdict | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 228 | 01:51 |  | X | 4 | Ed Damazine | Bread prices force switch to sorghum | 2 | 1 | 1 | 1 | **5** | Digest |  |
| 229 | 04:09 |  | X | 4 | Sudan | Paid queue-standing at fuel stations | 1 | 1 | 1 | 1 | **4** | Suppress |  |
| 230 | 08:24 |  | X | 4 | Sudan | 400+/day crossing to eastern Chad, 20x previous rate | 3 | 3 | 1 | 2 | **9** | Alert | Displacement |
| 231 | 08:35 |  | X | 4 | Sudan | Intensive drone strikes on El Fasher | 2 | 2 | 0 | 0 | **4** | Merge/suppress | Dup of #162 |
| 232 | 10:07 |  | X | 4 | Sudan | ICRC: rising civilian harm from airstrikes | 2 | 1 | 0 | 0 | **3** | Suppress | Roundup |
| 233 | 10:55 |  | X | 4 | Sudan | Poor rainfall threatens Darfur season | 2 | 2 | 0 | 0 | **4** | Merge/suppress | Dup of #216 |
| 234 | 11:05 |  | X | 4 | Sudan | Refugees in Egypt wait for permits until 2028 | 1 | 1 | 0 | 1 | **3** | Suppress |  |
| 235 | 12:56 | 10-26 | X | 4 | Kosti | 20,000 IDPs in Qoz al-Salaam camp face acute water shortage | 3 | 2 | 2 | 2 | **9** | Alert | Alerted 2 days late |
| 236 | 13:42 | 10-26 | X | 4 | West Kordofan | Airstrikes around Al-Nuhud destroy 10 RSF vehicles, fuel site | 1 | 1 | 2 | 2 | **6** | Digest | Military targets |
| 237 | 14:33 | 10-26 | X | 3 | Khartoum | Joint forces vehicle runs over 16, 8 killed | 2 | 2 | 2 | 2 | **8** | Alert | Severity 3 still alerted |
| 238 | 14:59 | 10-26 | X | 4 | Sudan | Airstrikes on RSF in El-Nahud, 10 vehicles 8 tankers | 1 | 1 | 2 | 0 | **4** | Merge/suppress | Dup of #236 |
| 239 | 15:04 | 10-26 | X | 4 | East Darfur | Food crisis in Sha'aria | 2 | 2 | 1 | 0 | **5** | Merge/suppress | Dup of #169 |
| 240 | 15:25 | 10-26 | X | 4 | Sudan | Military vehicle strikes civilians, 8 dead | 2 | 2 | 0 | 0 | **4** | Merge/suppress | Dup of #237 |
| 241 | 15:50 | 10-26 | X | 4 | West Kordofan | UN report: drone attacks on IDP camps, 25 dead | 3 | 3 | 1 | 0 | **7** | Merge/suppress | Dup of #226 |
| 242 | 15:55 | 10-26 | X | 4 | South Kordofan | Airstrikes on militia positions | 1 | 1 | 0 | 1 | **3** | Suppress |  |
| 243 | 16:04 | 10-26 | X | 4 | West Darfur | Malaria in El Geneina: 55+ deaths in 3 weeks | 3 | 3 | 2 | 2 | **10** | Alert |  |
| 244 | 16:58 | 10-26 | X | 4 | Um Durman | Long queues at charity kitchens in Al-Iskan | 2 | 1 | 1 | 1 | **5** | Digest |  |
| 245 | 18:16 | 10-26 | X | 4 | South Kordofan | RSF drones target miners at Bajun mine | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Earlier incident (c. 19 Oct), stale |
| 246 | 18:49 | 10-26 | X | 4 | Um Durman | Joint Forces vehicle into transport stop, 8 killed 30 injured | 2 | 2 | 2 | 0 | **6** | Merge/suppress | Dup of #237 |

### 2026-10-25 — 22 alerts

| # | UTC | Alerted | Src | Sev | Location | Alert | R | I | S | N | **/10** | Verdict | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 247 | 06:44 | 10-26 | X | 4 | Um Rawaba | Second day of protests at military bases, explosions | 2 | 2 | 1 | 2 | **7** | Alert |  |
| 248 | 06:48 | 10-26 | X | 4 | Sudan | Omdurman vehicle incident, 8 killed | 2 | 2 | 1 | 0 | **5** | Merge/suppress | Dup of #237 |
| 249 | 06:53 | 10-26 | X | 4 | Khartoum | Fuel crisis, transport near non-existent | 2 | 1 | 0 | 0 | **3** | Merge/suppress | Dup of #47 |
| 250 | 08:26 | 10-26 | X | 4 | Red Sea | Protesters block Egypt road over alleged strikes on miners | 2 | 2 | 1 | 2 | **7** | Alert | Partisan claim; road blockage real |
| 251 | 08:29 | 10-26 | X | 4 | South Darfur | Drone attacks 21-22 Oct on Nyala and Abu Jabra | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #95/#205 |
| 252 | 08:40 | 10-26 | X | 4 | Sudan | Flour sack 190,500 SDG | 2 | 1 | 1 | 0 | **4** | Merge/suppress | Dup of #209 |
| 253 | 08:45 | 10-26 | X | 4 | Gedaref | Gold mine collapse in Salmin, dozens trapped | 2 | 2 | 2 | 2 | **8** | Alert |  |
| 254 | 10:23 | 10-26 | X | 4 | Sudan | Fuel queues in Amira, Gezira | 1 | 1 | 1 | 0 | **3** | Merge/suppress | Dup of fuel cluster |
| 255 | 10:24 | 10-26 | X | 4 | North Kordofan | RSF kill 3 at Jebel Al-Dar, family flees on foot | 3 | 2 | 2 | 2 | **9** | Alert |  |
| 256 | 10:45 | 10-26 | X | 4 | West Darfur | Food crisis from agricultural failure | 2 | 2 | 0 | 1 | **5** | Digest |  |
| 257 | 13:04 | 10-26 | X | 4 | Sudan | Flour sack 200,000 SDG | 2 | 1 | 1 | 0 | **4** | Merge/suppress | Dup of #209 |
| 258 | 13:21 | 10-26 | X | 4 | Khartoum | Bread shortages, Damazin price approved | 2 | 1 | 0 | 0 | **3** | Merge/suppress | Dup of #118 |
| 259 | 13:39 | 10-26 | X | 4 | Khartoum | Fuel shortages, bread to 1,000 expected | 2 | 1 | 0 | 0 | **3** | Merge/suppress | Dup of #118 |
| 260 | 13:47 | 10-26 | X | 5 | Khartoum | RSF checkpoint violence, contaminated food, starvation | 2 | 2 | 0 | 0 | **4** | Suppress | Feature piece, no incident |
| 261 | 14:10 | 10-26 | X | 4 | Sudan | Damazin bakeries: 2 loaves for 1,000 | 2 | 1 | 1 | 0 | **4** | Merge/suppress | Dup of #228 |
| 262 | 14:12 | 10-26 | X | 4 | Sudan | Sultan of Dar Masalit appeals for refugees in Chad | 2 | 2 | 0 | 1 | **5** | Digest |  |
| 263 | 15:08 | 10-26 | X | 4 | Sudan | Airstrike destroys 7 militia vehicles in El Fasher | 1 | 1 | 1 | 1 | **4** | Suppress | Military |
| 264 | 16:53 | 10-26 | X | 4 | North Darfur | Dokki camp (Chad): starvation, aid halted 4 months, 4 deaths | 3 | 2 | 2 | 2 | **9** | Alert | Mislocated (Chad) |
| 265 | 17:10 | 10-26 | X | 4 | Nyala Janoub | Cash shortage: traders take 50% of transfers | 2 | 1 | 2 | 2 | **7** | Alert |  |
| 266 | 18:45 | 10-26 | X | 4 | West Darfur | Poor season, hunger and malnutrition rising | 2 | 2 | 0 | 0 | **4** | Merge/suppress | Dup of #256 |
| 267 | 18:53 | 10-26 | X | 4 | South Darfur | Airstrikes in Nyala kill foreign personnel and RSF | 1 | 1 | 1 | 1 | **4** | Suppress | Military |
| 268 | 19:56 | 10-26 | X | 4 | Kassala | 110 hostages rescued in Wadi al-Ashari | 2 | 2 | 2 | 2 | **8** | Alert | Trafficking |

### 2026-10-26 — 41 alerts

| # | UTC | Alerted | Src | Sev | Location | Alert | R | I | S | N | **/10** | Verdict | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 269 | 04:15 |  | DM | 4 | Al Fao | Drones hit Al Fao power station, 8h outage | 3 | 2 | 2 | 2 | **9** | Alert | First of power-station wave |
| 270 | 05:27 |  | X | 4 | Sennar | Drones from Ethiopia hit power stations in Sennar and other states | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #269 |
| 271 | 07:30 |  | DM | 4 | Wasat Al Gedaref | RSF hit 5 power stations in Gedaref | 3 | 2 | 1 | 1 | **7** | Alert | Wave widens |
| 272 | 07:40 |  | X | 4 | West Kordofan | 3 civilians incl. teacher killed in Gereisa prison | 3 | 2 | 2 | 2 | **9** | Alert |  |
| 273 | 07:58 |  | X | 4 | Gedaref | RSF target water and electricity stations | 3 | 2 | 0 | 0 | **5** | Merge/suppress | Dup of #271 |
| 274 | 08:23 |  | X | 4 | Kosti | 600 shelter kits, 500 food parcels distributed | 1 | 0 | 2 | 1 | **4** | Suppress | Aid delivery news |
| 275 | 08:27 |  | DM | 4 | Sinja | Drones on Sennar power stations, outages in 3 states | 3 | 3 | 1 | 1 | **8** | Alert | Scale update |
| 276 | 08:30 |  | DM | 4 | Wasat Al Gedaref | Power stations hit, outages in 4 states | 3 | 3 | 1 | 0 | **7** | Merge/suppress | Dup of #275 |
| 277 | 08:38 |  | X | 4 | Gedaref | Drones from Ethiopia hit electricity stations | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #271 |
| 278 | 08:42 |  | X | 4 | Al Fasher | 70,000 displaced returned to El Fasher; 100 women detained | 3 | 2 | 1 | 1 | **7** | Alert | Returns figure new; detention dup |
| 279 | 09:39 |  | X | 4 | Sennar | Electricity Co lists stations hit | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #269 |
| 280 | 09:56 |  | X | 4 | Sennar | Power stations attacked, outages | 3 | 2 | 0 | 0 | **5** | Merge/suppress | Dup of #269 |
| 281 | 10:01 |  | X | 5 | Central Darfur | Drone on restaurant in 'Ed Daein, Central Darfur', 19 killed | 3 | 3 | 1 | 0 | **7** | Merge/suppress | Dup of #67 (19 Oct), mislocated |
| 282 | 10:47 |  | X | 5 | Sudan | 974,000 fled to Chad since war began; 1.4M total | 3 | 2 | 0 | 0 | **5** | Digest | Cumulative statistic |
| 283 | 10:49 |  | X | 4 | Sennar | RSF drones bomb power stations | 3 | 2 | 0 | 0 | **5** | Merge/suppress | Dup of #269 |
| 284 | 10:59 |  | X | 4 | Gedaref | Electricity stations in Gedaref attacked | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #271 |
| 285 | 11:08 |  | X | 4 | North Darfur | El Fasher displaced in camps near Port Sudan lack food/medicine | 3 | 2 | 1 | 1 | **7** | Alert | Mislocated |
| 286 | 11:12 |  | X | 4 | Sudan | Vegetable prices alter consumption | 1 | 1 | 0 | 1 | **3** | Suppress |  |
| 287 | 11:56 |  | X | 4 | Gedaref | Militia from Ethiopia target water/electricity | 3 | 2 | 0 | 0 | **5** | Merge/suppress | Dup of #271 |
| 288 | 12:02 |  | X | 4 | Blue Nile | ~39,200 displaced/refugee households in Qaisan, Kurmuk, Khor al-Dhab | 3 | 3 | 2 | 2 | **10** | Alert | Displacement figures |
| 289 | 12:04 |  | X | 5 | North Darfur | Famine unfolding in Tawila for lack of funding | 3 | 2 | 0 | 1 | **6** | Digest |  |
| 290 | 13:04 |  | X | 4 | Sudan | Group survives 2 weeks in desert reaching Toloum camp | 2 | 1 | 1 | 1 | **5** | Digest | Anecdote (Chad) |
| 291 | 13:04 |  | X | 4 | Sudan | 9,000+ newly uprooted Sep to mid-Oct; aid <25% of needs | 3 | 2 | 1 | 2 | **8** | Alert |  |
| 292 | 13:20 |  | X | 4 | Sudan | Iridimi camp, Chad: 95,000 refugees, water scarce | 2 | 2 | 1 | 1 | **6** | Digest |  |
| 293 | 13:27 |  | X | 4 | Khartoum | 161 drone attacks on Khartoum over two nights | 2 | 2 | 1 | 2 | **7** | Alert | Escalation |
| 294 | 13:28 |  | X | 4 | Sudan | 11 electricity stations hit in October | 3 | 2 | 1 | 0 | **6** | Digest | Roundup of power wave |
| 295 | 13:51 |  | X | 4 | Sudan | El Fasher one year after capture | 2 | 1 | 0 | 0 | **3** | Suppress | Background |
| 296 | 14:02 |  | X | 4 | Ag Geneina | SAF strikes on RSF at El Geneina airport 22-26 Oct | 1 | 1 | 2 | 2 | **6** | Digest | Military targets |
| 297 | 14:03 |  | FIRMS | 4 | Heiban | 23 wild fire hotspots | 0 | 0 | 1 | 0 | **1** | Suppress |  |
| 298 | 14:41 |  | X | 4 | Northern | Al-Dabba camp: severe shortages | 3 | 2 | 1 | 2 | **8** | Alert |  |
| 299 | 15:06 |  | FIRMS | 4 | Al Radoum | 20 wild fire hotspots | 0 | 0 | 1 | 0 | **1** | Suppress |  |
| 300 | 15:36 |  | X | 4 | Sudan | Army advances in 17 areas incl. Sodri, Al-Muzrub | 1 | 1 | 1 | 2 | **5** | Digest | Frontline shift |
| 301 | 16:06 |  | X | 4 | Khartoum | Bread shortage plus armed looting at night | 2 | 2 | 1 | 1 | **6** | Digest |  |
| 302 | 16:26 |  | X | 4 | Sudan | Polio campaign launched for 11M children | 2 | 1 | 1 | 0 | **4** | Merge/suppress | Dup of #223 |
| 303 | 17:23 |  | X | 4 | Khartoum | Bakery looting amid hunger | 2 | 2 | 0 | 1 | **5** | Digest |  |
| 304 | 17:32 |  | X | 4 | Khartoum | Fuel shortage drives bread prices | 2 | 1 | 0 | 0 | **3** | Merge/suppress | Dup of #118 |
| 305 | 17:43 |  | X | 4 | Sennar | Drones hit electricity stations, Singa staff injured | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #269 |
| 306 | 17:44 |  | X | 4 | Ghubaish | 3 killed by militia in Dqris prison | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #272 |
| 307 | 19:51 | 10-27 | X | 5 | Khartoum | 40,000 fled; trapped at Kakuma camp (Kenya) | 2 | 2 | 1 | 1 | **6** | Digest | Mislocated (Kenya) |
| 308 | 20:08 | 10-27 | X | 4 | North Darfur | Two girls raped and beaten in Tarni forest | 3 | 2 | 2 | 2 | **9** | Alert | GBV |
| 309 | 20:20 | 10-27 | X | 4 | Sudan | WFP rations for refugees in Chad cut to 200k of 1M | 3 | 2 | 1 | 1 | **7** | Alert |  |

### 2026-10-27 — 16 alerts

| # | UTC | Alerted | Src | Sev | Location | Alert | R | I | S | N | **/10** | Verdict | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 310 | 02:28 |  | X | 4 | North Darfur | UN warns on Tawila (900k displaced) shortages | 3 | 2 | 1 | 1 | **7** | Alert |  |
| 311 | 02:53 |  | X | 4 | South Darfur | Night airstrikes on Tanqoj market west of Nyala | 3 | 2 | 1 | 2 | **8** | Alert |  |
| 312 | 04:35 |  | DM | 4 | Al Fasher | Countries highlight El Fasher food crisis | 2 | 1 | 0 | 1 | **4** | Suppress | Diplomacy |
| 313 | 07:01 |  | X | 4 | Al Leri | Militia drones hit mining areas, 2 killed | 3 | 2 | 2 | 2 | **9** | Alert |  |
| 314 | 07:52 |  | X | 5 | South Darfur | Drone on Nyala market, 21 killed 40+ injured | 3 | 3 | 2 | 1 | **9** | Alert | Toll update of #311 |
| 315 | 08:29 |  | X | 4 | North Kordofan | Polio and cholera response campaign | 3 | 2 | 1 | 2 | **8** | Alert | Cholera is new |
| 316 | 08:49 |  | DM | 4 | Um Durman | Protest marking El Fasher anniversary | 1 | 0 | 2 | 2 | **5** | Digest |  |
| 317 | 10:07 |  | X | 4 | Sudan | UK sanctions 15 commanders | 0 | 0 | 1 | 2 | **3** | Suppress | Politics |
| 318 | 10:55 |  | X | 4 | Sudan | Bread prices rise in Ed Damer | 2 | 1 | 1 | 0 | **4** | Merge/suppress | Dup of bread cluster |
| 319 | 11:03 |  | X | 4 | Sudan | 172 displaced detained by RSF at Kalma camp | 3 | 2 | 2 | 2 | **9** | Alert | Protection |
| 320 | 11:35 |  | X | 4 | Sudan | Government denies famine warnings | 1 | 1 | 0 | 1 | **3** | Suppress | Politics |
| 321 | 11:50 |  | X | 4 | South Kordofan | Drone strikes on mining areas, fires | 3 | 2 | 1 | 0 | **6** | Merge/suppress | Dup of #313 |
| 322 | 12:19 |  | X | 4 | Sudan | UN SG warns of famine risk | 2 | 2 | 0 | 1 | **5** | Digest |  |
| 323 | 13:02 |  | FIRMS | 4 | Abassiya | 9 wild fire hotspots | 0 | 0 | 1 | 0 | **1** | Suppress |  |
| 324 | 13:13 |  | X | 4 | Blue Nile | Militia attacks on health facilities; 27 camps in region | 3 | 2 | 1 | 1 | **7** | Alert |  |
| 325 | 13:23 |  | X | 4 | South Darfur | Army drone on Tanqunq market, Dumiya, 14 killed 6 injured | 3 | 3 | 2 | 0 | **8** | Merge/suppress | Dup of #314 |
