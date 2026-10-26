"""Expand {{aff:program|anchor text}} shortcodes into sponsored links."""
import html
import re

from .common import load_json

SHORTCODE = re.compile(r"\{\{aff:([a-z0-9_]+)\|([^}]+)\}\}")


def expand(body, programs=None):
    programs = programs or load_json("config/affiliates.json")["programs"]

    def repl(m):
        key, text = m.group(1), m.group(2).strip()
        link = programs.get(key, {}).get("link", "")
        if not link:  # unknown program or not yet approved: plain text, never a dead link
            return text
        return f'<a href="{html.escape(link, quote=True)}" rel="sponsored nofollow noopener" target="_blank">{text}</a>'

    return SHORTCODE.sub(repl, body)


def used_programs(body):
    return sorted({m.group(1) for m in SHORTCODE.finditer(body)})
