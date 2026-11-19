"""Practice variants derived from each case's own code and recorded mutation runs.

Exercises 1 and 2 must not repeat the worked examples. Exercise 1 changes one input
literal of worked example 1 and asks for a prediction; exercise 2 shows worked
example 2 with a one-token regression to diagnose. Every Verify line names a check
from its own case and a one-token change that was executed and observed to make that
check fail. Observations live in variants.json; qualify_variants.py refreshes them in
the prepared worker image. Rendering reads those records and never executes code.
"""

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECORDS = HERE / "variants.json"

LANGUAGE = "c"
CHECK_NAME = {"go": "check", "c": "CHECK", "java": "assert", "js": "assert"}[LANGUAGE]

_STRINGS = {
    "go": r'"(?:\\.|[^"\\\n])*"|`[^`]*`|\'(?:\\.|[^\'\\\n])*\'',
    "c": r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'',
    "java": r'"""(?:.|\n)*?"""|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'',
    "js": r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'|`(?:\\.|\$\{(?:[^{}`]|\{[^{}]*\})*\}|[^`\\])*`',
}[LANGUAGE]
_OPS = (
    r">>>=|<<=|>>=|>>>|===|!==|\.\.\.|&\^=|<-|->|=>|::|\?\?=|\?\?|\?\.|&&=|\|\|=|&&|\|\||==|!=|<=|>=|"
    r"<<|>>|&\^|:=|\+\+|--|\+=|-=|\*=|/=|%=|&=|\|=|\^=|\*\*|[-+*/%&|^<>=!:;,.(){}\[\]~?@#]"
)
TOKEN = re.compile(
    r"(?P<space>\s+)|(?P<comment>//[^\n]*|/\*.*?\*/)|(?P<string>" + _STRINGS + r")"
    r"|(?P<number>\b0[xXbBoO][0-9a-fA-F_]+[uUlLn]*\b|\b\d[\d_]*(?:\.\d[\d_]*)?(?:[eE][+-]?\d+)?[uUlLfFdDn]*\b)"
    r"|(?P<ident>[A-Za-z_$][\w$]*)|(?P<op>" + _OPS + r")|(?P<other>.)",
    re.S,
)
KEYWORDS = {
    "go": {"return", "case", "go", "defer", "range", "else", "if", "for", "switch", "var", "const"},
    "c": {
        "return",
        "case",
        "sizeof",
        "else",
        "if",
        "while",
        "for",
        "switch",
        "do",
        "int",
        "char",
        "long",
        "short",
        "unsigned",
        "signed",
        "double",
        "float",
        "void",
        "const",
        "static",
        "struct",
        "enum",
        "union",
        "bool",
        "size_t",
        "uint8_t",
        "uint16_t",
        "uint32_t",
        "uint64_t",
        "int8_t",
        "int16_t",
        "int32_t",
        "int64_t",
        "volatile",
        "register",
    },
    "java": {
        "return",
        "case",
        "new",
        "throw",
        "else",
        "assert",
        "yield",
        "instanceof",
        "int",
        "long",
        "double",
        "float",
        "char",
        "byte",
        "short",
        "boolean",
        "var",
        "final",
    },
    "js": {
        "return",
        "case",
        "typeof",
        "void",
        "delete",
        "throw",
        "else",
        "yield",
        "await",
        "in",
        "of",
        "new",
        "instanceof",
        "const",
        "let",
        "var",
    },
}[LANGUAGE]
SWAPS = {
    "==": "!=",
    "!=": "==",
    "===": "!==",
    "!==": "===",
    "<": "<=",
    "<=": "<",
    ">": ">=",
    ">=": ">",
    "&&": "||",
    "||": "&&",
    "+": "-",
    "-": "+",
    "*": "+",
    "+=": "-=",
    "-=": "+=",
}
if LANGUAGE == "js":
    del SWAPS["=="], SWAPS["!="]


