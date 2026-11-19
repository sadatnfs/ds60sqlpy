"""Plain-language explanations of failed classroom runs for beginners.

An explanation is derived only from the submitted source text and the bounded
runner output. It performs no I/O and never executes code. A line or column is
reported only when the runner's file naming maps it to the learner's editor
text with certainty; otherwise it is ``None``.
"""

from __future__ import annotations

import ast
import builtins
import difflib
import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from ds60sqlpy.worker_operations import PROFILES

KINDS = (
    "syntax",
    "compile",
    "runtime",
    "assertion",
    "timeout",
    "output-limit",
    "database",
    "unknown",
)
TITLE_LIMIT = 160
HINT_LIMIT = 240
RAW_LIMIT = 300
GENERIC_TITLE = "The program stopped with an error. The last error line is shown below."
GENERIC_HINT = (
    "Read the error line below, change one thing near the place it mentions, then run again."
)

# Placeholders keep titles consistent with the final, verified line number.
_AT = "\x00at\x00"  # " on line N" or ""
_LN = "\x00ln\x00"  # "line N" or "the line"
_LNC = "\x00lnc\x00"  # "Line N" or "The code"

_FAMILIES = {
    "python": "python",
    "sql": "sql",
    "stan": "stan",
    "julia": "julia",
    "r": "r",
    "c": "c",
    "cpp": "c",
    "go": "go",
    "csharp": "csharp",
    "rust": "rust",
    "swift": "swift",
    "java": "jvm",
    "scala": "jvm",
    "javascript": "node",
    "typescript": "typescript",
    "php": "php",
}
# Legacy pads execute a randomly named snapshot of the saved practice file. The
# in-lab Python runner prints that snapshot as main.py in learner tracebacks.
_LEGACY = {"python": ("python", "main.py"), "sql": ("sql", "lesson.sql")}
_SNAPSHOT = re.compile(r"(?:/[\w.@+-]+)*/\.submission-[A-Za-z0-9_]+\.(py|sql)\b")
_JOB_DIRECTORY = re.compile(r"(?:file://)?(?:/[\w.@+-]+)*/job-[A-Za-z0-9_]+/")
_CSPROJ = re.compile(r"\s*\[(?:/[\w.@+-]+)*/Lesson\.csproj\]\s*$")
_NOISE = re.compile(
    r"^\s*(?:Picked up JAVA_TOOL_OPTIONS:|WARNING: Using incubator modules|Using Spark's default"
    r"|\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} (?:INFO|WARN|DEBUG)\b|Execution halted$|Node\.js v\d"
    r"|make: \*\*\*|Time Elapsed|Build (?:FAILED|succeeded)\.|\d+ (?:Warning|Error)\(s\)"
    r"|error: aborting due to|For more information about this error|note: run with `RUST_BACKTRACE"
    r"|\d+ errors?$|\d+ warnings?$|Errors parsing |No syntax errors detected"
    r"|An issue was encountered verifying workloads|Calls: |\[output truncated"
    r"|\[\.\.\. output truncated|Suggestion: |Stack trace:|#\d+ \{main\}|thrown in )"
)
_ERRORISH = re.compile(r"error|exception|fatal|panic|failed|abort|traceback", re.IGNORECASE)
_SQL_KEYWORDS = (
    "SELECT",
    "FROM",
    "WHERE",
    "GROUP",
    "ORDER",
    "HAVING",
    "LIMIT",
    "OFFSET",
    "JOIN",
    "INNER",
    "LEFT",
    "RIGHT",
    "OUTER",
    "INSERT",
    "INTO",
    "VALUES",
    "UPDATE",
    "DELETE",
    "CREATE",
    "TABLE",
    "DISTINCT",
    "UNION",
    "CASE",
    "WHEN",
    "THEN",
    "ELSE",
    "WITH",
    "BETWEEN",
    "LIKE",
    "NULL",
)


@dataclass(frozen=True)
class _Context:
    family: str
    filename: str
    learner: re.Pattern[str]
    source_lines: tuple[str, ...] | None

    def is_learner(self, path: str) -> bool:
        return bool(path) and self.learner.search(path.removeprefix("file://")) is not None

    def source_line(self, line: int | None) -> str | None:
        if line is None or self.source_lines is None or not 1 <= line <= len(self.source_lines):
            return None
        return self.source_lines[line - 1]


@dataclass(frozen=True)
class _Finding:
    kind: str
    title: str
    hint: str
    raw: str = ""
    line: int | None = None
    column: int | None = None


_CHECKS_FAILED = _Finding(
    "assertion",
    "The program ran, but the lesson's checks did not pass.",
    "Open the check results to see which check failed, then compare that part with the "
    "lesson's instructions.",
)


def explain_run(
    profile: str,
    output: str,
    returncode: int | None,
    *,
    stopped: str | None = None,
    status: str | None = None,
    source: str = "",
) -> dict[str, object] | None:
    """Explain one failed run, or return ``None`` for success or nothing useful to say."""

    return _explain(profile, output, returncode, stopped, status, source, None)


def explain_pad_run(
    language: str, result: Mapping[str, object], source: str
) -> dict[str, object] | None:
    """Explain a legacy Python/SQL pad result, preferring the runner's verified error line."""

    output = result.get("output")
    returncode = result.get("returncode")
    stopped = result.get("stopped")
    error_line = result.get("error_line")
    return _explain(
        language,
        output if isinstance(output, str) else "",
        returncode if type(returncode) is int else None,
        stopped if isinstance(stopped, str) else None,
        None,
        source,
        error_line if type(error_line) is int and error_line > 0 else None,
    )


def explain_failed_checks() -> dict[str, object]:
    """Explain a run whose only recognizable failure is the lesson verifier's checks."""

    return _render(_CHECKS_FAILED, _context("", ""), None)


def _explain(
    profile: str,
    output: object,
    returncode: object,
    stopped: str | None,
    status: str | None,
    source: str,
    known_line: int | None,
) -> dict[str, object] | None:
    text = output if isinstance(output, str) else ""
    code = returncode if type(returncode) is int else None
    timed_out = stopped == "time limit" or status == "timed_out"
    output_limit = stopped == "output limit"
    if not timed_out and not output_limit:
        if status is not None and status != "failed":
            return None
        if status is None and code in (0, None):
            return None
    context = _context(profile, source if isinstance(source, str) else "")
    lines = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "").split("\n")
    finding: _Finding | None
    if timed_out:
        finding = _Finding(
            "timeout",
            "The program did not finish within the time limit, so the classroom stopped it.",
            "Look for a loop whose condition never becomes false. If the work is just slow, "
            "use less data or choose a longer run limit.",
        )
    elif output_limit:
        finding = _Finding(
            "output-limit",
            "The program printed more than the classroom's output limit (about 128 KB), "
            "so the run was stopped.",
            "Print less, for example only the first few rows or a short summary, then run again.",
        )
    else:
        finding = _PARSERS.get(context.family, _no_parser)(lines, context, text)
        finding = finding or _scratch_limit(lines) or _signal(code)
        if finding is None and status == "failed" and code == 0:
            finding = _CHECKS_FAILED
        if finding is None and code is None:
            return None  # No exit status: the job detail describes the infrastructure.
        if finding is None:
            raw = _last_error_line(lines)
            if raw:
                finding = _Finding("unknown", GENERIC_TITLE, GENERIC_HINT, raw)
            elif code not in (None, 0):
                finding = _Finding(
                    "unknown",
                    f"The program ended with exit code {code} instead of 0, "
                    "which means it reported a failure.",
                    "Look for a call that ends the program early, such as `exit(1)`, "
                    "or read the output below for clues.",
                )
    if finding is None:
        return None
    return _render(finding, context, known_line)


def _context(profile: str, source: str) -> _Context:
    if profile in _LEGACY:
        family, filename = _LEGACY[profile]
        suffix = filename.rsplit(".", 1)[1]
        learner = re.compile(
            rf"(?:^|/)(?:\.submission-[A-Za-z0-9_]+|practice)\.{suffix}$|^{re.escape(filename)}$"
        )
    else:
        spec = PROFILES.get(profile)
        language = spec.language if spec is not None else ""
        filename = spec.filename if spec is not None else ""
        family = "dbt" if profile == "dbt-duckdb" else _FAMILIES.get(language, "")
        learner = re.compile(
            r"^(?:(?:~|\.|program)/|(?:/[\w.@+-]+)*/job-[A-Za-z0-9_]+/)?"
            + (re.escape(filename) if filename else r"(?!)")
            + "$"
        )
    lines = tuple(source.split("\n")) if source else None
    return _Context(family, filename, learner, lines)


def _render(finding: _Finding, context: _Context, known_line: int | None) -> dict[str, object]:
    line, column = finding.line, finding.column
    if known_line is not None:
        if line != known_line:
            column = None
        line = known_line
    if line is not None and context.source_lines is not None:
        text = context.source_line(line)
        if text is None:
            line = column = None
        elif column is not None and (
            column > len(text) + 1 or "\t" in text[: column - 1] or not text[: column - 1].isascii()
        ):
            column = None
    if line is None or (column is not None and column < 1):
        column = None

    def fill(template: str) -> str:
        return (
            template.replace(_AT, f" on line {line}" if line else "")
            .replace(_LNC, f"Line {line}" if line else "The code")
            .replace(_LN, f"line {line}" if line else "the line")
        )

    return {
        "kind": finding.kind,
        "title": _cap(fill(finding.title), TITLE_LIMIT),
        "line": line,
        "column": column,
        "hint": _cap(fill(finding.hint), HINT_LIMIT),
        "raw": _shorten(finding.raw, context),
    }


def _cap(text: str, limit: int, *, collapse: bool = True) -> str:
    text = text.replace("\u2014", "-")
    text = " ".join(text.split()) if collapse else text.strip()
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def _shorten(text: str, context: _Context) -> str:
    text = _CSPROJ.sub("", text)
    text = _SNAPSHOT.sub(lambda m: "main.py" if m.group(1) == "py" else "lesson.sql", text)
    text = _JOB_DIRECTORY.sub("", text)
    if context.filename:
        text = re.sub(
            r"(?<![\w/.])(?:~|program)/(?=" + re.escape(context.filename) + r"\b)", "", text
        )
    return _cap(text, RAW_LIMIT, collapse=False)


def _code(token: str, limit: int = 40) -> str:
    """Quote a token from tool output as inline code with a bounded length."""
    token = " ".join(token.replace("`", "'").replace("\x00", "").split())
    if len(token) > limit:
        token = token[: limit - 3] + "..."
    return f"`{token}`"


def _an(token: str) -> str:
    """Inline code with its indefinite article, for example "an `int`"."""
    code = _code(token)
    return ("an " if code[1:2].lower() in tuple("aeiou") else "a ") + code


def _an_cap(token: str) -> str:
    text = _an(token)
    return text[0].upper() + text[1:]


def _last_error_line(lines: list[str]) -> str:
    for text in reversed(lines):
        if text.strip() and not _NOISE.match(text) and _ERRORISH.search(text):
            return text.strip()
    return ""


def _no_parser(lines: list[str], context: _Context, output: str) -> _Finding | None:
    return None


def _scratch_limit(lines: list[str]) -> _Finding | None:
    for text in lines:
        if text.startswith("Job exceeded its") and "scratch allowance" in text:
            return _Finding(
                "output-limit",
                "The program wrote more files or data than its 32 MiB, 1024-file work space "
                "allows.",
                "Write fewer or smaller files, and delete temporary files you no longer need.",
                text,
            )
    return None


