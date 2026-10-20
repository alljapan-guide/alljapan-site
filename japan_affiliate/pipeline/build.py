"""Build the static site into ./dist (articles, index, cluster pages, sitemap, robots, feed)."""
import datetime
import html
import json
import re
import shutil
from xml.sax.saxutils import escape

import markdown
from jinja2 import Environment, FileSystemLoader

from . import facts as F
from . import visuals as V
from .affiliate import expand
from .common import ARTICLES, ROOT, load_json, parse_article
from .quality import check, check_links, internal_links

DIST = ROOT / "dist"
CSS = """:root{--ink:#1d2330;--muted:#667085;--line:#e3e6ec;--brand:#c0392b;--bg:#fff;--card:#fff8ee;--link:#1a5fb4}
@media(prefers-color-scheme:dark){:root{--ink:#e8eaf0;--muted:#9aa3b5;--line:#2c3344;--bg:#14171f;--card:#1e2230;--link:#7fb0ff}}
*{box-sizing:border-box}body{font:17px/1.75 system-ui,-apple-system,"Segoe UI",sans-serif;margin:0;color:var(--ink);background:var(--bg)}
header,main,footer{max-width:46rem;margin:0 auto;padding-left:1rem;padding-right:1rem}
header{padding-top:1rem;padding-bottom:.8rem;border-bottom:1px solid var(--line)}header .brand{font-weight:800;font-size:1.3rem;color:var(--brand);text-decoration:none;margin-right:.8rem}
header span{color:var(--muted);font-size:.9rem}h1{line-height:1.2;font-size:2rem;margin:1rem 0 .4rem}h2{margin-top:2.4rem;padding-top:.4rem;border-top:3px solid var(--brand);display:inline-block;line-height:1.3}h3{margin-top:1.6rem}
a{color:var(--link)}.meta{color:var(--muted);font-size:.9rem}svg.hero{display:block;width:100%;height:auto;max-height:220px;border-radius:14px;margin:.6rem 0}
.disc{background:var(--card);border-left:4px solid #e0a100;padding:.6rem .9rem;font-size:.88rem;margin:1rem 0;border-radius:0 8px 8px 0}
.callout{border-radius:12px;padding:.8rem 1rem;margin:1.4rem 0;border-left:5px solid;background:var(--card)}.callout strong{display:block;font-size:.8rem;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.2rem}
.callout.tip{border-color:#2e9e5b}.callout.warn{border-color:#d9822b}.callout.note{border-color:#3b7dd8}.callout.pick{border-color:var(--brand)}
figure{margin:1.6rem 0}figure.photo img{width:100%;height:auto;border-radius:12px;display:block}figcaption{font-size:.85rem;color:var(--muted);margin-top:.4rem}figcaption .credit{display:block;font-size:.78rem}
figure.diagram{background:var(--card);border-radius:14px;padding:1rem;text-align:center}figure.diagram svg{width:100%;max-width:420px;height:auto}figure.photo.pending div{padding:2rem;border:2px dashed var(--line);border-radius:12px;color:var(--muted);text-align:center}
table{border-collapse:collapse;width:100%;display:block;overflow-x:auto;font-size:.95rem}th,td{border:1px solid var(--line);padding:.5rem .7rem;text-align:left}th{background:var(--card)}
.fact{background:linear-gradient(transparent 62%,#ffe58a88 0)}.fact sup{font-size:.7em}section.sources{margin-top:2.4rem;padding:1rem 1.2rem;background:var(--card);border-radius:12px;font-size:.88rem}section.sources h2{border:0;margin:0 0 .4rem;font-size:1.1rem}
footer{border-top:1px solid var(--line);margin-top:3rem;padding-top:1rem;padding-bottom:2rem;color:var(--muted);font-size:.85rem}
ul.posts{list-style:none;padding:0;display:grid;gap:.9rem}ul.posts li{background:var(--card);border-radius:12px;padding:.9rem 1rem}ul.posts a{font-weight:700;text-decoration:none}"""


