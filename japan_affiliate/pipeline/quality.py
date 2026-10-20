"""Quality gate. An article is published only if every blocking check passes.

Aimed at (1) the owner's rule "no unsourced claims": numbers/rules come from data/facts.json with official
sources, (2) Google's scaled-content-abuse risk: thin or unverified pages are rejected, and
(3) the owner's rule "never a wall of text": every article needs diagrams, callouts and photos."""
import re

from .affiliate import SHORTCODE, used_programs
from .common import load_json, word_count
from .facts import FACT, is_official, used_ids
from .visuals import count_visuals

REQUIRED_META = ["title", "slug", "description", "date", "cluster", "updated"]
# Any raw money amount must come from the fact registry instead (so it has an official source).
PRICE = re.compile(r"[¥$€£]\s?\d|\d[\d,]*\s?(yen|JPY|USD|dollars)\b", re.I)
BANNED = ["as an ai", "i cannot", "lorem ipsum", "delve into", "[insert", "todo",
          "recent guides", "most guides", "many guides", "according to guides", "reportedly", "experts say",
          "studies show", "it is said", "some say"]
INTERNAL = re.compile(r"\]\((?!https?:|mailto:|#)([a-z0-9-]+)\.html\)")


def check(meta, body, site=None, facts=None, strict=False):
    from . import facts as F
    site = site or load_json("config/site.json")
    facts = facts if facts is not None else F.load()
    errors, warnings = [], []
    for k in REQUIRED_META:
        if not meta.get(k):
            errors.append(f"missing meta: {k}")
    if len(meta.get("description", "")) > 160:
        errors.append("meta description > 160 chars")
    if len(meta.get("title", "")) > 70:
        warnings.append("title > 70 chars")
    wc = word_count(body)
    if wc < site["min_words"]:
        errors.append(f"too short: {wc} < {site['min_words']} words")
    if wc > site["max_words"]:
        warnings.append(f"long: {wc} words")
    if len(re.findall(r"^## ", body, re.M)) < 4:
        errors.append("needs at least 4 H2 sections")
    low = body.lower()
    for b in BANNED:
        if b in low:
            errors.append(f"banned phrase: {b!r} (cite an official source via {{{{fact:id}}}} instead)")
    if PRICE.search(body):
        errors.append("raw money amount in text: add it to data/facts.json with an official source and use {{fact:id}}")
    n_aff = len(SHORTCODE.findall(body))
    if n_aff == 0:
        warnings.append("no affiliate links")
    if n_aff > max(8, wc // 150):
        errors.append(f"too many affiliate links ({n_aff}) for {wc} words")
    unknown = set(used_programs(body)) - set(load_json("config/affiliates.json")["programs"])
    if unknown:
        errors.append(f"unknown affiliate program(s): {sorted(unknown)}")
    if not re.search(r"^## .*(FAQ|Frequently)", body, re.M | re.I):
        warnings.append("no FAQ section (reduces rich-result chance)")

    ids = used_ids(body, meta)
    missing = [i for i in ids if i not in facts]
    if missing:
        errors.append(f"unknown fact id(s): {missing}")
    known = [facts[i] for i in ids if i in facts]
    if len(known) < site["min_facts"]:
        errors.append(f"needs >= {site['min_facts']} sourced facts, has {len(known)}")
    for f in known:
        if not is_official(f["source_url"], site["official_domains"]):
            errors.append(f"fact {f['id']} source is not on the official-domain list: {f['source_url']}")
        if strict and not F.is_fresh(f):
            errors.append(f"fact {f['id']} is not verified within {F.MAX_AGE_DAYS} days")

    v = count_visuals(body)
    if v["diagrams"] < site["min_diagrams"]:
        errors.append(f"needs >= {site['min_diagrams']} diagram(s), has {v['diagrams']}")
    if v["callouts"] < site["min_callouts"]:
        errors.append(f"needs >= {site['min_callouts']} callout(s), has {v['callouts']}")
    if v["photos"] < site["min_photos"]:
        errors.append(f"needs >= {site['min_photos']} photo(s), has {v['photos']}")
    if v["photos"] > len(meta.get("image_queries", [])):
        errors.append("each {{photo:N|..}} needs a matching image_queries entry")
    return {"ok": not errors, "errors": errors, "warnings": warnings, "words": wc, "visuals": v, "facts": len(known)}


def check_links(body, known_slugs):
    """Return broken internal links (to unpublished slugs)."""
    return sorted({m for m in INTERNAL.findall(body) if m not in known_slugs})


def internal_links(body):
    return INTERNAL.findall(body)