def _signal(code: int | None) -> _Finding | None:
    if code in (-9, 137):
        return _Finding(
            "runtime",
            "The system stopped the program, which usually means it ran out of memory.",
            "Use less memory, for example smaller arrays or fewer rows, then run again.",
        )
    if code in (-11, 139, -7, 135):
        return _Finding(
            "runtime",
            "The program crashed with a segmentation fault, meaning it used memory it does "
            "not own.",
            "Check pointers and positions, for example a `NULL` pointer or a position past "
            "the end of an array.",
        )
    if code in (-8, 136):
        return _Finding(
            "runtime",
            "The program stopped because of an arithmetic error, such as dividing a whole "
            "number by zero.",
            "Check every division and make sure the number you divide by cannot be 0.",
        )
    if code in (-6, 134):
        return _Finding(
            "runtime",
            "The program stopped itself with an abort signal, usually after a failed check "
            "or an unhandled error.",
            "Look for a failed `assert` or an error message in the output, then fix that "
            "condition.",
        )
    if code in (-4, 132, -5, 133):
        return _Finding(
            "runtime",
            "The program crashed with a fatal runtime error.",
            "Look for a position outside an array or an empty optional value, then run again.",
        )
    if code in (-15, 143):
        return _Finding(
            "runtime",
            "The program was stopped by a signal before it finished.",
            "Run it again. If this repeats, use less data or a simpler version first.",
        )
    return None


def _suggestion(text: str) -> str | None:
    match = re.search(r"[Dd]id you mean:? [`'‘\"]?([^`'’\"?]+)[`'’\"]?\?", text)
    return match.group(1).strip() if match else None


def _name_hint(suggestion: str | None, declare: str) -> str:
    if suggestion:
        return f"Did you mean {_code(suggestion)}? Fix the spelling, then run again."
    return f"Check the spelling and capitalization, or {declare} before this line uses it."


def _python_close_name(missing: str, source_lines: tuple[str, ...] | None) -> str | None:
    """Suggest a defined name when the traceback has none (Python 3.11 omits it)."""
    try:
        tree = ast.parse("\n".join(source_lines or ()))
    except (SyntaxError, ValueError):
        return None
    names = {name for name in dir(builtins) if not name.startswith("_")}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.arg):
            names.add(node.arg)
        elif isinstance(node, ast.alias):
            names.add((node.asname or node.name).partition(".")[0])
    names.discard(missing)
    close = difflib.get_close_matches(missing, sorted(names), n=1, cutoff=0.8)
    return close[0] if close else None


# Python ---------------------------------------------------------------------

_PY_FRAME = re.compile(r'^\s*File "(?P<file>[^"\n]+)", line (?P<line>\d+)(?:, in .+)?\s*$')
_PY_EXCEPTION = re.compile(
    r"^(?P<qualified>(?:[A-Za-z_]\w*\.)*(?P<name>[A-Z]\w*))(?: \[[^\]]*\])?(?:: ?(?P<msg>.*))?$"
)
_PY_NOTEBOOK = re.compile(r"^Notebook cell \d+ failed at source line (?P<line>\d+)\b")
_PY_IPYTHON = re.compile(r"^(?P<name>[A-Z]\w*)\s+Traceback \(most recent call last\)")
_PY_BLOCK_KEYWORDS = frozenset(
    [
        "if",
        "elif",
        "else",
        "for",
        "while",
        "def",
        "class",
        "try",
        "except",
        "finally",
        "with",
        "match",
        "case",
    ]
)
_PY_BUILTIN_ERRORS = frozenset(
    [
        "SyntaxError",
        "IndentationError",
        "TabError",
        "NameError",
        "UnboundLocalError",
        "TypeError",
        "IndexError",
        "KeyError",
        "ZeroDivisionError",
        "AttributeError",
        "ModuleNotFoundError",
        "ImportError",
        "ValueError",
        "AssertionError",
        "RecursionError",
        "FileNotFoundError",
        "MemoryError",
        "OverflowError",
    ]
)


def _python(lines: list[str], context: _Context, output: str) -> _Finding | None:
    frames = [(i, m) for i, text in enumerate(lines) if (m := _PY_FRAME.match(text))]
    name = message = qualified = exception_line = ""
    line: int | None = None
    column: int | None = None
    code_text = ""
    if frames:
        last = frames[-1][0]
        start = max(
            (i for i, text in enumerate(lines[:last]) if text.startswith("Traceback (most")),
            default=0,
        )
        for i in range(last + 1, len(lines)):
            text = lines[i]
            if not text.strip() or text[0].isspace():
                continue
            match = _PY_EXCEPTION.match(text)
            if match:
                name, qualified = match.group("name"), match.group("qualified")
                message, exception_line = match.group("msg") or "", text
            break
        learner = [(i, m) for i, m in frames if i >= start and context.is_learner(m.group("file"))]
        if learner:
            index, frame = learner[-1]
            line = int(frame.group("line"))
            code_text, column = _python_column(lines, index, context.source_line(line))
    else:
        header = next((m for text in lines if (m := _PY_IPYTHON.match(text))), None)
        if header is not None:
            name = qualified = header.group("name")
            for text in reversed(lines):
                if text == name or text.startswith(name + ": "):
                    message, exception_line = text.partition(": ")[2], text
                    break
    for text in lines:
        if notebook := _PY_NOTEBOOK.match(text):
            line, column = int(notebook.group("line")), None
    if not name or not exception_line:
        return None
    kind, title, hint = _python_message(name, qualified, message, code_text, context.source_lines)
    return _Finding(kind, title, hint, exception_line, line, column)


def _python_column(lines: list[str], index: int, source_line: str | None) -> tuple[str, int | None]:
    shown = lines[index + 1] if index + 1 < len(lines) else ""
    if not shown.startswith("    ") or _PY_FRAME.match(shown):
        return "", None
    code_text = shown[4:].rstrip()
    caret = lines[index + 2] if index + 2 < len(lines) else ""
    if source_line is None or not re.fullmatch(r" *[~^]+[~^ ]*", caret):
        return code_text, None
    if code_text != source_line.strip():
        return code_text, None
    leading = len(source_line) - len(source_line.lstrip())
    offset = len(caret) - len(caret.lstrip(" ")) - 4
    return code_text, (leading + offset + 1 if offset >= 0 else None)


def _python_message(
    name: str,
    qualified: str,
    message: str,
    code_text: str,
    source_lines: tuple[str, ...] | None = None,
) -> tuple[str, str, str]:
    if name in {"SyntaxError", "IndentationError", "TabError"}:
        return ("syntax", *_python_syntax(name, message, code_text))
    if name == "AssertionError":
        return (
            "assertion",
            f"A check failed{_AT}: the `assert` condition was false.",
            "Compare the expected and actual values, often shown in the message below, then "
            "fix the code that computes them.",
        )
    suggestion = _suggestion(message)
    if name == "NameError":
        found = re.search(r"name '([^']+)' is not defined", message)
        module = re.search(r"forget to import '([^']+)'", message)
        if suggestion is None and found:
            suggestion = _python_close_name(found.group(1), source_lines)
        hint = (
            f"Add `import {module.group(1)}` at the top of the program, then run again."
            if module
            else _name_hint(suggestion, "create the variable")
        )
        target = _code(found.group(1)) if found else "a name"
        return "runtime", f"Python does not know the name {target}{_AT}.", hint
    if name == "UnboundLocalError":
        found = re.search(r"local variable '([^']+)'", message)
        target = _code(found.group(1)) if found else "A variable"
        return (
            "runtime",
            f"{target} is used{_AT} before it has a value inside this function.",
            "Give the variable a value earlier in the function, or pass it in as a parameter.",
        )
    if name == "TypeError":
        return "runtime", *_python_type_error(message)
    if name == "IndexError":
        kind = re.match(r"(list|string|tuple) index out of range", message)
        if kind:
            return (
                "runtime",
                f"{_LNC} asks for a {kind.group(1)} position that does not exist.",
                "Positions start at 0, so a list with 3 items has positions 0, 1 and 2. "
                "Check the position against `len(...)`.",
            )
        return (
            "runtime",
            f"{_LNC} asks for a position outside the data.",
            "Positions start at 0. Check the position against the size of the data.",
        )
    if name == "KeyError":
        return (
            "runtime",
            f"The key {_code(message or '?')} was not found{_AT}.",
            "Check the spelling of the key or column name. For a dictionary, `.get(key)` "
            "returns `None` instead of stopping the program.",
        )
    if name == "ZeroDivisionError":
        return (
            "runtime",
            f"{_LNC} divides by zero, which has no answer.",
            "Make sure the number you divide by is not 0, for example check it with `if` "
            "before dividing.",
        )
    if name == "AttributeError":
        return "runtime", *_python_attribute_error(message, suggestion)
    if name == "ModuleNotFoundError":
        found = re.search(r"No module named '([^']+)'", message)
        target = _code(found.group(1)) if found else "a module"
        return (
            "runtime",
            f"Python cannot find a module (library) named {target}{_AT}.",
            "Check the spelling. Pads cannot install packages, so use only the libraries this "
            "lesson's runtime provides.",
        )
    if name == "ImportError":
        found = re.search(r"cannot import name '([^']+)' from '([^']+)'", message)
        if found:
            return (
                "runtime",
                f"The module {_code(found.group(2))} has no name {_code(found.group(1))} to "
                f"import{_AT}.",
                "Check the spelling and capitalization of the name you import.",
            )
    if name == "ValueError":
        return "runtime", *_python_value_error(message)
    if name == "RecursionError":
        return (
            "runtime",
            f"A function kept calling itself until Python stopped it{_AT}.",
            "Make sure the function has a base case that returns without calling itself again.",
        )
    if name == "FileNotFoundError":
        found = re.search(r"No such file or directory: '([^']+)'", message)
        target = _code(found.group(1)) if found else "a file"
        return (
            "runtime",
            f"Python cannot find the file {target}{_AT}.",
            "Check the file name. Each run starts in a fresh folder, so create the file in the "
            "same program before reading it.",
        )
    if name == "MemoryError":
        return (
            "runtime",
            f"Python ran out of memory{_AT}.",
            "Use less data at once, for example smaller arrays or fewer rows, then run again.",
        )
    return "runtime", *_library_error(name, qualified, message)


def _python_syntax(name: str, message: str, code_text: str) -> tuple[str, str]:
    keyword = code_text.split()[0].rstrip(":") if code_text.split() else ""
    if message.startswith("expected ':'"):
        where = f"the `{keyword}` line" if keyword in _PY_BLOCK_KEYWORDS else _LN
        return (
            f"Python expected a colon (:) at the end of {_LN}.",
            f"Add `:` at the end of {where}, then run again.",
        )
    opened = re.match(r"'([(\[{])' was never closed", message)
    if opened:
        closing = {"(": ")", "[": "]", "{": "}"}[opened.group(1)]
        return (
            f"An opening `{opened.group(1)}` on {_LN} is never closed.",
            f"Add the matching `{closing}` where the expression ends, then run again.",
        )
    if message.startswith("unmatched "):
        return (
            f"There is an extra closing bracket{_AT}.",
            "Remove the extra bracket, or add the opening bracket it belongs to.",
        )
    if message.startswith("closing parenthesis"):
        return (
            f"The brackets{_AT} do not match.",
            "Close each bracket with its partner: `)` for `(`, `]` for `[` and `}` for `{`.",
        )
    if "unterminated" in message and "string" in message:
        return (
            f"A text value (string){_AT} is missing its closing quote.",
            'Add the matching quote at the end of the text, for example `"hello"`.',
        )
    if message.startswith("Missing parentheses in call to 'print'"):
        return (
            f"`print` needs parentheses in Python 3{_AT}.",
            'Write the value inside parentheses, for example `print("hi")`.',
        )
    if "forgot a comma" in message:
        return (
            f"Python could not read {_LN}. A comma may be missing between two values.",
            "Separate the items with commas, for example `[1, 2, 3]`.",
        )
    if "Maybe you meant '=='" in message:
        return (
            f"{_LNC} uses `=` where Python expected a comparison.",
            "Use `==` to compare two values. A single `=` stores a value in a variable.",
        )
    if message.startswith("expected an indented block"):
        return (
            f"{_LNC} needs to be indented.",
            "Add four spaces at the start of the line, so it belongs to the block that starts "
            "with the `:` line above it.",
        )
    if message.startswith("unexpected indent"):
        return (
            f"{_LNC} starts with more spaces than Python expects.",
            "Remove the extra spaces at the start of the line, so it lines up with the code "
            "around it.",
        )
    if message.startswith("unindent does not match"):
        return (
            f"{_LNC} does not line up with the lines above it.",
            "Use the same indentation as the block it belongs to, usually a multiple of four "
            "spaces.",
        )
    if name == "TabError":
        return (
            f"{_LNC} mixes tabs and spaces for indentation.",
            "Use spaces only. Replace each tab at the start of the line with four spaces.",
        )
    if message.startswith("invalid character"):
        return (
            f"{_LNC} contains a character Python cannot read, such as a curly quote.",
            "Retype quotes as straight quotes (\" or ') and remove symbols copied from documents.",
        )
    if message.startswith("invalid decimal literal"):
        return (
            f"Python could not read a number or name{_AT}.",
            "Names cannot start with a digit, and numbers cannot contain letters. Check the "
            "spelling.",
        )
    if "outside function" in message:
        return (
            f"{_code(message.split(chr(39))[1] if chr(39) in message else 'return')} is only "
            f"allowed inside a function{_AT}.",
            "Move the statement into a function body, or remove it.",
        )
    if name == "IndentationError":
        return (
            f"The indentation (spaces at the start) of {_LN} does not fit the code around it.",
            "Line up the code in each block using the same number of spaces, usually four.",
        )
    return (
        f"Python could not understand how {_LN} is written (a syntax error).",
        "Look near the marked spot for a missing bracket, quote, comma or colon, then run again.",
    )