def tokens(code):
    """Significant tokens as (kind, text, start, end); comments and spaces removed."""
    found = []
    for match in TOKEN.finditer(code):
        kind = match.lastgroup
        if kind in {"space", "comment"}:
            continue
        found.append((kind, match.group(), match.start(), match.end()))
    return found


def _closing(items, start):
    depth = 0
    for index in range(start, len(items)):
        text = items[index][1]
        if text in "([{":
            depth += 1
        elif text in ")]}":
            depth -= 1
            if depth == 0:
                return index
    return len(items) - 1


def checks(code):
    """Assertion spans: (first token, last token, condition text, message or None)."""
    items = tokens(code)
    spans = []
    index = 0
    while index < len(items):
        kind, text, start, _ = items[index]
        if kind == "ident" and text == CHECK_NAME:
            if LANGUAGE == "java":
                depth, end, colon = 0, index, None
                for probe in range(index + 1, len(items)):
                    value = items[probe][1]
                    depth += value in "([{"
                    depth -= value in ")]}"
                    if depth == 0 and value == ":" and colon is None:
                        colon = probe
                    if depth == 0 and value == ";":
                        end = probe
                        break
                stop = colon if colon is not None else end
                condition = code[items[index + 1][2] : items[stop - 1][3]]
                message = None
                if colon is not None and items[colon + 1][0] == "string":
                    message = items[colon + 1][1]
                spans.append((index, end, condition.strip(), message))
                index = end + 1
                continue
            following = items[index + 1][1] if index + 1 < len(items) else ""
            if LANGUAGE == "js" and following == ".":
                open_index = index + 3
            elif following == "(":
                open_index = index + 1
            else:
                index += 1
                continue
            if open_index >= len(items) or items[open_index][1] != "(":
                index += 1
                continue
            close = _closing(items, open_index)
            inner = code[items[open_index][3] : items[close][2]]
            message = None
            if LANGUAGE in {"go"}:
                parts = _split_top(inner)
                condition = parts[0].strip()
                message = parts[-1].strip() if len(parts) > 1 else None
            elif LANGUAGE == "c":
                condition = inner.strip()
            else:
                condition = code[start : items[close][3]].strip()
            spans.append((index, close, condition, message))
            index = close + 1
            continue
        index += 1
    return spans


def _split_top(text):
    parts, depth, current, quote = [], 0, "", None
    index = 0
    while index < len(text):
        char = text[index]
        if quote:
            current += char
            if char == "\\" and quote != "`":
                current += text[index + 1 : index + 2]
                index += 1
            elif char == quote:
                quote = None
        elif char in "\"'`":
            quote = char
            current += char
        elif char in "([{":
            depth += 1
            current += char
        elif char in ")]}":
            depth -= 1
            current += char
        elif char == "," and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += char
        index += 1
    parts.append(current)
    return parts


def _binary(items, index):
    if index == 0:
        return False
    kind, text, _, _ = items[index - 1]
    if kind == "ident":
        return text not in KEYWORDS
    return kind in {"number", "string"} or text in {")", "]"}


def _generic_angle(items, index):
    if LANGUAGE not in {"java", "js"}:
        return False
    text = items[index][1]
    if text == "<":
        previous = items[index - 1][1] if index else ""
        nxt = items[index + 1][1] if index + 1 < len(items) else ""
        return previous[:1].isupper() or nxt[:1].isupper() or nxt in {"?", ">"}
    if text == ">":
        previous = items[index - 1][1] if index else ""
        return previous[:1].isupper() or previous in {">", "?", "]", "<"}
    return False


COMPARISONS = {"==", "!=", "===", "!==", "<", "<=", ">", ">="}
CONSTANTS = {"true", "false", "nil", "NULL", "null", "undefined", "None"}


