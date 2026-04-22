#!/usr/bin/env python3
"""Concurrent crawler for le-guide-sante.org.

Downloads every page reachable from the seed URLs within the target domain,
plus the assets referenced by those pages (images, CSS, JS, fonts, media),
and rewrites links so the result is browsable offline.

State is persisted between runs so interruptions resume cleanly.
"""

from __future__ import annotations

import json
import logging
import os
import queue
import re
import signal
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse, quote, unquote

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "site"
STATE_DIR = ROOT / ".crawl"
STATE_DIR.mkdir(exist_ok=True)
LOG_FILE = STATE_DIR / "crawl.log"
DONE_FILE = STATE_DIR / "done.txt"
FAILED_FILE = STATE_DIR / "failed.txt"

SEEDS = [
    "https://www.le-guide-sante.org/",
    "https://www.le-guide-sante.org/sitemap.xml",
    "https://www.le-guide-sante.org/actualites/tendances/sitemap.xml",
    "https://www.le-guide-sante.org/actualites/tendances/sitemap-news.xml",
    "https://www.le-guide-sante.org/robots.txt",
]
DOMAINS = {"www.le-guide-sante.org", "le-guide-sante.org"}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

WORKERS = 8
REQUEST_TIMEOUT = 30
RETRY_ON_STATUS = {429, 500, 502, 503, 504}
MAX_RETRIES = 3
POLITE_DELAY = 0.1  # seconds per request, per worker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("clone")


def canonicalize(url: str) -> str:
    """Normalize a URL so equivalent forms map to the same key."""
    p = urlparse(url)
    scheme = "https"
    netloc = p.netloc.lower()
    if netloc == "le-guide-sante.org":
        netloc = "www.le-guide-sante.org"
    # Strip fragment, keep query
    path = p.path or "/"
    # Collapse duplicate slashes (but keep leading)
    path = re.sub(r"/+", "/", path)
    return urlunparse((scheme, netloc, path, "", p.query, ""))


def in_scope(url: str) -> bool:
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        return False
    return p.netloc.lower() in DOMAINS


def safe_segment(seg: str) -> str:
    seg = unquote(seg)
    # Replace characters not safe on common filesystems
    seg = re.sub(r'[<>:"\\|?*\x00-\x1f]', "_", seg)
    if not seg:
        seg = "_"
    if len(seg) > 180:
        seg = seg[:160] + "_" + str(abs(hash(seg)) % 10**8)
    return seg


def url_to_path(url: str, content_type: str | None = None) -> Path:
    """Map a URL to a local filesystem path under OUT/."""
    p = urlparse(url)
    parts = [p.netloc.lower() or "unknown"]
    path = p.path or "/"
    segments = [s for s in path.split("/") if s]
    is_html = content_type is not None and "html" in content_type.lower()
    is_xml = content_type is not None and (
        "xml" in content_type.lower() or url.endswith(".xml")
    )

    if path.endswith("/") or not segments:
        parts.extend(safe_segment(s) for s in segments)
        filename = "index.html"
    else:
        last = segments[-1]
        parts.extend(safe_segment(s) for s in segments[:-1])
        has_ext = "." in last and len(last.rsplit(".", 1)[-1]) <= 6
        if is_html and not has_ext:
            parts.append(safe_segment(last))
            filename = "index.html"
        else:
            filename = safe_segment(last)
            if is_html and not filename.lower().endswith((".html", ".htm")):
                filename += ".html"
            if is_xml and not filename.lower().endswith(".xml"):
                filename += ".xml"

    if p.query:
        qtag = re.sub(r"[^A-Za-z0-9._=-]", "_", p.query)[:80]
        stem, dot, ext = filename.rpartition(".")
        if dot:
            filename = f"{stem}@{qtag}.{ext}"
        else:
            filename = f"{filename}@{qtag}"

    return OUT.joinpath(*parts, filename)


def path_to_url_rel(from_path: Path, to_path: Path) -> str:
    rel = os.path.relpath(to_path, start=from_path.parent)
    return quote(rel.replace(os.sep, "/"), safe="/._-@=")


# --- Persistent state ----------------------------------------------------

state_lock = threading.Lock()
done: set[str] = set()
failed: dict[str, str] = {}

if DONE_FILE.exists():
    with DONE_FILE.open() as fh:
        done = {line.strip() for line in fh if line.strip()}
if FAILED_FILE.exists():
    with FAILED_FILE.open() as fh:
        for line in fh:
            if "\t" in line:
                u, err = line.rstrip("\n").split("\t", 1)
                failed[u] = err


def mark_done(url: str) -> None:
    with state_lock:
        if url in done:
            return
        done.add(url)
        with DONE_FILE.open("a") as fh:
            fh.write(url + "\n")


def mark_failed(url: str, err: str) -> None:
    with state_lock:
        failed[url] = err
        with FAILED_FILE.open("a") as fh:
            fh.write(f"{url}\t{err}\n")


