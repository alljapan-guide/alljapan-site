# Japan Compass: strategy and operating plan

## 1. What the reference sites show (research, Oct 2026)
- Revenue mix of a proven mid-size Japan blog (The Navigatio, ~$5k/mo, self-reported 2023): ~45% display ads, ~35% hotel affiliate, ~15% rail-pass affiliate, ~5% other.
  Source: https://www.nichepursuits.com/nele-van-hout-the-navigatio/
- A Travelpayouts case study reports ~$6,700/mo affiliate income from ~700k monthly readers (vendor-published, treat as upper-end marketing): https://www.travelpayouts.com/blog/from-traffic-loss-to-earnings/
- Large base sites: Japan Cheapo/Tokyo Cheapo (self-reported >850k combined monthly reach; affiliate + sponsored posts); Japan Guide; The Navigatio (3M readers/yr claimed).
- Money intents: hotels, passes/transport, eSIM/WiFi, tours/tickets. Information-only posts feed them.
- Verified-ish tour program rates (third-party directories, confirm in each program): GetYourGuide ~8%, Viator up to 8%, Klook ~2-5%, KKday ~2-3%, 30-day cookies.

## 2. Risk that shapes the design
Google's scaled-content-abuse policy and the August 2026 spam update reportedly hit thin affiliate and mass AI pages. So the system is "slow and gated", not "mass produced":
1 article/day max, hard quality gate (length, structure, dated prices, no unverified claims, link-density cap), honest editorial/disclosure pages, no invented first-person experience.

## 3. Steps to monetisation
| Step | What | Who |
|---|---|---|
| 1 | Pipeline + site (this repo, done) | built |
| 2 | Domain + GitHub Pages/Cloudflare, Search Console, sitemap | owner |
| 3 | Join programs: Travelpayouts (fastest, bundles many), Booking.com, Klook, Viator/GYG, Airalo; paste links in `config/affiliates.json` | owner |
| 4 | Seed 30-40 articles in 3 clusters (transport, hotels/areas, itineraries) over ~6 weeks | automated |
| 5 | Add real value signals: owner photos/trip notes, an About page with a real person | owner |
| 6 | Month 3-6: apply to display ads (Mediavine/Raptive need traffic thresholds), expand clusters, refresh old posts | automated + owner |
| 7 | Weekly: Search Console review, prune/merge underperformers, update dated prices | automated report + owner |

## 4. Honest expectations
New domains take 3-9 months to rank. Realistic first-year outcome is small (tens to a few hundred USD/mo) unless a cluster breaks through. Nothing here guarantees revenue.