def _claims(items, first, last):
    """Token indexes that state a check's claim rather than compute its value.

    The claim is the top-level comparison or logical structure, a leading negation and
    a literal expected operand. Everything else inside the check is the computation
    under test, so editing it is a genuine regression rather than an edit of the claim.
    """
    claim = set()
    if LANGUAGE == "java":
        start, stop = first + 1, last
        for probe in range(first + 1, last):
            if items[probe][1] == ":":
                stop = probe
                break
    else:
        opening = first + 1 if items[first + 1][1] == "(" else first + 3
        start, stop = opening + 1, last
    if LANGUAGE == "js" and items[first + 1][1] == "." and items[first + 2][1] not in {"ok"}:
        depth = 0
        for probe in range(start, stop):
            text = items[probe][1]
            depth += text in "([{"
            depth -= text in ")]}"
            if depth == 0 and text == ",":
                claim.update(range(probe, stop))
                break
        return claim
    if LANGUAGE == "go":
        depth = 0
        for probe in range(start, stop):
            text = items[probe][1]
            depth += text in "([{"
            depth -= text in ")]}"
            if depth == 0 and text == ",":
                stop = probe
    clauses, depth, current = [], 0, []
    for probe in range(start, stop):
        text = items[probe][1]
        if text in ")]}":
            depth -= 1
        level = depth
        if text in "([{":
            depth += 1
        if level == 0 and text in {"&&", "||"}:
            claim.add(probe)
            clauses.append(current)
            current = []
        else:
            current.append((probe, level))
    clauses.append(current)
    for clause in clauses:
        if not clause:
            continue
        if items[clause[0][0]][1] == "!":
            claim.add(clause[0][0])
        operator = next((i for i, d in clause if d == 0 and items[i][1] in COMPARISONS), None)
        if operator is None:
            continue
        claim.add(operator)
        right = [i for i, _ in clause if i > operator]
        literal = [i for i in right if items[i][1] not in {"-", "+", "(", ")"}]
        if len(literal) == 1 and (
            items[literal[0]][0] in {"number", "string"} or items[literal[0]][1] in CONSTANTS
        ):
            claim.update(right)
    return claim


INPUT_KINDS = ("literal", "fixture", "boolean", "text")
LOGIC_KINDS = ("operator", "negation", "verb")


def _string_digits(text):
    """Digit runs inside a string literal that are not part of an escape sequence."""
    for match in re.finditer(r"\d+", text):
        before = text[max(0, match.start() - 6) : match.start()]
        if re.search(r"\\(?:u\{?[0-9a-fA-F]{0,5}|x[0-9a-fA-F]?|[0-7]{0,2})$", before):
            continue
        yield match.start(), match.end(), match.group()