def _python_type_error(message: str) -> tuple[str, str]:
    if found := re.search(r'can only concatenate str \(not "(\w+)"\) to str', message):
        return (
            f"{_LNC} joins text with {_an(found.group(1))} value, which Python does not "
            "do automatically.",
            "Convert the value to text with `str(...)`, or use an f-string such as "
            '`f"Total: {total}"`.',
        )
    if found := re.search(r"unsupported operand type\(s\) for (.+?): '(\w+)' and '(\w+)'", message):
        return (
            f"{_LNC} uses {_code(found.group(1))} with {_an(found.group(2))} and "
            f"{_an(found.group(3))}, which Python cannot combine.",
            "Convert one value so both types match, for example `int(text)` or `str(number)`.",
        )
    if found := re.search(r"([\w.]+)\(\) missing \d+ required \w+ arguments?: (.+)", message):
        names = ", ".join(_code(n) for n in re.findall(r"'([^']+)'", found.group(2))[:3])
        return (
            f"The call to {_code(found.group(1) + '()')}{_AT} is missing a value for "
            f"{names or 'a parameter'}.",
            f"Pass a value for each parameter of {_code(found.group(1) + '()')} when you call it.",
        )
    if found := re.search(r"([\w.]+)\(\) takes (\d+) positional arguments? but (\d+)", message):
        return (
            f"The call to {_code(found.group(1) + '()')}{_AT} passes {found.group(3)} values, "
            f"but it accepts {found.group(2)}.",
            "Match the values in the call to the parameters in the definition. Methods also "
            "receive `self` automatically.",
        )
    if found := re.search(r"'(\w+)' object is not (callable|subscriptable|iterable)", message):
        target, problem = _code(found.group(1)), found.group(2)
        if problem == "callable":
            return (
                f"{_LNC} uses a {target} value as if it were a function.",
                "Remove the parentheses after the value, or check that a variable did not "
                "replace a function with the same name.",
            )
        if problem == "subscriptable":
            return (
                f"{_LNC} uses `[...]` on a {target} value, which does not support it.",
                "Check which value you index. A function may have returned `None` instead of "
                "a list or dictionary.",
            )
        return (
            f"{_LNC} tries to loop over a {target} value, which cannot be looped over.",
            "Loop over a list, string, range or other collection, for example `range(n)` for "
            "a number.",
        )
    if "indices must be integers" in message:
        return (
            f"{_LNC} uses a value that is not a whole number as a position.",
            "List positions are whole numbers starting at 0. Convert with `int(...)`, or use a "
            "dictionary for named keys.",
        )
    if "immutable" in message and "JAX" in message:
        return (
            f"JAX arrays cannot be changed in place{_AT}.",
            "Create an updated copy instead, for example `x = x.at[0].set(5.0)`.",
        )
    return (
        f"{_LNC} uses a value of the wrong type.",
        "Read the message below to see which types were involved, then convert or replace the "
        "value.",
    )


def _python_attribute_error(message: str, suggestion: str | None) -> tuple[str, str]:
    found = re.search(r"module '([\w.]+)' has no attribute '(\w+)'", message)
    if found:
        return (
            f"The module {_code(found.group(1))} has no name {_code(found.group(2))}{_AT}.",
            _name_hint(suggestion, "look up the exact name in the library's documentation")
            if suggestion
            else "Check the spelling and capitalization in the library's documentation.",
        )
    found = re.search(r"'(\w+)' object has no attribute '(\w+)'", message)
    if found:
        owner, attribute = found.group(1), found.group(2)
        if suggestion:
            hint = f"Did you mean {_code(suggestion)}? Fix the spelling, then run again."
        elif owner == "NoneType":
            hint = "The value is `None`. A function may have returned `None` instead of a result."
        elif owner == "list" and attribute == "push":
            hint = "Python lists use `append` to add an item, for example `items.append(3)`."
        else:
            hint = "Check the spelling, or use `dir(value)` to list the names it has."
        return (
            f"{_an_cap(owner)} value has no attribute or method named {_code(attribute)}{_AT}.",
            hint,
        )
    return (
        f"{_LNC} uses a name that the value does not have.",
        "Check the spelling, or use `dir(value)` to list the names it has.",
    )


def _python_value_error(message: str) -> tuple[str, str]:
    found = re.search(r"invalid literal for (int|float)\(\) with base \d+: (.+)", message)
    found = found or re.search(r"could not convert (string) to float: (.+)", message)
    if found:
        target = "int()" if found.group(1) == "int" else "float()"
        number = "whole number" if target == "int()" else "number"
        return (
            f"{_code(target)} cannot turn the text {_code(found.group(2))} into a {number}{_AT}.",
            'Convert only text that contains a number, such as `"12"`. Check the value before '
            "converting it.",
        )
    if "values to unpack" in message:
        return (
            f"{_LNC} unpacks a different number of values than there are names.",
            "Use the same number of names on the left as values on the right.",
        )
    if "math domain error" in message:
        return (
            f"A math function{_AT} received a value outside its allowed range.",
            "Check the input, for example a square root or logarithm of a negative number.",
        )
    return (
        f"{_LNC} received a value it cannot use.",
        "Read the message below to see which value was rejected, then check where that value "
        "comes from.",
    )


def _library_error(name: str, qualified: str, message: str) -> tuple[str, str]:
    column = re.search(r'unable to find column "([^"]+)"', message)
    if column:
        return (
            f"There is no column named {_code(column.group(1))} in this data{_AT}.",
            "Check the column name. The message below lists the valid columns.",
        )
    if "UNRESOLVED_COLUMN" in message:
        missing = re.search(r"name `([^`]+)` cannot be resolved", message)
        options = re.findall(r"`([^`]+)`", message.partition("Did you mean")[2])
        return (
            f"Spark cannot find a column named {_code(missing.group(1) if missing else '?')}{_AT}.",
            "Use one of the suggested columns: " + ", ".join(_code(o) for o in options[:4]) + "."
            if options
            else "Check the column names with `df.columns`.",
        )
    if "TABLE_OR_VIEW_NOT_FOUND" in message:
        return (
            f"Spark cannot find the table or view used{_AT}.",
            "Check the name, and create the view with `createOrReplaceTempView` before using it.",
        )
    if any(
        marker in message
        for marker in ("shapes cannot be multiplied", "size-incompatible", "Incompatible shapes")
    ):
        return (
            f"The shapes of the arrays{_AT} do not fit together for this operation.",
            "For matrix multiplication `a @ b`, the columns of `a` must equal the rows of `b`. "
            "Print `.shape` to check.",
        )
    if "could not be broadcast" in message or "shape mismatch" in message:
        return (
            f"The shapes of the arrays{_AT} do not fit together.",
            "Print `.shape` for each array and make the sizes match.",
        )
    if name.startswith("Arrow") and "Could not convert" in message:
        return (
            f"Arrow could not convert a value to the column's type{_AT}.",
            "Make all values in a column the same type, for example all numbers or all text.",
        )
    if "." in qualified or name not in _PY_BUILTIN_ERRORS:
        return (
            f"The program stopped{_AT} with {_an(name)} error.",
            "Read the error message below. It usually names the value, column or setting that "
            "caused the problem.",
        )
    return (
        f"The program stopped{_AT} with {_an(name)}.",
        "Read the error message below, then check the values used on that line.",
    )


# SQL ------------------------------------------------------------------------

_PSQL = re.compile(r"^psql:(?P<file>[^:]+):(?P<line>\d+): (?:ERROR|FATAL|error):\s+(?P<msg>.*)$")


def _sql(lines: list[str], context: _Context, output: str) -> _Finding | None:
    text = output.strip()
    if text.startswith("{"):
        try:
            data = json.loads(text)
        except ValueError:
            data = None
        if isinstance(data, dict) and isinstance(data.get("message"), str):
            sqlstate = data.get("sqlstate") if isinstance(data.get("sqlstate"), str) else None
            line = data.get("error_line")
            message = data["message"]
            if sqlstate is None:
                return _Finding(
                    "database",
                    "The SQL pad could not complete the query.",
                    "Read the message below. It explains what the course database needs "
                    "before you run again.",
                    message,
                )
            kind, title, hint = _sql_message(message, sqlstate, "PostgreSQL")
            return _Finding(
                kind,
                title,
                hint,
                f"{message} (SQLSTATE {sqlstate})",
                line if type(line) is int and line > 0 else None,
            )
    for text_line in lines:
        match = _PSQL.match(text_line)
        if match:
            kind, title, hint = _sql_message(match.group("msg"), None, "PostgreSQL")
            line = int(match.group("line")) if context.is_learner(match.group("file")) else None
            return _Finding(kind, title, hint, text_line, line)
    return None


_SQL_STATES = {
    "syntax error at or near": "42601",
    "syntax error at end of input": "42601",
    "does not exist": "",
    "division by zero": "22012",
    "duplicate key value": "23505",
    "violates not-null constraint": "23502",
    "violates foreign key constraint": "23503",
    "violates check constraint": "23514",
    "invalid input syntax for type": "22P02",
    "permission denied": "42501",
    "already exists": "42P07",
    "is ambiguous": "42702",
    "must appear in the GROUP BY clause": "42803",
    "canceling statement due to statement timeout": "57014",
    "current transaction is aborted": "25P02",
}


