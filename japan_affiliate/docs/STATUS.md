# Status - 2026-10-20
Network opened (owner added hosts). Real verification run: all 23 facts OK against official pages (data/facts.json, verified_on set).
Found & fixed by the real check: 'Yamanote' was NOT on the GO TOKYO Shinjuku page (fact text corrected); pocket-WiFi page says 'delivered' not 'delivery'.
JR East (jreast.co.jp) blocks automated access (Akamai 403), so JR East-sourced facts were removed; the IC-card article now cites Apple Support and PASMO.
Wikimedia: needs a descriptive User-Agent with a REAL contact (placeholder => 403), thumbnails are served from upload.wikimedia.org (not thumb.), and rate-limits (429): fetch_images waits and retries.
Still not exercised: research / generate / verify --heal (need ANTHROPIC_API_KEY). 
Local preview: python -m pipeline.build --draft. Strict build needs contact_email in config/site.json.
Unknown official affiliate programs: Japan Rail Pass seller, pocket WiFi rental, Viator, GetYourGuide (links stay plain text until confirmed).

## 2026-10-21 design update
Home page redesigned (Wa theme): hero, left sidebar with search/topics/latest, topic tabs, photo cards, dark mode, mobile layout. See docs/DESIGN.md. Tests: 33 pass. Search is client-side (titles, descriptions, topics).

## 2026-10-21 hosting
Owner prefers hosting on Cloudflare Pages with GitHub kept only as storage/automation. Workflow publishes to Cloudflare Pages when secrets CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID exist (project name from repo variable CF_PAGES_PROJECT, default 'alljapan'); otherwise it keeps publishing to GitHub Pages. See docs/CLOUDFLARE_SETUP.md.

## 2026-10-21 hosting switched
Public site now served by Cloudflare Pages (project alljapan, custom domain alljapan.win). The workflow deploys there (secrets CLOUDFLARE_API_TOKEN / CLOUDFLARE_ACCOUNT_ID set); GitHub Pages was unpublished by the owner. www.alljapan.win still has an old GitHub CNAME (optional cleanup). Desktop tabs now wrap instead of scrolling.

## 2026-10-22 daily articles
Added osaka-food-guide, japan-luggage-forwarding, japan-cherry-blossom-guide (38 facts, all verified against official pages). 11 articles total. Scheduled routine cannot push (no add_repo in routine sessions); today's batch was produced in the main session. Fix: attach the repo (push access) as the routine's source in claude.ai.

## 2026-10-23 daily articles
Added nara-day-trip-from-kyoto-osaka, fushimi-inari-guide, japan-travel-insurance (57 new facts, all verified against official pages; 6 Wikimedia photos). 14 articles; local strict build and tests pass.
DEPLOY BLOCKED (not caused by these articles): gotokyo.org returns 502 / is unreachable, so 7 facts (shinjuku_lines, sensoji_oldest, tokyo_station_area, tokyo_sakura_window, tokyo_full_bloom, tokyo_hanami, tokyo_rikugien) fail verification in CI and the strict build stops at japan-cherry-blossom-guide. CI runs since 2026-10-22 13:54 UTC fail for this reason; the live site stays on the last good deploy. Fix when gotokyo.org recovers, or re-source those facts to another official page.

## 2026-10-24 daily articles + deploy fix
Re-sourced 7 facts from gotokyo.org (unreachable from CI since 2026-10-22) to JNTO pages (Shinjuku, Tokyo Station area, Tokyo itineraries page, Shinjuku Gyoen, Rikugien, hanami guide); cherry-blossom and where-to-stay-in-tokyo wording updated to match. CI deploy of the 2026-10-23 batch then succeeded.
Added japan-visa-and-entry-basics, japan-local-laws-for-visitors, japan-weather-by-season (36 new facts, 6 photos). 17 articles. Wikimedia download 429s: retry or change the subject.

## 2026-10-25 daily articles
Added japan-licensed-tour-guides, japan-halal-travel-guide, which-airport-to-fly-into-japan (43 new facts, all verified on JNTO pages; 6 photos). 20 articles. Two photos needed a different subject because Wikimedia returned 429 on download.

## 2026-10-26 daily articles
Added japan-opening-hours-and-holidays, japan-etiquette-for-first-timers, japan-budget-travel-tips (47 new facts, all verified on JNTO pages; 6 photos). 23 articles. One photo subject was changed after repeated "no licensed photo" results. Travel topics in topics.json are used up; new topics come from JNTO plan pages (still unused: plug-and-electricity, traveling-with-disability, emergencies).