def candidates(code):
    """One-token mutations in source order.

    Each candidate is a dict with token, start/end offsets inside the token, before,
    after, kind and inside (whether it edits a check's own expression).
    """
    items = tokens(code)
    inside = {}
    names = set()
    for first, last, _, _ in checks(code):
        names.add(first)
        for index in _claims(items, first, last):
            inside[index] = True
    found = []
    for index, (kind, text, _, _) in enumerate(items):
        within = inside.get(index, False)
        if index in names:
            continue
        if kind == "op" and text in SWAPS:
            if text in {"+", "-", "*"} and not _binary(items, index):
                continue
            if _generic_angle(items, index):
                continue
            found.append(
                {
                    "token": index,
                    "start": 0,
                    "end": len(text),
                    "before": text,
                    "after": SWAPS[text],
                    "kind": "operator",
                    "inside": within,
                }
            )
        elif (
            kind == "op"
            and text == "!"
            and index + 1 < len(items)
            and (items[index + 1][0] == "ident" or items[index + 1][1] == "(")
        ):
            found.append(
                {
                    "token": index,
                    "start": 0,
                    "end": 1,
                    "before": "!",
                    "after": "",
                    "kind": "negation",
                    "inside": within,
                }
            )
        elif kind == "number" and re.fullmatch(r"\d+", text):
            previous = items[index - 1][1] if index else ""
            if previous in {".", "#"}:
                continue
            found.append(
                {
                    "token": index,
                    "start": 0,
                    "end": len(text),
                    "before": text,
                    "after": str(int(text) + 1),
                    "kind": "literal",
                    "inside": within,
                }
            )
        elif kind == "ident" and text in {"true", "false"}:
            found.append(
                {
                    "token": index,
                    "start": 0,
                    "end": len(text),
                    "before": text,
                    "after": "false" if text == "true" else "true",
                    "kind": "boolean",
                    "inside": within,
                }
            )
        elif kind == "string":
            if _is_message(items, index):
                continue  # a check's message label is not part of the claim
            if LANGUAGE == "go" and not within:
                for match in re.finditer(r"%w", text):
                    found.append(
                        {
                            "token": index,
                            "start": match.start(),
                            "end": match.end(),
                            "before": "%w",
                            "after": "%v",
                            "kind": "verb",
                            "inside": False,
                        }
                    )
            digits = list(_string_digits(text))[:3]
            for start, end, value in digits:
                found.append(
                    {
                        "token": index,
                        "start": start,
                        "end": end,
                        "before": value,
                        "after": str(int(value) + 1),
                        "kind": "fixture",
                        "inside": within,
                    }
                )
            quote = text[-1]
            body = text[1:-1] if not text.startswith('"""') else ""
            if body and "\n" not in text and len(text) <= 60 and quote in "\"'":
                found.append(
                    {
                        "token": index,
                        "start": len(text) - 1,
                        "end": len(text) - 1,
                        "before": "",
                        "after": "!",
                        "kind": "text",
                        "inside": within,
                    }
                )
    return found


def _is_message(items, index):
    """A Go check label or a Java assertion message string."""
    previous = items[index - 1][1] if index else ""
    following = items[index + 1][1] if index + 1 < len(items) else ""
    if LANGUAGE == "go" and previous == "," and following == ")":
        return True
    return LANGUAGE == "java" and previous == ":" and following == ";"


def apply(code, candidate):
    items = tokens(code)
    _, text, start, _ = items[candidate["token"]]
    edited = text[: candidate["start"]] + candidate["after"] + text[candidate["end"] :]
    return code[:start] + edited + code[start + len(text) :]


def ordered(code, case_index):
    """Worked example 1 prefers an input change; other cases prefer a logic regression."""
    found = candidates(code)
    rank = INPUT_KINDS + LOGIC_KINDS if case_index == 0 else LOGIC_KINDS + INPUT_KINDS
    outside = [c for kind in rank for c in found if c["kind"] == kind and not c["inside"]]
    within = [c for kind in rank for c in found if c["kind"] == kind and c["inside"]]
    return outside + within


def digest(code):
    return hashlib.sha256(code.encode("utf-8", "surrogatepass")).hexdigest()[:16]


def load_records():
    return json.loads(RECORDS.read_text(encoding="utf-8")) if RECORDS.exists() else {}


def _significant(code):
    return [t for t in tokens(code) if t[1] != ";"]


def locate(raw, formatted, candidate):
    """Original and edited excerpts of the formatted line containing a raw token."""
    raw_items = tokens(raw)
    target = raw_items[candidate["token"]]
    position = sum(1 for t in raw_items[: candidate["token"]] if t[1] != ";")
    shown = _significant(formatted)
    source = formatted
    if position < len(shown) and shown[position][1] == target[1]:
        start = shown[position][2]
    else:
        source, start = raw, target[2]
    token_text = target[1]
    edit_start = start + candidate["start"]
    edit_end = start + candidate["end"]
    line_start = source.rfind("\n", 0, start) + 1
    line_end = source.find("\n", start)
    line_end = len(source) if line_end < 0 else line_end
    if target[0] == "string" and candidate["kind"] in {"fixture", "text"} and len(token_text) > 40:
        left = edit_start
        while left > start + 1 and source[left - 1] not in ",{[ \t\n":
            left -= 1
        right = edit_end
        while right < start + len(token_text) - 1 and source[right] not in ",}] \t\n":
            right += 1
        lo, hi = left, right
    elif line_end - line_start <= 100:
        lo, hi = line_start, line_end
    else:
        lo, hi = _clause(source, line_start, line_end, start)
    original = source[lo:hi].strip()
    edited = (source[lo:edit_start] + candidate["after"] + source[edit_end:hi]).strip()
    return original, edited