def _sql_message(message: str, sqlstate: str | None, engine: str) -> tuple[str, str, str]:
    state = sqlstate or next(
        (code for marker, code in _SQL_STATES.items() if marker in message and code), ""
    )
    token = re.search(r'at or near "([^"]*)"', message)
    if token:
        word = token.group(1)
        close = difflib.get_close_matches(word.upper(), _SQL_KEYWORDS, n=1, cutoff=0.7)
        hint = (
            f"Did you mean {_code(close[0])}? Fix the spelling, then run again."
            if close and close[0] != word.upper()
            else f"Check the words just before {_code(word)}. A comma, keyword or parenthesis "
            "may be missing or misspelled."
        )
        return "syntax", f"{engine} could not read the SQL near {_code(word)}.", hint
    if "syntax error at end of input" in message:
        return (
            "syntax",
            f"The SQL ended before {engine} expected it to.",
            "Finish the statement, for example add the table name after `FROM`, and check for "
            "an unclosed parenthesis or quote.",
        )
    if state == "42601" or message.startswith("syntax error"):
        return (
            "syntax",
            f"{engine} could not read part of the SQL (a syntax error).",
            "Check the spelling of keywords and the commas, quotes and parentheses near the "
            "marked spot.",
        )
    if found := re.search(r'relation "([^"]+)" does not exist', message):
        return (
            "database",
            f"{engine} cannot find a table named {_code(found.group(1))}.",
            "Check the table name and its schema prefix, such as `training.`. The lesson guide "
            "lists the available tables.",
        )
    if found := re.search(r'column "?([^"\s]+)"? does not exist', message):
        return (
            "database",
            f"{engine} cannot find a column named {_code(found.group(1))}.",
            "Check the spelling and which table the column belongs to. "
            "`SELECT * FROM table_name LIMIT 5` shows the columns.",
        )
    if found := re.search(r"function (.+?) does not exist", message):
        return (
            "database",
            f"{engine} has no function {_code(found.group(1))} that accepts these values.",
            "Check the function name and the types of its arguments. A cast such as "
            "`::numeric` can help.",
        )
    if state == "22012":
        return (
            "database",
            "The query divided a number by zero.",
            "Guard the divisor, for example `NULLIF(divisor, 0)`, so a zero becomes NULL "
            "instead of stopping the query.",
        )
    if state == "23505":
        return (
            "database",
            "A row with the same unique value already exists, so the new row was rejected.",
            "Use a different value for the unique column, or check the existing rows first. "
            "The failed statement was rolled back.",
        )
    if state == "23502":
        return (
            "database",
            "A required column was left empty (NULL), so the row was rejected.",
            "Give that column a value in the `INSERT` or `UPDATE` statement.",
        )
    if state == "23503":
        return (
            "database",
            "The row refers to a value that does not exist in the related table.",
            "Insert the related row first, or use a value that already exists there.",
        )
    if state == "23514":
        return (
            "database",
            "A value broke a rule (a CHECK constraint) on the table.",
            "Read the constraint name in the message below, then use a value that meets it.",
        )
    if state == "22P02":
        return (
            "database",
            f"{engine} could not convert a text value to the required type.",
            "Check the value in the message below. Numbers must contain only digits, and dates "
            "use the form `2024-01-31`.",
        )
    if state == "42501":
        return (
            "database",
            "The course login is not allowed to perform this operation.",
            "Pads use a limited course account. Work only with the lesson's own tables.",
        )
    if state == "42P07":
        return (
            "database",
            "An object with that name already exists.",
            "Use a new name, or drop the existing object first if the lesson asks you to.",
        )
    if state == "42702":
        return (
            "database",
            "A column name matches more than one table in the query.",
            "Put the table name or alias in front of the column, for example `c.customer_id`.",
        )
    if state == "42803":
        return (
            "database",
            "A selected column is neither grouped nor summarized.",
            "Add the column to `GROUP BY`, or wrap it in an aggregate such as `SUM`, `COUNT` or "
            "`MAX`.",
        )
    if state == "57014":
        return (
            "timeout",
            "The query ran longer than the database's statement time limit.",
            "Filter rows earlier with `WHERE`, add a `LIMIT`, or simplify joins, then run again.",
        )
    if state == "25P02":
        return (
            "database",
            "An earlier statement failed, so the rest of this transaction was ignored.",
            "Fix the first error, then end the transaction with `ROLLBACK` before running more "
            "statements.",
        )
    suffix = f" (SQLSTATE {state})" if state else ""
    return (
        "database",
        f"{engine} reported an error{suffix}.",
        "Read the database message below. It names the table, column or value that caused the "
        "problem.",
    )


# dbt ------------------------------------------------------------------------

_DBT_HEADER = re.compile(
    r"(?P<type>Runtime|Compilation|Database|Parsing|Dependency) Error in \w+ \S+ \([^)]*\)"
)


def _dbt(lines: list[str], context: _Context, output: str) -> _Finding | None:
    for index, text in enumerate(lines):
        header = _DBT_HEADER.search(text)
        if header is None:
            continue
        message = next(
            (
                item.strip()
                for item in lines[index + 1 : index + 6]
                if item.strip() and not re.match(r"^\d{2}:\d{2}:\d{2}\s", item)
            ),
            "",
        )
        if not message:
            continue
        if parser := re.match(r"Parser Error: (.+)", message):
            kind, title, hint = _sql_message(parser.group(1), None, "DuckDB")
            if kind == "syntax":
                hint = _cap(
                    hint + " The `LINE` number in the message counts lines that dbt adds.",
                    HINT_LIMIT,
                )
            return _Finding(kind, title, hint, message)
        if found := re.match(r'Binder Error: Referenced column "([^"]+)" not found', message):
            return _Finding(
                "database",
                f"DuckDB cannot find a column named {_code(found.group(1))} in the tables after "
                "`FROM`.",
                "Use one of the candidate columns listed below, or check which model or seed "
                "you select from.",
                message,
            )
        if found := re.match(r"Catalog Error: Table with name (\S+) does not exist", message):
            return _Finding(
                "database",
                f"DuckDB cannot find a table named {_code(found.group(1))}.",
                "Refer to models and seeds with `{{ ref('name') }}` and to sources with "
                "`{{ source('raw', 'orders') }}`.",
                message,
            )
        if found := re.match(r"Required var '([^']+)' not found", message):
            return _Finding(
                "compile",
                f"dbt cannot find a variable named {_code(found.group(1))}.",
                "Use one of the variables listed in the message below, or give a default as the "
                "second argument: `{{ var('name', 'default') }}`.",
                message,
            )
        if found := re.search(r"depends on a node named '([^']+)'", message):
            return _Finding(
                "compile",
                f"The model refers to {_code(found.group(1))}, but no model or seed has that name.",
                "Check the name inside `ref()`. The available seeds are `raw_orders` and "
                "`customers`.",
                message,
            )
        if header.group("type") == "Compilation":
            return _Finding(
                "compile",
                "dbt could not read the Jinja template in the model.",
                "Check each `{{ ... }}` and `{% ... %}` block for a missing closing brace, "
                "quote or parenthesis.",
                message,
            )
        kind, title, hint = _sql_message(message.partition(": ")[2] or message, None, "DuckDB")
        return _Finding(kind, title, hint, message)
    return None


# JVM: Java and Scala --------------------------------------------------------

_JVM_COMPILE = re.compile(r"^(?P<file>[^\s:]+\.(?:java|scala)):(?P<line>\d+): error: (?P<msg>.+)$")
_JVM_EXCEPTION = re.compile(
    r'^Exception in thread "[^"]*" (?P<qualified>[\w.$]+)(?::\s?(?P<msg>.*))?$'
)
_JVM_FRAME = re.compile(r"^\s*at [^(\s]+\((?P<file>[^():]+):(?P<line>\d+)\)")


def _jvm(lines: list[str], context: _Context, output: str) -> _Finding | None:
    language = "Java" if context.filename.endswith(".java") else "Scala"
    for index, text in enumerate(lines):
        match = _JVM_COMPILE.match(text)
        if not match:
            continue
        message = match.group("msg")
        line = int(match.group("line")) if context.is_learner(match.group("file")) else None
        column = _caret_column(lines, index, context.source_line(line))
        details = "\n".join(lines[index + 1 : index + 6])
        kind, title, hint = _jvm_compile_message(language, message, details, context)
        return _Finding(kind, title, hint, text, line, column)
    for index, text in enumerate(lines):
        match = _JVM_EXCEPTION.match(text)
        if not match:
            continue
        line = None
        for frame_text in lines[index + 1 :]:
            frame = _JVM_FRAME.match(frame_text)
            if frame and context.is_learner(frame.group("file")):
                line = int(frame.group("line"))
                break
        name = match.group("qualified").rsplit(".", 1)[-1]
        kind, title, hint = _jvm_runtime_message(name, match.group("msg") or "")
        return _Finding(kind, title, hint, text, line)
    return None


def _caret_column(lines: list[str], index: int, source_line: str | None) -> int | None:
    """Columns from compilers that echo the original line followed by a caret."""
    if source_line is None:
        return None
    for offset in range(index + 1, min(index + 6, len(lines) - 1)):
        shown, caret = lines[offset], lines[offset + 1]
        if shown.rstrip() == source_line.rstrip() and re.fullmatch(r" *\^[~^]*\s*", caret):
            return len(caret) - len(caret.lstrip(" ")) + 1
    return None


def _jvm_compile_message(
    language: str, message: str, details: str, context: _Context
) -> tuple[str, str, str]:
    if found := re.match(r"'(.+)' expected", message):
        symbol = found.group(1)
        if symbol == ";":
            return (
                "syntax",
                f"{language} expected a semicolon (;) at the end of {_LN}.",
                f"Add `;` at the end of {_LN}, then run again.",
            )
        return (
            "syntax",
            f"{language} expected {_code(symbol)}{_AT}.",
            "Add the missing symbol, and check that brackets and parentheses are balanced.",
        )
    if message.startswith(
        (
            "illegal start of",
            "class, interface, enum, or record expected",
            "<identifier> expected",
            "unclosed",
            "reached end of file while parsing",
            "not a statement",
            "unclosed string literal",
        )
    ):
        return (
            "syntax",
            f"{language} could not understand how {_LN} is written (a syntax error).",
            "Check for a missing bracket, semicolon or quote near the marked spot.",
        )
    if message.startswith("cannot find symbol"):
        symbol = re.search(r"symbol:\s+(\w+) (\w+)", details)
        what, name = (symbol.group(1), symbol.group(2)) if symbol else ("name", "?")
        if what == "class":
            return (
                "compile",
                f"Java cannot find a class named {_code(name)}{_AT}.",
                "Check the spelling and capitalization, or add the missing `import` line.",
            )
        if what == "method":
            return (
                "compile",
                f"Java cannot find a method named {_code(name)} that accepts these values{_AT}.",
                "Check the method's spelling and the number and types of its arguments.",
            )
        return (
            "compile",
            f"Java does not know the name {_code(name)}{_AT}.",
            _name_hint(None, "declare it with a type"),
        )
    if found := re.match(r"not found: (?:value|type|object) (\S+)", message):
        return (
            "compile",
            f"Scala does not know the name {_code(found.group(1))}{_AT}.",
            _name_hint(_suggestion(details), "define it"),
        )
    if found := re.match(r"incompatible types: (.+?) cannot be converted to (.+)", message):
        source_type, target = found.group(1), found.group(2)
        hint = (
            "Use a value of the declared type, or convert it, for example `Integer.parseInt(text)`."
            if source_type == "String" and target == "int"
            else "Use a value of the declared type, or change the variable's type."
        )
        return (
            "compile",
            f"{_LNC} puts {_an(source_type)} where {_an(target)} is required.",
            hint,
        )
    if message.startswith("type mismatch"):
        found_type = re.search(r"found\s*:\s*(\S+?)(?:\(|$)", details, re.MULTILINE)
        required = re.search(r"required\s*:\s*(\S+)", details)
        if found_type and required:
            return (
                "compile",
                f"{_LNC} has {_an(found_type.group(1))} value where "
                f"{_an(required.group(1))} is required.",
                "Use a value of the required type, or convert it, for example with `.toInt` "
                "or `.toString`.",
            )
    if found := re.match(r"class (\w+) is public, should be declared in a file named", message):
        return (
            "compile",
            f"The public class is named {_code(found.group(1))}, but this pad's file is "
            f"{_code(context.filename)}.",
            "Rename the class to `Main`, so the line reads `public class Main {`.",
        )
    if message.startswith("missing return statement"):
        return (
            "compile",
            f"A method that promises a value can finish without returning one{_AT}.",
            "Add a `return` statement for every path through the method.",
        )
    if found := re.match(r"variable (\w+) might not have been initialized", message):
        return (
            "compile",
            f"{_code(found.group(1))} might be used{_AT} before it has a value.",
            "Give the variable a value when you declare it, or on every path before using it.",
        )
    if found := re.match(r"unreported exception (\S+); must be caught", message):
        return (
            "compile",
            f"{_LNC} can throw {_code(found.group(1))}, which must be handled.",
            "Wrap the call in `try`/`catch`, or add `throws` to the method declaration.",
        )
    return (
        "compile",
        f"The {language} compiler could not compile {_LN}.",
        "Read the first error message below. Later errors often follow from the first one.",
    )


