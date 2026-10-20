import datetime
import json

from pipeline import facts as F
from pipeline import fetch_images as FI
from pipeline import visuals as V
from pipeline.quality import check

FACT = {"id": "x1", "text": "¥50,000", "claim": "c", "source_name": "S", "source_url": "https://japanrailpass.net/en/p/",
        "must_contain": ["50,000"], "verified_on": None}


def test_render_numbers_footnotes_and_sources():
    f = {"x1": FACT}
    out = F.render("Costs {{fact:x1}}.", f, ["x1"])
    assert 'class="fact">¥50,000<sup><a href="#src-x1">[1]</a>' in out
    assert "not yet verified" in F.sources_html(["x1"], f)


def test_official_domain_and_freshness():
    assert F.is_official("https://global.jr-central.co.jp/x", ["jr-central.co.jp"])
    assert not F.is_official("https://evil-jr-central.co.jp.example.com/x", ["jr-central.co.jp"])
    assert not F.is_fresh(FACT)
    assert F.is_fresh({**FACT, "verified_on": datetime.date.today().isoformat()})
    old = (datetime.date.today() - datetime.timedelta(days=F.MAX_AGE_DAYS + 1)).isoformat()
    assert not F.is_fresh({**FACT, "verified_on": old})


def test_verify_marks_only_confirmed_facts(tmp_path, monkeypatch):
    p = tmp_path / "facts.json"
    bad = {**FACT, "id": "x2", "must_contain": ["99,999"]}
    p.write_text(json.dumps([FACT, bad]))
    monkeypatch.setattr(F, "PATH", p)
    res = F.verify(fetch=lambda url: "<html><body>Price <b>50,000</b> yen</body></html>")
    assert res["x1"][0] and not res["x2"][0]
    saved = {f["id"]: f for f in json.loads(p.read_text())}
    assert saved["x1"]["verified_on"] and saved["x2"]["verified_on"] is None


def test_verify_fetch_error_is_not_verified(tmp_path, monkeypatch):
    p = tmp_path / "facts.json"
    p.write_text(json.dumps([FACT]))
    monkeypatch.setattr(F, "PATH", p)

    def boom(url):
        raise OSError("down")
    assert F.verify(fetch=boom)["x1"][0] is False


def test_diagrams_render_all_types():
    for spec in ("type: flow\nsteps: A | B | C\ncaption: c", "type: cards\nitems: T=body text | U=more", "type: route\nstops: Tokyo=3 nights | Kyoto=3 nights"):
        out = V.diagram_svg(spec)
        assert out.startswith("<figure class=\"diagram\"><svg") and "</svg>" in out


def test_diagram_text_is_escaped():
    assert "<script>" not in V.diagram_svg("type: flow\nsteps: <script>alert(1)</script>")


def test_gate_blocks_unsourced_money_and_vague_attribution():
    meta = {"title": "t", "slug": "s", "description": "d", "date": "2026-01-01", "updated": "2026-01-01", "cluster": "c",
            "image_queries": ["a", "b"]}
    visuals = "```diagram\ntype: flow\nsteps: A | B\n```\n\n{{tip|a}}\n\n{{note|b}}\n\n{{photo:1|x}}\n\n{{photo:2|y}}\n\n"
    body = visuals + "\n\n".join(f"## S{i}\n\n" + "word " * 250 for i in range(4)) + "\n\n## FAQ\n\n### Q?\n\nA.\n"
    site = {"min_words": 900, "max_words": 3500, "official_domains": ["japanrailpass.net"], "min_facts": 2,
            "min_photos": 2, "min_callouts": 2, "min_diagrams": 1}
    facts = {"x1": FACT, "x2": {**FACT, "id": "x2"}}
    good = body + "{{fact:x1}} {{fact:x2}}"
    assert check(meta, good, site, facts)["ok"]
    assert not check(meta, good + " Costs ¥5,000.", site, facts)["ok"]
    assert not check(meta, good + " Recent guides say so.", site, facts)["ok"]
    assert not check(meta, body + "{{fact:x1}}", site, facts)["ok"]  # only one fact
    assert not check(meta, good, site, {**facts, "x2": {**FACT, "id": "x2", "source_url": "https://blog.example.com/a"}})["ok"]


API = {"query": {"pages": {
    "1": {"index": 2, "title": "File:A.jpg", "imageinfo": [{"mime": "image/jpeg", "width": 2000, "height": 1000, "thumburl": "u1", "descriptionurl": "d1",
          "extmetadata": {"LicenseShortName": {"value": "CC BY-SA 4.0"}, "Artist": {"value": "<a>Ann</a>"}, "LicenseUrl": {"value": "l1"}}}]},
    "2": {"index": 1, "title": "File:B.jpg", "imageinfo": [{"mime": "image/jpeg", "width": 2000, "height": 1000, "thumburl": "u2", "descriptionurl": "d2",
          "extmetadata": {"LicenseShortName": {"value": "CC BY 4.0"}, "Artist": {"value": "Bob"}, "LicenseUrl": {"value": "l2"}}}]},
    "3": {"index": 0, "title": "File:C.jpg", "imageinfo": [{"mime": "image/jpeg", "width": 2000, "height": 1000, "thumburl": "u3", "descriptionurl": "d3",
          "extmetadata": {"LicenseShortName": {"value": "CC BY-NC 4.0"}, "Artist": {"value": "Cy"}}}]},
    "4": {"index": 3, "title": "File:D.png", "imageinfo": [{"mime": "image/png", "width": 2000, "height": 1000, "extmetadata": {}}]},
}}}


