"""Shared helpers: paths, config loading, front matter parsing."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES = ROOT / "content" / "articles"


def load_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def parse_article(text):
    """Split '---\\nkey: value\\n---\\nbody' into (meta dict, body). Lists are comma separated."""
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if k.strip() in ("affiliates", "claims_to_verify", "references", "image_queries"):
            meta[k.strip()] = [x.strip() for x in v.split("|") if x.strip()]
        else:
            meta[k.strip()] = v
    return meta, m.group(2).strip()


def word_count(body):
    return len(re.findall(r"[A-Za-z0-9']+", re.sub(r"\{\{aff:[^}]*\}\}", " ", body)))
