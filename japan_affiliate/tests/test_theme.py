import html

from pipeline import theme as T


def test_palette_meets_wcag_aa_contrast():
    for mode, pairs in T.PALETTE.items():
        for name, (fg, bg) in pairs.items():
            assert T.contrast(fg, bg) >= 4.5, f"{mode} {name}: {T.contrast(fg, bg):.2f}"


def test_contrast_known_values():
    assert round(T.contrast("#000000", "#ffffff"), 2) == 21.0
    assert round(T.contrast("#777777", "#ffffff"), 2) == 4.48  # fails AA (4.5) by design of the WCAG formula


def test_seigaiha_is_a_data_uri_tile():
    u = T.seigaiha_uri()
    assert u.startswith('url("data:image/svg+xml,') and "circle" in u.replace("%3C", "<") and "%3Csvg" in u


META = {"title": "Where <to> stay", "description": "A & B", "slug": "s1", "cluster": "hotels", "updated": "2026-10-20"}


def test_card_escapes_and_has_searchable_text():
    c = T.card_html(META, 900, {"author": "Ann <x>", "license": "CC0"}, "images/t/a.jpg")
    assert "&lt;to&gt;" in c and "Ann &lt;x&gt;" in c and 'data-cluster="hotels"' in c
    assert "where <to> stay" in html.unescape(c.split('data-text="')[1].split('"')[0])
    assert "5 min read" in c  # ceil(900/200)=5


def test_card_without_photo_uses_pattern_fallback():
    assert "card-media fallback" in T.card_html(META, 100, None, None)


def test_home_has_accessible_search_and_tabs():
    h = T.home_html({}, ["<article class='card'></article>"], {"hotels": 1, "culture": 2}, 10, [("T", "s", "2026-10-20")])
    assert 'role="tablist"' in h and h.count('role="tab"') == 3  # All + 2 topics
    assert '<label for="q">' in h and 'type="search"' in h and 'role="search"' in h
    assert 'aria-selected="true"' in h and 'role="tabpanel"' in h and "10 facts re-checked" in h


def test_unknown_topic_gets_a_default_label():
    assert T.topic("hot-springs") == ("Hot Springs", "和")
