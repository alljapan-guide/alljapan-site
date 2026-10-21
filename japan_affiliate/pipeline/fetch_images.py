"""Fetch licensed photos from Wikimedia Commons for each article's `image_queries` (needs internet; run in CI).

Only CC0 / public domain / CC BY / CC BY-SA files are used; author + license + source URL are stored in
data/images.json and shown under every photo."""
import json
import re
import urllib.parse
import urllib.request

from .common import ARTICLES, ROOT, parse_article

API = "https://commons.wikimedia.org/w/api.php"
UA = "JapanCompassBot/1.0 (https://github.com/; contact via site owner)"
OK_LICENSE = re.compile(r"^(CC0|Public domain|PD|CC BY(?!-NC)(?!-ND)(-SA)?\b)", re.I)
RANK = lambda lic: 0 if re.match(r"(CC0|Public domain|PD)", lic, re.I) else (1 if not re.search("SA", lic) else 2)  # noqa: E731
IMAGES = ROOT / "data" / "images.json"
FILES = ROOT / "assets" / "images"


def _ua():
    """Wikimedia requires a descriptive User-Agent with a REAL contact (a URL or address); placeholders get HTTP 403."""
    from .common import load_json
    site = load_json("config/site.json")
    contact = site.get("repo_url") or site.get("contact_email")
    if not contact:
        raise SystemExit("config/site.json: set repo_url or contact_email (Wikimedia needs a real contact in the User-Agent)")
    return f"JapanCompassBot/1.0 ({contact}) python-urllib"


def _get(url, tries=4):
    """GET with the descriptive User-Agent Wikimedia asks for; waits and retries on 429/503 (rate limit)."""
    import time
    import urllib.error
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": _ua()}), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503) or i == tries - 1:
                raise
            time.sleep(min(int(e.headers.get("Retry-After", "5") or 5), 30) + 2 * i)


def http_json(url):
    return json.loads(_get(url))


def http_bytes(url):
    return _get(url)


def canonical_download(url):
    """The API returns thumb.wikimedia.org URLs; the same files are served from upload.wikimedia.org (no tracking query)."""
    return re.sub(r"^https://thumb\.wikimedia\.org/", "https://upload.wikimedia.org/", (url or "").split("?")[0])


def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def pick(api_json):
    """Choose the best licensed landscape JPEG from a Commons API response, or None."""
    cands = []
    for p in (api_json.get("query", {}).get("pages", {}) or {}).values():
        ii = (p.get("imageinfo") or [None])[0]
        if not ii or ii.get("mime") != "image/jpeg" or ii.get("width", 0) < 1000 or ii.get("width", 0) < ii.get("height", 0):
            continue
        meta = ii.get("extmetadata", {})
        lic = strip_html(meta.get("LicenseShortName", {}).get("value", ""))
        if not OK_LICENSE.match(lic):
            continue
        cands.append((RANK(lic), p.get("index", 99), {
            "title": p["title"], "author": strip_html(meta.get("Artist", {}).get("value", "")) or "Unknown",
            "license": lic, "license_url": meta.get("LicenseUrl", {}).get("value", ""),
            "source_url": ii.get("descriptionurl", ""), "download": canonical_download(ii.get("thumburl") or ii.get("url"))}))
    return sorted(cands, key=lambda c: c[:2])[0][2] if cands else None


def search(query, get=http_json):
    """`file:Exact Commons title.jpg` pins one file; anything else is a ranked Commons search."""
    if query.lower().startswith("file:"):
        title = "File:" + query[5:].strip()
        q = urllib.parse.urlencode({"action": "query", "format": "json", "titles": title, "prop": "imageinfo",
                                    "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 1200})
        data = get(f"{API}?{q}")
        for p in (data.get("query", {}).get("pages", {}) or {}).values():
            p["index"] = 0
        return pick(data)
    q = urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search", "gsrsearch": f"{query} filetype:bitmap",
                                "gsrnamespace": 6, "gsrlimit": 15, "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime",
                                "iiurlwidth": 1200})
    return pick(get(f"{API}?{q}"))


def run(get=http_json, download=http_bytes, pause=3):
    images = json.loads(IMAGES.read_text()) if IMAGES.exists() else {}
    FILES.mkdir(parents=True, exist_ok=True)
    for p in sorted(ARTICLES.glob("*.md")):
        meta, _ = parse_article(p.read_text(encoding="utf-8"))
        for i, q in enumerate(meta.get("image_queries", []), 1):
            key = f"{meta['slug']}/{i}"
            if key in images and (FILES / images[key]["file"]).exists():
                continue
            import time
            time.sleep(pause)  # be gentle: Wikimedia rate-limits bursts (HTTP 429)
            try:
                rec = search(q, get)
            except Exception as e:  # one failed query must not stop the other photos
                print(f"search failed for {key}: {e}")
                rec = None
            if not rec:
                print(f"no licensed photo for {key}: {q}")
                continue
            fn = f"{meta['slug']}-{i}.jpg"
            try:
                (FILES / fn).write_bytes(download(rec.pop("download")))
            except Exception as e:
                print(f"download failed for {key}: {e}")
                continue
            images[key] = {**rec, "file": fn, "query": q}
            print(f"fetched {key}: {rec['title']} ({rec['license']})")
    IMAGES.write_text(json.dumps(images, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    run()
