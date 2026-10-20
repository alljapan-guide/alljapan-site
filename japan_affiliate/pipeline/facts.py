"""Fact registry: every number/rule an article states must come from here, with an official source.

Articles use {{fact:id}}; the build renders the value with a numbered footnote and appends a Sources
section. `verify` fetches each source page and checks that every `must_contain` string is on it."""
import datetime
import json
import re
import urllib.request
from urllib.parse import urlparse

from .common import ROOT, load_json

FACT = re.compile(r"\{\{fact:([a-z0-9_]+)\}\}")
MAX_AGE_DAYS = 90
PATH = ROOT / "data" / "facts.json"


def load():
    return {f["id"]: f for f in load_json("data/facts.json")}


def used_ids(body, meta=None):
    ids = list(dict.fromkeys(FACT.findall(body)))
    for r in (meta or {}).get("references", []):
        if r not in ids:
            ids.append(r)
    return ids


def is_official(url, domains):
    host = (urlparse(url).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in domains)


def is_fresh(fact, today=None):
    v = fact.get("verified_on")
    if not v:
        return False
    today = today or datetime.date.today()
    return (today - datetime.date.fromisoformat(v)).days <= MAX_AGE_DAYS


def render(body, facts, order):
    """Replace {{fact:id}} with value + footnote number; `order` is the list of ids used in this article."""
    def repl(m):
        f = facts.get(m.group(1))
        if not f:
            return m.group(0)
        n = order.index(f["id"]) + 1
        return f'<span class="fact">{f["text"]}<sup><a href="#src-{f["id"]}">[{n}]</a></sup></span>'
    return FACT.sub(repl, body)


def sources_html(order, facts):
    items = []
    for i in order:
        f = facts[i]
        status = f'checked {f["verified_on"]}' if f.get("verified_on") else "not yet verified"
        items.append(f'<li id="src-{i}">{f["claim"]}: <a href="{f["source_url"]}" rel="noopener" target="_blank">'
                     f'{f["source_name"]}</a> <span class="meta">({status})</span></li>')
    return ('<section class="sources" id="sources"><h2>Sources</h2>'
            '<p class="meta">Figures and rules above come from these official pages. They can change; '
            'confirm with the provider before you book.</p><ol>' + "".join(items) + "</ol></section>") if items else ""


def _text(raw):
    raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    return re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", raw))


def default_fetch(url, tries=3):
    """GET a public page as text. Retries transient network errors; a 4xx (blocked or gone) is not retried."""
    import time
    import urllib.error
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 JapanCompassFactCheck/1.0",
        "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.9"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError:
            raise
        except OSError:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def verify(fetch=default_fetch, today=None, only=None):
    """Check each fact against its source. Returns {id: (ok, reason)} and updates facts.json."""
    today = today or datetime.date.today()
    facts = json.loads(PATH.read_text(encoding="utf-8"))
    cache, results = {}, {}
    for f in facts:
        if only and f["id"] not in only:
            continue
        try:
            if f["source_url"] not in cache:
                cache[f["source_url"]] = _text(fetch(f["source_url"]))
            page = cache[f["source_url"]]
            missing = [s for s in f["must_contain"] if s.lower() not in page.lower()]
            ok, reason = (not missing), ("" if not missing else f"missing on page: {missing}")
        except Exception as e:  # network/HTTP errors must not silently verify
            ok, reason = False, f"fetch failed: {e}"
        f["verified_on"] = today.isoformat() if ok else None
        results[f["id"]] = (ok, reason)
    PATH.write_text(json.dumps(facts, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return results


HEAL_PROMPT = """An official page no longer contains the text we recorded, so a fact may have changed.
Fact: {claim}
Recorded value: "{text}"
Page: {url}  (must have contained: {must})
Search only the official sources you are allowed to use and find the CURRENT official wording for this exact fact.
Return ONLY one JSON object: {{"text": "the current value or rule as it reads in a sentence",
"source_url": "the exact official URL you read", "must_contain": ["1 to 3 strings that appear VERBATIM on that page"]}}
If the fact no longer exists or you cannot find it on an official page, return {{}}."""


def apply_heal(fact, cand, domains, fetch=default_fetch, today=None):
    """Accept a repaired fact only if the new source is official AND every new must_contain string is really on the page.
    Returns a change description, or None if rejected."""
    today = today or datetime.date.today()
    try:
        if not isinstance(cand, dict) or not cand.get("text") or not cand.get("source_url") or not cand.get("must_contain"):
            return None
        if not is_official(cand["source_url"], domains) or not all(isinstance(s, str) and s for s in cand["must_contain"]):
            return None
        page = _text(fetch(cand["source_url"])).lower()
        if any(s.lower() not in page for s in cand["must_contain"]):
            return None
    except Exception:
        return None
    change = f'{fact["id"]}: "{fact["text"]}" -> "{cand["text"]}"' if cand["text"] != fact["text"] else f'{fact["id"]}: re-sourced, same value'
    fact.update(text=cand["text"], source_url=cand["source_url"], must_contain=cand["must_contain"], verified_on=today.isoformat())
    return change
