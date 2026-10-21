# Design notes (Wa / 和 theme)

Honest note: this is not the opinion of a hired designer. It applies published, citable guidelines and common practice, and every choice below is testable.

| Decision | Why | Source |
|---|---|---|
| Text contrast >= 4.5:1 for normal text (palette checked by `tests/test_theme.py`, light and dark) | WCAG 2.2 success criterion 1.4.3 (AA) | https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html |
| Topic tabs use the tablist / tab / tabpanel roles, roving tabindex, Left/Right/Home/End keys, automatic activation (panels switch instantly) | W3C WAI-ARIA Authoring Practices, Tabs pattern | https://www.w3.org/WAI/ARIA/apg/patterns/tabs/ |
| A visible, wide, type-in search field near the top, labelled, with a button; site-wide scope by default; also in the header of every page | Nielsen Norman Group: search should be a visible input, wide enough, top of page, scope stated | https://www.nngroup.com/articles/search-visible-and-simple/ |
| Left sidebar on desktop (search, topics, latest); stacked above the cards on mobile | Owner request; keeps search reachable while browsing | (owner request) |
| Colours named after traditional Japanese colours: kon (deep indigo) for hero and footer, ai (indigo) for links, vermilion for accents, washi (paper cream) for the page | Wa feel without external assets | https://nipponcolors.com/ (list of traditional colours; the exact hex values here are our own choices and were contrast-tested) |
| Seigaiha (wave) pattern on hero and footer, ichimatsu (checker) stripe under the top edge, vermilion disc motif | Traditional Japanese patterns; drawn as original SVG, no licensing | (own artwork) |
| Serif headings with Japanese Mincho fallbacks, system sans for body | Editorial tone; no external font requests (privacy page says the site loads nothing third-party) | (own decision) |
| Reduced-motion and dark-mode support | Accessibility and comfort | W3C WCAG / browser media queries |
| Card thumbnails are 640px copies (about 5-10x smaller than the originals) with photographer and license shown | Page weight; licence attribution must stay near the image | Wikimedia licences |

What the owner can adjust: colours (`PALETTE` and `CSS_TEMPLATE` in `pipeline/theme.py`), topic labels and kanji (`TOPICS`), hero text (`home_html`).
Limits: kanji labels are decorative (aria-hidden); the search is client-side over titles, descriptions and topic names, not over full article text.
