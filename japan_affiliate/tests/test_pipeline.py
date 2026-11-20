from pipeline import affiliate, plan
from pipeline.common import parse_article

META = {"title": "T", "slug": "t", "description": "d", "date": "2026-10-18", "updated": "2026-10-18", "cluster": "x"}


def body(words=1300, extra=""):
    sec = "\n\n".join(f"## Section {i}\n\n" + "word " * (words // 5) for i in range(5))
    return sec + "\n\n## FAQ\n\n### Q?\n\nA.\n" + extra


def test_shortcode_empty_link_is_plain_text():
    assert affiliate.expand("{{aff:klook|book here}}", {"klook": {"link": ""}}) == "book here"


def test_shortcode_link_is_sponsored():
    out = affiliate.expand("{{aff:klook|go}}", {"klook": {"link": "https://x"}})
    assert out == '<a href="https://x" rel="sponsored nofollow noopener" target="_blank">go</a>'


def test_planner_orders_by_priority_and_skips_done():
    topics = [{"slug": "a", "priority": 5, "intent": "informational"}, {"slug": "b", "priority": 9, "intent": "commercial"},
              {"slug": "c", "priority": 9, "intent": "informational"}]
    assert [t["slug"] for t in plan.next_topics(2, topics, set())] == ["b", "c"]
    assert [t["slug"] for t in plan.next_topics(5, topics, {"b"})] == ["c", "a"]


def test_parse_article_lists():
    m, b = parse_article("---\ntitle: X\naffiliates: a | b\n---\nbody")
    assert m["affiliates"] == ["a", "b"] and b == "body"


def test_check_links():
    from pipeline.quality import check_links
    assert check_links("[a](x.html) [b](y.html) [c](https://z.com/q.html)", {"x"}) == ["y"]


def test_faq_jsonld():
    import json
    from pipeline.build import faq_jsonld
    out = json.loads(faq_jsonld("## FAQ\n\n### Q1?\n\nA1 {{aff:klook|go}}.\n\n### Q2?\n\nA2.\n"))
    assert [q["name"] for q in out["mainEntity"]] == ["Q1?", "Q2?"]
    assert out["mainEntity"][0]["acceptedAnswer"]["text"] == "A1 go."


def test_sitemap_has_per_article_lastmod_and_valid_xml():
    import xml.dom.minidom
    from pipeline.build import build_sitemap
    arts = [({"slug": "a", "updated": "2026-11-01"}, ""), ({"slug": "b", "updated": "2026-11-12"}, "")]
    base = "https://x.test"
    xml_ = build_sitemap([f"{base}/", f"{base}/a", f"{base}/b"], arts, base)
    d = xml.dom.minidom.parseString(xml_.encode())
    mods = [n.firstChild.data for n in d.getElementsByTagName("lastmod")]
    assert mods == ["2026-11-12", "2026-11-01", "2026-11-12"]  # home = newest article date, not today's date


def test_atom_feed_lists_newest_articles_with_clean_urls():
    import xml.dom.minidom
    from pipeline.build import build_feed
    arts = [({"slug": "old", "title": "Old & Co", "updated": "2026-11-01", "description": "d1"}, ""),
            ({"slug": "new", "title": "New", "updated": "2026-11-12", "description": "d2"}, "")]
    d = xml.dom.minidom.parseString(build_feed(arts, "https://x.test", "Site", limit=1).encode())
    assert [n.getAttribute("href") for n in d.getElementsByTagName("entry")[0].getElementsByTagName("link")] == ["https://x.test/new"]
    assert len(d.getElementsByTagName("entry")) == 1


def test_own_photo_is_credited_to_the_site_without_a_commons_link():
    from pipeline import visuals as V
    rec = {"file": "a.jpg", "author": "All Japan", "license": "Own work", "license_url": "", "source_url": "", "own": True, "caption": "Cap"}
    html_ = V.photo_html(rec, "fallback")
    assert "Photo: All Japan" in html_ and "Wikimedia" not in html_ and "Cap" in html_
