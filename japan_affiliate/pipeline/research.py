"""Find sourced facts for upcoming topics (needs ANTHROPIC_API_KEY + internet; run in CI).

Claude searches ONLY the official domains and proposes registry entries. Nothing it says is trusted:
`pipeline.verify` then fetches each source page and checks every must_contain string is really there,
and the quality gate only lets articles use facts that passed."""
import argparse
import datetime
import json
import os
import re

from . import facts as F
from .common import load_json
from .plan import needing_research

MODEL = os.environ.get("ARTICLE_MODEL", "claude-opus-5-5")
REQUIRED = ("id", "text", "claim", "source_name", "source_url", "must_contain")

PROMPT = """Find {n} to {m} verifiable facts for an English travel article titled "{title}" (search intent: {keyword}).
Search only the official sources you are allowed to use. Useful facts: prices, travel times, rules, validity periods,
eligibility, how to book. Prefer facts a first-time visitor needs to decide.

Return ONLY a JSON array. Each item:
{{"id": "snake_case_unique_id", "text": "the value or rule as it will appear in a sentence",
  "claim": "what the fact is about", "source_name": "official page title",
  "source_url": "the exact official URL you read",
  "must_contain": ["1 to 3 strings that appear VERBATIM on that page, e.g. the number or a distinctive phrase"],
  "topics": ["slug", "..."]}}
Also list in "topics" every slug from this list the fact is genuinely useful for (always include {slug}): {all_slugs}.
Rules: only facts you read on the page; no estimates; no facts from news or blogs; do not repeat these existing ids: {existing}."""


def parse_candidates(text):
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        return []
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return []


def merge(candidates, existing, domains, valid_slugs=None):
    """Return (accepted, rejected_reasons). Accepted entries are unverified and appended by the caller."""
    ok, bad = [], []
    ids = set(existing)
    for c in candidates:
        if not isinstance(c, dict) or any(not c.get(k) for k in REQUIRED):
            bad.append(("malformed", c))
        elif not re.fullmatch(r"[a-z0-9_]+", c["id"]) or c["id"] in ids:
            bad.append(("bad or duplicate id", c.get("id")))
        elif not F.is_official(c["source_url"], domains):
            bad.append(("not an official domain", c["source_url"]))
        elif not isinstance(c["must_contain"], list) or not all(isinstance(s, str) and s for s in c["must_contain"]):
            bad.append(("bad must_contain", c["id"]))
        else:
            ids.add(c["id"])
            tags = [x for x in c.get("topics", []) if isinstance(x, str) and (valid_slugs is None or x in valid_slugs)]
            ok.append({k: c[k] for k in REQUIRED} | {"verified_on": None, "topics": tags})
    return ok, bad


def ask_claude(prompt, domains):
    import anthropic
    client = anthropic.Anthropic()
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 10, "allowed_domains": domains}]
    messages = [{"role": "user", "content": prompt}]
    for _ in range(5):  # server tools can return pause_turn: send the turn back to continue
        resp = client.messages.create(model=MODEL, max_tokens=16000, tools=tools, messages=messages,
                                      thinking={"type": "adaptive"})
        if resp.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": resp.content})
            continue
        return "".join(b.text for b in resp.content if b.type == "text")
    return ""


def main(argv=None, ask=ask_claude):
    ap = argparse.ArgumentParser()
    ap.add_argument("--buffer", type=int, default=3, help="keep this many ready topics ahead of the writer")
    a = ap.parse_args(argv)
    site = load_json("config/site.json")
    domains = site["official_domains"]
    facts = json.loads(F.PATH.read_text(encoding="utf-8"))
    slugs = {t["slug"] for t in load_json("data/topics.json")}
    todo = needing_research(a.buffer, {f["id"]: f for f in facts}, site["min_facts"])
    if not todo:
        print("research buffer full: nothing to do (no API call made)")
    for t in todo:
        facts = json.loads(F.PATH.read_text(encoding="utf-8"))
        text = ask(PROMPT.format(n=4, m=8, title=t["title"], keyword=t["keyword"],
                                 existing=", ".join(f["id"] for f in facts), slug=t["slug"],
                                 all_slugs=", ".join(sorted(slugs))), domains)
        ok, bad = merge(parse_candidates(text), {f["id"] for f in facts}, domains, slugs)
        for f in ok:
            f["topics"] = sorted(set(f.get("topics", [])) | {t["slug"]})
            f["proposed_on"] = datetime.date.today().isoformat()
        F.PATH.write_text(json.dumps(facts + ok, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{t['slug']}: proposed {len(ok)} facts, rejected {len(bad)}: {bad}")


if __name__ == "__main__":
    main()