## 2026-10-26 owner direction
Owner asked for more articles on famous souvenirs and famous shrine pilgrimages. 12 topics added to data/topics.json (priority 9) with source pages listed in docs/TOPIC_BACKLOG.md. The daily routine should take these first.

## 2026-10-26 Search Console "page has redirect"
Cause: Cloudflare Pages redirects /x.html to /x, but canonical, sitemap and internal links used the .html form. Fix: build.py now emits extensionless canonical/sitemap URLs and rewrites internal links (clean_url / clean_links). Re-submit the sitemap and use "Validate fix" in Search Console.

## 2026-10-27 daily articles
Added japan-souvenirs-guide, shinto-shrine-etiquette, meiji-jingu-guide from the owner-requested backlog (docs/TOPIC_BACKLOG.md; 57 new facts, all verified on JNTO pages; 6 photos). 26 articles. Remaining backlog: osaka-souvenir-sweets, hiroshima-souvenirs-momiji-manju, shotengai-souvenir-shopping, tohoku-souvenirs, japan-ekiben-guide, ise-jingu-guide, izumo-taisha-guide, itsukushima-miyajima-guide, famous-shrines-in-japan.

## 2026-10-27 more photos per article (owner request)
Added 2 photos to every article (most pages now have 4, three have 3: japan-etiquette-for-first-timers, japan-halal-travel-guide, tokyo-kyoto-osaka-7-day-itinerary because no suitable licensed photo was found). All credited, licence-checked Commons files. Search results were reviewed by title: unrelated hits (games, museum items, paintings, people) were dropped and re-queried. fetch_images now saves data/images.json after every photo, so an interrupted run keeps its progress.

## 2026-10-28 daily articles
Added ise-jingu-guide, izumo-taisha-guide, itsukushima-miyajima-guide from the owner-requested backlog (62 new facts, all verified on JNTO pages; 4 photos each = 12 new). 29 articles. data/images.json may now carry an optional "caption" per photo (used instead of the Commons-title caption when the title is unreadable; set only after checking the photo by eye). Note: two JNTO pages give slightly different Izumo shimenawa lengths (13.5 vs 13.6 m); the Izumo article says so. Remaining backlog: osaka-souvenir-sweets, hiroshima-souvenirs-momiji-manju, shotengai-souvenir-shopping, tohoku-souvenirs, japan-ekiben-guide, famous-shrines-in-japan.

## 2026-10-28 new article banners (owner chose option A)
Article hero images are now original Japanese-style illustrations per cluster (pipeline/hero_art.py): itineraries = Fuji, sun and sakura petals; culture = torii at dusk; transport = bullet train and Fuji; hotels = ryokan roof and pine; food = noodle bowl; shopping = paper lanterns; seasonal = sakura branch over Fuji; connectivity = radio arcs; planning = folding fan. Unknown clusters fall back to the Fuji scene. The old generic banner is kept as _legacy_hero_svg in visuals.py (unused).

## 2026-10-28 Search Console review
First impressions appeared (70 impressions, 0 clicks, avg position 45.1 over 10/20-10/25). Titles/descriptions/H2 of where-to-stay-in-kyoto, japan-ic-card-guide and osaka-food-guide were adjusted toward the queries already seen (text only; no facts changed). Recheck Performance (Pages/Queries) in 1-2 weeks.

## 2026-10-29 daily articles
Added osaka-souvenir-sweets, hiroshima-souvenirs-momiji-manju, shotengai-souvenir-shopping from the owner-requested backlog (46 new facts, all verified on JNTO pages; 10 photos: Osaka 4, Hiroshima 3, shotengai 3 because no suitable licensed photo was found for the other slots). 32 articles. Remaining backlog: tohoku-souvenirs, japan-ekiben-guide, famous-shrines-in-japan.

## 2026-10-30 affiliate-oriented articles (owner request)
Added tokyo-to-osaka-bullet-train (Trip.com Tokyo-Osaka trains + rail pass), where-to-stay-in-osaka (Trip.com Osaka hotels + Booking.com), tokyo-things-to-do-first-time (Trip.com Tokyo things to do + Klook + Viator). 60 new facts from JNTO (Osaka and Tokyo pages, five Osaka area pages) and JR Central (Shinkansen page); all verified; 12 photos. 35 articles. Singapore question: JNTO statistics pages (jnto.go.jp) are not reachable from this environment, so no visitor-profile figures are used in articles.

