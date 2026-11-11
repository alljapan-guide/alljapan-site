import json

import pytest

from pipeline import fetch_images as FI
from pipeline import image_dupes as D
from tests.test_facts_visuals import API


def test_pick_skips_photos_already_used_elsewhere():
    best = FI.pick(API)
    assert best["title"] == "File:B.jpg"
    assert FI.pick(API, exclude={"File:B.jpg"})["title"] != "File:B.jpg"


def _site(tmp_path, bodies, files):
    arts = tmp_path / "a"
    arts.mkdir()
    for slug, body in bodies.items():
        (arts / f"{slug}.md").write_text(body)
    img = tmp_path / "i"
    img.mkdir()
    for name, data in files.items():
        (img / name).write_bytes(data)
    return arts, img


def test_same_bytes_or_same_source_page_is_a_duplicate(tmp_path):
    arts, img = _site(tmp_path, {"x": "{{photo:1|a}}", "y": "{{photo:1|b}} {{photo:2|c}}", "z": "{{photo:1|d}}"},
                      {"1.jpg": b"same", "2.jpg": b"same", "3.jpg": b"other", "4.jpg": b"third"})
    images = {"x/1": {"file": "1.jpg", "source_url": "u1"}, "y/1": {"file": "2.jpg", "source_url": "u2"},  # same bytes
              "y/2": {"file": "3.jpg", "source_url": "u3"}, "z/1": {"file": "4.jpg", "source_url": "u3"}}  # same page
    groups = D.duplicate_groups(images, D.used_slots(arts), img)
    assert sorted(groups) == [["x/1", "y/1"], ["y/2", "z/1"]]


def test_new_duplicate_fails_but_listed_backlog_passes(tmp_path):
    arts, img = _site(tmp_path, {"x": "{{photo:1|a}}", "y": "{{photo:1|b}}"}, {"1.jpg": b"s", "2.jpg": b"s"})
    images = {"x/1": {"file": "1.jpg"}, "y/1": {"file": "2.jpg"}}
    with pytest.raises(SystemExit):
        D.check(images, True, arts, img, baseline=set())
    assert D.check(images, True, arts, img, baseline={"x/1", "y/1"})  # backlog: reported, not fatal


def test_site_has_no_new_duplicate_photos():
    """Whole-site guard: every duplicate must be in the shrinking clean-up backlog; new ones fail CI."""
    images = json.loads((D.ROOT / "data" / "images.json").read_text())
    assert D.violations(D.duplicate_groups(images, D.used_slots()), D.load_baseline()) == []