def load_articles(strict=True):
    site = load_json("config/site.json")
    facts = F.load()
    out = []
    for p in sorted(ARTICLES.glob("*.md")):
        meta, body = parse_article(p.read_text(encoding="utf-8"))
        res = check(meta, body, site, facts, strict=strict)
        if not res["ok"]:
            if strict:
                raise SystemExit(f"{p.name} fails quality gate: {res['errors']}")
            continue
        out.append((meta, body))
    out.sort(key=lambda a: a[0]["date"], reverse=True)
    return out


def article_jsonld(meta, site, url):
    return json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": meta["title"],
                       "datePublished": meta["date"], "dateModified": meta["updated"],
                       "author": {"@type": "Organization", "name": site["author"]},
                       "mainEntityOfPage": url, "description": meta["description"]})


def render_body(body, meta, facts, images, strict):
    """Markdown -> HTML with diagrams, callouts, photos, fact footnotes and the Sources section."""
    blocks = []
    order = F.used_ids(body, meta)  # before stashing, so facts inside callouts are counted

    def stash(html_):
        blocks.append(html_)
        return f"@@B{len(blocks)-1}@@"

    inline = lambda t: re.sub(r"^<p>|</p>$", "", markdown.markdown(expand(F.render(t, facts, order))).strip())  # noqa: E731
    body = V.BLOCK.sub(lambda m: stash(V.diagram_svg(m.group(1))), body)
    body = V.CALL.sub(lambda m: stash(V.callout_html(m.group(1), m.group(2), inline)), body)

    def photo(m):
        rec = images.get(f"{meta['slug']}/{m.group(1)}")
        if strict and (not rec or not (ROOT / "assets" / "images" / rec["file"]).exists()):
            raise SystemExit(f"{meta['slug']}: photo {m.group(1)} missing; run pipeline.fetch_images")
        return stash(V.photo_html(rec, m.group(2)))

    body = V.PHOTO.sub(photo, body)
    out = markdown.markdown(expand(F.render(body, facts, order)), extensions=["extra", "toc"])
    for i, b in enumerate(blocks):
        out = out.replace(f"<p>@@B{i}@@</p>", b).replace(f"@@B{i}@@", b)
    return out + F.sources_html(order, facts)


def faq_jsonld(body):
    """Build FAQPage JSON-LD from '## FAQ' with '### Question' + answer paragraphs."""
    m = re.search(r"^## FAQ.*?\n(.*)$", body, re.S | re.M)
    if not m:
        return ""
    qa = []
    for blk in re.split(r"^### ", m.group(1), flags=re.M)[1:]:
        q, _, a = blk.partition("\n")
        a = re.sub(r"\s+", " ", re.sub(r"\{\{aff:[^|]*\|([^}]*)\}\}", r"\1", a)).strip()
        if q.strip() and a:
            qa.append({"@type": "Question", "name": q.strip(),
                       "acceptedAnswer": {"@type": "Answer", "text": a}})
    return json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": qa}) if qa else ""


