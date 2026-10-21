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
