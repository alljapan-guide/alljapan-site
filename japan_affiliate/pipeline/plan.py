"""Pick the next topics. A topic is READY when enough fresh, relevant facts exist for it, so one topic that
lacks sources never blocks the queue: the run simply moves on to the next ready one."""
import datetime

from . import facts as F
from .common import ARTICLES, load_json


def published_slugs():
    return {p.stem for p in ARTICLES.glob("*.md")}


def _ordered(topics, done):
    todo = [t for t in topics if t["slug"] not in done]
    todo.sort(key=lambda t: (-t["priority"], t["intent"] != "commercial", t["slug"]))
    return todo


def relevant_facts(slug, facts):
    """Fresh facts that are untagged (shared by all articles) or tagged for this topic."""
    return {i: f for i, f in facts.items() if F.is_fresh(f) and (not f.get("topics") or slug in f["topics"])}


def is_ready(topic, facts, min_facts):
    return len(relevant_facts(topic["slug"], facts)) >= min_facts


def next_topics(n=1, topics=None, done=None):
    topics = topics if topics is not None else load_json("data/topics.json")
    return _ordered(topics, done if done is not None else published_slugs())[:n]


def next_ready(n, facts, min_facts, topics=None, done=None):
    topics = topics if topics is not None else load_json("data/topics.json")
    ordered = _ordered(topics, done if done is not None else published_slugs())
    return [t for t in ordered if is_ready(t, facts, min_facts)][:n]


def _recently_researched(slug, facts, today=None, days=14):
    today = today or datetime.date.today()
    for f in facts.values():
        d = f.get("proposed_on")
        if d and slug in f.get("topics", []) and (today - datetime.date.fromisoformat(d)).days < days:
            return True
    return False


def needing_research(buffer, facts, min_facts, topics=None, done=None, today=None):
    """Keep `buffer` ready topics ahead of the writer. Returns the not-ready topics to research (none if the buffer is full)."""
    topics = topics if topics is not None else load_json("data/topics.json")
    ordered = _ordered(topics, done if done is not None else published_slugs())
    ready = [t for t in ordered if is_ready(t, facts, min_facts)]
    missing = max(0, buffer - len(ready))
    pending = [t for t in ordered if not is_ready(t, facts, min_facts) and not _recently_researched(t["slug"], facts, today)]
    return pending[:missing]