def _jvm_runtime_message(name: str, message: str) -> tuple[str, str, str]:
    if name in {
        "ArrayIndexOutOfBoundsException",
        "IndexOutOfBoundsException",
        "StringIndexOutOfBoundsException",
    }:
        return (
            "runtime",
            f"{_LNC} asks for a position that does not exist.",
            "Positions start at 0, so a collection of length 2 has positions 0 and 1.",
        )
    if name == "NullPointerException":
        return (
            "runtime",
            f"{_LNC} uses a value that is `null`.",
            "Make sure the variable refers to an object before calling methods on it.",
        )
    if name == "ArithmeticException":
        return (
            "runtime",
            f"{_LNC} divides a whole number by zero.",
            "Make sure the number you divide by is not 0 before dividing.",
        )
    if name == "NumberFormatException":
        return (
            "runtime",
            f"Text that is not a valid number was converted to a number{_AT}.",
            "Check the text before converting it. It must contain only digits.",
        )
    if name == "AssertionError":
        return (
            "assertion",
            f"The `assert` check{_AT} failed.",
            "Compare the expected value with what the program computed, then fix the calculation.",
        )
    if name == "IllegalArgumentException" and message.startswith("requirement failed"):
        return (
            "assertion",
            f"A `require` check failed{_AT}.",
            "Read the requirement message below, then pass a value that meets it.",
        )
    if name == "OutOfMemoryError":
        return (
            "runtime",
            "The program ran out of memory.",
            "Use less data at once, for example smaller collections, then run again.",
        )
    if name == "StackOverflowError":
        return (
            "runtime",
            f"A method kept calling itself until the program ran out of stack space{_AT}.",
            "Make sure the recursive method has a base case that stops calling itself.",
        )
    if name == "AnalysisException":
        return ("runtime", *_library_error(name, name, message))
    return (
        "runtime",
        f"The program stopped{_AT} with {_an(name)}.",
        "Read the message below, then check the values used on that line.",
    )


# C and C++ -----------------------------------------------------------------

_GCC = re.compile(
    r"^(?P<file>[^\s:]+):(?P<line>\d+):(?P<col>\d+): (?:fatal error|error): (?P<msg>.+)$"
)
_NVCC = re.compile(r"^(?P<file>\S+\.cu)\((?P<line>\d+)\): error: (?P<msg>.+)$")
_C_ASSERT = re.compile(r"^\S+: (?P<file>[^\s:]+):(?P<line>\d+): .*Assertion `(?P<expr>.+)' failed")
_TERMINATE = re.compile(r"^terminate called after throwing an instance of '(?P<type>[^']+)'")
_UNDEFINED = re.compile(r"undefined reference to `(?P<symbol>[^'(]+)")
_QUOTED = r"[‘'](.+?)[’']"


def _gcc(lines: list[str], context: _Context, output: str) -> _Finding | None:
    language = "C++" if context.filename.endswith((".cpp", ".cu")) else "C"
    for text in lines:
        match = _GCC.match(text) or _NVCC.match(text)
        if match:
            learner = context.is_learner(match.group("file"))
            line = int(match.group("line")) if learner else None
            groups = match.groupdict()
            column = int(groups["col"]) if learner and groups.get("col") else None
            kind, title, hint = _gcc_message(language, match.group("msg"))
            return _Finding(kind, title, hint, text, line, column)
    for text in lines:
        if found := _UNDEFINED.search(text):
            symbol = found.group("symbol").strip()
            if "fixtures" in text or "verifier" in text:
                hint = (
                    "Define each function the lesson requires, with exactly the same name and "
                    "parameter types."
                )
            elif symbol == "main":
                hint = "Add a `main` function, for example `int main(void) { return 0; }`."
            else:
                hint = "Define the function, or check that its name matches the declaration."
            return _Finding("compile", f"The linker could not find {_code(symbol)}.", hint, text)
    for text in lines:
        if found := _C_ASSERT.match(text):
            line = int(found.group("line")) if context.is_learner(found.group("file")) else None
            return _Finding(
                "assertion",
                f"The `assert` check{_AT} failed: {_code(found.group('expr'))} was false.",
                "Compare the values in the condition with what the program computes, then fix "
                "the calculation.",
                text,
                line,
            )
        if found := _TERMINATE.match(text):
            error_type = found.group("type")
            hint = (
                "A position was outside the valid range. With `.at(i)`, `i` must be less than "
                "the container's `size()`."
                if error_type == "std::out_of_range"
                else "Read the `what()` message below. Fix the value that caused it, or handle "
                "it with `try` and `catch`."
            )
            return _Finding(
                "runtime",
                f"The program stopped with an unhandled {_code(error_type)} error.",
                hint,
                text,
            )
    return None


def _gcc_message(language: str, message: str) -> tuple[str, str, str]:
    if found := re.match(rf"expected {_QUOTED} before {_QUOTED}", message):
        symbol, before = found.group(1), found.group(2)
        if symbol == ";":
            return (
                "syntax",
                f"The compiler expected a semicolon (;) at the end of {_LN}, before "
                f"{_code(before)}.",
                f"Add `;` at the end of {_LN}, then run again.",
            )
        return (
            "syntax",
            f"The compiler expected {_code(symbol)} before {_code(before)}{_AT}.",
            "Add the missing symbol, or check the brackets and semicolons just before it.",
        )
    if message.startswith("expected declaration or statement at end of input"):
        return (
            "syntax",
            "The code ends before every `{` block is closed.",
            "Add the missing `}`, so each opening brace has a matching closing brace.",
        )
    if message.startswith(("expected", "missing terminating", "stray ")):
        return (
            "syntax",
            f"The compiler could not understand how {_LN} is written (a syntax error).",
            "Check for a missing semicolon, bracket or quote near the marked spot.",
        )
    if found := re.match(rf"{_QUOTED} undeclared", message):
        return (
            "compile",
            f"{language} does not know the name {_code(found.group(1))}{_AT}.",
            "Declare the variable with a type before using it, for example `int total = 0;`, "
            "or check the spelling.",
        )
    if found := re.match(rf"{_QUOTED} was not declared in this scope", message):
        return (
            "compile",
            f"{language} does not know the name {_code(found.group(1))}{_AT}.",
            _name_hint(_suggestion(message), "declare it"),
        )
    if found := re.match(rf"implicit declaration of function {_QUOTED}", message):
        suggestion = _suggestion(message)
        return (
            "compile",
            f"{language} does not know a function named {_code(found.group(1))}{_AT}.",
            f"Did you mean {_code(suggestion)}? Fix the spelling, then run again."
            if suggestion
            else "Check the spelling, or add the `#include` line for the header that declares it.",
        )
    if found := re.search(rf"conversion from {_QUOTED} to (?:non-scalar type )?{_QUOTED}", message):
        return (
            "compile",
            f"{_LNC} cannot convert {_an(found.group(1))} into {_an(found.group(2))}.",
            "Use a value of the declared type, or convert it explicitly.",
        )
    if found := re.search(rf"cannot convert {_QUOTED} to {_QUOTED}", message):
        return (
            "compile",
            f"{_LNC} cannot convert {_an(found.group(1))} into {_an(found.group(2))}.",
            "Use a value of the declared type, or convert it explicitly.",
        )
    if found := re.match(r"(\S+): No such file or directory", message):
        return (
            "compile",
            f"The compiler cannot find the header file {_code(found.group(1))}{_AT}.",
            "Check the file name in the `#include` line. Only standard library headers are "
            "available.",
        )
    if found := re.match(rf"too (few|many) arguments to function {_QUOTED}", message):
        return (
            "compile",
            f"The call to {_code(found.group(2))}{_AT} passes too {found.group(1)} values.",
            "Match the values in the call to the parameters in the function's declaration.",
        )
    if message.startswith("lvalue required as left operand of assignment"):
        return (
            "compile",
            f"{_LNC} assigns with `=` where a comparison may be intended.",
            "Use `==` to compare two values. A single `=` stores a value in a variable.",
        )
    return (
        "compile",
        f"The compiler could not compile {_LN}.",
        "Read the first error message below. Later errors often follow from the first one.",
    )


# C# -------------------------------------------------------------------------

_CSC = re.compile(
    r"^(?P<file>\S+)\((?P<line>\d+),(?P<col>\d+)\): error (?P<code>CS\d+): (?P<msg>.+?)"
    r"(?:\s*\[[^\]]*\])?$"
)
_CS_EXCEPTION = re.compile(r"^Unhandled exception\. (?P<qualified>[\w.`]+)(?::\s?(?P<msg>.*))?$")
_CS_FRAME = re.compile(r"^\s*at .+ in (?P<file>\S+):line (?P<line>\d+)\s*$")
_CS_SYNTAX = {"CS1002", "CS1003", "CS1001", "CS1010", "CS1022", "CS1026", "CS1513", "CS1514"}


def _csharp(lines: list[str], context: _Context, output: str) -> _Finding | None:
    for text in lines:
        match = _CSC.match(text)
        if not match:
            continue
        learner = context.is_learner(match.group("file"))
        line = int(match.group("line")) if learner else None
        column = int(match.group("col")) if learner else None
        kind, title, hint = _csharp_message(match.group("code"), match.group("msg"))
        return _Finding(kind, title, hint, text, line, column)
    for index, text in enumerate(lines):
        exception = _CS_EXCEPTION.match(text)
        failed = text.strip() == "Assertion failed." and index > 0
        if not exception and not failed:
            continue
        line = None
        for frame_text in lines[index + 1 :]:
            frame = _CS_FRAME.match(frame_text)
            if frame and context.is_learner(frame.group("file")):
                line = int(frame.group("line"))
                break
        if failed:
            return _Finding(
                "assertion",
                f"The `Debug.Assert` check{_AT} failed.",
                "Read the assertion message below, then fix the value it checks.",
                text,
                line,
            )
        assert exception is not None
        name = exception.group("qualified").rsplit(".", 1)[-1]
        kind, title, hint = _csharp_runtime(name, exception.group("msg") or "")
        return _Finding(kind, title, hint, text, line)
    return None


def _csharp_message(code: str, message: str) -> tuple[str, str, str]:
    if code == "CS1002":
        return (
            "syntax",
            f"C# expected a semicolon (;) at the end of {_LN}.",
            f"Add `;` at the end of {_LN}, then run again.",
        )
    if code in _CS_SYNTAX or code.startswith("CS10") or code == "CS1525":
        return (
            "syntax",
            f"C# could not understand how {_LN} is written (a syntax error).",
            "Check for a missing semicolon, bracket, parenthesis or quote near the marked spot.",
        )
    if found := re.match(r"The name '([^']+)' does not exist in the current context", message):
        return (
            "compile",
            f"C# does not know the name {_code(found.group(1))}{_AT}.",
            _name_hint(None, "declare it with a type or `var`"),
        )
    if found := re.match(r"Cannot implicitly convert type '([^']+)' to '([^']+)'", message):
        source_type, target = found.group(1), found.group(2)
        hint = (
            "Use a value of the declared type, or convert it, for example `int.Parse(text)`."
            if (source_type, target) == ("string", "int")
            else "Use a value of the declared type, or convert it explicitly."
        )
        return (
            "compile",
            f"{_LNC} puts {_an(source_type)} where {_an(target)} is required.",
            hint,
        )
    if found := re.match(r"The type or namespace name '([^']+)' could not be found", message):
        return (
            "compile",
            f"C# cannot find a type named {_code(found.group(1))}{_AT}.",
            "Check the spelling, or add the missing `using` line at the top.",
        )
    if found := re.match(r"'([^']+)' does not contain a definition for '([^']+)'", message):
        return (
            "compile",
            f"{_code(found.group(1))} has no member named {_code(found.group(2))}{_AT}.",
            "Check the spelling and capitalization of the member name.",
        )
    if found := re.match(r"Use of unassigned local variable '([^']+)'", message):
        return (
            "compile",
            f"{_code(found.group(1))} is used{_AT} before it has a value.",
            "Give the variable a value when you declare it.",
        )
    return (
        "compile",
        f"The C# compiler could not compile {_LN} (error {code}).",
        "Read the first error message below. Later errors often follow from the first one.",
    )


