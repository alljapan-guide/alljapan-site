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
