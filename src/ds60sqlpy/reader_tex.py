"""Build-compiled TeX and locally bundled typography with a native fallback."""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import re
from functools import lru_cache
from importlib.resources import files
from typing import Any

from ds60sqlpy._tex_cache_digest import TEX_CACHE_SHA256
from ds60sqlpy.reader_content import render_code_block
from ds60sqlpy.reader_math import _validate_source, render_math

ASSET_ROUTE = "/src/ds60sqlpy/assets/vendor/textbook/"


def expression_key(expression: str, display: bool) -> str:
    return hashlib.sha256(
        (("display" if display else "inline") + "\n" + expression).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def compiled_expressions() -> dict[str, Any]:
    path = files("ds60sqlpy").joinpath("assets/vendor/textbook/compiled-tex.json")
    try:
        if not path.is_file():
            return {}
        with path.open("rb") as stream:
            encoded = stream.read(64_000_001)
        if len(encoded) > 64_000_000 or hashlib.sha256(encoded).hexdigest() != TEX_CACHE_SHA256:
            raise ValueError("Compiled TeX integrity mismatch")
        raw = json.loads(encoded)
        if (
            not isinstance(raw, dict)
            or type(raw.get("schema_version")) is not int
            or raw["schema_version"] != 1
            or raw.get("compiler") != "KaTeX 0.19.1"
            or not isinstance(raw.get("expressions"), dict)
        ):
            raise ValueError("Invalid compiled TeX schema")
        entries = raw["expressions"]
        for key, item in entries.items():
            if (
                not isinstance(item, dict)
                or set(item) != {"source", "display", "html"}
                or not isinstance(item["source"], str)
                or type(item["display"]) is not bool
                or not isinstance(item["html"], str)
                or key != expression_key(item["source"], item["display"])
            ):
                raise ValueError("Invalid compiled TeX entry")
        return dict(entries)
    except (OSError, ValueError, TypeError, RecursionError):
        logging.getLogger(__name__).warning(
            "Compiled mathematics cache is invalid; using safe native MathML. Rebuild lesson TeX."
        )
        return {}


def render_lesson_math(expression: str, *, display: bool = False) -> str:
    """Use exact-source precompiled HTML+MathML; new drafts retain safe native math."""
    try:
        _validate_source(expression)
    except ValueError:
        return render_math(expression, display=display)
    entry = compiled_expressions().get(expression_key(expression, display))
    if not entry or entry["source"] != expression or entry["display"] is not display:
        return render_math(expression, display=display)
    # This is a versioned build artifact compiled with trust=false, never request HTML.
    body = entry["html"]
    if not isinstance(body, str):
        raise ValueError("Invalid compiled TeX output. Rebuild lesson mathematics.")
    if not display:
        return body
    return (
        '<figure class="equation"><div class="math-display tex-compiled">' + body + "</div>"
        '<figcaption class="equation-label">Equation</figcaption>'
        '<details class="equation-source"><summary>TeX source</summary>'
        + render_code_block(expression, "tex")
        + "</details></figure>"
    )


def font_stylesheet() -> str:
    """Build one local sheet with embedded font bytes for HTTP and portable readers."""
    assets = files("ds60sqlpy").joinpath("assets/vendor/textbook")
    manifest = json.loads(assets.joinpath("provenance.json").read_text("utf-8"))

    def font_url(name: str) -> str:
        data = assets.joinpath("fonts/" + name).read_bytes()
        if hashlib.sha256(data).hexdigest() != manifest["files"]["fonts/" + name]:
            raise ValueError("Bundled font integrity mismatch")
        return "data:font/woff2;base64," + base64.b64encode(data).decode("ascii")

    css = assets.joinpath("katex.min.css").read_text("utf-8")
    rules = "\n".join(re.findall(r"@font-face\{[^}]*\}", css))
    rules = re.sub(r',url\([^)]*\.(?:woff|ttf)\) format\("[^\"]+"\)', "", rules)
    rules = re.sub(
        r"url\(fonts/([A-Za-z0-9_-]+\.woff2)\)",
        lambda match: 'url("' + font_url(match[1]) + '")',
        rules,
    )
    for variant, weight, style in (
        ("regular", 400, "normal"),
        ("bold", 700, "normal"),
        ("italic", 400, "italic"),
        ("bolditalic", 700, "italic"),
    ):
        rules += (
            '\n@font-face{font-family:"Latin Modern";src:url("'
            + font_url("lmroman10-" + variant + ".woff2")
            + '") format("woff2");'
            + f"font-weight:{weight};font-style:{style};font-display:swap;"
            + "}"
        )
    return (
        "/* Generated local font sheet. See KaTeX and Latin Modern licenses beside this file. */\n"
        + rules
        + "\n"
    )


@lru_cache(maxsize=1)
def textbook_styles() -> str:
    """Textbook layout; font data is shared once in the local fonts.css asset."""
    css = files("ds60sqlpy").joinpath("assets/vendor/textbook/katex.min.css").read_text("utf-8")
    css = re.sub(r"@font-face\{[^}]*\}", "", css)
    return (
        css
        + "\n"
        + """
.guide, .artifact-content, article.document {
  font-family: "Latin Modern", "STIX Two Text", Georgia, serif;
  font-size: var(--reading-size, 1.15rem); line-height: 1.7;
  font-kerning: normal; text-wrap: pretty;
}
.guide p, .artifact-content p, article.document p { max-width: 72ch; }
.guide h1, .guide h2, .guide h3, .guide h4,
.artifact-content h2, .artifact-content h3, article.document h2, article.document h3 {
  font-family: inherit; font-weight: 700; line-height: 1.25; text-wrap: balance;
}
.katex { font-size: 1.05em; text-align: initial; }
.katex math { font-size: inherit; }
.katex-display { margin: 0; }
.katex .base { white-space: nowrap; }
.tex-compiled { scrollbar-width: thin; }
.guide, .artifact-content, article.document { counter-reset: equation; }
.equation { margin: 1.4rem 0; counter-increment: equation; }
.equation-label { text-align: right; font: .8rem/1.4 system-ui, sans-serif; opacity: .75; }
.equation-label::after { content: " " counter(equation); }
.equation-source { font: .8rem/1.4 system-ui, sans-serif; margin-top: .4rem; }
.equation-source pre { white-space: pre-wrap; overflow-wrap: anywhere; padding: .65rem; }
.equation-source summary { cursor: pointer; }
@media print {
  .guide, .artifact-content, article.document { font-size: 11pt; line-height: 1.45; }
  h1, h2, h3, h4 { break-after: avoid; }
  pre, table, .math-display { break-inside: avoid; }
}
"""
    )


@lru_cache(maxsize=1)
def public_font_names() -> frozenset[str]:
    manifest = json.loads(
        files("ds60sqlpy").joinpath("assets/vendor/textbook/provenance.json").read_text("utf-8")
    )
    return frozenset(
        name for name in manifest["files"] if name.startswith("fonts/") and name.endswith(".woff2")
    )