def build(strict=True):
    site = load_json("config/site.json")
    base = site["base_url"].rstrip("/")
    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")), autoescape=True)
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST / "style.css").write_text(CSS, encoding="utf-8")
    facts = F.load()
    images = json.loads((ROOT / 'data' / 'images.json').read_text()) if (ROOT / 'data' / 'images.json').exists() else {}
    shutil.copytree(ROOT / 'assets' / 'images', DIST / 'images') if (ROOT / 'assets' / 'images').exists() else None
    articles = load_articles(strict)
    page = env.from_string("{% extends 'base.html' %}{% block main %}" + "{{ content|safe }}" + "{% endblock %}")

    def write(name, **kw):
        kw.setdefault("jsonld", "")
        kw.setdefault("faq", "")
        kw.update(site=site, root=kw.get("root", ""))
        kw["canonical"] = f"{base}/{name}" if name != "index.html" else f"{base}/"
        (DIST / name).write_text(page.render(**kw), encoding="utf-8")

    slugs = {m["slug"] for m, _ in articles}
    for meta, body in articles:
        broken = check_links(body, slugs)
        if broken and strict:
            raise SystemExit(f"{meta['slug']} has broken internal links: {broken}")
    by_cluster = {}
    for m, _ in articles:
        by_cluster.setdefault(m["cluster"], []).append(m)

    urls = [f"{base}/"]
    for meta, body in articles:
        content = render_body(body, meta, facts, images, strict)
        name = f"{meta['slug']}.html"
        urls.append(f"{base}/{name}")
        related = [r for r in by_cluster[meta["cluster"]] if r["slug"] != meta["slug"]][:3]
        rel_html = ("<h2>Related guides</h2><ul>" + "".join(
            f"<li><a href='{r['slug']}.html'>{html.escape(r['title'])}</a></li>" for r in related) + "</ul>") if related else ""
        write(name, title=f"{meta['title']} | {site['name']}", description=meta["description"],
              jsonld=article_jsonld(meta, site, f"{base}/{name}"),
              faq=faq_jsonld(body),
              content=f"<article><h1>{html.escape(meta['title'])}</h1>"
                      f"{V.hero_svg(meta['cluster'], meta['slug'])}<p class='meta'>Updated {meta['updated']} · {site['author']}</p>"
                      f"<p class='disc'>{html.escape(site['disclosure'])}</p>{content}{rel_html}</article>")
    items = "".join(f"<li><a href='{m['slug']}.html'>{html.escape(m['title'])}</a><br>"
                    f"<span class='meta'>{html.escape(m['description'])}</span></li>" for m, _ in articles)
    write("index.html", title=f"{site['name']} – {site['tagline']}", description=site["tagline"],
          content=f"<h1>Latest guides</h1><ul class='posts'>{items}</ul>")
    for cl, ms in by_cluster.items():
        lst = "".join(f"<li><a href='{m['slug']}.html'>{html.escape(m['title'])}</a></li>" for m in ms)
        urls.append(f"{base}/c-{cl}.html")
        write(f"c-{cl}.html", title=f"{cl.title()} guides | {site['name']}", description=f"{cl.title()} guides for Japan",
              content=f"<h1>{html.escape(cl.title())}</h1><ul class='posts'>{lst}</ul>")
    if strict and not site.get("contact_email"):
        raise SystemExit("config/site.json: set contact_email (shown on the privacy page) before publishing")
    contact = html.escape(site.get("contact_email") or "(set contact_email in config/site.json)")
    write("privacy.html", title=f"Privacy & affiliate disclosure | {site['name']}", description="Privacy and affiliate disclosure",
          content="<h1>Privacy &amp; affiliate disclosure</h1>"
                  f"<p>{html.escape(site['disclosure'])}</p>"
                  "<p>This site is a static website. It does not ask you for personal information. When you click an affiliate link, "
                  "the partner site may set its own cookies to record that you came from us; those cookies are governed by the partner's "
                  "privacy policy. If we add analytics or advertising later, this page will be updated first.</p>"
                  f"<p>Contact: {contact}</p>")
    write("about.html", title=f"About | {site['name']}", description="Editorial policy",
          content="<h1>About &amp; editorial policy</h1><p>We publish practical Japan travel guides. Drafts are produced with AI "
                  "assistance and pass automated quality checks; prices and schedules are dated and should be confirmed with "
                  "the provider before booking. We earn commissions from some links, which never changes what we recommend "
                  "or what you pay.</p>")
    today = datetime.date.today().isoformat()
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{escape(u)}</loc><lastmod>{today}</lastmod></url>" for u in urls) + "</urlset>")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    return len(articles)


if __name__ == "__main__":
    import sys
    draft = "--draft" in sys.argv  # local preview: unverified facts / missing photos are allowed
    print(f"built {build(strict=not draft)} articles -> {DIST}{' (DRAFT, not publishable)' if draft else ''}")
