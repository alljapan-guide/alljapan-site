"""Original visuals made at build time (no third-party assets): hero art, flow/cards/route diagrams,
callout boxes. Photos come from pipeline.fetch_images (licensed, with attribution)."""
import html
import re
import textwrap

INK, MUTED, LINE = "#1d2330", "#667085", "#d6dbe6"
THEMES = {  # cluster -> (sky top, sky bottom, sun, far hills, near hills): washi sky, vermilion sun, indigo/pine hills
    "transport": ("#e6edf4", "#f7f2e7", "#b8301b", "#8aa5bf", "#1d5a85"),
    "hotels": ("#f3e4de", "#f7f2e7", "#b8301b", "#b79a96", "#6b3f4a"),
    "itineraries": ("#e5ede3", "#f7f2e7", "#b8301b", "#8fae95", "#2f6b4f"),
    "connectivity": ("#e4e6f2", "#f7f2e7", "#b8301b", "#9aa0c8", "#3a4580"),
    "culture": ("#efe6d6", "#f7f2e7", "#b8301b", "#c2a77a", "#7a5a2b"),
}
DEFAULT_THEME = ("#e6edf4", "#f7f2e7", "#b8301b", "#8aa5bf", "#1d5a85")
CALLOUTS = {"tip": "Tip", "warn": "Watch out", "note": "Good to know", "pick": "Our pick"}


def esc(s):
    return html.escape(str(s), quote=True)


def hero_svg(cluster, seed):
    from .hero_art import hero  # Japanese-style scene per cluster (see hero_art.py)
    return hero(cluster, seed)


def _legacy_hero_svg(cluster, seed):
    top, bottom, sun, far, near = THEMES.get(cluster, DEFAULT_THEME)
    h = sum(ord(c) for c in seed)
    sx = 180 + (h * 37) % 840
    peak = 60 + (h * 13) % 80
    return (f'<svg class="hero" viewBox="0 0 1200 300" role="img" aria-label="Decorative illustration" '
            f'preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><linearGradient id="g{h}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
            f'<stop offset="1" stop-color="{bottom}"/></linearGradient></defs>'
            f'<rect width="1200" height="300" fill="url(#g{h})"/><circle cx="{sx}" cy="95" r="46" fill="{sun}" opacity=".9"/>'
            f'<path d="M0 230 L180 {150-peak//4} L330 215 L520 {120-peak//3} L720 220 L900 {140-peak//5} L1200 230 V300 H0Z" fill="{far}"/>'
            f'<path d="M0 262 L240 205 L430 250 L640 {190+peak//10} L860 255 L1040 215 L1200 262 V300 H0Z" fill="{near}"/>'
            f'<path d="M0 285 H1200" stroke="#fff" stroke-width="4" stroke-dasharray="14 10" opacity=".8"/></svg>')


def _parse_block(text):
    spec = {}
    for line in text.strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            spec[k.strip().lower()] = v.strip()
    return spec


def _items(spec, key):
    return [x.strip() for x in spec.get(key, "").split("|") if x.strip()]


def _lines(text, width):
    return textwrap.wrap(text, width) or [""]