def _csharp_runtime(name: str, message: str) -> tuple[str, str, str]:
    if name in {"IndexOutOfRangeException", "ArgumentOutOfRangeException"}:
        return (
            "runtime",
            f"{_LNC} asks for a position that does not exist.",
            "Positions start at 0, so an array of length 2 has positions 0 and 1.",
        )
    if name == "NullReferenceException":
        return (
            "runtime",
            f"{_LNC} uses a value that is `null`.",
            "Make sure the variable refers to an object before using its members.",
        )
    if name == "DivideByZeroException":
        return (
            "runtime",
            f"{_LNC} divides a whole number by zero.",
            "Make sure the number you divide by is not 0 before dividing.",
        )
    if name == "FormatException":
        return (
            "runtime",
            f"Text could not be converted to the requested type{_AT}.",
            "Check the text before converting it, or use `int.TryParse`.",
        )
    if name == "KeyNotFoundException":
        return (
            "runtime",
            f"The dictionary has no entry for the requested key{_AT}.",
            "Check the key, or use `TryGetValue` to handle a missing key.",
        )
    return (
        "runtime",
        f"The program stopped{_AT} with {_an(name)}.",
        "Read the message below, then check the values used on that line.",
    )


# Go -------------------------------------------------------------------------

_GO_COMPILE = re.compile(r"^(?P<file>[^\s:]+\.go):(?P<line>\d+):(?P<col>\d+): (?P<msg>.+)$")
_GO_PANIC = re.compile(r"^(?:panic|fatal error): (?P<msg>.+)$")
_GO_FRAME = re.compile(r"^\t(?P<file>\S+\.go):(?P<line>\d+)(?: \+0x[0-9a-f]+)?$")


def _go(lines: list[str], context: _Context, output: str) -> _Finding | None:
    for text in lines:
        match = _GO_COMPILE.match(text)
        if not match:
            continue
        learner = context.is_learner(match.group("file"))
        line = int(match.group("line")) if learner else None
        column = int(match.group("col")) if learner else None
        kind, title, hint = _go_message(match.group("msg"))
        return _Finding(kind, title, hint, text, line, column)
    for index, text in enumerate(lines):
        match = _GO_PANIC.match(text)
        if not match:
            continue
        line = None
        for frame_text in lines[index + 1 :]:
            frame = _GO_FRAME.match(frame_text)
            if frame and context.is_learner(frame.group("file")):
                line = int(frame.group("line"))
                break
        kind, title, hint = _go_runtime(match.group("msg"))
        return _Finding(kind, title, hint, text, line)
    return None


def _go_message(message: str) -> tuple[str, str, str]:
    if message.startswith("syntax error"):
        detail = message.removeprefix("syntax error: ")
        if "possibly missing comma or )" in detail:
            return (
                "syntax",
                f"Go could not read {_LN}. A comma or closing parenthesis `)` may be missing.",
                "Close the call with `)`, or separate the arguments with commas, then run again.",
            )
        return (
            "syntax",
            f"Go could not understand how {_LN} is written (a syntax error).",
            "Check for a missing bracket, brace, comma or quote near the marked spot.",
        )
    if found := re.match(r"undefined: (\S+)", message):
        return (
            "compile",
            f"Go does not know the name {_code(found.group(1))}{_AT}.",
            _name_hint(None, "declare it"),
        )
    if found := re.match(r"declared and not used: (\S+)", message):
        return (
            "compile",
            f"The variable {_code(found.group(1))} is created{_AT} but never used, and Go "
            "does not allow unused variables.",
            "Use the variable, or delete the line. While you work, you can write "
            f"`_ = {found.group(1)}`.",
        )
    if found := re.match(r'"([^"]+)" imported and not used', message):
        return (
            "compile",
            f"The package {_code(found.group(1))} is imported{_AT} but never used, and Go does "
            "not allow unused imports.",
            "Delete that import line, or use the package in the program.",
        )
    if found := re.match(r"cannot use .+? \((?:untyped )?(\w+).*?\) as (\w+) value", message):
        return (
            "compile",
            f"{_LNC} uses {_an(found.group(1))} value where {_an(found.group(2))} is required.",
            "Use a value of the required type, or convert it explicitly.",
        )
    if message.startswith("missing return"):
        return (
            "compile",
            f"A function that promises a value can finish without returning one{_AT}.",
            "Add a `return` statement at the end of the function.",
        )
    return (
        "compile",
        f"The Go compiler could not compile {_LN}.",
        "Read the first error message below. Later errors often follow from the first one.",
    )


def _go_runtime(message: str) -> tuple[str, str, str]:
    if found := re.search(r"index out of range \[(-?\d+)\] with length (\d+)", message):
        return (
            "runtime",
            f"{_LNC} asks for position {found.group(1)}, but there are only {found.group(2)} "
            "items.",
            "Positions start at 0, so the last valid position is the length minus 1.",
        )
    if "nil pointer dereference" in message:
        return (
            "runtime",
            f"{_LNC} uses a pointer that is `nil`.",
            "Make sure the pointer refers to a value before using it.",
        )
    if "integer divide by zero" in message:
        return (
            "runtime",
            f"{_LNC} divides a whole number by zero.",
            "Make sure the number you divide by is not 0 before dividing.",
        )
    if "assignment to entry in nil map" in message:
        return (
            "runtime",
            f"{_LNC} writes to a map that was never created.",
            "Create the map first, for example `counts := make(map[string]int)`.",
        )
    if "deadlock" in message:
        return (
            "runtime",
            "All goroutines are waiting for each other, so the program can never continue "
            "(a deadlock).",
            "Make sure every channel receive has a matching send, or close the channel.",
        )
    return (
        "runtime",
        f"The program stopped with a panic (a fatal error){_AT}.",
        "Read the panic message below, then check the values used on that line.",
    )


# Rust -----------------------------------------------------------------------

_RUST_ERROR = re.compile(r"^error(?:\[(?P<code>E\d{4})\])?: (?P<msg>.+)$")
_RUST_LOCATION = re.compile(r"^\s*--> (?P<file>[^\s:]+):(?P<line>\d+):(?P<col>\d+)$")
_RUST_PANIC = re.compile(
    r"^thread '[^']*'(?: \(\d+\))? panicked at (?P<file>[^\s:]+):(?P<line>\d+):(?P<col>\d+):$"
)


def _rust(lines: list[str], context: _Context, output: str) -> _Finding | None:
    for index, text in enumerate(lines):
        match = _RUST_ERROR.match(text)
        if not match or match.group("msg").startswith("aborting due to"):
            continue
        line = column = None
        for location_text in lines[index + 1 : index + 4]:
            location = _RUST_LOCATION.match(location_text)
            if location:
                if context.is_learner(location.group("file")):
                    line, column = int(location.group("line")), int(location.group("col"))
                break
        details = "\n".join(lines[index + 1 : index + 16])
        kind, title, hint = _rust_message(match.group("code"), match.group("msg"), details)
        return _Finding(kind, title, hint, text, line, column)
    for index, text in enumerate(lines):
        match = _RUST_PANIC.match(text)
        if not match:
            continue
        learner = context.is_learner(match.group("file"))
        message = lines[index + 1] if index + 1 < len(lines) else ""
        kind, title, hint = _rust_panic(message, lines[index + 2 : index + 4])
        return _Finding(
            kind,
            title,
            hint,
            message or text,
            int(match.group("line")) if learner else None,
            int(match.group("col")) if learner else None,
        )
    return None


def _rust_message(code: str | None, message: str, details: str) -> tuple[str, str, str]:
    if code is None:
        if found := re.match(r"expected `([^`]+)`, found `([^`]+)`", message):
            symbol = found.group(1)
            if symbol == ";":
                return (
                    "syntax",
                    f"Rust expected a semicolon (;) at the end of {_LN}.",
                    f"Add `;` at the end of {_LN}, then run again.",
                )
            return (
                "syntax",
                f"Rust expected {_code(symbol)} but found {_code(found.group(2))}{_AT}.",
                "Add the missing symbol, and check the brackets and semicolons nearby.",
            )
        return (
            "syntax",
            f"Rust could not understand how {_LN} is written (a syntax error).",
            "Check for a missing semicolon, bracket or quote near the marked spot.",
        )
    if code == "E0308":
        found = re.search(r"expected `([^`]+)`, found `([^`]+)`", details)
        if found:
            return (
                "compile",
                f"{_LNC} has {_an(found.group(2))} value where Rust expected "
                f"{_an(found.group(1))}.",
                "Use a value of the expected type, or convert it, for example with `.parse()` "
                "or `.to_string()`.",
            )
        return (
            "compile",
            f"{_LNC} has a value of the wrong type.",
            "Compare the expected and found types in the message below.",
        )
    if code in {"E0425", "E0412", "E0433"}:
        found = re.search(r"`([^`]+)`", message)
        similar = "similar name exists" in details
        return (
            "compile",
            f"Rust does not know the name {_code(found.group(1) if found else '?')}{_AT}.",
            "A similar name exists, so check the spelling, then run again."
            if similar
            else _name_hint(None, "declare it with `let`"),
        )
    if code == "E0382":
        found = re.search(r"`([^`]+)`", message)
        target = _code(found.group(1)) if found else "A value"
        return (
            "compile",
            f"{_LNC} uses {target} after its value was moved to another variable.",
            "Borrow it with `&` instead of moving it, or call `.clone()` when you need a "
            "second copy.",
        )
    if code == "E0384":
        return (
            "compile",
            f"{_LNC} changes a variable that was not declared as changeable.",
            "Declare it with `let mut` if its value needs to change.",
        )
    if code in {"E0499", "E0502", "E0505", "E0506"}:
        return (
            "compile",
            f"{_LNC} uses a value while it is borrowed somewhere else.",
            "Finish using the first borrow before the second one, or clone the value.",
        )
    if code == "E0599":
        return (
            "compile",
            f"{_LNC} calls a method that this type does not have.",
            "Check the method name and the type of the value, shown in the message below.",
        )
    return (
        "compile",
        f"The Rust compiler found a problem on {_LN} (error {code}).",
        "Read the explanation below. The `help:` lines often show the exact change to make.",
    )


def _rust_panic(message: str, following: list[str]) -> tuple[str, str, str]:
    if found := re.search(r"the len is (\d+) but the index is (\d+)", message):
        return (
            "runtime",
            f"{_LNC} asks for position {found.group(2)}, but there are only {found.group(1)} "
            "items.",
            "Positions start at 0, so the last valid position is the length minus 1.",
        )
    if message.startswith("assertion `left == right` failed"):
        left = next((t.split(":", 1)[1].strip() for t in following if "left:" in t), "")
        right = next((t.split(":", 1)[1].strip() for t in following if "right:" in t), "")
        detail = f": the left side was {_code(left)} and the right side was {_code(right)}"
        return (
            "assertion",
            f"The `assert_eq!` check{_AT} failed" + (detail if left and right else "") + ".",
            "Compare the two values, then fix the code that computes the one that is wrong.",
        )
    if message.startswith("assertion"):
        return (
            "assertion",
            f"The `assert!` check{_AT} failed.",
            "Compare the condition with what the program computes, then fix the calculation.",
        )
    if "unwrap()` on a `None` value" in message:
        return (
            "runtime",
            f"{_LNC} calls `.unwrap()` on a `None` value.",
            "Handle the missing value with `match` or `if let` instead of `.unwrap()`.",
        )
    if "unwrap()` on an `Err` value" in message:
        return (
            "runtime",
            f"{_LNC} calls `.unwrap()` on an error result.",
            "Handle the error with `match`, or check the input that caused it.",
        )
    if "divide by zero" in message:
        return (
            "runtime",
            f"{_LNC} divides by zero.",
            "Make sure the number you divide by is not 0 before dividing.",
        )
    if "overflow" in message:
        return (
            "runtime",
            f"A number{_AT} became too large or too small for its type.",
            "Use a larger number type such as `i64`, or check the values before the calculation.",
        )
    return (
        "runtime",
        f"The program panicked (stopped with a fatal error){_AT}.",
        "Read the panic message below, then check the values used on that line.",
    )


