"""Convert explicitly authored LaTeX into safe native MathML, entirely offline."""

from __future__ import annotations

import html
import re
from functools import lru_cache
from xml.etree import ElementTree

from latex2mathml.converter import convert

# Inline delimiters are explicit. Dollar delimiters avoid common currency pairs
# and escaped dollars; authoring documentation recommends the unambiguous \(...\).
INLINE_MATH = re.compile(
    r"(?<!\\)\\\((?P<expression>.+?)\\\)"
    r"|(?<![\\$])\$(?![\s$])(?P<dollar>[^\n$]*?\S)(?<!\\)\$(?![\d$])"
)
MATH_NAMESPACE = "http://www.w3.org/1998/Math/MathML"
_ALLOWED_TAGS = frozenset(
    {
        "math",
        "mrow",
        "mi",
        "mn",
        "mo",
        "mtext",
        "mspace",
        "ms",
        "mfrac",
        "msqrt",
        "mroot",
        "mstyle",
        "merror",
        "mpadded",
        "mphantom",
        "mfenced",
        "menclose",
        "msub",
        "msup",
        "msubsup",
        "munder",
        "mover",
        "munderover",
        "mmultiscripts",
        "mprescripts",
        "none",
        "mtable",
        "mtr",
        "mtd",
        "mlabeledtr",
    }
)
_ALLOWED_ATTRIBUTES = frozenset(
    {
        "display",
        "mathvariant",
        "mathsize",
        "mathcolor",
        "mathbackground",
        "displaystyle",
        "scriptlevel",
        "stretchy",
        "fence",
        "form",
        "separator",
        "accent",
        "accentunder",
        "largeop",
        "movablelimits",
        "symmetric",
        "lspace",
        "rspace",
        "minsize",
        "maxsize",
        "linethickness",
        "bevelled",
        "width",
        "height",
        "depth",
        "voffset",
        "notation",
        "open",
        "close",
        "separators",
        "columnalign",
        "rowalign",
        "columnspacing",
        "rowspacing",
        "columnlines",
        "rowlines",
        "frame",
        "framespacing",
        "equalrows",
        "equalcolumns",
        "rowspan",
        "columnspan",
        "side",
        "minlabelspacing",
        "linebreak",
        "indentalign",
    }
)


def _validate_source(expression: str) -> None:
    if (
        not expression
        or len(expression) > 8192
        or re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", expression)
    ):
        raise ValueError("Mathematics expression length or characters are unsupported")
    depth = 0
    for match in re.finditer(r"\\.|[{}]", expression):
        if match.group() == "{":
            depth += 1
            if depth > 32:
                raise ValueError("Mathematics nesting limit exceeded")
        elif match.group() == "}":
            depth -= 1
            if depth < 0:
                raise ValueError("Unmatched mathematics group")
    if depth or re.search(r"(?<!\\)[_^]\s*[_^]", expression):
        raise ValueError("Unmatched group or repeated mathematics script")


def _safe_element(node: ElementTree.Element, depth: int = 0) -> str:
    """Serialize a strict MathML allowlist instead of trusting converter HTML."""

    tag = node.tag.removeprefix("{" + MATH_NAMESPACE + "}")
    if tag not in _ALLOWED_TAGS or depth > 96:
        raise ValueError("Unsupported MathML element")
    attrs = []
    for key, value in node.attrib.items():
        if key not in _ALLOWED_ATTRIBUTES or any(c in value for c in "<>\\\"'"):
            raise ValueError("Unsupported MathML attribute")
        if key in {"mathcolor", "mathbackground"} and not re.fullmatch(
            r"[a-zA-Z]+|#[0-9a-fA-F]{3,8}", value
        ):
            raise ValueError("Unsupported mathematics color")
        attrs.append(f' {key}="{html.escape(value, quote=True)}"')
    # Unrecognized commands are returned as literal identifiers by latex2mathml.
    # Retain their complete original expression as a visible source fallback.
    if tag in {"mi", "mo"} and re.search(r"\\[A-Za-z]+", node.text or ""):
        raise ValueError("Unsupported mathematics command")
    content = html.escape(node.text or "", quote=True)
    for child in node:
        content += _safe_element(child, depth + 1) + html.escape(child.tail or "", quote=True)
    return f"<{tag}{''.join(attrs)}>{content}</{tag}>"


@lru_cache(maxsize=2048)
def render_math(expression: str, *, display: bool = False) -> str:
    """Typeset LaTeX with its source annotation, or show escaped source on error.

    Generated MathML has no links, event handlers, style attributes, foreign
    elements, or active HTML. Unsupported input never vanishes from the lesson.
    """

    try:
        _validate_source(expression)
        # Upstream supports align* but leaves aligned as literal text. Both are
        # unnumbered aligned rows here; preserve the author's source annotation.
        prepared = expression.replace(r"\begin{aligned}", r"\begin{align*}").replace(
            r"\end{aligned}", r"\end{align*}"
        )
        converted = convert(prepared, display="block" if display else "inline")
        # The converter leaves text arguments unescaped. Escape their contents
        # before XML parsing, then validate every emitted element and attribute.
        converted = re.sub(
            r"(<mtext(?:\s[^>]*)?>)(.*?)(</mtext>)",
            lambda match: (
                match.group(1) + html.escape(html.unescape(match.group(2))) + match.group(3)
            ),
            converted,
            flags=re.DOTALL,
        )
        root = ElementTree.fromstring(converted)
        if root.tag != "{" + MATH_NAMESPACE + "}math":
            raise ValueError("Missing MathML root")
        body = "".join(_safe_element(child) for child in root)
    except Exception:
        # The library raises multiple parse exception classes. Every failure
        # has one bounded, visible, escaped fallback rather than broken markup.
        opening, closing = (r"\[", r"\]") if display else (r"\(", r"\)")
        return (
            '<code class="math-source">' + html.escape(opening + expression + closing) + "</code>"
        )
    mode = "block" if display else "inline"
    result = (
        f'<math xmlns="{MATH_NAMESPACE}" display="{mode}"><semantics>{body}'
        f'<annotation encoding="application/x-tex">'
        f"{html.escape(expression, quote=True)}</annotation>"
        "</semantics></math>"
    )
    return f'<div class="math-display">{result}</div>' if display else result
