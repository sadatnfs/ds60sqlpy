"""Textbook exposition for llm-025 through llm-048, without program changes."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from runpy import run_path
from typing import cast

BASE = Path(__file__).resolve().parent / "textbook_advanced"
START = "<!-- textbook-advanced-start -->"
END = "<!-- textbook-advanced-end -->"

REBASE_LINKS = cast(
    Callable[[str, Path, Path], str],
    run_path(str(Path(__file__).with_name("textbook_links.py")))["rebase_links"],
)


def fenced_blocks(document: str) -> list[str]:
    return re.findall(r"^```[^\n]*\n.*?^```[ \t]*$", document, re.M | re.S)


def enrich_guide(identity: str, document: str) -> str:
    match = re.fullmatch(r"llm-(\d{3})", identity)
    if match is None or not 25 <= int(match.group(1)) <= 48:
        return document
    path = BASE / (identity + ".md")
    if not path.exists():
        return document
    before = fenced_blocks(document)
    raw = path.read_text(encoding="utf-8").strip()
    if "\u2014" in raw or "```" in raw or raw.count("<!-- bridge -->") != 1:
        raise ValueError("Textbook input requires prose, one bridge and no code fences")
    raw = REBASE_LINKS(raw, path, BASE.parent.parent / "guides" / f"{identity}.md")
    body, bridge = (part.strip() for part in raw.split("<!-- bridge -->"))
    body = re.sub(r"^(#{2,3}) ", r"#\1 ", body, flags=re.M)
    document = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n*", "", document, flags=re.S)
    purpose = re.compile(r"^## Purpose and mental model\n.*?(?=^## |\Z)", re.M | re.S)
    if not purpose.search(document):
        raise ValueError("Expected purpose section for " + identity)
    replacement = "## Purpose and mental model\n\n" + START + "\n\n" + body + "\n\n" + END + "\n\n"
    document = purpose.sub(lambda _: replacement, document, count=1)
    next_step = re.compile(r"^## Next step\n.*?(?=^## |\Z)", re.M | re.S)
    if not next_step.search(document):
        raise ValueError("Expected chapter bridge for " + identity)
    document = next_step.sub(lambda _: "## Next step\n\n" + bridge + "\n\n", document, count=1)
    if fenced_blocks(document) != before:
        raise ValueError("Textbook exposition changed a fenced program or prompt")
    return document
