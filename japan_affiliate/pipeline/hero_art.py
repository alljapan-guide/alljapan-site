"""Original Japanese-style banner illustrations (SVG, 1200x300), one scene per article cluster.

Flat, ukiyo-e-like shapes in the site's own palette: indigo (ai/kon), vermilion (shu), washi cream, with a seigaiha (wave) band.
Everything is drawn here; no third-party artwork, so there is nothing to license or credit."""

SHU, KON, AI, WASHI, GOLD = "#b8301b", "#14283f", "#1d5a85", "#f7f2e7", "#e3c37a"


def _seigaiha_pattern(pid, bg, line):
    circles = []
    for k in range(-2, 5):
        for m in range(-2, 3):
            cx, cy = 24 * m + (12 if k % 2 else 0), 6 * k
            for r in (12, 9, 6, 3):
                circles.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{bg}" stroke="{line}" stroke-width=".7"/>')
    return (f'<pattern id="{pid}" width="24" height="12" patternUnits="userSpaceOnUse" patternTransform="scale(2.4)">'
            + "".join(circles) + "</pattern>")


def _fuji(cx, base, w, h, body, snow=WASHI):
    l, r, top = cx - w / 2, cx + w / 2, base - h
    cap = h * 0.26
    body_path = (f'<path d="M{l:.0f} {base} Q{cx - w*0.22:.0f} {base - h*0.42:.0f} {cx - w*0.07:.0f} {top:.0f} '
                 f'L{cx + w*0.07:.0f} {top:.0f} Q{cx + w*0.22:.0f} {base - h*0.42:.0f} {r:.0f} {base}Z" fill="{body}"/>')
    y2 = top + cap
    cap_path = (f'<path d="M{cx - w*0.07:.0f} {top:.0f} L{cx + w*0.07:.0f} {top:.0f} L{cx + w*0.115:.0f} {y2 - cap*0.1:.0f} '
                f'L{cx + w*0.07:.0f} {y2 - cap*0.45:.0f} L{cx + w*0.035:.0f} {y2:.0f} L{cx:.0f} {y2 - cap*0.4:.0f} '
                f'L{cx - w*0.04:.0f} {y2 + cap*0.05:.0f} L{cx - w*0.075:.0f} {y2 - cap*0.4:.0f} L{cx - w*0.115:.0f} {y2 - cap*0.1:.0f}Z" fill="{snow}"/>')
    return body_path + cap_path


def _mist(x, y, w, color=WASHI, op=.75):
    return f'<rect x="{x}" y="{y}" width="{w}" height="9" rx="4.5" fill="{color}" opacity="{op}"/>'


def _petals(seed, n=14, color="#f2b5c4", area=(0, 1200, 20, 200)):
    out, h = [], seed
    for i in range(n):
        h = (h * 1103515245 + 12345) & 0x7FFFFFFF
        x = area[0] + (h % (area[1] - area[0]))
        h = (h * 1103515245 + 12345) & 0x7FFFFFFF
        y = area[2] + (h % (area[3] - area[2]))
        rot = h % 180
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="5.5" ry="3" fill="{color}" opacity=".9" transform="rotate({rot} {x} {y})"/>')
    return "".join(out)


def _torii(cx, base, h, color=SHU):
    w = h * 1.25
    l, r = cx - w / 2, cx + w / 2
    pil = h * 0.075
    top = base - h
    return (f'<g fill="{color}"><rect x="{l + w*0.1:.0f}" y="{top + h*0.12:.0f}" width="{pil:.0f}" height="{h*0.88:.0f}"/>'
            f'<rect x="{r - w*0.1 - pil:.0f}" y="{top + h*0.12:.0f}" width="{pil:.0f}" height="{h*0.88:.0f}"/>'
            f'<path d="M{l - w*0.08:.0f} {top + h*0.1:.0f} Q{cx:.0f} {top + h*0.2:.0f} {r + w*0.08:.0f} {top + h*0.1:.0f} '
            f'L{r + w*0.12:.0f} {top - h*0.02:.0f} Q{cx:.0f} {top + h*0.08:.0f} {l - w*0.12:.0f} {top - h*0.02:.0f}Z"/>'
            f'<rect x="{l + w*0.04:.0f}" y="{top + h*0.26:.0f}" width="{w*0.92:.0f}" height="{h*0.07:.0f}"/>'
            f'<rect x="{cx - pil*0.8:.0f}" y="{top + h*0.12:.0f}" width="{pil*1.6:.0f}" height="{h*0.14:.0f}"/></g>')


