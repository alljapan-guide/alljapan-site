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
from . import theme as T
from . import visuals as V
from .affiliate import expand
from .common import ARTICLES, ROOT, load_json, parse_article, word_count
from .quality import check, check_links, internal_links

DIST = ROOT / "dist"



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
    (DIST / "style.css").write_text(T.css(), encoding="utf-8")
    (DIST / "app.js").write_text(T.JS + "\n" + T.HEADER_JS, encoding="utf-8")
    facts = F.load()
    images = json.loads((ROOT / 'data' / 'images.json').read_text()) if (ROOT / 'data' / 'images.json').exists() else {}
    shutil.copytree(ROOT / 'assets' / 'images', DIST / 'images') if (ROOT / 'assets' / 'images').exists() else None
    articles = load_articles(strict)
    page = env.from_string("{% extends 'base.html' %}{% block main %}" + "{{ content|safe }}" + "{% endblock %}")

    def write(name, **kw):
        kw.setdefault("jsonld", "")
        kw.setdefault("faq", "")
        kw.setdefault("body_class", "")
        kw.setdefault("main_class", "article-main")
        kw.update(site=site, root=kw.get("root", ""), logo=T.logo_svg())
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
    cards, thumbs_done = [], 0
    for meta, body in articles:
        rec = images.get(f"{meta['slug']}/1")
        thumb = None
        if rec and (ROOT / "assets" / "images" / rec["file"]).exists():
            if T.thumbnail(ROOT / "assets" / "images" / rec["file"], DIST / "images" / "t" / rec["file"]):
                thumb = f"images/t/{rec['file']}"
            else:
                thumb = f"images/{rec['file']}"
        cards.append(T.card_html(meta, word_count(body), rec if thumb else None, thumb))
    counts = {cl: len(ms) for cl, ms in by_cluster.items()}
    latest = [(m["title"], m["slug"], m["updated"]) for m, _ in articles[:3]]
    fresh = sum(1 for f in facts.values() if F.is_fresh(f))
    write("index.html", title=f"{site['name']} – {site['tagline']}", description=site["tagline"],
          body_class="home", main_class="", content=T.home_html(site, cards, counts, fresh, latest))
    for cl, ms in by_cluster.items():
        lst = "".join(f"<li><a href='{m['slug']}.html'>{html.escape(m['title'])}</a></li>" for m in ms)
        urls.append(f"{base}/c-{cl}.html")
        write(f"c-{cl}.html", title=f"{T.topic(cl)[0]} guides | {site['name']}", description=f"{T.topic(cl)[0]} guides for Japan",
              content=f"<h1>{html.escape(T.topic(cl)[0])}</h1><ul class='posts'>{lst}</ul>")
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
