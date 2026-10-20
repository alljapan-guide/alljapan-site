# Decisions needing owner approval
1. **Site name/domain**: placeholder "Japan Compass" at example.github.io. Buy a domain (~$10-15/yr) or keep GitHub Pages.
2. **Hosting**: GitHub Pages via the included workflow (free). Needs Pages enabled (Source: GitHub Actions) and the base_url updated.
3. **API cost**: article drafting uses the Claude API (`ANTHROPIC_API_KEY` secret). Roughly cents to ~$0.2 per article; 1/day.
4. **Publishing autonomy**: fully automatic after passing the gate (default) vs. PR-for-review. Kill switch: repo variable `JA_AUTOPUBLISH=false`.
5. **Affiliate sign-ups**: require your identity/tax details; I cannot do these. Start with Travelpayouts.
6. **Disclosure of AI assistance**: the About page states AI-assisted drafting. Recommended to keep.
7. **Repo placement**: dedicated repository under a neutral organization.

## Update: niche scope (owner direction)
Owner wants more than inbound travel. Decision (Claude): **Japan products + travel for overseas readers** ("Japan Compass"), run as one site with two clusters:
- `products` (snack boxes, knives, matcha, skincare, stationery, buying from overseas) - monetised via Bokksu, Dokodemo, Amazon, proxy services.
- travel clusters (transport, hotels, itineraries) - Booking/Klook/Airalo etc.
Products come first in the queue (priority 10), because they do not depend on travel seasonality and fit "PR Japanese goods".

### Fallback rule (Plan B: Japanese-language, domestic products for Japanese readers)
Switch if, after 6 months (about 150+ indexed articles): fewer than 5,000 organic sessions/month, OR no affiliate program has approved/paid out. Plan B is a second site config (`language: ja`, ASPs: A8.net / Rakuten / Amazon.co.jp / ValueCommerce). The pipeline is reusable; only config, prompt language and topics change.
Why not start with Plan B: Japanese product-comparison niches are dominated by large media and ASP-fed affiliate sites; new automated sites compete head-on.
