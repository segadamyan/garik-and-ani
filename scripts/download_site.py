#!/usr/bin/env python3
"""Mirror the public Webgency Tilda page and its visual/runtime assets."""

from __future__ import annotations

import hashlib
import html
import gzip
import os
import re
from collections import deque
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen


PAGE_URL = "https://webgency.tilda.ws/"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MIRROR_ROOT = PROJECT_ROOT / "assets-mirror"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
)

ASSET_HOSTS = {
    "static.tildacdn.net",
    "neo.tildacdn.com",
    "thb.tildacdn.net",
    "ws.tildacdn.com",
    "dl.dropboxusercontent.com",
    "res.cloudinary.com",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
}
ASSET_EXTENSIONS = {
    ".css", ".js", ".mjs", ".png", ".jpg", ".jpeg", ".webp", ".gif",
    ".svg", ".ico", ".mp3", ".mp4", ".webm", ".woff", ".woff2", ".ttf", ".eot",
}
TEXT_EXTENSIONS = {".html", ".css", ".js", ".mjs", ".svg"}

ATTRIBUTE_RE = re.compile(
    r"(?:src|href|data-original|data-bg|data-src)=[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)
ABSOLUTE_URL_RE = re.compile(r"https?://[^\s\"'<>`\\)]+", re.IGNORECASE)
PROTOCOL_URL_RE = re.compile(r"(?<!:)//[^\s\"'<>`\\)]+", re.IGNORECASE)
CSS_URL_RE = re.compile(r"url\(\s*[\"']?([^\"')]+)", re.IGNORECASE)


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
    with urlopen(request, timeout=60) as response:
        body = response.read()
        encoding = (response.headers.get("Content-Encoding") or "").lower()
        if encoding == "gzip" or body.startswith(b"\x1f\x8b"):
            body = gzip.decompress(body)
        return body


def suffix_for(url: str) -> str:
    return Path(urlparse(url).path).suffix.lower()


def is_asset_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc in ASSET_HOSTS and suffix_for(url) in ASSET_EXTENSIONS


def destination(url: str) -> Path:
    parsed = urlparse(url)
    path = parsed.path.lstrip("/") or "index"
    output = MIRROR_ROOT / parsed.netloc / path
    if parsed.query and output.suffix == "":
        digest = hashlib.sha256(parsed.query.encode()).hexdigest()[:10]
        output = output.with_name(output.name + "-" + digest)
    return output


def discover(base_url: str, body: bytes) -> set[str]:
    suffix = suffix_for(base_url)
    if suffix not in TEXT_EXTENSIONS and base_url != PAGE_URL:
        return set()

    text = html.unescape(body.decode("utf-8", errors="replace"))
    candidates: set[str] = set()
    candidates.update(ABSOLUTE_URL_RE.findall(text))
    candidates.update("https:" + value for value in PROTOCOL_URL_RE.findall(text))
    candidates.update(ATTRIBUTE_RE.findall(text))
    if suffix == ".css" or base_url == PAGE_URL:
        candidates.update(CSS_URL_RE.findall(text))

    assets: set[str] = set()
    for value in candidates:
        value = value.strip().rstrip(";,}")
        if not value or value.startswith(("data:", "#", "mailto:", "tel:", "javascript:")):
            continue
        absolute = urldefrag(urljoin(base_url, value))[0]
        if is_asset_url(absolute):
            assets.add(absolute)
    return assets


def relative_reference(from_path: Path, to_path: Path) -> str:
    return Path(os.path.relpath(to_path, from_path.parent)).as_posix()


def rewrite_text(body: bytes, output: Path, mapping: dict[str, Path]) -> bytes:
    text = body.decode("utf-8", errors="replace")
    for original, local_path in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
        replacement = relative_reference(output, local_path)
        text = text.replace(original, replacement)
        text = text.replace(html.escape(original, quote=False), replacement)
    return text.encode("utf-8")


def make_local_page(source: bytes, mapping: dict[str, Path]) -> None:
    original = PROJECT_ROOT / "original-response.html"
    original.write_bytes(source)

    body = rewrite_text(source, PROJECT_ROOT / "index.html", mapping)
    body = body.replace(b"\x00", b"\\u0000")
    (PROJECT_ROOT / "index.html").write_bytes(body)


def main() -> None:
    source = fetch(PAGE_URL)
    pending = deque(sorted(discover(PAGE_URL, source)))
    seen: set[str] = set()
    mapping: dict[str, Path] = {}
    bodies: dict[str, bytes] = {}
    failures: list[tuple[str, str]] = []

    while pending:
        url = pending.popleft()
        if url in seen:
            continue
        seen.add(url)
        output = destination(url)
        mapping[url] = output
        try:
            body = fetch(url)
            bodies[url] = body
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(body)
            print(f"saved {url} -> {output.relative_to(PROJECT_ROOT)}")
            pending.extend(sorted(discover(url, body) - seen))
        except Exception as exc:
            failures.append((url, str(exc)))
            print(f"failed {url}: {exc}")

    # Rewrite cross-host absolute asset references after the complete map is known.
    for url, body in bodies.items():
        output = mapping[url]
        if suffix_for(url) in TEXT_EXTENSIONS:
            output.write_bytes(rewrite_text(body, output, mapping))

    make_local_page(source, mapping)

    print(f"downloaded {len(bodies)} assets")
    if failures:
        print(f"{len(failures)} assets failed")
        for url, message in failures:
            print(f"  {url}: {message}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