def _lantern(x, y, r, h=None):
    h = h or r * 1.5
    return (f'<line x1="{x}" y1="{y - 18}" x2="{x}" y2="{y}" stroke="{KON}" stroke-width="2"/>'
            f'<ellipse cx="{x}" cy="{y + h/2:.0f}" rx="{r}" ry="{h/2:.0f}" fill="{SHU}"/>'
            f'<rect x="{x - r*0.55:.0f}" y="{y - 3}" width="{r*1.1:.0f}" height="6" rx="2" fill="{KON}"/>'
            f'<rect x="{x - r*0.55:.0f}" y="{y + h - 3:.0f}" width="{r*1.1:.0f}" height="6" rx="2" fill="{KON}"/>'
            f'<path d="M{x - r*0.7:.0f} {y + h*0.35:.0f} Q{x} {y + h*0.45:.0f} {x + r*0.7:.0f} {y + h*0.35:.0f}" stroke="{GOLD}" stroke-width="1.5" fill="none" opacity=".8"/>'
            f'<path d="M{x - r*0.7:.0f} {y + h*0.65:.0f} Q{x} {y + h*0.75:.0f} {x + r*0.7:.0f} {y + h*0.65:.0f}" stroke="{GOLD}" stroke-width="1.5" fill="none" opacity=".8"/>')


def scene_fuji(h):
    """Classic: Fuji, vermilion sun, mist, sakura petals. (itineraries)"""
    sx = 170 + (h * 37) % 220
    return (f'<rect width="1200" height="300" fill="url(#sky)"/><circle cx="{sx}" cy="90" r="52" fill="{SHU}"/>'
            + _fuji(760, 246, 700, 190, "#3f5f86") + _fuji(1050, 246, 420, 110, "#6e8bb0", snow="#f1ece0")
            + _mist(560, 150, 300) + _mist(640, 176, 380) + _mist(80, 200, 260, op=.6) + _petals(h))


def scene_torii(h):
    """Torii in dusk mist with a pale moon. (culture)"""
    mx = 880 + (h % 120)
    return (f'<rect width="1200" height="300" fill="url(#dusk)"/><circle cx="{mx}" cy="80" r="40" fill="{WASHI}" opacity=".95"/>'
            f'<path d="M0 230 L170 150 L320 205 L520 120 L700 210 L900 140 L1200 215 V300H0Z" fill="#2c4562"/>'
            f'<path d="M0 262 L240 205 L470 252 L720 196 L980 250 L1200 215 V300H0Z" fill="#17304b"/>'
            + _torii(560, 262, 190) + _mist(80, 170, 320, op=.25) + _mist(760, 190, 330, op=.25) + _petals(h, 8, "#f2b5c4", (0, 1200, 20, 130)))


def scene_shinkansen(h):
    """Bullet train passing Fuji. (transport)"""
    return (f'<rect width="1200" height="300" fill="url(#sky)"/><circle cx="{190 + (h % 100)}" cy="82" r="46" fill="{SHU}"/>'
            + _fuji(820, 226, 680, 170, "#4d7099") + _mist(560, 130, 320) + _mist(700, 156, 330)
            + f'<rect y="214" width="1200" height="26" fill="#2c4562"/><rect y="224" width="1200" height="4" fill="#9aa8ba"/>'
            f'<path d="M120 214 H760 Q840 214 900 196 Q860 186 800 180 H120Z" fill="#f4f6f8" stroke="#9aa8ba" stroke-width="2"/>'
            f'<rect x="120" y="198" width="700" height="6" fill="{AI}"/>'
            f'<path d="M760 214 Q840 214 900 196" stroke="{AI}" stroke-width="3" fill="none"/>'
            + "".join(f'<rect x="{150 + i*62}" y="186" width="34" height="9" rx="3" fill="{AI}"/>' for i in range(10))
            + f'<path d="M780 190 Q830 190 868 190" stroke="#c9d4e2" stroke-width="5" fill="none"/>')


