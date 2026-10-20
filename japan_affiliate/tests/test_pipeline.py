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