## 2026-10-29 daily articles (second batch)
Added famous-shrines-in-japan (reuses 31 existing shrine facts, tagged for the new topic), tohoku-souvenirs and japan-ekiben-guide (52 new facts, all verified on JNTO pages; 12 photos). 38 articles. Tohoku source story is dated 24 December 2019, so the article tells readers to check shops and hours. Wikimedia returned 429 repeatedly; the Daruma Bento photo slot was replaced with a generic bento photo and captions were checked by eye. Remaining backlog: none in docs/TOPIC_BACKLOG.md; unused travel ideas from JNTO plan pages (plug-and-electricity, traveling-with-disability, emergencies).

## 2026-10-29 owner direction: prioritise Trip.com-friendly articles
Trip.com affiliate is approved. Daily routine: prefer topics where a Trip.com link fits naturally (hotels, trains, things to do), using programs already in config/affiliates.json: trip_hotels (Tokyo hotels), trip_kyoto_hotels, trip_osaka_hotels, trip_trains (Tokyo-Kyoto), trip_trains_osaka (Tokyo-Osaka), trip_things, trip_tokyo_things. Link only where it helps the reader's decision, and keep facts sourced from official pages. Candidate topics (each needs official sources first): Kyoto things to do for first-timers, Osaka things to do, Kyoto-Osaka and Osaka-Hiroshima train guides, where to stay in Hiroshima / Nara, airport-to-city access with hotel picks. New programs need an owner-generated link in the Trip.com portal before they can be added.

## 2026-10-31 daily articles (Trip.com-friendly, owner direction)
Added kyoto-things-to-do-first-time (Trip.com things to do + Kyoto hotels, Klook, Viator), osaka-things-to-do-first-time (Trip.com things to do + Osaka hotels, Klook, Viator), tokyo-to-kyoto-bullet-train (Trip.com Tokyo-Kyoto trains, rail pass, Kyoto hotels). 75 new facts from JNTO (Kyoto, Gion and Higashiyama, Central Kyoto, Osaka, Osaka Castle, Dotonbori and Shinsaibashi) and JR Central (Kyoto page); shinkansen and rail pass facts reused. 12 photos, all checked by eye; two search hits were rejected (a painting of the Siege of Osaka Castle, and a local train at Kyoto Station) and re-fetched. 41 articles. The Tokyo-Kyoto article deliberately gives no travel time because the JR Central Kyoto page shows it only as a graphic, so no verifiable figure could be quoted. Agoda application was declined (generic reasons, no specific cause given); retry later.

## 2026-11-01 daily articles (Trip.com things-to-do destinations)
Added hiroshima-things-to-do-first-time, fukuoka-things-to-do-first-time, kanazawa-things-to-do-first-time, each with Trip.com things to do (trip_things) plus Klook and Viator. 81 new facts from JNTO (Hiroshima, Hiroshima City, Fukuoka, Fukuoka City, Ishikawa); the Hiroshima article also reuses the Miyajima facts. 12 photos, checked by eye. Rejected and re-fetched: a residential tower mislabelled "Momochi Tower" (replaced by a real Fukuoka Tower photo). Hiroshima's fourth photo is a tram-stop entrance, not a tram, and the caption says so. The Kanazawa article rests on one JNTO page (Ishikawa prefecture); no Kanazawa-specific JNTO page was reachable (404). 44 articles. Fact ids use prefix hr_ for Hiroshima prefecture because hs_ was already taken by the Hiroshima souvenirs article.