def scene_ryokan(h):
    """Gabled tiled roof, lattice walls, lanterns and a pine at night. (hotels)"""
    shoji = "".join(f'<line x1="{345 + i*28}" y1="212" x2="{345 + i*28}" y2="250" stroke="#8a6a3b" stroke-width="2"/>' for i in range(12))
    return (f'<rect width="1200" height="300" fill="url(#dusk)"/><circle cx="{950 + (h % 100)}" cy="70" r="34" fill="{GOLD}" opacity=".95"/>'
            f'<path d="M180 204 Q300 196 352 118 H648 Q700 196 820 204 Q710 208 668 216 H332 Q290 208 180 204Z" fill="#2a2f3a"/>'
            f'<path d="M352 118 H648" stroke="#0e1a29" stroke-width="10" stroke-linecap="round"/>'
            f'<path d="M334 118 q-10 -14 2 -22 q4 8 12 10 M666 118 q10 -14 -2 -22 q-4 8 -12 10" fill="none" stroke="#0e1a29" stroke-width="5" stroke-linecap="round"/>'
            f'<rect x="332" y="212" width="336" height="40" fill="#efe3c8"/>' + shoji
            + f'<rect x="332" y="206" width="336" height="8" fill="#8a6a3b"/><rect x="470" y="222" width="60" height="30" fill="#14283f" opacity=".75"/>'
            + _lantern(300, 226, 13) + _lantern(700, 226, 13)
            + f'<path d="M1020 252 Q1030 170 1060 120 Q1080 150 1090 190 M1060 150 Q1120 120 1170 150 M1050 180 Q1110 160 1160 190" stroke="#0e1a29" stroke-width="7" fill="none" stroke-linecap="round"/>'
            f'<g fill="#1f4a3a"><ellipse cx="1130" cy="140" rx="44" ry="14"/><ellipse cx="1105" cy="182" rx="50" ry="14"/><ellipse cx="1065" cy="118" rx="36" ry="12"/></g>')


def scene_bowl(h):
    """Steaming bowl of noodles with chopsticks under a vermilion sun. (food)"""
    return (f'<rect width="1200" height="300" fill="url(#sky)"/><circle cx="{760 + (h % 120)}" cy="96" r="58" fill="{SHU}"/><g transform="translate(0 -30)">'
            f'<g fill="none" stroke="{WASHI}" stroke-width="7" stroke-linecap="round" opacity=".9">'
            f'<path d="M520 150 Q500 120 520 96 Q540 72 520 48"/><path d="M590 156 Q570 124 590 100 Q610 76 590 52"/><path d="M660 150 Q640 120 660 96 Q680 72 660 48"/></g>'
            f'<path d="M430 176 H750 Q745 262 590 268 Q435 262 430 176Z" fill="#f4efe3" stroke="#8a7a5b" stroke-width="3"/>'
            f'<path d="M430 176 H750 V190 H430Z" fill="{SHU}"/><path d="M470 218 Q590 242 710 218" stroke="{AI}" stroke-width="4" fill="none"/>'
            f'<path d="M455 176 Q590 120 725 176Z" fill="#e8c87a"/><path d="M500 172 Q590 140 690 172" stroke="#c9a14a" stroke-width="4" fill="none"/>'
            f'<circle cx="560" cy="160" r="12" fill="#f4efe3"/><circle cx="560" cy="160" r="5" fill="#e8a33a"/>'
            f'<line x1="690" y1="80" x2="560" y2="166" stroke="#3a2a1b" stroke-width="7" stroke-linecap="round"/>'
            f'<line x1="716" y1="98" x2="590" y2="170" stroke="#3a2a1b" stroke-width="7" stroke-linecap="round"/></g>')


def scene_lanterns(h):
    """A string of paper lanterns over a shopping street. (shopping)"""
    out = [f'<rect width="1200" height="300" fill="url(#dusk)"/>',
           f'<path d="M0 60 Q300 110 600 70 T1200 60" stroke="{KON}" stroke-width="3" fill="none"/>',
           f'<path d="M0 118 Q300 168 600 128 T1200 118" stroke="{KON}" stroke-width="3" fill="none" opacity=".7"/>']
    for i, x in enumerate(range(80, 1200, 130)):
        y = 78 + (28 if i % 2 else 0) + (h % 7)
        out.append(_lantern(x, y, 26, 62))
    for i, x in enumerate(range(150, 1200, 260)):
        out.append(_lantern(x, 160, 20, 48))
    out.append(f'<rect y="232" width="1200" height="8" fill="{GOLD}" opacity=".6"/>')
    return "".join(out)


