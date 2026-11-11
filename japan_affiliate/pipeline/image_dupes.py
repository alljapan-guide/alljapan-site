"""Guard against the same photo appearing in more than one article (or twice in one).

Why this exists: fetch_images used to take the top Commons hit for every query, so similar topics (insurance, IC cards,
luggage, Kansai hubs) all got the same file, and card thumbnails on the home page showed identical pictures.
Rule: one source photo = one photo slot on the whole site. Two slots are "the same photo" if the file bytes match
or the Commons source page matches.

`data/known_duplicate_images.json` lists slots that still duplicate an older photo (the clean-up backlog). The check
fails on any duplicate that is NOT in that list, so no new duplicate can be added; shrink the list to [] to finish."""
import collections
import hashlib
import json
import re

from .common import ARTICLES, ROOT

PHOTO = re.compile(r"\{\{photo:(\d+)\|")
IMAGES_DIR = ROOT / "assets" / "images"
BASELINE = ROOT / "data" / "known_duplicate_images.json"


def used_slots(articles_dir=ARTICLES):
    """{'slug/N': slug} for every {{photo:N|..}} marker actually used in an article body."""
    out = {}
    for p in sorted(articles_dir.glob("*.md")):
        for n in PHOTO.findall(p.read_text(encoding="utf-8")):
            out[f"{p.stem}/{n}"] = p.stem
    return out


def _digest(rec, files_dir):
    try:
        return hashlib.sha256((files_dir / rec["file"]).read_bytes()).hexdigest()
    except OSError:
        return None


def duplicate_groups(images, slots, files_dir=IMAGES_DIR):
    """Groups (lists of 'slug/N') of used slots that show the same photo, matched by file bytes or Commons page."""
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    seen = {}
    for key in slots:
        rec = images.get(key)
        if not rec:
            continue
        for sig in filter(None, (_digest(rec, files_dir), rec.get("source_url") or rec.get("title"))):
            if sig in seen:
                parent[find(key)] = find(seen[sig])
            else:
                seen[sig] = key
            find(key)
    groups = collections.defaultdict(list)
    for key in list(parent):
        if key in slots and images.get(key):
            groups[find(key)].append(key)
    return [sorted(g) for g in groups.values() if len(g) > 1]


def load_baseline(path=BASELINE):
    return set(json.loads(path.read_text())) if path.exists() else set()


def violations(groups, baseline):
    """Duplicate groups containing at least one slot that is not in the allowed backlog."""
    return [g for g in groups if any(k not in baseline for k in g)]


def check(images, strict=True, articles_dir=ARTICLES, files_dir=IMAGES_DIR, baseline=None):
    groups = duplicate_groups(images, used_slots(articles_dir), files_dir)
    bad = violations(groups, load_baseline() if baseline is None else baseline)
    if bad and strict:
        lines = "\n".join("  " + " = ".join(g) for g in bad)
        raise SystemExit("The same photo is used in more than one place (each photo may appear once on the whole site):\n"
                         f"{lines}\nGive each slot its own photo (change its image_queries entry or pin another file:), "
                         "or drop the slot; never copy an existing photo.")
    return groups
