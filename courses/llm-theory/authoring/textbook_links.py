"""Rebase local inline Markdown links when prose moves from a template to a guide."""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

INLINE_LINK = re.compile(r'(\]\()(?P<target><[^>\n]+>|[^\s)]+)(?P<title>(?:\s+"[^"\n]*")?)\)')


def rebase_links(document: str, source: Path, destination: Path) -> str:
    """Keep linked resources fixed while changing the Markdown document location.

    The textbook inputs contain prose only. URLs, root-relative application
    routes and same-document anchors remain literal. Query/fragment suffixes,
    optional link titles and angle-bracket destinations are preserved.
    """

    def replace(match: re.Match[str]) -> str:
        target = match.group("target")
        angled = target.startswith("<")
        address = target[1:-1] if angled else target
        parts = urlsplit(address)
        if parts.scheme or parts.netloc or not parts.path or parts.path.startswith("/"):
            return match.group(0)
        resource = (source.parent / parts.path).resolve()
        relative = Path(os.path.relpath(resource, destination.parent.resolve())).as_posix()
        rebased = urlunsplit(("", "", relative, parts.query, parts.fragment))
        if angled:
            rebased = "<" + rebased + ">"
        return match.group(1) + rebased + match.group("title") + ")"

    return INLINE_LINK.sub(replace, document)