# --- Queue management ----------------------------------------------------

seen_lock = threading.Lock()
seen: set[str] = set()
work: queue.Queue[str] = queue.Queue()
stop_event = threading.Event()


def enqueue(url: str) -> None:
    if not in_scope(url):
        return
    canon = canonicalize(url)
    with seen_lock:
        if canon in seen:
            return
        seen.add(canon)
    if canon in done:
        return
    work.put(canon)


# --- HTTP ----------------------------------------------------------------

session_local = threading.local()


def get_session() -> requests.Session:
    s = getattr(session_local, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update(HEADERS)
        session_local.s = s
    return s


def fetch(url: str) -> requests.Response:
    sess = get_session()
    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            r = sess.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            if r.status_code in RETRY_ON_STATUS:
                time.sleep(1 + attempt * 2)
                continue
            return r
        except requests.RequestException as exc:
            last_exc = exc
            time.sleep(1 + attempt * 2)
    if last_exc:
        raise last_exc
    raise RuntimeError("fetch exhausted retries")


# --- Link extraction & rewriting ----------------------------------------

ASSET_ATTRS = {
    "img": ["src", "data-src", "data-lazy-src"],
    "script": ["src"],
    "link": ["href"],
    "source": ["src", "srcset"],
    "video": ["src", "poster"],
    "audio": ["src"],
    "iframe": ["src"],
    "object": ["data"],
    "embed": ["src"],
    "input": ["src"],
    "track": ["src"],
}
NAV_ATTRS = {
    "a": ["href"],
    "area": ["href"],
    "form": ["action"],
}

URL_IN_CSS = re.compile(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", re.IGNORECASE)
IMPORT_IN_CSS = re.compile(r"@import\s+['\"]([^'\"]+)['\"]", re.IGNORECASE)


def extract_from_srcset(value: str) -> list[str]:
    out = []
    for piece in value.split(","):
        piece = piece.strip()
        if not piece:
            continue
        out.append(piece.split(" ", 1)[0])
    return out


def process_html(url: str, html: str, local_path: Path) -> tuple[str, list[str], list[str]]:
    """Return (rewritten_html, page_links, asset_links)."""
    soup = BeautifulSoup(html, "lxml")

    pages: list[str] = []
    assets: list[str] = []

    def rewrite(tag, attr, value, kind):
        if not value:
            return
        value = value.strip()
        if value.startswith(("javascript:", "mailto:", "tel:", "data:", "#")):
            return
        try:
            absolute = urljoin(url, value)
        except Exception:
            return
        absolute = canonicalize(absolute) if in_scope(absolute) else absolute
        if kind == "srcset":
            # rebuild srcset with each candidate
            rebuilt = []
            for piece in value.split(","):
                piece = piece.strip()
                if not piece:
                    continue
                parts = piece.split(None, 1)
                u = parts[0]
                descriptor = " " + parts[1] if len(parts) > 1 else ""
                abs_u = urljoin(url, u)
                if in_scope(abs_u):
                    abs_c = canonicalize(abs_u)
                    assets.append(abs_c)
                    target = url_to_path(abs_c, content_type="")
                    rebuilt.append(path_to_url_rel(local_path, target) + descriptor)
                else:
                    rebuilt.append(piece)
            tag[attr] = ", ".join(rebuilt)
            return
        if in_scope(absolute):
            if kind == "page":
                pages.append(absolute)
                target = url_to_path(absolute, content_type="text/html")
            else:
                assets.append(absolute)
                target = url_to_path(absolute, content_type="")
            tag[attr] = path_to_url_rel(local_path, target)

    for sel, attrs in NAV_ATTRS.items():
        for tag in soup.find_all(sel):
            for attr in attrs:
                if tag.has_attr(attr):
                    rewrite(tag, attr, tag.get(attr), "page")

    for sel, attrs in ASSET_ATTRS.items():
        for tag in soup.find_all(sel):
            for attr in attrs:
                if not tag.has_attr(attr):
                    continue
                val = tag.get(attr)
                if attr == "srcset" or (sel == "source" and attr == "srcset"):
                    rewrite(tag, attr, val, "srcset")
                else:
                    rewrite(tag, attr, val, "asset")

    # inline styles (style="..." and <style>...</style>)
    for tag in soup.find_all(style=True):
        tag["style"] = rewrite_css_refs(url, tag["style"], local_path, assets)
    for tag in soup.find_all("style"):
        if tag.string:
            tag.string.replace_with(rewrite_css_refs(url, tag.string, local_path, assets))

    return str(soup), pages, assets


def rewrite_css_refs(base_url: str, css: str, local_path: Path, assets: list[str]) -> str:
    def repl_url(m: re.Match) -> str:
        raw = m.group(1).strip()
        if raw.startswith("data:"):
            return m.group(0)
        abs_u = urljoin(base_url, raw)
        if in_scope(abs_u):
            abs_c = canonicalize(abs_u)
            assets.append(abs_c)
            target = url_to_path(abs_c, content_type="")
            return f"url({path_to_url_rel(local_path, target)})"
        return m.group(0)

    def repl_import(m: re.Match) -> str:
        raw = m.group(1).strip()
        abs_u = urljoin(base_url, raw)
        if in_scope(abs_u):
            abs_c = canonicalize(abs_u)
            assets.append(abs_c)
            target = url_to_path(abs_c, content_type="")
            return f'@import "{path_to_url_rel(local_path, target)}"'
        return m.group(0)

    css = URL_IN_CSS.sub(repl_url, css)
    css = IMPORT_IN_CSS.sub(repl_import, css)
    return css


def process_css(url: str, css: str, local_path: Path) -> tuple[str, list[str]]:
    assets: list[str] = []
    rewritten = rewrite_css_refs(url, css, local_path, assets)
    return rewritten, assets


def extract_sitemap_urls(xml_bytes: bytes) -> list[str]:
    # Extract <loc> entries — cheap regex is fine for sitemap XML
    text = xml_bytes.decode("utf-8", errors="replace")
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text)


# --- Worker --------------------------------------------------------------

counter_lock = threading.Lock()
counter = {"ok": 0, "fail": 0, "bytes": 0}


def worker() -> None:
    while not stop_event.is_set():
        try:
            url = work.get(timeout=1)
        except queue.Empty:
            if stop_event.is_set():
                return
            continue
        try:
            handle(url)
        except Exception as exc:  # pragma: no cover - defensive
            log.exception("worker crashed on %s", url)
            mark_failed(url, f"crash: {exc}")
        finally:
            work.task_done()
            time.sleep(POLITE_DELAY)


def handle(url: str) -> None:
    if url in done:
        return
    try:
        r = fetch(url)
    except Exception as exc:
        mark_failed(url, f"fetch: {exc}")
        with counter_lock:
            counter["fail"] += 1
        return

    if r.status_code >= 400:
        mark_failed(url, f"http {r.status_code}")
        with counter_lock:
            counter["fail"] += 1
        return

    ctype = r.headers.get("Content-Type", "")
    final_url = canonicalize(r.url) if in_scope(r.url) else url
    # Save under requested url OR final url; prefer the canonical final url so
    # subsequent rewrites find the same file.
    save_url = final_url if in_scope(r.url) else url
    local_path = url_to_path(save_url, content_type=ctype)
    local_path.parent.mkdir(parents=True, exist_ok=True)

    is_html = "html" in ctype.lower()
    is_css = "css" in ctype.lower() or url.endswith(".css")
    is_xml = "xml" in ctype.lower() or url.endswith(".xml")

    try:
        if is_html:
            html, pages, assets = process_html(save_url, r.text, local_path)
            local_path.write_text(html, encoding="utf-8", errors="replace")
            for u in pages:
                enqueue(u)
            for u in assets:
                enqueue(u)
        elif is_css:
            css, assets = process_css(save_url, r.text, local_path)
            local_path.write_text(css, encoding="utf-8", errors="replace")
            for u in assets:
                enqueue(u)
        elif is_xml:
            local_path.write_bytes(r.content)
            for u in extract_sitemap_urls(r.content):
                enqueue(u)
        else:
            local_path.write_bytes(r.content)
    except Exception as exc:
        mark_failed(url, f"write: {exc}")
        with counter_lock:
            counter["fail"] += 1
        return

    mark_done(url)
    # Also mark the canonical form as done so redirects don't re-fetch
    if save_url != url:
        mark_done(save_url)

    with counter_lock:
        counter["ok"] += 1
        counter["bytes"] += len(r.content)


def reporter() -> None:
    last_ok = 0
    while not stop_event.is_set():
        time.sleep(15)
        with counter_lock:
            ok = counter["ok"]
            fail = counter["fail"]
            total_bytes = counter["bytes"]
        rate = (ok - last_ok) / 15.0
        last_ok = ok
        log.info(
            "progress ok=%d fail=%d queue=%d rate=%.1f/s downloaded=%.1fMB",
            ok, fail, work.qsize(), rate, total_bytes / (1024 * 1024),
        )


def main() -> int:
    OUT.mkdir(exist_ok=True)

    def handle_sig(signum, _frame):
        log.warning("signal %s received; stopping workers", signum)
        stop_event.set()

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    for seed in SEEDS:
        enqueue(seed)

    rep = threading.Thread(target=reporter, daemon=True)
    rep.start()

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for _ in range(WORKERS):
            pool.submit(worker)

        # Wait until queue is drained and no worker is busy
        while not stop_event.is_set():
            try:
                work.join()
                # give any late enqueues a chance to surface
                time.sleep(2)
                if work.empty():
                    break
            except Exception:
                break

        stop_event.set()

    with counter_lock:
        log.info("done ok=%d fail=%d bytes=%.1fMB", counter["ok"], counter["fail"], counter["bytes"] / (1024 * 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
