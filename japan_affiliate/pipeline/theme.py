"""Wa (和) theme: palette, CSS, JS, SVG motifs and the home page (hero, search, topic tabs, cards).

Design rules applied (sources in docs/DESIGN.md):
- WCAG 2.2 SC 1.4.3: text contrast >= 4.5:1 (checked by tests against PALETTE).
- W3C APG Tabs pattern: tablist/tab/tabpanel roles, roving tabindex, arrow/Home/End keys.
- NN/g: a visible, wide, type-in search field near the top; home search covers the whole site by default.
Motifs: seigaiha (青海波, waves), ichimatsu (市松, checker) stripe, hinomaru-style vermilion disc, washi paper tones.
"""
import html
import math
import re
from pathlib import Path
from urllib.parse import quote

PALETTE = {  # (foreground, background) pairs the stylesheet relies on; tests enforce >= 4.5:1
    "light": {"ink/washi": ("#1f2326", "#f7f2e7"), "muted/washi": ("#5a5f66", "#f7f2e7"), "link/washi": ("#1d5a85", "#f7f2e7"),
              "link/card": ("#1d5a85", "#fffdf8"), "white/shu": ("#ffffff", "#b8301b"), "white/ai": ("#ffffff", "#1d5a85"),
              "cream/kon": ("#f7f2e7", "#14283f"), "gold/kon": ("#e3c37a", "#14283f"), "shu/washi": ("#b8301b", "#f7f2e7"),
              "heromuted/kon": ("#c9d4e2", "#14283f")},
    "dark": {"ink/bg": ("#efe8d8", "#0f1b2b"), "muted/bg": ("#a9b3c1", "#0f1b2b"), "link/bg": ("#8fc1e8", "#0f1b2b"),
             "link/card": ("#8fc1e8", "#172a40"), "ink/card": ("#efe8d8", "#172a40"), "white/shu": ("#ffffff", "#c4412a")},
}

TOPICS = {  # cluster -> (label, decorative kanji)
    "transport": ("Getting around", "交通"), "hotels": ("Where to stay", "宿"), "itineraries": ("Itineraries", "旅"),
    "connectivity": ("Stay connected", "通信"), "culture": ("Culture", "文化"), "food": ("Food", "食"),
    "seasonal": ("Seasons", "季節"), "planning": ("Planning", "計画"), "products": ("Shopping", "買物"),
}
TOPIC_ORDER = list(TOPICS)


def topic(cluster):
    return TOPICS.get(cluster, (cluster.replace("-", " ").title(), "和"))


