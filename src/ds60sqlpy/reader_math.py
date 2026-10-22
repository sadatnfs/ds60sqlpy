"""Render a bounded inline mathematics subset without network dependencies."""

from __future__ import annotations

import html
import re

INLINE_MATH = re.compile(r"\\\((?P<expression>.*?)\\\)")
_SYMBOLS = {
    "mid": "|",
    "times": "×",
    "cdot": "·",
    "le": "≤",
    "leq": "≤",
    "ge": "≥",
    "geq": "≥",
    "ne": "≠",
    "neq": "≠",
    "in": "∈",
    "approx": "≈",
    "sum": "∑",
    "infty": "∞",
    "to": "→",
    "alpha": "α",
    "beta": "β",
    "gamma": "γ",
    "delta": "δ",
    "epsilon": "ε",
    "theta": "θ",
    "lambda": "λ",
    "mu": "μ",
    "sigma": "σ",
    "pi": "π",
}
_GREEK_IDENTIFIERS = {
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "theta",
    "lambda",
    "mu",
    "sigma",
    "pi",
}


class _Parser:
    def __init__(self, source: str) -> None:
        self.source = source
        self.position = 0

    def _space(self) -> None:
        while self.position < len(self.source) and self.source[self.position].isspace():
            self.position += 1

    def row(self, depth: int = 0, *, grouped: bool = False) -> str:
        if depth > 24:
            raise ValueError("Mathematics nesting limit exceeded")
        parts = []
        while True:
            self._space()
            if self.position == len(self.source):
                if grouped:
                    raise ValueError("Unclosed mathematics group")
                break
            if self.source[self.position] == "}":
                if not grouped:
                    raise ValueError("Unexpected mathematics group end")
                self.position += 1
                break
            base = self.atom(depth + 1)
            scripts: dict[str, str] = {}
            self._space()
            while self.position < len(self.source) and self.source[self.position] in "^_":
                marker = self.source[self.position]
                self.position += 1
                if marker in scripts:
                    raise ValueError("Repeated mathematics script")
                scripts[marker] = self.atom(depth + 1)
                self._space()
            if "^" in scripts and "_" in scripts:
                base = f"<msubsup>{base}{scripts['_']}{scripts['^']}</msubsup>"
            elif scripts:
                tag = "msup" if "^" in scripts else "msub"
                base = f"<{tag}>{base}{next(iter(scripts.values()))}</{tag}>"
            parts.append(base)
        return "<mrow>" + "".join(parts) + "</mrow>"

    def atom(self, depth: int) -> str:
        if depth > 24:
            raise ValueError("Mathematics nesting limit exceeded")
        self._space()
        if self.position >= len(self.source):
            raise ValueError("Missing mathematics argument")
        character = self.source[self.position]
        self.position += 1
        if character == "{":
            return self.row(depth, grouped=True)
        if character == "\\":
            command = re.match(r"[a-zA-Z]+", self.source[self.position :])
            if command is None:
                raise ValueError("Unsupported mathematics command")
            name = command.group()
            self.position += len(name)
            if name == "text":
                self._space()
                group = re.match(r"\{([^{}]*)\}", self.source[self.position :])
                if group is None:
                    raise ValueError("Unsupported mathematics text group")
                self.position += len(group.group())
                return f"<mtext>{html.escape(group.group(1))}</mtext>"
            if name == "frac":
                numerator, denominator = self.atom(depth + 1), self.atom(depth + 1)
                return f"<mfrac>{numerator}{denominator}</mfrac>"
            if name == "sqrt":
                return f"<msqrt>{self.atom(depth + 1)}</msqrt>"
            if name not in _SYMBOLS:
                raise ValueError("Unsupported mathematics command")
            tag = "mi" if name in _GREEK_IDENTIFIERS else "mo"
            return f"<{tag}>{_SYMBOLS[name]}</{tag}>"
        if character.isdigit():
            number = re.match(r"\d+(?:\.\d+)?", self.source[self.position - 1 :])
            assert number is not None
            self.position += len(number.group()) - 1
            return f"<mn>{number.group()}</mn>"
        if character.isalpha():
            return f"<mi>{html.escape(character)}</mi>"
        if character in "+-=(),[]|<>/!:;":
            return f"<mo>{html.escape(character)}</mo>"
        raise ValueError("Unsupported mathematics token")


def render_math(expression: str) -> str:
    """Render supported notation as MathML, preserving unknown source visibly."""

    try:
        if not expression or len(expression) > 2048:
            raise ValueError("Mathematics expression length is unsupported")
        body = _Parser(expression).row()
    except ValueError:
        return '<code class="math-source">' + html.escape(r"\(" + expression + r"\)") + "</code>"
    original = html.escape(expression, quote=True)
    return (
        '<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">'
        f'<semantics>{body}<annotation encoding="application/x-tex">{original}</annotation>'
        "</semantics></math>"
    )