def scene_petals(h):
    """Pink dawn, Fuji, a sakura branch in the foreground. (seasonal)"""
    branch = (f'<path d="M-10 40 Q200 70 360 20 Q500 -10 640 30" stroke="#3a2a2a" stroke-width="9" fill="none" stroke-linecap="round"/>'
              f'<path d="M180 60 Q240 110 300 120 M360 22 Q380 80 430 96" stroke="#3a2a2a" stroke-width="5" fill="none" stroke-linecap="round"/>')
    blossoms = "".join(f'<g transform="translate({x} {y})"><circle r="15" fill="#f4b6c4"/><circle r="6" fill="#fbe3e9"/>'
                       f'<circle cx="0" cy="0" r="2.5" fill="#c4415a"/></g>' for x, y in
                       [(90, 54), (150, 62), (230, 90), (310, 44), (380, 28), (440, 90), (510, 14), (570, 30), (610, 44), (290, 118)])
    return (f'<rect width="1200" height="300" fill="url(#dawn)"/><circle cx="{930 + (h % 100)}" cy="92" r="44" fill="{SHU}" opacity=".95"/>'
            + _fuji(780, 246, 640, 170, "#5a6f96", snow="#f7f2e7") + _mist(560, 168, 380, op=.85) + _mist(640, 192, 340, op=.8)
            + branch + blossoms + _petals(h, 20, "#f4b6c4", (300, 1200, 60, 230)))


def scene_signal(h):
    """Waves and radio arcs under a vermilion sun. (connectivity)"""
    cx = 600
    arcs = "".join(f'<path d="M{cx - r} 190 A{r} {r} 0 0 1 {cx + r} 190" fill="none" stroke="{WASHI}" stroke-width="7" stroke-linecap="round" opacity="{o}"/>'
                   for r, o in ((60, .95), (110, .8), (160, .6), (210, .4)))
    return (f'<rect width="1200" height="300" fill="url(#dusk)"/><circle cx="{cx}" cy="190" r="14" fill="{SHU}"/>' + arcs
            + _fuji(190, 246, 380, 100, "#2c4562", snow="#c9d4e2") + _fuji(1020, 246, 420, 110, "#2c4562", snow="#c9d4e2"))


def scene_fan(h):
    """A folding fan (sensu) between two Fuji silhouettes. (planning)"""
    import math
    cx, cy, rad = 600, 274, 250
    pts = lambda deg: (cx + rad * math.cos(math.radians(deg)), cy + rad * math.sin(math.radians(deg)))
    (lx, ly), (rx, ry) = pts(215), pts(325)
    ribs = "".join(f'<line x1="{cx}" y1="{cy}" x2="{pts(215 + i * 13.75)[0]:.0f}" y2="{pts(215 + i * 13.75)[1]:.0f}" stroke="#8a6a3b" stroke-width="2"/>'
                   for i in range(9))
    return (f'<rect width="1200" height="300" fill="url(#sky)"/>' + _fuji(250, 246, 500, 130, "#6e8bb0", snow="#f1ece0")
            + _fuji(1000, 246, 520, 150, "#4d7099") + _mist(60, 150, 280) + _mist(840, 170, 300)
            + f'<path d="M{cx} {cy} L{lx:.0f} {ly:.0f} A{rad} {rad} 0 0 1 {rx:.0f} {ry:.0f}Z" fill="{WASHI}" stroke="#8a6a3b" stroke-width="3"/>'
            + ribs + f'<circle cx="{cx}" cy="205" r="44" fill="{SHU}"/>'
            + f'<path d="M{lx:.0f} {ly:.0f} A{rad} {rad} 0 0 1 {rx:.0f} {ry:.0f}" stroke="{GOLD}" stroke-width="6" fill="none"/>'
            + f'<circle cx="{cx}" cy="{cy}" r="8" fill="#8a6a3b"/>')


SCENES = {"itineraries": scene_fuji, "culture": scene_torii, "transport": scene_shinkansen, "hotels": scene_ryokan,
          "food": scene_bowl, "shopping": scene_lanterns, "seasonal": scene_petals, "connectivity": scene_signal,
          "planning": scene_fan}
SKIES = {"sky": ("#f2d9c4", "#f7f2e7"), "dusk": ("#14283f", "#46607f"), "dawn": ("#f6c9cf", "#f7f2e7")}


def hero(cluster, seed):
    h = sum(ord(c) for c in seed)
    scene = SCENES.get(cluster, scene_fuji)(h)
    grads = "".join(f'<linearGradient id="{k}{h}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'
                    for k, (a, b) in SKIES.items())
    scene = scene.replace('url(#sky)', f'url(#sky{h})').replace('url(#dusk)', f'url(#dusk{h})').replace('url(#dawn)', f'url(#dawn{h})')
    waves = (f'<rect y="244" width="1200" height="56" fill="url(#sg{h})"/>'
             f'<rect y="244" width="1200" height="3" fill="{GOLD}" opacity=".7"/>')
    return (f'<svg class="hero" viewBox="0 0 1200 300" role="img" aria-label="Decorative Japanese-style illustration" '
            f'preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg"><defs>{grads}'
            f'{_seigaiha_pattern(f"sg{h}", "#1d4f7a", "#4f7fab")}</defs>{scene}{waves}</svg>')