# Swift ----------------------------------------------------------------------

_SWIFT_ERROR = re.compile(
    r"^(?P<file>[^\s:]+\.swift):(?P<line>\d+):(?P<col>\d+): error: (?P<msg>.+)$"
)
_SWIFT_FATAL = re.compile(
    r"^(?P<file>[^\s:]+\.swift):(?P<line>\d+): "
    r"(?P<what>Fatal error|Precondition failed|Assertion failed)(?::\s?(?P<msg>.*))?$"
)


def _swift(lines: list[str], context: _Context, output: str) -> _Finding | None:
    for text in lines:
        match = _SWIFT_ERROR.match(text)
        if not match:
            continue
        learner = context.is_learner(match.group("file"))
        kind, title, hint = _swift_message(match.group("msg"))
        return _Finding(
            kind,
            title,
            hint,
            text,
            int(match.group("line")) if learner else None,
            int(match.group("col")) if learner else None,
        )
    for text in lines:
        match = _SWIFT_FATAL.match(text)
        if not match:
            continue
        line = int(match.group("line")) if context.is_learner(match.group("file")) else None
        message = match.group("msg") or ""
        if match.group("what") != "Fatal error":
            return _Finding(
                "assertion",
                f"A `{'precondition' if match.group('what').startswith('Pre') else 'assert'}` "
                f"check failed{_AT}.",
                "Read the check's message below, then fix the value it tests.",
                text,
                line,
            )
        if "Index out of range" in message:
            title, hint = (
                f"The program asked for an array position that does not exist{_AT}.",
                "Positions start at 0. Check the position against the array's `count`.",
            )
        elif "Unexpectedly found nil" in message:
            title, hint = (
                f"The program unwrapped an optional value that was `nil`{_AT}.",
                "Use `if let` or `guard let` to handle a missing value instead of `!`.",
            )
        elif "Division by zero" in message:
            title, hint = (
                f"The program divided by zero{_AT}.",
                "Make sure the number you divide by is not 0 before dividing.",
            )
        else:
            title, hint = (
                f"The program stopped with a fatal error{_AT}.",
                "Read the message below, then check the values used where it stopped.",
            )
        return _Finding("runtime", title, hint, text, line)
    return None


def _swift_message(message: str) -> tuple[str, str, str]:
    if found := re.match(r"cannot find '([^']+)' in scope", message):
        return (
            "compile",
            f"Swift does not know the name {_code(found.group(1))}{_AT}.",
            _name_hint(None, "declare it with `let` or `var`"),
        )
    if found := re.match(
        r"cannot convert value of type '([^']+)' to (?:specified )?type '([^']+)'", message
    ):
        return (
            "compile",
            f"{_LNC} has {_an(found.group(1))} value where {_an(found.group(2))} is required.",
            "Use a value of the required type, or convert it, for example `Int(text)`.",
        )
    if message.startswith(("expected", "consecutive statements", "unterminated", "extraneous")):
        return (
            "syntax",
            f"Swift could not understand how {_LN} is written (a syntax error).",
            "Check for a missing bracket, brace, parenthesis or quote near the marked spot.",
        )
    return (
        "compile",
        f"The Swift compiler could not compile {_LN}.",
        "Read the first error message below. Later errors often follow from the first one.",
    )


# PHP ------------------------------------------------------------------------

_PHP_PARSE = re.compile(
    r"^(?:PHP )?Parse error: +(?P<msg>.+?) in (?P<file>\S+) on line (?P<line>\d+)$"
)
_PHP_FATAL = re.compile(
    r"^(?:PHP )?Fatal error: +(?:Uncaught (?P<qualified>[\w\\]+): )?(?P<msg>.+?)"
    r"(?: in (?P<file>\S+?)(?::(?P<line>\d+)| on line (?P<on>\d+)))?$"
)


def _php(lines: list[str], context: _Context, output: str) -> _Finding | None:
    for text in lines:
        match = _PHP_PARSE.match(text)
        if not match:
            continue
        line = int(match.group("line")) if context.is_learner(match.group("file")) else None
        message = match.group("msg")
        if found := re.search(r'unexpected token "([^"]+)", expecting "," or ";"', message):
            title, hint = (
                f"PHP expected `;` before {_code(found.group(1))}{_AT}.",
                "A semicolon is probably missing at the end of the previous statement. Add `;` "
                "there, then run again.",
            )
        elif "unexpected end of file" in message:
            title, hint = (
                "PHP reached the end of the file while a block or text was still open.",
                "Check for a missing `}` or a missing closing quote.",
            )
        else:
            title, hint = (
                f"PHP could not understand how {_LN} is written (a syntax error).",
                "Check for a missing semicolon, bracket or quote on this line or the line "
                "before it.",
            )
        return _Finding("syntax", title, hint, text, line)
    for text in lines:
        match = _PHP_FATAL.match(text)
        if not match:
            continue
        message = match.group("msg")
        file_name = match.group("file") or ""
        number = match.group("line") or match.group("on")
        line = int(number) if number and context.is_learner(file_name) else None
        called = re.search(r"called in (\S+) on line (\d+)", message)
        if called and context.is_learner(called.group(1)):
            line = int(called.group(2))
        kind, title, hint = _php_message((match.group("qualified") or "Error"), message)
        return _Finding(kind, title, hint, text, line)
    return None


def _php_message(name: str, message: str) -> tuple[str, str, str]:
    if found := re.match(r"Call to undefined function (\S+?)\(\)", message):
        return (
            "runtime",
            f"PHP has no function named {_code(found.group(1) + '()')}{_AT}.",
            "Check the spelling, or define the function with `function name(...) { ... }`.",
        )
    if name.endswith("TypeError") and (
        found := re.match(
            r"(\S+?)\(\): Argument #\d+ \((\$\w+)\) must be of type (\S+), (\S+) given", message
        )
    ):
        return (
            "runtime",
            f"The call to {_code(found.group(1) + '()')}{_AT} passes {_an(found.group(4))} "
            f"for {_code(found.group(2))}, which must be {_an(found.group(3))}.",
            "Pass a value of the required type, or convert it first, for example with `(int)`.",
        )
    if name.endswith("AssertionError"):
        return (
            "assertion",
            f"The `assert` check{_AT} failed.",
            "Read the assertion message below, then fix the value it checks.",
        )
    if name.endswith("DivisionByZeroError"):
        return (
            "runtime",
            f"{_LNC} divides by zero.",
            "Make sure the number you divide by is not 0 before dividing.",
        )
    if name.endswith("ArgumentCountError"):
        return (
            "runtime",
            f"A function call{_AT} passes the wrong number of values.",
            "Match the values in the call to the parameters in the function's definition.",
        )
    if message.startswith("Allowed memory size"):
        return (
            "runtime",
            "The program used more memory than PHP allows.",
            "Use less data at once, for example smaller arrays, then run again.",
        )
    return (
        "runtime",
        f"PHP stopped with a fatal error{_AT}.",
        "Read the message below, then check the values used on that line.",
    )


# R --------------------------------------------------------------------------

_R_ERROR = re.compile(r"^Error(?: in (?P<call>.+?))? ?: (?P<msg>.*)$")
_R_PARSE = re.compile(r"^\s*(?P<file>[^\s:]+):(?P<line>\d+):(?P<col>\d+): (?P<msg>unexpected .+)$")


def _r(lines: list[str], context: _Context, output: str) -> _Finding | None:
    for text in lines:
        match = _R_PARSE.match(text)
        if match and context.is_learner(match.group("file")):
            what = match.group("msg").removeprefix("unexpected ")
            hint = (
                "Add the missing closing `)`, `]` or `}`, or the closing quote, at the end of "
                "the expression."
                if what == "end of input"
                else "Check this line for a missing operator, comma or parenthesis between two "
                "parts."
            )
            return _Finding(
                "syntax",
                f"R could not read {_LN}: it found an unexpected {_plain_r(what)}.",
                hint,
                text,
                int(match.group("line")),
                int(match.group("col")),
            )
    for index, text in enumerate(lines):
        match = _R_ERROR.match(text)
        if not match:
            continue
        message = match.group("msg").strip()
        if not message and index + 1 < len(lines):
            message = lines[index + 1].strip()
        kind, title, hint = _r_message(message, match.group("call"))
        return _Finding(kind, title, hint, text if match.group("msg").strip() else message)
    return None


def _plain_r(what: str) -> str:
    return {
        "symbol": "name",
        "string constant": "text value",
        "numeric constant": "number",
        "input": "character",
    }.get(what, _code(what.strip("'")) if what.startswith("'") else what)


def _r_message(message: str, call: str | None) -> tuple[str, str, str]:
    if found := re.match(r"object '([^']+)' not found", message):
        return (
            "runtime",
            f"R cannot find an object (a variable) named {_code(found.group(1))}.",
            "Check the spelling and capitalization, or create it with `<-` before it is used.",
        )
    if found := re.match(r'could not find function "([^"]+)"', message):
        return (
            "runtime",
            f"R cannot find a function named {_code(found.group(1))}.",
            "Check the spelling, or load the package that provides it with `library(...)`.",
        )
    if found := re.match(r"there is no package called [‘']([^’']+)[’']", message):
        return (
            "runtime",
            f"R cannot find a package named {_code(found.group(1))}.",
            "Check the spelling. Pads cannot install packages, so use the packages this runtime "
            "provides.",
        )
    if re.search(r" (?:is|are) not (?:all )?TRUE$", message):
        return (
            "assertion",
            f"A `stopifnot` check failed: {_code(message.rsplit(' is not', 1)[0])} is not TRUE.",
            "Compare the values in the check with what the code computes, then fix the "
            "calculation.",
        )
    if "non-numeric argument to binary operator" in message:
        return (
            "runtime",
            "R tried to do arithmetic with a value that is not a number.",
            "Check that both values are numbers. Convert text with `as.numeric(...)`.",
        )
    if "subscript out of bounds" in message:
        return (
            "runtime",
            "The code asks for a position or name that does not exist.",
            "R positions start at 1. Check the position against `length(...)`.",
        )
    if "missing value where TRUE/FALSE needed" in message:
        return (
            "runtime",
            "An `if` or `while` condition was `NA` instead of TRUE or FALSE.",
            "Check for missing values first, for example with `is.na(...)`.",
        )
    where = f" in {_code(call)}" if call and not call.startswith(("eval(", "source(")) else ""
    return (
        "runtime",
        f"R stopped with an error{where}.",
        "Read the error message below, then check the values used in that expression.",
    )


# Julia ----------------------------------------------------------------------

_JL_ERROR = re.compile(r"^ERROR: (?:LoadError: )?(?P<name>[A-Z]\w*)(?::\s?(?P<msg>.*))?$")
_JL_FRAME = re.compile(r"^\s*@ (?:\w+ )?(?P<file>\S+):(?P<line>\d+)(?: \[inlined\])?$")
_JL_PARSE_AT = re.compile(r"^# Error @ (?P<file>\S+):(?P<line>\d+):(?P<col>\d+)$")


def _julia(lines: list[str], context: _Context, output: str) -> _Finding | None:
    for index, text in enumerate(lines):
        match = _JL_ERROR.match(text)
        if not match:
            continue
        name, message = match.group("name"), (match.group("msg") or "").strip()
        line = column = None
        raw = text
        if name == "ParseError":
            for detail_index, detail in enumerate(lines[index + 1 : index + 6], index + 1):
                at = _JL_PARSE_AT.match(detail)
                if at and context.is_learner(at.group("file")):
                    line, column = int(at.group("line")), int(at.group("col"))
                    marker = lines[detail_index + 2] if detail_index + 2 < len(lines) else ""
                    message = marker.lstrip("#").strip(" └┘╙╜─-") or message
                    raw = marker if message else raw
                    break
        else:
            for frame_text in lines[index + 1 :]:
                frame = _JL_FRAME.match(frame_text)
                if frame and context.is_learner(frame.group("file")):
                    line = int(frame.group("line"))
                    break
        kind, title, hint = _julia_message(name, message)
        return _Finding(kind, title, hint, raw, line, column)
    return None