BOUNDARIES = {"&&", "||", ",", ";", "{", "}", ":=", "=", "return"}


def _clause(source, line_start, line_end, start):
    """The smallest boolean or argument clause around a token on a long line."""
    items = [
        t
        for t in TOKEN.finditer(source, line_start, line_end)
        if t.lastgroup not in {"space", "comment"}
    ]
    here = next(i for i, t in enumerate(items) if t.start() <= start < t.end())
    left, depth = here, 0
    while left > 0:
        text = items[left - 1].group()
        if text in ")]":
            depth += 1
        elif text in "([":
            if depth == 0:
                break
            depth -= 1
        elif depth == 0 and text in BOUNDARIES:
            break
        left -= 1
    right, depth = here, 0
    while right < len(items) - 1:
        text = items[right + 1].group()
        if text in "([":
            depth += 1
        elif text in ")]":
            if depth == 0:
                break
            depth -= 1
        elif depth == 0 and text in BOUNDARIES:
            break
        right += 1
    if items[right].end() - items[left].start() < 30 and (left > 0 or right < len(items) - 1):
        while left > 0 and items[left - 1].group() not in "(":
            left -= 1
        if left > 0:
            left -= 1
            while left > 0 and (
                items[left - 1].lastgroup == "ident" or items[left - 1].group() == "."
            ):
                left -= 1
        depth = 0
        for probe in range(left, len(items)):
            text = items[probe].group()
            depth += text in "(["
            depth -= text in ")]"
            if depth == 0 and probe >= right:
                right = probe
                break
    return items[left].start(), items[right].end()


def code_span(text):
    """Inline Markdown code span that survives backticks in the content."""
    text = text.strip()

    def join(match):
        before = text[match.start() - 1] if match.start() else ""
        after = text[match.end()] if match.end() < len(text) else ""
        if after in ")]":
            return ""  # also drops a formatter's trailing comma
        if after == "}":
            return " "
        if match.group(1):
            return ", "
        return "" if after == "." or before in "([" else " "

    text = re.sub(r"(,?)[ \t]*\n\s*", join, text)
    text = " ".join(text.split())
    fence = "`"
    while fence in text:
        fence += "`"
    padding = " " if text.startswith("`") or text.endswith("`") else ""
    return fence + padding + text + padding + fence


def variant(records, ident, case_index, raw, formatted):
    """The recorded qualified mutation for one case, with display text, or None."""
    entry = records.get(ident, {}).get(str(case_index + 1))
    if not entry:
        return None
    if entry["sha"] != digest(raw):
        raise ValueError(
            f"{ident} case {case_index + 1} changed after its variant was qualified; "
            "run qualify_variants.py with the prepared worker image."
        )
    if entry.get("outcome") != "killed":
        return None
    line, broken = locate(raw, formatted, entry)
    spans = checks(formatted)
    condition = spans[entry["check"]][2] if entry["check"] < len(spans) else None
    message = spans[entry["check"]][3] if entry["check"] < len(spans) else None
    # A computation token inside a check statement edits the check, not the code under test.
    in_check = entry["inside"] or any(
        first <= entry["token"] <= last for first, last, _, _ in checks(raw)
    )
    return {
        **entry,
        "line": line,
        "broken": broken,
        "condition": condition,
        "message": message,
        "in_check": in_check,
    }
