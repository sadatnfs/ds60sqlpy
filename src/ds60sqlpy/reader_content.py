"""Offline syntax rendering shared by the browser classroom and static readers.

Pygments supplies lexers, not trusted HTML. Only fixed token classes and escaped
source text reach the document. Source reconstruction is checked before output.
"""

from __future__ import annotations

import html
import re
from functools import lru_cache

from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.token import Token, _TokenType, is_token_subtype
from pygments.util import ClassNotFound

_ALIASES = {
    "py": "python",
    "python3": "python",
    "ipython": "python",
    "postgresql": "postgres",
    "psql": "postgres",
    "c++": "cpp",
    "cxx": "cpp",
    "js": "javascript",
    "ts": "typescript",
    "sh": "bash",
    "shell": "bash",
    "shell-session": "console",
    "yml": "yaml",
    "ps1": "powershell",
    "pwsh": "powershell",
    "docker": "dockerfile",
    "md": "markdown",
    "text": "text",
    "plain": "text",
    "plaintext": "text",
    "": "text",
}

_BUILTIN_ALIASES = frozenset(
    alias for _name, aliases, _files, _mime in get_all_lexers(plugins=False) for alias in aliases
)


def normalize_language(language: str) -> str:
    """Return a bounded class-safe lexer alias, retaining unknown safe names."""

    value = language.strip().lower()
    if not re.fullmatch(r"[a-z0-9_+.-]{0,64}", value):
        return "text"
    return _ALIASES.get(value, value)


def _token_class(token: _TokenType) -> str:
    for family, name in (
        (Token.Comment, "comment"),
        (Token.Keyword, "keyword"),
        (Token.Literal.String, "string"),
        (Token.Literal.Number, "number"),
        (Token.Name.Function, "function"),
        (Token.Name.Class, "class"),
        (Token.Name.Builtin, "builtin"),
        (Token.Name.Tag, "tag"),
        (Token.Name.Attribute, "attribute"),
        (Token.Name.Decorator, "decorator"),
        (Token.Operator, "operator"),
        (Token.Punctuation, "punctuation"),
        (Token.Generic, "generic"),
    ):
        if is_token_subtype(token, family):
            return name
    return ""


@lru_cache(maxsize=256)
def highlight_source(source: str, language: str = "text") -> str:
    """Return copy-faithful escaped HTML tokens; unknown lexers stay readable.

    Large examples retain every character without invoking a regex lexer. No
    filename, plugin path, or source content is ever loaded or executed as code.
    """

    escaped = html.escape(source, quote=True)
    if len(source) > 200_000:
        return escaped
    alias = normalize_language(language)
    if alias == "text" or alias not in _BUILTIN_ALIASES:
        return escaped
    try:
        lexer = get_lexer_by_name(alias, stripnl=False, ensurenl=False, tabsize=0)
    except ClassNotFound:
        return escaped
    try:
        tokens = list(lexer.get_tokens_unprocessed(source))
    except Exception:
        # An unfamiliar or malformed snippet remains readable if its lexer fails.
        return escaped
    if "".join(value for _offset, _kind, value in tokens) != source:
        return escaped
    output: list[str] = []
    for _offset, kind, value in tokens:
        token_class = _token_class(kind)
        # Close spans at every newline so source line numbers remain valid HTML.
        chunks = value.split("\n")
        output.append(
            "\n".join(
                f'<span class="syntax-{token_class}">{html.escape(chunk, quote=True)}</span>'
                if token_class and chunk
                else html.escape(chunk, quote=True)
                for chunk in chunks
            )
        )
    return "".join(output)


def render_code_block(source: str, language: str = "text", *, line_numbers: bool = False) -> str:
    """Render a source block without inserting line numbers into copied text."""

    language = normalize_language(language)
    normalized = source.replace("\r\n", "\n").replace("\r", "\n")
    content = highlight_source(normalized, language)
    if line_numbers:
        content = "\n".join(
            f'<span class="source-line">{line}</span>' for line in content.split("\n")
        )
        return f'<pre class="source-code language-{language}"><code>{content}</code></pre>'
    return f'<pre class="highlighted-code"><code class="language-{language}">{content}</code></pre>'


def rich_content_styles() -> str:
    """Return self-contained CSS for MathML and syntax tokens on every surface."""

    return """
/* Shared offline reader rendering. Code retains a dark surface in both themes. */
pre.highlighted-code, pre.source-code {
  color: var(--code-text, #e5edf8); background: var(--code-bg, #111d32);
  border: 1px solid #35435c; border-radius: .7rem; overflow-x: auto;
  padding: 1rem 1.1rem; font-size: .9rem; line-height: 1.65; white-space: pre;
  tab-size: 4; text-align: left; font-weight: 400;
}
pre.highlighted-code code, pre.source-code code {
  font-family: "Cascadia Code", "SFMono-Regular", Consolas, monospace;
  font-weight: 400; padding: 0; color: inherit; background: transparent;
  font-size: inherit; line-height: inherit; white-space: inherit;
}
pre.source-code { padding: 1rem 0; }
pre.source-code code { display: block; counter-reset: source-line; white-space: normal; }
pre.source-code code > .source-line {
  display: block; white-space: pre; min-height: 1.65em;
  padding: 0 1rem 0 4.2rem; position: relative;
}
pre.source-code code > .source-line::before {
  counter-increment: source-line; content: counter(source-line);
  position: absolute; float: none; margin-left: 0; left: .75rem; width: 2.5rem; text-align: right;
  color: #97a7be; user-select: none; pointer-events: none;
}
pre .syntax-keyword { color: #cbb5ff; font-weight: 650; }
pre .syntax-string { color: #a9e6b1; }
pre .syntax-number { color: #ffd39b; }
pre .syntax-comment { color: #a4b3ca; font-style: italic; }
pre .syntax-function, pre .syntax-builtin { color: #91d8fc; }
pre .syntax-class, pre .syntax-tag { color: #f8b6d5; }
pre .syntax-attribute, pre .syntax-decorator { color: #f7df96; }
pre .syntax-operator { color: #b6e4f5; }
pre .syntax-punctuation { color: #c5cfe0; }
pre .syntax-generic { color: #e5edf8; }
math { color: inherit; font-size: 1.08em; font-weight: normal; }
math[display="inline"] { margin-inline: .12em; }
.math-display {
  max-width: 100%; overflow-x: auto; overflow-y: hidden;
  margin: 1.3rem 0; padding: .7rem .3rem; color: inherit;
}
.math-display math { margin: 0 auto; min-width: min-content; }
code.math-source { white-space: pre-wrap; overflow-wrap: anywhere; }
@media print {
  pre.highlighted-code, pre.source-code { background: #fff; color: #172033; border-color: #777; }
  pre [class^="syntax-"] { color: #172033; }
  .math-display { overflow: visible; }
}
""".strip()
