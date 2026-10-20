# Genre comparison (Oct 2026) - evidence and gaps
Confidence: L = low (self-reported / vendor / secondhand), M = medium. No genre has audited data. Direct traffic figures for Japanese investing sites could not be obtained (Similarweb not reachable from the research environment).

| Axis | 訪日旅行 (EN) | 投資・証券 (JA) | 雑学 (JA) | 高単価生活系 (JA: 光回線/転職/脱毛等) |
|---|---|---|---|---|
| Payout per conversion | Hotels ~4% (Booking) / ~4-7% (Agoda), paid after stay; tours 2-8% (L) | Securities account: ~300-3,000 JPY listed; credit card/FX 5k-80k JPY (L, dated) | AdSense only, no affiliate intent | 5k-30k JPY (L) |
| Display ad RPM | Travel $6-18 (L, conflicting) | Finance $15-40 (L); JA AdSense generic ~250-400 JPY RPM | Entertainment proxy $7-15 (L); no trivia data | n/a |
| Demand | 42.7M visitors in 2025 (+15.8%, JNTO, M) | NISA accounts 23.3M (FSA, Mar 2024, M); keyword volumes unobtained | Large but AI Overviews target informational queries | n/a |
| Competition / YMYL | Mid; incumbents japan-guide.com etc. | Highest: YMYL; 67% of YMYL sites hit by Dec 2025 update (vendor, L) | Low barrier but traffic erosion (median -85% over 4y across 100 blogs, Semrush via blog, L) | Large media dominate; mid |
| Regulation | Light | FIEA/advertising rules, stealth-marketing rules; no stock-picking advice | Light | Light-mid (consumer law) |
| Fit with AI automation | Needs first-hand signals; mid | Worst (YMYL expertise) | Easy to produce, hard to rank/monetise | Mid |
| Owner can QA content | English: harder for JA-native owner | JA: yes | JA: yes | JA: yes |

Conclusion: 訪日旅行 is NOT shown to be the best. It is mid on every axis. Finalists to validate with real keyword data (Keyword Planner / Ahrefs / Search Console): (A) 訪日旅行 EN, (B) 国内向け高単価生活系 JA. 投資 offers the largest audience but is the worst fit for automation. 雑学 is the worst for revenue.
Validation protocol: per finalist pick 30 target keywords; record monthly volume, whether top-10 contains individual blogs, and payout; estimate revenue = volume x CTR x CVR x payout. Decide on numbers, not narratives.

## Validation round 1: SERP composition (Oct 2026)
Method: 11 decision-stage queries run through the research search tool (not Google; US-based, ordering is indicative only). Counted individual blogs vs corporate/comparison media in the top results. Search volume NOT obtainable here (Ahrefs/Similarweb/Keyword Planner unreachable); fill `validation/keywords.csv` -> `python -m validation.estimate`.

| Query | Result mix | Individual blogs |
|---|---|---|
| is japan rail pass worth it | solo blogs (Two Wandering Soles, A Brother Abroad etc.) + 2 sellers | ~7/9 |
| where to stay in tokyo first time | all solo travel blogs | 8/8 |
| 7 day japan itinerary | Rough Guides + solo blogs | ~6/7 |
| japan esim vs pocket wifi | vendor blogs (Saily, MicroEsim) | 0/10 (vendors) |
| suica vs pasmo vs icoca | thin: one translated site + housing blog | ~1/2 |
| 光回線 おすすめ 比較 | Selectra, Exidea, GMO (companies) | 0/9 |
| ポケットWiFi おすすめ 比較 | my-best, Selectra, GMO, Exidea | 0/9 |
| 格安SIM おすすめ 比較 | BCN, my-best, Selectra, ciatr | 0/9 |
| ウォーターサーバー おすすめ 比較 | Oricon, my-best | 0/9 |
| 転職エージェント おすすめ 20代 | Coeteco, Exidea, financial-field, crex etc. | ~1/9 |
| NISA おすすめ 証券会社 | Oricon, my-best, SOICO, crex | 0/9 |

Finding: individual blogs rank on inbound decision queries; corporate comparison media hold every Japanese head term tested. Payout per conversion is far higher in JA (10-20k JPY vs ~1-2k JPY per hotel booking), but a new site cannot realistically reach those head terms; only long-tail would be winnable.
Limits: small sample, non-Google engine, no volumes, payouts from third-party pages.
