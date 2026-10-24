#!/usr/bin/env python3
"""Check published HTML targets, fragments and IDs without a server or network.

Run after the reader drift check, from a clone or a staged source package. This
checks static HTML attributes only: JavaScript/API-created links, CSS url(),
srcset and external URLs remain the responsibility of their separate checks.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ds60sqlpy.curriculum_framework import is_content_link  # noqa: E402

ORIGIN = "https://published.invalid"
CLASSROOM_ALIASES = ("/", "/classroom", "/learn", "/journeys", "/journey-preview")
ASSETS = {
    "/assets/classroom.css": "src/ds60sqlpy/assets/classroom.css",
    "/assets/classroom.js": "src/ds60sqlpy/assets/classroom.js",
    "/assets/browser-preview.js": "src/ds60sqlpy/assets/browser-preview.js",
    # The server generates this stylesheet. Its source module must be packaged;
    # actual CSS generation is covered by the rendering gate, not this scanner.
    "/assets/rich-content.css": "src/ds60sqlpy/reader_content.py",
}
LINK_ATTRIBUTES = {"a": "href", "link": "href", "script": "src", "img": "src", "source": "src"}


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.anchors: set[str] = set()
        self.links: list[tuple[int, str]] = []
        self.duplicate_ids: list[tuple[int, str]] = []
        self.base_lines: list[int] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        line = self.getpos()[0]
        identity = values.get("id")
        if identity is not None:
            if identity in self.ids:
                self.duplicate_ids.append((line, identity))
            self.ids.add(identity)
        if tag == "a" and values.get("name") is not None:
            self.anchors.add(str(values["name"]))
        attribute = LINK_ATTRIBUTES.get(tag)
        if attribute is not None and values.get(attribute) is not None:
            self.links.append((line, str(values[attribute])))
        if tag == "base" and "href" in values:
            self.base_lines.append(line)


def inspect_published(root: Path) -> dict[str, Any]:
    root = root.resolve()
    failures: list[dict[str, Any]] = []
    pages: dict[str, Page] = {}
    sources: dict[str, str] = {}
    resources: set[str] = set()

    def fail(path: str, kind: str, *, line: int = 0, target: str = "") -> None:
        failures.append({"path": path, "line": line, "kind": kind, "target": target})

    def linked_source(path: Path) -> bool:
        # Check from the root towards the leaf so even lstat on a child cannot
        # traverse a linked ancestor. The shared helper recognizes Windows
        # junctions on Python 3.11 as well as ordinary symlinks.
        candidate = root
        for part in path.relative_to(root).parts:
            candidate /= part
            if is_content_link(candidate):
                return True
        return False

    def regular_source(relative: str) -> Path | None:
        path = root / relative
        if linked_source(path):
            fail(relative, "linked_published_source")
            return None
        if not path.is_file():
            fail(relative, "missing_published_source")
            return None
        if not path.resolve().is_relative_to(root):
            fail(relative, "linked_published_source")
            return None
        return path

    def add_page(relative: str, route: str) -> None:
        path = regular_source(relative)
        if path is None:
            return
        try:
            page = Page()
            page.feed(path.read_text(encoding="utf-8"))
            page.close()
        except (OSError, UnicodeError, ValueError) as exc:
            fail(relative, "unreadable_html", target=type(exc).__name__)
            return
        pages[route] = page
        sources[route] = relative
        resources.add(route)
        for line, identity in page.duplicate_ids:
            fail(relative, "duplicate_id", line=line, target=identity)
        for line in page.base_lines:
            fail(relative, "unsupported_base_url", line=line)

    add_page("START_HERE.html", "/START_HERE.html")
    for folder in ("lesson-pages", "reference-pages"):
        directory = root / folder
        if linked_source(directory):
            fail(folder, "linked_published_source")
            continue
        paths: list[Path] = []
        if directory.is_dir():
            for current, names, filenames in os.walk(directory, followlinks=False):
                descend = []
                for name in sorted(names):
                    child = Path(current) / name
                    if is_content_link(child):
                        fail(child.relative_to(root).as_posix(), "linked_published_source")
                    else:
                        descend.append(name)
                # Python 3.11 os.walk can enter Windows junctions even with
                # followlinks=False, so remove them before traversal resumes.
                names[:] = descend
                paths.extend(Path(current) / name for name in filenames if name.endswith(".html"))
        if not paths:
            fail(folder, "missing_published_pages")
        for path in sorted(paths):
            relative = path.relative_to(root).as_posix()
            if any(part.startswith(".") for part in Path(relative).parts):
                fail(relative, "unserved_published_path")
            else:
                add_page(relative, "/" + relative)
    add_page("src/ds60sqlpy/assets/classroom.html", "/classroom")
    for route, relative in ASSETS.items():
        if regular_source(relative) is not None:
            resources.add(route)
    aliases = {alias: "/classroom" for alias in CLASSROOM_ALIASES if "/classroom" in pages}
    links_checked = 0
    fragments_checked = 0
    external_skipped = 0
    text_fragments_skipped = 0
    for route, page in pages.items():
        relative = sources[route]
        for line, href in page.links:
            try:
                parsed = urlsplit(href)
                # Absolute URLs, protocol-relative URLs and non-HTTP schemes are
                # not fetched or claimed valid, including documentation localhost URLs.
                if parsed.scheme or parsed.netloc:
                    external_skipped += 1
                    continue
                link = urlsplit(urljoin(ORIGIN + route, href))
                target = unquote(link.path)
                target = aliases.get(target, target)
                fragment = unquote(link.fragment)
            except ValueError:
                fail(relative, "invalid_url", line=line, target=href)
                continue
            links_checked += 1
            if target not in resources:
                fail(relative, "missing_local_target", line=line, target=href)
                continue
            if not fragment:
                continue
            if ":~:text=" in fragment:
                fragment = fragment.split(":~:text=", maxsplit=1)[0]
                text_fragments_skipped += 1
                if not fragment:
                    continue
            target_page = pages.get(target)
            if target_page is None:
                fail(relative, "unsupported_asset_fragment", line=line, target=href)
                continue
            fragments_checked += 1
            if (
                fragment not in target_page.ids
                and fragment not in target_page.anchors
                and fragment.lower() != "top"
            ):
                fail(relative, "missing_fragment", line=line, target=href)
    return {
        "schema_version": 1,
        "html_pages_checked": len(pages),
        "local_links_checked": links_checked,
        "fragments_checked": fragments_checked,
        "external_urls_skipped": external_skipped,
        "text_fragment_directives_skipped": text_fragments_skipped,
        "failure_count": len(failures),
        "failures": failures,
        "limitations": [
            "External URLs and text-fragment text matching are not fetched or validated.",
            "JavaScript/API-created links, CSS url() and srcset are not interpreted.",
            "This is an offline HTML check, not HTTP or browser execution evidence.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--report", type=Path, help="optional JSON report destination")
    args = parser.parse_args(argv)
    report = inspect_published(args.root)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"Published HTML links: {report['html_pages_checked']} pages; "
        f"{report['local_links_checked']} local links; {report['fragments_checked']} fragments; "
        f"{report['failure_count']} failures."
    )
    for failure in report["failures"]:
        print(f"- {failure['path']}:{failure['line']}: {failure['kind']}: {failure['target']}")
    return int(bool(report["failure_count"]))


if __name__ == "__main__":
    raise SystemExit(main())