def diagram_svg(text):
    """Render a ```diagram block. Types: flow (steps), cards (items 'Title=text'), route (stops 'Place=detail')."""
    spec = _parse_block(text)
    kind, caption = spec.get("type", "flow"), spec.get("caption", "")
    W, y, parts = 360, 12, []
    if kind == "flow":
        steps = _items(spec, "steps")
        for i, s in enumerate(steps):
            ls = _lines(s, 34)
            h = 28 + 18 * len(ls)
            parts.append(f'<rect x="10" y="{y}" width="340" height="{h}" rx="12" fill="#fff" stroke="{LINE}" stroke-width="2"/>'
                         f'<circle cx="32" cy="{y+h/2}" r="12" fill="#c0392b"/><text x="32" y="{y+h/2+5}" text-anchor="middle" '
                         f'font-size="13" font-weight="700" fill="#fff">{i+1}</text>')
            for j, l in enumerate(ls):
                parts.append(f'<text x="54" y="{y+22+18*j}" font-size="14" fill="{INK}">{esc(l)}</text>')
            y += h
            if i < len(steps) - 1:
                parts.append(f'<path d="M180 {y} v16 m-6 -7 l6 7 l6 -7" fill="none" stroke="{MUTED}" stroke-width="2"/>')
                y += 20
    elif kind == "cards":
        for it in _items(spec, "items"):
            title, _, body = it.partition("=")
            ls = _lines(body, 38)
            h = 38 + 17 * len(ls)
            parts.append(f'<rect x="10" y="{y}" width="340" height="{h}" rx="12" fill="#fff8ee" stroke="{LINE}" stroke-width="2"/>'
                         f'<text x="24" y="{y+24}" font-size="15" font-weight="700" fill="#c0392b">{esc(title.strip())}</text>')
            for j, l in enumerate(ls):
                parts.append(f'<text x="24" y="{y+44+17*j}" font-size="13.5" fill="{INK}">{esc(l)}</text>')
            y += h + 10
        y -= 10
    elif kind == "route":
        stops = _items(spec, "stops")
        for i, s in enumerate(stops):
            place, _, detail = s.partition("=")
            ls = _lines(detail.strip(), 36)
            h = 46 + 17 * len(ls)
            if i < len(stops) - 1:
                parts.append(f'<line x1="40" y1="{y+22}" x2="40" y2="{y+h+22}" stroke="#c0392b" stroke-width="4" stroke-dasharray="2 7" stroke-linecap="round"/>')
            parts.append(f'<circle cx="40" cy="{y+22}" r="14" fill="#c0392b"/><text x="40" y="{y+27}" text-anchor="middle" font-size="13" '
                         f'font-weight="700" fill="#fff">{i+1}</text><text x="68" y="{y+20}" font-size="16" font-weight="700" fill="{INK}">{esc(place.strip())}</text>')
            for j, l in enumerate(ls):
                parts.append(f'<text x="68" y="{y+40+17*j}" font-size="13.5" fill="{MUTED}">{esc(l)}</text>')
            y += h
    else:
        raise ValueError(f"unknown diagram type {kind!r}")
    svg = (f'<svg viewBox="0 0 {W} {y+14}" role="img" aria-label="{esc(caption or kind)}" '
           f'font-family="system-ui,sans-serif" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>')
    return f'<figure class="diagram">{svg}<figcaption>{esc(caption)}</figcaption></figure>'


def callout_html(kind, text, inline_md):
    kind = kind if kind in CALLOUTS else "note"
    return f'<aside class="callout {kind}"><strong>{CALLOUTS[kind]}</strong> {inline_md(text)}</aside>'


def commons_caption(title):
    """Honest caption from the Commons file title (not our guess): drop 'File:', extension and leading dates."""
    t = re.sub(r"^File:", "", title or "")
    t = re.sub(r"\.(jpe?g|png)$", "", t, flags=re.I)
    t = re.sub(r"^(\d{8}|\d{4}-\d{2}-\d{2})[ _-]*", "", t)
    return re.sub(r"\s+", " ", t.replace("_", " ")).strip()


def photo_html(rec, caption, root=""):
    if rec:
        # an explicit "caption" in data/images.json (set only after the photo was checked by eye) beats the Commons title
        caption = rec.get("caption") or commons_caption(rec.get("title", "")) or caption
    if not rec:
        return f'<figure class="photo pending"><div>Photo pending: {esc(caption)}</div></figure>'
    lic = f'<a href="{esc(rec["license_url"])}" rel="noopener">{esc(rec["license"])}</a>' if rec.get("license_url") else esc(rec["license"])
    return (f'<figure class="photo"><img src="{root}images/{esc(rec["file"])}" alt="{esc(caption)}" loading="lazy">'
            f'<figcaption>{esc(caption)}<span class="credit">Photo: {esc(rec["author"])} · {lic} · '
            f'<a href="{esc(rec["source_url"])}" rel="noopener">Wikimedia Commons</a></span></figcaption></figure>')


BLOCK = re.compile(r"^```diagram\n(.*?)\n```$", re.S | re.M)
CALL = re.compile(r"^\{\{(tip|warn|note|pick)\|(.+?)\}\}$", re.M)
PHOTO = re.compile(r"^\{\{photo:(\d+)\|(.+?)\}\}$", re.M)


def count_visuals(body):
    return {"diagrams": len(BLOCK.findall(body)), "callouts": len(CALL.findall(body)), "photos": len(PHOTO.findall(body))}