def test_pick_prefers_permissive_license_and_rejects_noncommercial():
    rec = FI.pick(API)
    assert rec["title"] == "File:B.jpg" and rec["license"] == "CC BY 4.0" and rec["author"] == "Bob"


def test_pick_returns_none_when_nothing_licensed():
    only_nc = {"query": {"pages": {"3": API["query"]["pages"]["3"]}}}
    assert FI.pick(only_nc) is None


def test_photo_html_has_attribution_and_pending_fallback():
    h = V.photo_html({"file": "a.jpg", "author": "Bob", "license": "CC BY 4.0", "license_url": "l", "source_url": "s"}, "cap")
    assert "Photo: Bob" in h and "CC BY 4.0" in h and 'src="images/a.jpg"' in h
    assert "pending" in V.photo_html(None, "cap")


def test_research_merge_rejects_untrusted_candidates():
    from pipeline import research as R
    doms = ["japanrailpass.net"]
    good = {"id": "new_fact", "text": "t", "claim": "c", "source_name": "n", "source_url": "https://japanrailpass.net/x", "must_contain": ["a"]}
    cands = [good, {**good, "id": "new_fact"}, {**good, "id": "blog", "source_url": "https://myblog.example.com/p"},
             {**good, "id": "BAD ID"}, {"id": "x"}, {**good, "id": "empty", "must_contain": []}]
    ok, bad = R.merge(cands, {"old"}, doms)
    assert [o["id"] for o in ok] == ["new_fact"] and ok[0]["verified_on"] is None
    assert len(bad) == 5


def test_research_parse_candidates_tolerates_prose():
    from pipeline import research as R
    assert R.parse_candidates('Here you go:\n[{"id": "a"}]\nDone') == [{"id": "a"}]
    assert R.parse_candidates("no json") == []
    assert R.parse_candidates("[not json]") == []


def test_research_tags_facts_with_valid_topic_slugs_only():
    from pipeline import research as R
    c = {"id": "k1", "text": "t", "claim": "c", "source_name": "n", "source_url": "https://japanrailpass.net/x",
         "must_contain": ["a"], "topics": ["a-topic", "bogus"]}
    ok, _ = R.merge([c], set(), ["japanrailpass.net"], {"a-topic"})
    assert ok[0]["topics"] == ["a-topic"]


def test_apply_heal_accepts_only_text_really_on_official_page():
    old = {**FACT, "id": "h1"}
    cand = {"text": "¥55,000", "source_url": "https://japanrailpass.net/en/p/", "must_contain": ["55,000"]}
    page = lambda url: "<p>now 55,000 yen</p>"  # noqa: E731
    change = F.apply_heal(old, dict(cand), ["japanrailpass.net"], fetch=page)
    assert change and "¥50,000" in change and old["text"] == "¥55,000" and old["verified_on"]
    old2 = {**FACT, "id": "h2"}
    assert F.apply_heal(old2, dict(cand), ["japanrailpass.net"], fetch=lambda u: "<p>nothing</p>") is None
    assert old2["text"] == "¥50,000" and old2["verified_on"] is None  # untouched
    assert F.apply_heal({**FACT}, {**cand, "source_url": "https://blog.example.com/x"}, ["japanrailpass.net"], fetch=page) is None
    assert F.apply_heal({**FACT}, {}, ["japanrailpass.net"], fetch=page) is None


def _fresh(i, topics=None):
    return {"id": i, "verified_on": datetime.date.today().isoformat(), **({"topics": topics} if topics is not None else {})}


def test_queue_never_stalls_and_research_only_fills_the_buffer():
    from pipeline import plan as P
    topics = [{"slug": "a", "priority": 9, "intent": "commercial"}, {"slug": "b", "priority": 8, "intent": "commercial"},
              {"slug": "c", "priority": 7, "intent": "commercial"}]
    facts = {"f1": _fresh("f1", ["b"]), "f2": _fresh("f2", ["b"]), "f3": _fresh("f3", ["c"])}
    # 'a' has no facts: skipped, 'b' is next (ready), 'c' has only one fact (not ready)
    assert [t["slug"] for t in P.next_ready(2, facts, 2, topics, set())] == ["b"]
    assert [t["slug"] for t in P.needing_research(2, facts, 2, topics, set())] == ["a"]  # buffer 2, 1 ready -> research 1
    assert P.needing_research(1, facts, 2, topics, set()) == []  # buffer full: no API call
    facts["f9"] = {"id": "f9", "verified_on": None, "topics": ["a"], "proposed_on": datetime.date.today().isoformat()}
    assert P.needing_research(2, facts, 2, topics, set()) == [topics[2]]  # 'a' researched recently: not repeated, try 'c'


def test_canonical_download_uses_upload_host_without_tracking_query():
    u = "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/8a/A.jpg/1280px-A.jpg?utm_source=x"
    assert FI.canonical_download(u) == "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/A.jpg/1280px-A.jpg"
    assert FI.canonical_download("https://upload.wikimedia.org/x.jpg") == "https://upload.wikimedia.org/x.jpg"


def test_photo_caption_comes_from_commons_title_not_article_guess():
    assert V.commons_caption("File:20181110 Fushimi Inari Torii 12.jpg") == "Fushimi Inari Torii 12"
    h = V.photo_html({"title": "File:Yagi-Uda antenna for Wi-Fi on Router.jpg", "file": "a.jpg", "author": "A", "license": "CC0",
                      "license_url": "", "source_url": "s"}, "A portable WiFi router")
    assert "Yagi-Uda antenna for Wi-Fi on Router" in h and "portable WiFi router" not in h