def _julia_message(name: str, message: str) -> tuple[str, str, str]:
    if name == "ParseError":
        return (
            "syntax",
            f"Julia could not read {_LN}"
            + (f": {message[0].lower()}{message[1:]}." if message else "."),
            "Add the missing bracket, comma or keyword such as `end`, then run again.",
        )
    if name == "UndefVarError":
        found = re.search(r"`([^`]+)` not defined", message)
        return (
            "runtime",
            f"Julia does not know the name {_code(found.group(1) if found else '?')}{_AT}.",
            _name_hint(None, "give it a value"),
        )
    if name == "MethodError":
        found = re.search(r"no method matching (.+?)\((.*)\)", message)
        if found:
            types = [t.strip(" :") for t in found.group(2).split(",") if t.strip()]
            values = " and ".join(_code(t) for t in types[:3])
            return (
                "runtime",
                f"Julia has no way to use {_code(found.group(1))} with {values or 'these values'}"
                f"{_AT}.",
                "Convert a value so the types fit, for example `parse(Int, text)` or "
                "`string(number)`.",
            )
    if name == "AssertionError":
        return (
            "assertion",
            f"The `@assert` check{_AT} failed.",
            "Compare the condition with what the program computes, then fix the calculation.",
        )
    if name == "BoundsError":
        return (
            "runtime",
            f"{_LNC} asks for a position that does not exist.",
            "Julia positions start at 1. Check the position against `length(...)`.",
        )
    if name == "DivideError":
        return (
            "runtime",
            f"{_LNC} divides a whole number by zero.",
            "Make sure the number you divide by is not 0 before dividing.",
        )
    if name == "ArgumentError" and (found := re.match(r"Package (\S+) not found", message)):
        return (
            "runtime",
            f"Julia cannot find a package named {_code(found.group(1))}{_AT}.",
            "Check the spelling. Pads cannot install packages, so use the packages this runtime "
            "provides.",
        )
    if name == "KeyError":
        return (
            "runtime",
            f"The key was not found{_AT}.",
            "Check the key's spelling, or use `get(dict, key, default)`.",
        )
    return (
        "runtime",
        f"The program stopped{_AT} with {_an(name)}.",
        "Read the message below, then check the values used on that line.",
    )


# Stan -----------------------------------------------------------------------

_STAN_ERROR = re.compile(
    r"^(?P<what>Syntax|Semantic) error in '(?P<file>[^']+)', line (?P<line>\d+), "
    r"column (?P<col>\d+)"
)
_STAN_RUNTIME = re.compile(
    r"^\s*(?:Exception|Error): (?P<msg>.+?) \(in '(?P<file>[^']+)', line (?P<line>\d+), "
    r"column (?P<col>\d+)"
)


def _stan(lines: list[str], context: _Context, output: str) -> _Finding | None:
    for index, text in enumerate(lines):
        match = _STAN_ERROR.match(text)
        if not match:
            continue
        learner = context.is_learner(match.group("file"))
        line = int(match.group("line")) if learner else None
        column = int(match.group("col")) + 1 if learner else None  # Stan columns start at 0.
        rules = [i for i in range(index + 1, len(lines)) if lines[i].strip().startswith("---")]
        start = rules[1] + 1 if len(rules) > 1 else index + 1
        message = next((t.strip() for t in lines[start:] if t.strip()), text)
        if found := re.search(r'Identifier "([^"]+)" not in scope', message):
            title, hint = (
                f"Stan does not know the name {_code(found.group(1))}{_AT}.",
                "Declare it first, for example in the `data` or `parameters` block, or check "
                "the spelling.",
            )
        elif 'Expected ";"' in message:
            title, hint = (
                "Stan expected a semicolon (;) after a statement or declaration.",
                f"Add `;` at the end of the statement just before {_LN}, then run again.",
            )
        elif match.group("what") == "Syntax":
            title, hint = (
                f"Stan could not read the model{_AT} (a syntax error).",
                "Read the message below the marked code. It says what Stan expected.",
            )
        else:
            title, hint = (
                f"Stan found a problem in the model{_AT}.",
                "Read the message below the marked code, then fix the names or types it mentions.",
            )
        kind = "syntax" if match.group("what") == "Syntax" else "compile"
        return _Finding(kind, title, hint, message, line, column)
    for text in lines:
        match = _STAN_RUNTIME.match(text)
        if match:
            learner = context.is_learner(match.group("file"))
            return _Finding(
                "runtime",
                f"Stan stopped the model{_AT} with the message {_code(match.group('msg'))}.",
                "A `reject` call or an invalid value, such as a negative scale, stops the "
                "model. Check the values used on that line.",
                text,
                int(match.group("line")) if learner else None,
                int(match.group("col")) + 1 if learner else None,
            )
    return None


# Node JavaScript and TypeScript ---------------------------------------------

_NODE_HEADER = re.compile(r"^(?P<file>(?:file://)?/\S+?|node:\S+?):(?P<line>\d+)$")
# Node opens an error's extra properties with " {" after the last stack line.
_NODE_ERROR = re.compile(
    r"^(?:Uncaught )?(?P<name>(?:[A-Z]\w*)?Error)(?: \[(?P<code>[A-Z0-9_]+)\])?: "
    r"(?P<msg>.*?)(?P<props> \{)?$"
)
_NODE_FRAME = re.compile(
    r"^\s+at (?:.*?\()?(?P<file>(?:file://)?[^\s()]+?):(?P<line>\d+):(?P<col>\d+)\)?(?: \{)?$"
)
_TSC = re.compile(
    r"^(?P<file>\S+?)\((?P<line>\d+),(?P<col>\d+)\): error (?P<code>TS\d+): (?P<msg>.+)$"
)


def _node(lines: list[str], context: _Context, output: str) -> _Finding | None:
    for index, text in enumerate(lines):
        match = _NODE_ERROR.match(text)
        if not match:
            continue
        line = column = None
        for frame_text in lines[index + 1 :]:
            frame = _NODE_FRAME.match(frame_text)
            if frame and context.is_learner(frame.group("file")):
                line, column = int(frame.group("line")), int(frame.group("col"))
                break
        if line is None:
            for header_index, header_text in enumerate(lines[:index]):
                header = _NODE_HEADER.match(header_text)
                if header and context.is_learner(header.group("file")):
                    line = int(header.group("line"))
                    column = _caret_column(lines, header_index, context.source_line(line))
                    break
        kind, title, hint = _node_message(
            match.group("name"), match.group("code"), match.group("msg")
        )
        raw = text[: match.start("props")] if match.group("props") else text
        return _Finding(kind, title, hint, raw, line, column)
    return None


def _node_message(name: str, code: str | None, message: str) -> tuple[str, str, str]:
    if name == "SyntaxError":
        if message.startswith("missing ) after argument list"):
            return (
                "syntax",
                f"JavaScript expected a closing parenthesis `)`{_AT}.",
                "Close the function call with `)` before the end of the statement.",
            )
        return (
            "syntax",
            f"JavaScript could not understand how {_LN} is written (a syntax error).",
            "Check for a missing bracket, brace, comma or quote near the marked spot.",
        )
    if name == "ReferenceError" and (found := re.match(r"(\S+) is not defined", message)):
        return (
            "runtime",
            f"JavaScript does not know the name {_code(found.group(1))}{_AT}.",
            _name_hint(None, "declare it with `const` or `let`"),
        )
    if found := re.match(
        r"Cannot read properties of (undefined|null) \(reading '([^']*)'\)", message
    ):
        return (
            "runtime",
            f"{_LNC} reads {_code('.' + found.group(2))} from a value that is "
            f"{_code(found.group(1))}.",
            "Check that the value was set before this line uses it.",
        )
    if found := re.match(r"(\S+) is not a function", message):
        return (
            "runtime",
            f"{_LNC} calls {_code(found.group(1))} as a function, but it is not one.",
            "Check the spelling of the method name, and the type of the value before the dot.",
        )
    if name == "AssertionError":
        return (
            "assertion",
            f"The `assert` check{_AT} failed.",
            "Compare the actual and expected values shown below, then fix the code that "
            "computes the actual value.",
        )
    if code == "ERR_MODULE_NOT_FOUND" and (
        found := re.search(r"Cannot find (?:package|module) '([^']+)'", message)
    ):
        return (
            "runtime",
            f"Node cannot find the package {_code(found.group(1))}.",
            "Pads cannot install npm packages. Use built-in `node:` modules, such as "
            "`node:assert`.",
        )
    if name == "RangeError" and "call stack" in message:
        return (
            "runtime",
            f"A function kept calling itself until the program ran out of stack space{_AT}.",
            "Make sure the recursive function has a base case that stops calling itself.",
        )
    return (
        "runtime",
        f"The program stopped{_AT} with {_an(name)}.",
        "Read the message below, then check the values used on that line.",
    )


def _typescript(lines: list[str], context: _Context, output: str) -> _Finding | None:
    for text in lines:
        match = _TSC.match(text)
        if not match:
            continue
        learner = context.is_learner(match.group("file"))
        kind, title, hint = _typescript_message(match.group("code"), match.group("msg"))
        return _Finding(
            kind,
            title,
            hint,
            text,
            int(match.group("line")) if learner else None,
            int(match.group("col")) if learner else None,
        )
    return _node(lines, context, output)


def _typescript_message(code: str, message: str) -> tuple[str, str, str]:
    if code.startswith("TS1"):
        return (
            "syntax",
            f"TypeScript could not understand how {_LN} is written (a syntax error).",
            "Check for a missing value, bracket, comma or semicolon near the marked spot.",
        )
    if found := re.match(r"Type '(.+?)' is not assignable to type '(.+?)'\.", message):
        return (
            "compile",
            f"{_LNC} puts {_an(found.group(1))} value where {_an(found.group(2))} is required.",
            "Change the value to the declared type, or change the type if the value is right.",
        )
    if found := re.match(r"Cannot find name '([^']+)'", message):
        return (
            "compile",
            f"TypeScript does not know the name {_code(found.group(1))}{_AT}.",
            _name_hint(_suggestion(message), "declare it with `const` or `let`"),
        )
    if found := re.match(
        r"Argument of type '(.+?)' is not assignable to parameter of type '(.+?)'", message
    ):
        return (
            "compile",
            f"A call{_AT} passes {_an(found.group(1))} where {_an(found.group(2))} is required.",
            "Pass a value of the parameter's type, or convert it before the call.",
        )
    if found := re.match(r"Property '([^']+)' does not exist on type '(.+?)'", message):
        return (
            "compile",
            f"The type {_code(found.group(2))} has no property named {_code(found.group(1))}{_AT}.",
            _name_hint(_suggestion(message), "add the property to the type"),
        )
    if found := re.match(r"Expected (\d+) arguments?, but got (\d+)", message):
        return (
            "compile",
            f"A call{_AT} passes {found.group(2)} values, but the function needs {found.group(1)}.",
            "Match the values in the call to the function's parameters.",
        )
    if found := re.match(r"'([^']+)' is possibly '(undefined|null)'", message):
        return (
            "compile",
            f"{_code(found.group(1))} might be {_code(found.group(2))}{_AT}.",
            "Check the value first, for example with `if (value !== undefined)`.",
        )
    return (
        "compile",
        f"TypeScript found a type problem on {_LN} before running the code.",
        "Read the message below. The code runs only after every type error is fixed.",
    )


_PARSERS: dict[str, Callable[[list[str], _Context, str], _Finding | None]] = {
    "python": _python,
    "sql": _sql,
    "dbt": _dbt,
    "jvm": _jvm,
    "c": _gcc,
    "csharp": _csharp,
    "go": _go,
    "rust": _rust,
    "swift": _swift,
    "php": _php,
    "r": _r,
    "julia": _julia,
    "stan": _stan,
    "node": _node,
    "typescript": _typescript,
}
