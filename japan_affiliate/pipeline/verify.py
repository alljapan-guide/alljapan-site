"""CLI: python -m pipeline.verify [--heal]  (needs internet; run in CI).

--heal: for facts whose page no longer matches, ask Claude (official domains only) for the current wording and accept it
only if the new text is really on the official page. Changed values are listed so a human can skim them; because articles
render values from the registry, a corrected fact updates every article that uses it with no rewriting."""
import json
import os
import sys

from . import facts as F
from .common import load_json


def main(argv=None):
    heal = "--heal" in (argv if argv is not None else sys.argv[1:])
    res = F.verify()
    changes = []
    if heal and os.environ.get("ANTHROPIC_API_KEY"):
        from .research import ask_claude, parse_candidates  # noqa: F401
        domains = load_json("config/site.json")["official_domains"]
        facts = json.loads(F.PATH.read_text(encoding="utf-8"))
        for fact in facts:
            if res.get(fact["id"], (True, ""))[0]:
                continue
            text = ask_claude(F.HEAL_PROMPT.format(claim=fact["claim"], text=fact["text"], url=fact["source_url"],
                                                   must=fact["must_contain"]), domains)
            m = text[text.find("{"): text.rfind("}") + 1]
            try:
                cand = json.loads(m) if m else {}
            except json.JSONDecodeError:
                cand = {}
            change = F.apply_heal(fact, cand, domains)
            if change:
                changes.append(change)
                res[fact["id"]] = (True, "healed")
        F.PATH.write_text(json.dumps(facts, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for k, (ok, why) in res.items():
        print(("OK   " if ok else "FAIL ") + k + ("" if ok else f"  {why}"))
    if changes:
        print("\nCHANGED BY HEAL (skim these; each was re-verified on the official page):")
        for c in changes:
            print(" - " + c)
    return 1 if any(not v[0] for v in res.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