def contrast(fg, bg):
    def lum(h):
        h = h.lstrip("#")
        c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    a, b = sorted((lum(fg), lum(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def seigaiha_uri(bg="#14283f", line="#2f5273"):
    """Seamless seigaiha tile (24x12) as a data URI. Rows 6 apart, alternate rows offset 12; lower rows overlap upper ones."""
    circles = []
    for k in range(-2, 5):
        for m in range(-2, 3):
            cx, cy = 24 * m + (12 if k % 2 else 0), 6 * k
            for r in (12, 9, 6, 3):
                circles.append(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='{bg}' stroke='{line}' stroke-width='.7'/>")
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='24' height='12' viewBox='0 0 24 12'>{''.join(circles)}</svg>"
    return "url(\"data:image/svg+xml," + quote(svg, safe="/:=' ") .replace("'", "%27") + "\")"


def logo_svg():
    return ("<svg class='logo' viewBox='0 0 40 40' aria-hidden='true' xmlns='http://www.w3.org/2000/svg'>"
            "<circle cx='20' cy='20' r='19' fill='#b8301b'/><g fill='none' stroke='#fff' stroke-opacity='.85' stroke-width='1.6'>"
            "<path d='M6 28a7 7 0 0 1 14 0a7 7 0 0 1 14 0'/><path d='M10 28a3 3 0 0 1 6 0a3 3 0 0 1 6 0a3 3 0 0 1 6 0'/>"
            "<path d='M3 33a8.5 8.5 0 0 1 17 0a8.5 8.5 0 0 1 17 0'/></g></svg>")


CSS_TEMPLATE = r"""
:root{--washi:#f7f2e7;--card:#fffdf8;--ink:#1f2326;--muted:#5a5f66;--line:#e1d6bf;--ai:#1d5a85;--kon:#14283f;--shu:#b8301b;--kin:#b58a2b;
--link:#1d5a85;--radius:14px;--shadow:0 1px 2px rgba(20,40,63,.08),0 8px 24px rgba(20,40,63,.06);
--serif:"Hiragino Mincho ProN","Yu Mincho","Noto Serif JP","Source Han Serif JP","Songti SC",Georgia,"Times New Roman",serif;
--sans:system-ui,-apple-system,"Segoe UI","Hiragino Sans","Yu Gothic UI","Noto Sans JP",sans-serif}
@media(prefers-color-scheme:dark){:root{--washi:#0f1b2b;--card:#172a40;--ink:#efe8d8;--muted:#a9b3c1;--line:#2a4058;--link:#8fc1e8;--shu:#c4412a;--shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.25)}}
*{box-sizing:border-box}html{scroll-behavior:smooth}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important;animation:none!important}}
body{margin:0;font:17px/1.75 var(--sans);color:var(--ink);background:var(--washi)}
a{color:var(--link)}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid var(--kin);outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:-999px}.skip:focus{left:8px;top:8px;background:var(--card);padding:.5rem .8rem;z-index:50}
.stripe{height:8px;background:repeating-conic-gradient(var(--kon) 0 25%,var(--shu) 0 50%) 0 0/16px 16px}
.wrap{max-width:46rem;margin:0 auto;padding:0 1rem}.home .wrap{max-width:76rem}
.site-header{background:var(--card);border-bottom:1px solid var(--line)}
.site-header .wrap,.site-footer .wrap{max-width:76rem}.site-header .wrap{display:flex;align-items:center;gap:1rem;padding-top:.7rem;padding-bottom:.7rem;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:.6rem;text-decoration:none;color:var(--ink)}.logo{width:34px;height:34px;flex:none}
.brand b{font:700 1.25rem/1 var(--serif);letter-spacing:.12em;text-transform:uppercase}.brand small{display:block;font:.72rem/1.2 var(--sans);color:var(--muted);letter-spacing:.04em}
.nav{margin-left:auto;display:flex;gap:1.1rem;align-items:center;font-size:.92rem}.nav a{color:var(--ink);text-decoration:none;padding:.2rem 0;border-bottom:2px solid transparent}.nav a:hover{border-color:var(--shu)}
.header-search{display:flex;gap:.4rem;flex:1 1 14rem;max-width:22rem}.home .header-search{display:none}
input[type=search]{width:100%;font:inherit;font-size:1rem;padding:.6rem .8rem;border:1.5px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink)}
input[type=search]::placeholder{color:var(--muted)}
.btn{display:inline-block;font:600 .95rem var(--sans);padding:.65rem 1.1rem;border-radius:10px;border:1.5px solid var(--shu);background:var(--shu);color:#fff;text-decoration:none;cursor:pointer}
.btn.ghost{background:transparent;color:var(--ink);border-color:currentColor}.hero .btn.ghost{color:#f7f2e7}
.hero{position:relative;color:#f7f2e7;background-color:var(--kon);background-image:__SEIGAIHA__;background-size:48px 24px;overflow:hidden}
.hero:before{content:"";position:absolute;right:max(2rem,6vw);top:-3.5rem;width:15rem;height:15rem;border-radius:50%;background:var(--shu);opacity:.92;box-shadow:0 0 0 14px rgba(184,48,27,.18)}
.hero .wrap{position:relative;padding-top:2.6rem;padding-bottom:3rem}
.hero .kicker{font:600 .8rem var(--sans);letter-spacing:.22em;text-transform:uppercase;color:#e3c37a;margin:0 0 .7rem}
.hero h1{font:700 clamp(2rem,5vw,3.4rem)/1.15 var(--serif);margin:0 0 1rem;max-width:20ch;text-wrap:balance}
.hero p.lead{max-width:38rem;font-size:1.1rem;color:#c9d4e2;margin:0 0 1.5rem}
.hero .cta{display:flex;gap:.7rem;flex-wrap:wrap}.trust{display:flex;gap:.6rem 1.4rem;flex-wrap:wrap;margin:1.8rem 0 0;padding:0;list-style:none;font-size:.88rem;color:#e3c37a}
.trust li:before{content:"◆ ";font-size:.7em;vertical-align:.12em}
.hero:after{content:"";position:absolute;left:0;right:0;bottom:0;height:10px;background:var(--washi);clip-path:polygon(0 100%,100% 100%,100% 0,98% 60%,96% 0,94% 60%,92% 0,90% 60%,88% 0,86% 60%,84% 0,82% 60%,80% 0,78% 60%,76% 0,74% 60%,72% 0,70% 60%,68% 0,66% 60%,64% 0,62% 60%,60% 0,58% 60%,56% 0,54% 60%,52% 0,50% 60%,48% 0,46% 60%,44% 0,42% 60%,40% 0,38% 60%,36% 0,34% 60%,32% 0,30% 60%,28% 0,26% 60%,24% 0,22% 60%,20% 0,18% 60%,16% 0,14% 60%,12% 0,10% 60%,8% 0,6% 60%,4% 0,2% 60%,0 0)}
.home-grid{display:grid;grid-template-columns:19rem minmax(0,1fr);gap:2rem;padding:2rem 0 3rem;align-items:start}
.home-grid>*{min-width:0}.sidebar{position:sticky;top:1rem;display:grid;gap:1.2rem}
.panel{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:1rem 1.1rem;box-shadow:var(--shadow)}
.panel h2{font:700 1rem var(--serif);letter-spacing:.06em;margin:0 0 .7rem;display:flex;align-items:center;gap:.5rem}.panel h2:before{content:"";width:.55rem;height:.55rem;background:var(--shu);border-radius:50%}
.search label{display:block;font:600 .85rem var(--sans);margin-bottom:.35rem}.search .row{display:grid;gap:.5rem}.search .row .btn{width:100%}.search .count{margin:.6rem 0 0;font-size:.85rem;color:var(--muted);min-height:1.3em}
.clear{background:none;border:0;color:var(--link);cursor:pointer;font:inherit;text-decoration:underline;padding:0}
.topics{list-style:none;margin:0;padding:0}.topics button{width:100%;display:flex;justify-content:space-between;align-items:center;gap:.5rem;background:none;border:0;border-radius:8px;padding:.5rem .6rem;color:var(--ink);font:inherit;font-size:.95rem;cursor:pointer;text-align:left}
.topics button:hover{background:rgba(184,48,27,.08)}.topics button[aria-pressed=true]{background:var(--ai);color:#fff}.topics .n{font-size:.8rem;opacity:.8}
.latest{list-style:none;margin:0;padding:0;display:grid;gap:.6rem;font-size:.92rem}.latest a{text-decoration:none;color:var(--ink);font-family:var(--serif);font-weight:600;line-height:1.35}.latest a:hover{text-decoration:underline}
.latest span{display:block;font:.78rem var(--sans);color:var(--muted)}.note{font-size:.85rem;color:var(--muted)}
.tabs{display:none;gap:.4rem;overflow-x:auto;padding:.2rem 0 .8rem;margin:0 0 .6rem;border-bottom:1px solid var(--line);scrollbar-width:thin}.js .tabs{display:flex}
.tab{flex:none;display:flex;align-items:center;gap:.45rem;border:1.5px solid var(--line);background:var(--card);color:var(--ink);border-radius:999px;padding:.45rem .95rem;font:600 .9rem var(--sans);cursor:pointer;white-space:nowrap}
.tab .ja{font:700 .85rem var(--serif);color:var(--shu)}.tab .n{font-weight:500;color:var(--muted);font-size:.8rem}
.tab:hover{border-color:var(--shu)}.tab[aria-selected=true]{background:var(--kon);border-color:var(--kon);color:#f7f2e7}.tab[aria-selected=true] .ja{color:#e3c37a}.tab[aria-selected=true] .n{color:#c9d4e2}
@media(prefers-color-scheme:dark){.tab[aria-selected=true]{background:var(--ai);border-color:var(--ai)}}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(17rem,1fr));gap:1.3rem}.noscript-note{margin:0 0 1rem}
.card{position:relative;display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);transition:transform .18s,box-shadow .18s}
.card:hover{transform:translateY(-3px);box-shadow:0 2px 4px rgba(20,40,63,.1),0 14px 30px rgba(20,40,63,.12)}.card[hidden]{display:none}
.card-media{display:block;aspect-ratio:16/10;background:var(--kon);overflow:hidden;position:relative}.card-media img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .35s}.card:hover img{transform:scale(1.04)}
.card-media.fallback{background-color:var(--kon);background-image:__SEIGAIHA__;background-size:48px 24px}
.badge{position:absolute;left:.7rem;top:.7rem;margin:0;background:var(--shu);color:#fff;font:600 .75rem var(--sans);padding:.2rem .6rem;border-radius:999px;display:flex;gap:.35rem;align-items:center;box-shadow:0 2px 6px rgba(0,0,0,.25)}
.badge .ja{font-family:var(--serif);font-weight:700}
.card-body{padding:1rem 1.1rem 1.1rem;display:flex;flex-direction:column;gap:.45rem;flex:1}
.card h3{font:700 1.15rem/1.35 var(--serif);margin:0}.card h3 a{color:var(--ink);text-decoration:none}.card h3 a:after{content:"";position:absolute;inset:0}
.card .desc{margin:0;font-size:.93rem;line-height:1.6;color:var(--muted);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.card .meta{margin:auto 0 0;padding-top:.4rem;font-size:.8rem;color:var(--muted);display:flex;gap:.5rem;flex-wrap:wrap}
.card .credit{margin:0;font-size:.7rem;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.empty{text-align:center;padding:2.5rem 1rem;border:2px dashed var(--line);border-radius:var(--radius);color:var(--muted)}.empty strong{display:block;font:700 1.2rem var(--serif);color:var(--ink);margin-bottom:.4rem}
main.article-main{max-width:46rem;margin:0 auto;padding:0 1rem}
h1,h2,h3{font-family:var(--serif)}h1{line-height:1.22;font-size:2.1rem;margin:1.2rem 0 .4rem}
article h2{margin-top:2.4rem;padding:.1rem 0 .1rem .8rem;border-left:5px solid var(--shu);line-height:1.3;border-top:0;display:block}h3{margin-top:1.6rem}
.meta{color:var(--muted);font-size:.9rem}svg.hero{display:block;width:100%;height:auto;max-height:220px;border-radius:var(--radius);margin:.6rem 0}
.disc{background:var(--card);border-left:4px solid var(--kin);padding:.6rem .9rem;font-size:.88rem;margin:1rem 0;border-radius:0 8px 8px 0}
.callout{border-radius:12px;padding:.8rem 1rem;margin:1.4rem 0;border-left:5px solid;background:var(--card)}.callout strong{display:block;font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.2rem}
.callout.tip{border-color:#2e9e5b}.callout.warn{border-color:#d9822b}.callout.note{border-color:#3b7dd8}.callout.pick{border-color:var(--shu)}
figure{margin:1.6rem 0}figure.photo img{width:100%;height:auto;border-radius:12px;display:block}figcaption{font-size:.85rem;color:var(--muted);margin-top:.4rem}figcaption .credit{display:block;font-size:.78rem}
figure.diagram{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:1rem;text-align:center}figure.diagram svg{width:100%;max-width:420px;height:auto}figure.photo.pending div{padding:2rem;border:2px dashed var(--line);border-radius:12px;color:var(--muted);text-align:center}
table{border-collapse:collapse;width:100%;display:block;overflow-x:auto;font-size:.95rem}th,td{border:1px solid var(--line);padding:.5rem .7rem;text-align:left}th{background:var(--card)}
.fact{background:linear-gradient(transparent 62%,rgba(227,195,122,.55) 0)}.fact sup{font-size:.7em}section.sources{margin-top:2.4rem;padding:1rem 1.2rem;background:var(--card);border:1px solid var(--line);border-radius:12px;font-size:.88rem}section.sources h2{border:0;margin:0 0 .4rem;font-size:1.1rem;padding:0}
ul.posts{list-style:none;padding:0;display:grid;gap:.9rem}ul.posts li{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:.9rem 1rem}ul.posts a{font-weight:700;text-decoration:none}
.site-footer{margin-top:3rem;color:#c9d4e2;background-color:var(--kon);background-image:__SEIGAIHA__;background-size:48px 24px}.site-footer .wrap{padding-top:2rem;padding-bottom:2.2rem;font-size:.85rem}
.site-footer a{color:#e3c37a}.site-footer p{margin:.3rem 0}
@media(max-width:60rem){.home-grid{grid-template-columns:1fr}.sidebar{position:static}.hero:before{width:9rem;height:9rem;top:-2rem}.sidebar .topics-panel,.sidebar .latest-panel,.search .note{display:none}.nav{margin-left:0;width:100%}}
"""

JS = r"""(function(){
document.documentElement.classList.add('js');
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
var cards=$$('.card'),tabs=$$('.tab'),topicBtns=$$('.topics button'),input=$('#q'),count=$('#count'),empty=$('#empty'),panel=$('#guides-panel');
if(!panel){return}
var state={topic:'all',q:''};
function norm(s){return (s||'').toLowerCase()}
function apply(){
  var tokens=norm(state.q).split(/\s+/).filter(Boolean),shown=0;
  cards.forEach(function(c){
    var ok=(state.topic==='all'||c.dataset.cluster===state.topic)&&tokens.every(function(t){return c.dataset.text.indexOf(t)>-1});
    c.hidden=!ok;if(ok)shown++;
  });
  empty.hidden=shown>0;
  count.textContent=(state.q||state.topic!=='all')?('Showing '+shown+' of '+cards.length+' guides'):(cards.length+' guides');
  tabs.forEach(function(t){var on=t.dataset.topic===state.topic;t.setAttribute('aria-selected',on);t.tabIndex=on?0:-1;if(on)panel.setAttribute('aria-labelledby',t.id)});
  topicBtns.forEach(function(b){b.setAttribute('aria-pressed',b.dataset.topic===state.topic)});
  try{var h=state.topic==='all'?'':'#'+state.topic,q=state.q?'?q='+encodeURIComponent(state.q):'';history.replaceState(null,'',location.pathname+q+h)}catch(e){}
}
function setTopic(t,focus){state.topic=t;apply();if(focus){var el=tabs.filter(function(x){return x.dataset.topic===t})[0];if(el)el.focus()}}
tabs.forEach(function(t,i){
  t.addEventListener('click',function(){setTopic(t.dataset.topic)});
  t.addEventListener('keydown',function(e){
    var n=tabs.length,j=null;
    if(e.key==='ArrowRight')j=(i+1)%n;else if(e.key==='ArrowLeft')j=(i-1+n)%n;else if(e.key==='Home')j=0;else if(e.key==='End')j=n-1;
    if(j!==null){e.preventDefault();setTopic(tabs[j].dataset.topic,true)}
  });
});
topicBtns.forEach(function(b){b.addEventListener('click',function(){setTopic(b.dataset.topic===state.topic?'all':b.dataset.topic)})});
input.addEventListener('input',function(){state.q=input.value;apply()});
input.addEventListener('keydown',function(e){if(e.key==='Escape'){input.value='';state.q='';apply()}});
$('#search-form').addEventListener('submit',function(e){e.preventDefault();apply();panel.scrollIntoView({behavior:'smooth',block:'start'})});
$$('.clear-all').forEach(function(b){b.addEventListener('click',function(){input.value='';state.q='';state.topic='all';apply();input.focus()})});
document.addEventListener('keydown',function(e){if(e.key==='/'&&!/input|textarea/i.test(document.activeElement.tagName)){e.preventDefault();input.focus()}});
var p=new URLSearchParams(location.search);if(p.get('q')){input.value=p.get('q');state.q=p.get('q')}
var h=(location.hash||'').slice(1);if(h&&tabs.some(function(t){return t.dataset.topic===h}))state.topic=h;
apply();
})();"""

HEADER_JS = r"""(function(){var f=document.querySelector('.header-search');if(f){var i=f.querySelector('input');document.addEventListener('keydown',function(e){if(e.key==='/'&&!/input|textarea/i.test(document.activeElement.tagName)&&getComputedStyle(f).display!=='none'){e.preventDefault();i.focus()}})}})();"""


def css():
    return CSS_TEMPLATE.replace("__SEIGAIHA__", seigaiha_uri())


def thumbnail(src: Path, dest: Path, width=640):
    """Resize a photo for card use (Pillow). Returns True on success; the caller falls back to the full image."""
    try:
        from PIL import Image
        dest.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as im:
            im = im.convert("RGB")
            ratio = width / im.width
            im.resize((width, max(1, round(im.height * ratio))), Image.LANCZOS).save(dest, "JPEG", quality=76, optimize=True)
        return True
    except Exception:
        return False


def card_html(meta, words, rec, thumb_rel):
    label, ja = topic(meta["cluster"])
    text = " ".join([meta["title"], meta["description"], label, meta["cluster"]]).lower()
    mins = max(1, math.ceil(words / 200))
    if rec and thumb_rel:
        media = (f'<a class="card-media" href="{html.escape(meta["slug"])}.html" tabindex="-1" aria-hidden="true">'
                 f'<img src="{thumb_rel}" alt="" loading="lazy" width="640" height="400"><p class="badge"><span class="ja" lang="ja">{ja}</span>{html.escape(label)}</p></a>')
        credit = f'<p class="credit">Photo: {html.escape(rec["author"])} · {html.escape(rec["license"])}</p>'
    else:
        media = (f'<a class="card-media fallback" href="{html.escape(meta["slug"])}.html" tabindex="-1" aria-hidden="true">'
                 f'<p class="badge"><span class="ja" lang="ja">{ja}</span>{html.escape(label)}</p></a>')
        credit = ""
    return (f'<article class="card" data-cluster="{html.escape(meta["cluster"])}" data-text="{html.escape(text)}">{media}'
            f'<div class="card-body"><h3><a href="{html.escape(meta["slug"])}.html">{html.escape(meta["title"])}</a></h3>'
            f'<p class="desc">{html.escape(meta["description"])}</p>'
            f'<p class="meta"><span>Updated {html.escape(meta["updated"])}</span><span>· {mins} min read</span></p>{credit}</div></article>')


def home_html(site, cards, topics_count, fact_count, latest):
    """cards: list of card html (newest first); topics_count: {cluster: n}; latest: [(title, slug, date)]."""
    n = len(cards)
    order = [c for c in TOPIC_ORDER if c in topics_count] + sorted(c for c in topics_count if c not in TOPICS)
    tab_html = ['<button class="tab" role="tab" id="tab-all" data-topic="all" aria-selected="true" aria-controls="guides-panel" tabindex="0">'
                f'<span class="ja" lang="ja" aria-hidden="true">全</span>All guides <span class="n">{n}</span></button>']
    side_btns = [f'<li><button type="button" data-topic="all" aria-pressed="true">All guides <span class="n">{n}</span></button></li>']
    for c in order:
        label, ja = topic(c)
        tab_html.append(f'<button class="tab" role="tab" id="tab-{c}" data-topic="{c}" aria-selected="false" aria-controls="guides-panel" tabindex="-1">'
                        f'<span class="ja" lang="ja" aria-hidden="true">{ja}</span>{html.escape(label)} <span class="n">{topics_count[c]}</span></button>')
        side_btns.append(f'<li><button type="button" data-topic="{c}" aria-pressed="false">'
                         f'<span><span lang="ja" aria-hidden="true">{ja}</span> {html.escape(label)}</span><span class="n">{topics_count[c]}</span></button></li>')
    latest_html = "".join(f'<li><a href="{html.escape(s)}.html">{html.escape(t)}</a><span>{html.escape(d)}</span></li>' for t, s, d in latest)
    return f"""
<section class="hero"><div class="wrap">
<p class="kicker">Japan travel guides</p>
<h1>Japan, explained with sources.</h1>
<p class="lead">Practical guides for first-time visitors. Every number links to an official page that we re-check, and every photo is credited.</p>
<div class="cta"><a class="btn" href="#guides">Browse the guides</a><a class="btn ghost" href="about.html">How we source</a></div>
<ul class="trust"><li>{n} guides</li><li>{fact_count} facts re-checked against official pages</li><li>Licensed, credited photos</li></ul>
</div></section>
<div class="wrap"><div class="home-grid" id="guides">
<aside class="sidebar" aria-label="Find a guide">
 <div class="panel search"><h2>Find a guide</h2>
  <form id="search-form" role="search" action="#guides"><label for="q">Search all guides</label>
  <div class="row"><input id="q" name="q" type="search" placeholder="e.g. rail pass, onsen, Kyoto" autocomplete="off" aria-controls="guides-panel"><button class="btn" type="submit">Search</button></div></form>
  <p class="count" id="count" aria-live="polite">{n} guides</p><p class="note">Tip: press <kbd>/</kbd> to jump to search, <kbd>Esc</kbd> to clear.</p></div>
 <div class="panel topics-panel"><h2>Topics</h2><ul class="topics">{"".join(side_btns)}</ul></div>
 <div class="panel latest-panel"><h2>Latest</h2><ul class="latest">{latest_html}</ul></div>
</aside>
<section class="content" aria-label="Guides">
 <div class="tabs" role="tablist" aria-label="Guide topics">{"".join(tab_html)}</div>
 <noscript><p class="noscript-note">Topic pages: {" · ".join(f'<a href="c-{c}.html">{html.escape(topic(c)[0])}</a>' for c in order)}</p></noscript>
 <div id="guides-panel" role="tabpanel" aria-labelledby="tab-all" tabindex="0"><div class="grid">{"".join(cards)}</div>
 <div class="empty" id="empty" hidden><strong>No guides match yet.</strong>Try a shorter word, or <button class="clear clear-all" type="button">show all guides</button>.</div></div>
</section></div></div>"""
