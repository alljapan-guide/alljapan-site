"""Draft an article with the Claude API (needs ANTHROPIC_API_KEY). --dry-run prints the prompt only."""
import argparse
import datetime
import os
import sys

from .common import ARTICLES, load_json
from .plan import next_ready, relevant_facts
from . import facts as F
from .common import parse_article
from .quality import check

MODEL = os.environ.get("ARTICLE_MODEL", "claude-opus-5-5")

PROMPT = """You are an experienced Japan travel writer producing an English guide for first-time visitors.

Topic: {title}
Target search query: {keyword}
Search intent: {intent}
Affiliate programs you may mention (use ONLY these shortcodes, max 1 per section): {aff}

SOURCING RULES (hard requirements, the article is rejected otherwise):
- Never write a price, fare, time, date, opening hour or rule from memory. Use only facts from this registry, written as {{{{fact:id}}}}:
{facts}
- Use at least {min_facts} of these facts. If you need a fact that is not listed, leave it out and say the reader should check the provider's page.
- No money amounts (no yen or dollar signs) in the text, and no vague attributions such as "guides say" or "reportedly".
- Opinions are allowed but must be labelled "Our view" or "our editorial recommendation". Never invent personal experiences, quotes or photos; write as an editorial team.

STRUCTURE AND VISUALS (also required; the article is rejected otherwise):
- {min_words}-{max_words} words, original structure, concrete and specific. Start with a direct answer in the first two sentences. At least 5 H2 headings; end with "## FAQ" with 4 questions as H3.
- At least {min_diagrams} diagram block in this exact format (types: flow with steps, cards with items "Title=text", route with stops "Place=detail"):
```diagram
type: flow
caption: <caption>
steps: step one | step two | step three
```
- At least {min_callouts} callouts on their own line: {{{{tip|text}}}}, {{{{warn|text}}}}, {{{{note|text}}}} or {{{{pick|text}}}}.
- At least {min_photos} photo placeholders on their own line: {{{{photo:1|caption}}}}, {{{{photo:2|caption}}}} ... and a matching image_queries list in the front matter of specific Wikimedia Commons search terms (e.g. "Fushimi Inari Taisha torii gates").
- Use a table where a comparison helps. Link to related guides on this site with markdown links like [text](slug.html) only for these slugs: {siblings}.
- Place affiliate links only where a reader would naturally act, as {{{{aff:program|anchor text}}}}. Be honest about downsides.
- Output ONLY the document below, no commentary.

---
title: <max 65 chars>
slug: {slug}
description: <max 155 chars>
date: {today}
updated: {today}
cluster: {cluster}
affiliates: {aff_pipe}
references: <optional extra fact ids separated by |>
image_queries: <term one> | <term two>
---
<markdown body>
"""


def build_prompt(t):
    from . import facts as F
    site = load_json("config/site.json")
    today = datetime.date.today()
    all_facts = F.load()
    rel = relevant_facts(t["slug"], all_facts) or all_facts  # all facts only for a local dry run with nothing verified yet
    reg = "\n".join(f"  - {i}: {f['claim']} => \"{f['text']}\"" for i, f in rel.items())
    siblings = ", ".join(p.stem for p in ARTICLES.glob("*.md") if p.stem != t["slug"]) or "(none yet)"
    return PROMPT.format(facts=reg, siblings=siblings, min_facts=site["min_facts"], min_diagrams=site["min_diagrams"],
                         min_callouts=site["min_callouts"], min_photos=site["min_photos"],title=t["title"], keyword=t["keyword"], intent=t["intent"], slug=t["slug"],
                         cluster=t["cluster"], aff=", ".join(t["affiliates"]), aff_pipe=" | ".join(t["affiliates"]),
                         min_words=site["min_words"], max_words=site["max_words"],
                         today=today.isoformat(), month_year=today.strftime("%B %Y"))


def generate(t, retries=2):
    import anthropic
    client = anthropic.Anthropic()
    prompt = build_prompt(t)
    last = None
    for _ in range(retries + 1):
        msg = client.messages.create(model=MODEL, max_tokens=16000, thinking={"type": "adaptive"},
                                     messages=[{"role": "user", "content": prompt}])
        text = "".join(b.text for b in msg.content if b.type == "text").strip()
        try:
            meta, body = parse_article(text)
        except ValueError as e:
            last = str(e)
            continue
        res = check(meta, body, facts=relevant_facts(t["slug"], F.load()) or None)
        if res["ok"]:
            return text, res
        last = res["errors"]
        prompt += f"\n\nYour previous draft failed these checks, fix them: {last}"
    raise RuntimeError(f"gave up on {t['slug']}: {last}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    site = load_json("config/site.json")
    n = a.n or site["articles_per_run"]
    facts = F.load()
    if a.dry_run:
        from .plan import next_topics
        for t in next_topics(n):
            print(build_prompt(t))
        return 0
    # Candidates in priority order; a topic that fails the gate is skipped, never blocks the others.
    ready = next_ready(n + 3, facts, site["min_facts"])
    if not ready:
        print("no topic has enough verified facts yet (research/verify first)")
    made = 0
    for t in ready:
        if made >= n:
            break
        try:
            text, res = generate(t)
        except RuntimeError as e:
            print(f"SKIPPED {t['slug']}: {e}")
            continue
        (ARTICLES / f"{t['slug']}.md").write_text(text + "\n", encoding="utf-8")
        made += 1
        print(f"wrote {t['slug']} ({res['words']} words) warnings={res['warnings']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