## 2026-11-02 Search Console review (owner screenshots, 7 days 10/25-10/31)
Totals: 1 click, 328 impressions, CTR 0.3%, average position 52.5. Only click: "osaka itinerary 7 days" -> tokyo-kyoto-osaka-7-day-itinerary. Impressions are dominated by the travel insurance cluster: page japan-travel-insurance 92 impressions; queries "japan travel insurance" 35, "is travel insurance mandatory for japan" 7, "japan travel insurance requirements" 7, "do you need travel insurance for japan" 6, "japanese travel insurance" 5, "japan travel insurance for visitors" 5, "visiting japan insurance" 4. Other queries seen: "tokyo kyoto osaka" 7, "best area to stay in kyoto" 4. Top pages: itinerary 13, japan-travel-insurance 92, home 80, japan-ic-card-guide 30, nara-day-trip 13, osaka-food-guide 13, where-to-stay-in-kyoto 11. Old .html URLs still appear next to the clean ones (japan-ic-card-guide.html, nara-day-trip-from-kyoto-osaka.html, japan-travel-insurance.html): this is the leftover of the 10/26 redirect fix and should merge over time.
Actions for the next daily runs: (1) text-only tuning of japan-travel-insurance: H2s and FAQ phrased like the questions people search ("Is travel insurance mandatory for Japan?", "Do you need travel insurance for Japan?", requirements, for visitors); no fact changes. (2) Add itinerary-style articles that do not overlap the existing 7-day route, e.g. an Osaka-centred 3-day itinerary and a Kyoto-Osaka 5-day itinerary, with Trip.com links. (3) Keep adding internal links from new articles to the insurance and itinerary pages. Recheck Performance weekly (owner sends screenshots of Queries and Pages).

## 2026-11-03 daily articles (5, owner raised the daily count from 3 to 5)
Added kansai-3-day-itinerary-kyoto-nara-osaka, kobe-day-trip-from-osaka, himeji-castle-day-trip-from-osaka, osaka-one-day-itinerary, osaka-3-day-itinerary, aimed at the "osaka itinerary" queries seen in Search Console. 82 new facts from JNTO (itineraries: Kansai Trio, Kobe in 1 Day, Osaka from North to South; pages: Kobe and around, Himeji Castle, Kokoen Garden); the Osaka 3-day article reuses facts from the others. 20 photos, all checked by eye. Rejected and re-fetched: a painting ("The Siege of Osaka Castle", twice; pinned file:Osaka Castle 02bs3200.jpg instead) and a Yodo River view from the Sky Building (replaced by a photo of the building itself). One photo shows shika senbei crackers, not deer, and the caption says so. japan-travel-insurance: headings, title, description and FAQ-style H2 tuned to the searched questions ("Is travel insurance mandatory for Japan?"); no fact changes. 49 articles. Himeji's JNTO destination page was navigation-only, so only the two spot pages were used.

## 2026-11-04 daily articles (5)
Added hakone-trip-from-tokyo (JNTO itinerary, 2 days), kamakura-day-trip-from-tokyo (JNTO itinerary, 1 day), nikko-trip-from-tokyo (JNTO itinerary, 2 days), tokyo-one-day-cultural-itinerary (JNTO "A Cultural Day in Tokyo") and kyoto-one-day-itinerary (JNTO blog "24 Hours in Kyoto", published Feb. 6, 2020; the article says to check current hours). 82 new facts, all verified on JNTO pages; the Nikko article also reuses three Nikko National Park facts. 20 photos, checked by eye. Rejected and re-fetched: a mislabelled Lake Asahi photo (Hakone; replaced by pirate-ship cruise photo), a John La Farge painting and a relief map of Lake Chuzenji (Nikko). Nikko photo 3 is a road sign on the Iroha-zaka seen from a bus window, because no usable real photo of the lake was found; the caption says so; replace it when a better Commons file is found. Trip.com links used: trip_hotels (Tokyo), trip_kyoto_hotels, trip_things. 54 articles.

## 2026-11-05 daily articles (5)
Added kawagoe-day-trip-from-tokyo, mt-takao-day-trip-from-tokyo, tokyo-traditional-and-contemporary-itinerary, amanohashidate-trip-from-kyoto, hida-takayama-to-kyoto-5-day-itinerary, all from JNTO itinerary pages (Kawagoe 1 day, Mt. Takao 1 day, Tokyo Traditional and Contemporary 1 day, Amanohashidate 2 days, Hida Takayama to Kyoto 5 days). 91 new facts, all verified. 18 photos: Mt. Takao and Amanohashidate have 3 photos each because the fourth slot only returned unusable files (a train coupler close-up; an old black-and-white factory photo), so the fourth slot and its photo marker were removed. Kawagoe photo 3 shows traditional candy, not the alley itself, and the caption says so. Rejected earlier in the day: nothing else. The Tokyo article notes that JNTO asks readers to check the Edo Tokyo Museum status (page said it was under renovation). Hida Takayama to Kyoto reuses the Kyoto temple area covered in kyoto-one-day-itinerary. 59 articles. Pace note: Wikimedia 429s again cost most of the time; the routine now publishes the articles whose photos are complete first and finishes the rest later.
