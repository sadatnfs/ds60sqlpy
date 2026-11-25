#!/usr/bin/env python3
"""Run the fenced code examples in every lesson companion guide.

Each guide named by curriculum/coverage-matrix.json is split into fenced blocks
with the classroom reader's own fence rules. Every block is then one of:

* documentation (text, DAX, HTML, shell transcripts and similar): recorded, not run;
* statically checked on the host (``bash -n``, JSON, YAML and XML parsing);
* run against a disposable PostgreSQL database (SQL track blocks), one cumulative
  script per guide; a block that fails there but is a verbatim excerpt of its own
  lesson file (ignoring comments and whitespace) passes as an excerpt, because CI
  runs every SQL lesson in full with ON_ERROR_STOP;
* run in its lesson's worker image, either as one cumulative session per guide
  and language (Python, R and Julia, so later blocks see earlier definitions) or
  as one complete program per block (compiled and scripting languages);
* compiled with stanc (Stan models).

Python lessons that need the advanced extras (ml, production, deep-learning,
nlp, geo) use the ``python-advanced`` profile. No published worker image
carries those extras, so these sessions run on the host with the interpreter
named by --advanced-python (an environment synced with every extra, as in CI).
Without that option they are reported as skipped.

A fence may carry one annotation after its language tag: ``fragment`` for an
intentionally partial excerpt (reported, not run), ``external`` for code that
needs a browser, GPU, cluster, network, secret or a prepared local artifact such
as a trained model (reported, not run), ``expect-error`` for code that must fail
and ``isolated`` for a complete program that must start in a fresh session
because it sets process-wide state (Django settings, say). A Python, R or Scala
fence may also name a companion file with ``prelude=<path relative to the
guide>``: its definitions load into the session before the block. A Python
prelude skips its ``__main__`` entry point; an R or Scala prelude runs in full,
so it should only define things. A fence may also name the worker profile that runs it
with ``profile=<name>``, for a block whose lesson image lacks its libraries (a
pandas sketch in a Spark lesson, say).

Python sessions that read ``DS60_DATABASE_URL`` need the course database. With
--database-container (a PostgreSQL container started with ``--network none``)
the harness loads the course seed into a disposable database and runs those
sessions in a worker that shares only the database container's loopback
network. Without it, the blocks that read the variable are reported as skipped.

A course whose guides need its own project image (the TMB course compiles its
models into ``TMB_BUILD_DIR``) can run in that image with
``--track-image <course>=<image>``; build the image locally first. Without that
option the course's executed blocks are reported as skipped.

Worker execution reuses the classroom runner inside the published worker image,
with no network, a read-only root, dropped capabilities and a non-root job
identity. Nothing executes without --confirm-disposable.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
import uuid
from collections import Counter, defaultdict, deque
from collections.abc import Collection, Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import quote
from xml.parsers import expat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from ds60sqlpy.browser_runs import BROWSER_PROFILES  # noqa: E402
from ds60sqlpy.exercises import code_language  # noqa: E402
from ds60sqlpy.gpu_runtime import GPU_PROFILES  # noqa: E402
from ds60sqlpy.lesson_reader import _FENCE_RE, _is_fence_closer  # noqa: E402
from ds60sqlpy.modules import LANGUAGES  # noqa: E402

SCHEMA_VERSION = 1
DEFAULT_REPORT = Path("work/guide-example-results.json")
MATRIX = Path("curriculum/coverage-matrix.json")
SQL_SETUP = Path("sql/postgres-60day/00_setup.sql")
DATABASE_ENV = "DS60_DATABASE_URL"
FLAGS = frozenset({"fragment", "external", "expect-error", "isolated"})
PRELUDE = "prelude="
PROFILE = "profile="
PRELUDE_LANGUAGES = frozenset({"python", "r", "scala"})
SPARK_SCALA = "spark-local-scala"
SPARK_PYTHON = "spark-local-python"
# The same local session the Spark worked examples and solutions build for themselves.
SPARK_SETTINGS = (
    ("spark.ui.enabled", "false"),
    ("spark.driver.host", "127.0.0.1"),
    ("spark.driver.bindAddress", "127.0.0.1"),
    ("spark.sql.shuffle.partitions", "2"),
    ("spark.sql.adaptive.enabled", "false"),
    ("spark.sql.ansi.enabled", "true"),
    ("spark.sql.session.timeZone", "UTC"),
)
DOCUMENTATION = frozenset(
    {
        "",
        "text",
        "dax",
        "html",
        "powershell",
        "css",
        "dockerfile",
        "properties",
        "mermaid",
        "hql",
        "cmake",
        "http",
        "markdown",
        "console",
        "toml",
        "ini",
        "diff",
    }
)
STATIC = frozenset({"bash", "json", "yaml", "xml"})
SESSIONS = frozenset({"python", "r", "julia"})
PROGRAMS = frozenset(
    {
        "c",
        "cpp",
        "go",
        "rust",
        "swift",
        "java",
        "csharp",
        "scala",
        "javascript",
        "typescript",
        "php",
    }
)
DEFAULTS = {
    "python": "python-core",
    "c": "c17",
    "cpp": "cpp20",
    "go": "go",
    "rust": "rust-stable",
    "swift": "swift-linux",
    "java": "java21",
    "csharp": "csharp-dotnet",
    "scala": "scala-jvm",
    "javascript": "javascript-node",
    "typescript": "typescript-node",
    "php": "php-cli",
    "r": "r-statistics",
    "julia": "julia",
    "stan": "stan-cpu",
}
RUNTIME_ALIASES = {"python": "python-core"}
ORDINARY = (
    frozenset(LANGUAGES)
    - {"reading", "k8s-kind", "dax-offline"}
    - BROWSER_PROFILES.keys()
    - GPU_PROFILES
)
EXTERNAL_PROFILES = {
    **dict.fromkeys(GPU_PROFILES, "needs a GPU"),
    **dict.fromkeys(BROWSER_PROFILES, "needs a browser page"),
    "k8s-kind": "needs a Kubernetes cluster",
}
POSTGRES_TAGS = frozenset({"postgres", "postgresql", "psql"})
SESSION_TIMEOUT = 300
PROGRAM_TIMEOUT = 120
SLOW_PROFILES = frozenset({"spark-local-scala", "spark-local-python"})
BLOCK_SECONDS = 90
MAX_ROUNDS = 12
GPU_CODE = re.compile(r"__global__|<<<|\bcuda[A-Z]\w*\s*\(")
TEMPLATED = re.compile(r"\{\{|\{%")
MARKER = re.compile(r"^@@DS60-RESULT (\d+) (passed|failed) ([0-9a-f]*)\s*$", re.MULTILINE)
SQL_ERROR = re.compile(
    r"^psql:[^\n]*?:\d+: (?:ERROR|FATAL|error):|^(?:ERROR|FATAL):|invalid command"
)
ADVANCED_PROFILE = "python-advanced"
ADVANCED_DEPENDENCIES = frozenset({"ml", "production", "deep-learning", "nlp", "geo", "advanced"})
SELECTORS = frozenset({"all", "host", "postgres", ADVANCED_PROFILE})
HOST = "host:"
# Tracks whose executed blocks need the track's own project image, not a worker image.
TRACK_IMAGE_SOURCES = {"tmb-modeling": "courses/tmb-modeling/projects/tmb-local/Dockerfile"}
EXECUTED_KINDS = frozenset({"session", "program", "stan"})


@dataclass(slots=True, eq=False)
class Block:
    """One fenced block and, after the run, its outcome."""

    guide: str
    lesson: str
    track: str
    runtime: str
    index: int
    line: int
    tag: str
    language: str
    flags: frozenset[str]
    text: str
    dependencies: frozenset[str] = frozenset()
    lesson_path: str = ""
    prelude: str = ""
    fence_profile: str = ""
    fence_error: str = ""
    kind: str = ""
    profile: str = ""
    status: str = "pending"
    detail: str = ""

    def settle(self, ok: bool, detail: str = "") -> None:
        if "expect-error" in self.flags:
            self.status = "failed" if ok else "passed"
            self.detail = "expected an error, but the block succeeded" if ok else ""
        else:
            self.status = "passed" if ok else "failed"
            self.detail = "" if ok else _clip(detail)

    def skip(self, detail: str) -> None:
        self.status, self.detail = "skipped", detail

    def record(self) -> dict[str, Any]:
        return {
            "guide": self.guide,
            "lesson": self.lesson,
            "block": self.index,
            "line": self.line,
            "language": self.language,
            "kind": self.kind,
            "profile": self.profile,
            "status": self.status,
            "detail": self.detail,
        }


@dataclass(slots=True, eq=False)
class Job:
    """One unit of worker execution: a session for a guide or one program."""

    profile: str
    language: str
    blocks: list[Block]
    replay: list[Block] = field(default_factory=list)
    source: str = ""
    stanc: bool = False
    retried: bool = False
    lane: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    @property
    def key(self) -> str:
        """The image lane: the profile, or ``profile@track`` under --track-image."""

        return self.lane or self.profile

    @property
    def session(self) -> bool:
        return self.language in SESSIONS

    @property
    def database(self) -> bool:
        return any(DATABASE_ENV in block.text for block in (*self.replay, *self.blocks))

    @property
    def timeout(self) -> int:
        if self.session or self.profile in SLOW_PROFILES:
            return SESSION_TIMEOUT
        return PROGRAM_TIMEOUT

    def payload(self) -> dict[str, Any]:
        source = self.source or build_session(self.language, self.replay, self.blocks, self.profile)
        return {
            "id": self.id,
            "profile": self.profile,
            "source": source,
            "timeout": self.timeout,
            "stanc": self.stanc,
        }


def _clip(text: str, limit: int = 900) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[: limit // 3] + " ... " + text[-2 * limit // 3 :]


# Inventory --------------------------------------------------------------------


def fenced_blocks(markdown: str) -> list[tuple[int, str, str]]:
    """Return (line, info, code) for each fence, using the reader's fence rules."""

    lines = markdown.split("\n")
    found: list[tuple[int, str, str]] = []
    index = 0
    while index < len(lines):
        fence = _FENCE_RE.match(lines[index])
        if fence is None:
            index += 1
            continue
        marker = fence.group(1)
        indent = len(lines[index]) - len(lines[index].lstrip(" "))
        start = index + 1
        code: list[str] = []
        index += 1
        while index < len(lines) and not _is_fence_closer(lines[index], marker):
            line = lines[index]
            strip = min(indent, len(line) - len(line.lstrip(" ")))
            code.append(line[strip:])
            index += 1
        index += 1
        found.append((start, fence.group(2).strip(), "\n".join(code)))
    return found


def _prelude(root: Path, guide: str, tokens: Sequence[str]) -> tuple[str, str]:
    """Read the companion file named by a ``prelude=<relative path>`` fence token."""

    names = [token[len(PRELUDE) :] for token in tokens if token.startswith(PRELUDE)]
    if not names:
        return "", ""
    if len(names) > 1:
        return "", "a fence may name only one prelude"
    path = ((root / guide).parent / names[0]).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        return "", f"prelude {names[0]!r} is not a file inside the repository"
    return path.read_text(encoding="utf-8"), ""


def _fence_profile(tokens: Sequence[str]) -> tuple[str, str]:
    """Read the worker profile named by a ``profile=<name>`` fence token."""

    names = [token[len(PROFILE) :] for token in tokens if token.startswith(PROFILE)]
    if not names:
        return "", ""
    if len(names) > 1:
        return "", "a fence may name only one profile"
    if names[0] not in LANGUAGES and names[0] != ADVANCED_PROFILE:
        return "", f"unknown worker profile {names[0]!r}"
    return names[0], ""


def inventory(root: Path, patterns: Sequence[str]) -> list[Block]:
    matrix = json.loads((root / MATRIX).read_text(encoding="utf-8"))
    blocks: list[Block] = []
    for lesson in matrix["lessons"]:
        guide = str(lesson["paths"]["guide"])
        if patterns and not any(fnmatch.fnmatch(guide, pattern) for pattern in patterns):
            continue
        text = (root / guide).read_text(encoding="utf-8")
        number = 0
        for line, info, code in fenced_blocks(text):
            tokens = info.split()
            tag = tokens[0] if tokens else ""
            if tag.lower() == "math":
                continue
            number += 1
            prelude, prelude_error = _prelude(root, guide, tokens[1:])
            fence_profile, profile_error = _fence_profile(tokens[1:])
            blocks.append(
                Block(
                    guide=guide,
                    lesson=str(lesson["id"]),
                    track=str(lesson["track"]),
                    runtime=str(lesson["runtime"]),
                    index=number,
                    line=line,
                    tag=tag,
                    language=code_language(tag),
                    flags=frozenset(token for token in tokens[1:] if token in FLAGS),
                    text=code,
                    dependencies=frozenset(str(item) for item in lesson.get("dependencies", ())),
                    lesson_path=str(lesson["paths"].get("lesson", "")),
                    prelude=prelude,
                    fence_profile=fence_profile,
                    fence_error=prelude_error or profile_error,
                )
            )
    return blocks


# Classification ---------------------------------------------------------------


def _track_profiles(root: Path) -> tuple[dict[str, Counter[str]], set[str]]:
    matrix = json.loads((root / MATRIX).read_text(encoding="utf-8"))
    profiles: dict[str, Counter[str]] = defaultdict(Counter)
    sql_tracks: set[str] = set()
    for lesson in matrix["lessons"]:
        runtime = RUNTIME_ALIASES.get(lesson["runtime"], lesson["runtime"])
        if lesson["runtime"] == "sql":
            sql_tracks.add(lesson["track"])
        elif runtime in LANGUAGES and runtime != "reading":
            profiles[lesson["track"]][runtime] += 1
    return profiles, sql_tracks


def resolve_profile(block: Block, track_profiles: dict[str, Counter[str]]) -> str:
    runtime = RUNTIME_ALIASES.get(block.runtime, block.runtime)
    if block.language in LANGUAGES.get(runtime, ()):
        if runtime == "python-core" and block.dependencies & ADVANCED_DEPENDENCIES:
            return ADVANCED_PROFILE
        return runtime
    for profile, _count in track_profiles[block.track].most_common():
        if block.language in LANGUAGES[profile]:
            return profile
    return DEFAULTS[block.language]


def classify(blocks: Iterable[Block], root: Path) -> None:
    track_profiles, sql_tracks = _track_profiles(root)
    for block in blocks:
        language = block.language
        if block.tag.lower() == "ipython":
            prompts = re.search(r"^(?:In \[\d*\]|%|\s*[\w.]+\s*=\s*%)", block.text, re.MULTILINE)
            language = block.language = "text" if prompts else "python"
        profile_languages = (
            ("python",)
            if block.fence_profile == ADVANCED_PROFILE
            else LANGUAGES.get(block.fence_profile, ())
        )
        if block.fence_error or (block.prelude and language not in PRELUDE_LANGUAGES):
            block.kind = "unclassified"
            block.status = "failed"
            block.detail = (
                block.fence_error or "a prelude is supported only for Python, R and Scala blocks"
            )
        elif block.fence_profile and language not in profile_languages:
            block.kind = "unclassified"
            block.status = "failed"
            block.detail = f"profile {block.fence_profile!r} does not run {language!r} blocks"
        elif "fragment" in block.flags:
            block.kind = "fragment"
            block.skip("marked fragment")
        elif "external" in block.flags:
            block.kind = "external"
            block.skip("marked external")
        elif language in DOCUMENTATION:
            block.kind = "doc"
            block.skip("documentation block")
        elif language in STATIC:
            block.kind = "static"
        elif language == "sql":
            if TEMPLATED.search(block.text):
                block.kind = "sql-templated"
                block.skip("templated SQL (dbt or Jinja)")
            elif block.tag.lower() in POSTGRES_TAGS or block.track in sql_tracks:
                block.kind = "sql"
            else:
                block.kind = "sql-dialect"
                block.skip("SQL for a non-PostgreSQL engine")
        elif language == "stan":
            block.kind, block.profile = "stan", "stan-cpu"
        elif language in SESSIONS or language in PROGRAMS:
            profile = block.fence_profile or resolve_profile(block, track_profiles)
            block.profile = profile
            gpu = "cuda" in block.track or (
                language in {"c", "cpp"} and GPU_CODE.search(block.text)
            )
            if gpu or profile in EXTERNAL_PROFILES:
                block.kind = "external"
                block.skip(
                    EXTERNAL_PROFILES.get(profile, "needs a GPU") if not gpu else "needs a GPU"
                )
            else:
                block.kind = "session" if language in SESSIONS else "program"
        else:
            block.kind = "unclassified"
            block.status, block.detail = "failed", f"no runner for fence language {language!r}"


def selected(block: Block, selection: frozenset[str]) -> bool:
    if "all" in selection:
        return True
    if block.kind == "static":
        return "host" in selection
    if block.kind == "sql":
        return "postgres" in selection
    return block.profile in selection


# Program shaping --------------------------------------------------------------

_LITERAL = re.compile(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])'|`[^`]*`")
_CONTINUE_START = re.compile(r"^(?:[{.)\]?:]|else\b|catch\b|finally\b|where\b|&&|\|\||->|=>|\+)")
_CONTINUE_END = re.compile(r"(?:[,(\[=+\-*/&|.\\{]|->|=>)$")
_ATTRIBUTE = re.compile(r"^(?:@\w+(?:\(.*\))?|#!?\[.*\]|\[[A-Z]\w*(?:\(.*\))?\])$")


def _code(line: str) -> str:
    stripped = _LITERAL.sub('""', line)
    cut = stripped.find("//")
    return (stripped if cut < 0 else stripped[:cut]).strip()


def _comment(code: str) -> bool:
    return not code or code.startswith(("/*", "*", "*/"))


def chunks(text: str, semicolons: bool) -> list[str]:
    """Split source into depth-zero statements and declarations."""

    result: list[list[str]] = []
    current: list[str] = []
    pending: list[str] = []
    depth = 0
    previous = ""
    for line in text.split("\n"):
        code = _code(line)
        if _comment(code):
            (current if depth > 0 else pending).append(line)
            continue
        if depth == 0 and current:
            ended = previous.endswith((";", "}")) or (
                previous.startswith("#") and not _ATTRIBUTE.match(previous)
            )
            if not semicolons:
                ended = ended or not _CONTINUE_END.search(previous)
            if ended and not _CONTINUE_START.match(code) and not _ATTRIBUTE.match(previous):
                result.append(current)
                current = []
        current.extend(pending)
        pending = []
        current.append(line)
        opened = sum(code.count(character) for character in "({[")
        closed = sum(code.count(character) for character in ")}]")
        depth = max(0, depth + opened - closed)
        previous = code
    current.extend(pending)
    if current:
        result.append(current)
    return ["\n".join(chunk) for chunk in result]


def _head(chunk: str) -> str:
    for line in chunk.split("\n"):
        code = _code(line)
        if not _comment(code) and not _ATTRIBUTE.match(code):
            return code
    return ""


def _code_only(chunk: str) -> bool:
    return bool(_head(chunk))


_C_TOP = re.compile(
    r"^(?:#|template\b|struct\b|class\b|union\b|enum\b|namespace\b|typedef\b|using\b|extern\b"
    r"|static_assert\b|concept\b|static\b|const\b|constexpr\b|inline\b|thread_local\b)"
)
_C_FUNCTION = re.compile(
    r"^(?:[\w:<>,*&\[\]]+\s+)+[*&]*\s*~?[A-Za-z_][\w:]*(?:<[^()]*>)?\s*\([^;]*\)"
    r"\s*(?:const|noexcept|override|final|->\s*[\w:<>*&]+|\s)*(?:\{.*)?$"
)
_GO_TOP = re.compile(r"^(?:package|import|func|type|var|const)\b")
_RUST_TOP = re.compile(
    r"^(?:#!?\[|use\b|mod\b|fn\b|struct\b|enum\b|impl\b|trait\b|type\b|const\b|static\b|extern\b"
    r"|macro_rules!|pub\b|unsafe\s+(?:fn|impl|trait)\b|async\s+fn\b)"
)
_SWIFT_TOP = re.compile(
    r"^(?:(?:public|private|fileprivate|internal|open|final|indirect|nonisolated|static)\s+)*"
    r"(?:import|func|struct|class|enum|protocol|extension|actor|typealias|precedencegroup"
    r"|infix|prefix|postfix)\b"
)
_JAVA_TYPE = re.compile(
    r"^(?:(?:public|protected|private|abstract|final|sealed|non-sealed|static|strictfp)\s+)*"
    r"(?:class|interface|enum|record|@interface)\s+(\w+)"
)
_JAVA_MEMBER = re.compile(
    r"^(?:(?:public|protected|private|static|final|synchronized|abstract)\s+)+"
    r"|^(?:<[^>]+>\s*)?[\w<>\[\],.? ]+\s+\w+\s*\([^;]*\)\s*(?:throws\s+[\w.,\s]+)?\{?$"
)
_CS_USING = re.compile(r"^(?:global\s+)?using\s+(?:static\s+)?[\w.]+(?:\s*=\s*[\w.<>,\s]+)?;$")
_CS_TYPE = re.compile(
    r"^(?:(?:public|internal|private|protected|static|sealed|abstract|partial|readonly|file"
    r"|unsafe|ref|new)\s+)*(?:class|struct|interface|enum|record|namespace|delegate)\b"
)


def _indent(text: str, spaces: int = 4) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in text.split("\n"))


def _split(text: str, semicolons: bool, top: re.Pattern[str]) -> tuple[list[str], list[str]]:
    declarations: list[str] = []
    statements: list[str] = []
    for chunk in chunks(text, semicolons):
        head = _head(chunk)
        function = top is _C_TOP and _C_FUNCTION.match(head) and "{" in chunk
        if not head or top.match(head) or function:
            declarations.append(chunk)
        else:
            statements.append(chunk)
    return declarations, statements


def _shape_c(text: str, cpp: bool) -> str:
    if re.search(r"\bmain\s*\(", text):
        return text
    declarations, statements = _split(text, True, _C_TOP)
    signature = "int main()" if cpp else "int main(void)"
    body = _indent("\n".join(statements) + "\nreturn 0;")
    return "\n".join(declarations) + f"\n\n{signature} {{\n{body}\n}}\n"


def _shape_go(text: str) -> str:
    text = re.sub(r"^package\s+\w+\s*$", "", text, flags=re.MULTILINE)
    if re.search(r"^func main\(\)", text, re.MULTILINE):
        return "package main\n\n" + text
    declarations, statements = _split(text, False, _GO_TOP)
    body = _indent("\n".join(statements))
    return "package main\n\n" + "\n".join(declarations) + f"\n\nfunc main() {{\n{body}\n}}\n"


def _shape_rust(text: str) -> str:
    if re.search(r"\bfn main\s*\(", text):
        return text
    declarations, statements = _split(text, True, _RUST_TOP)
    body = _indent("\n".join(statements))
    return "\n".join(declarations) + f"\n\nfn main() {{\n{body}\n}}\n"


def _shape_swift(text: str) -> str:
    if re.search(r"^\s*@main\b", text, re.MULTILINE):
        return text
    declarations, statements = _split(text, False, _SWIFT_TOP)
    body = _indent("\n".join(statements), 8)
    return (
        "\n".join(declarations)
        + "\n\n@main\nstruct DS60GuideMain {\n    static func main() async throws {\n"
        + body
        + "\n    }\n}\n"
    )


def _shape_java(text: str) -> str:
    text = re.sub(r"^package\s+[\w.]+\s*;\s*$", "", text, flags=re.MULTILINE)
    imports: list[str] = []
    types: list[tuple[str, str]] = []
    members: list[str] = []
    statements: list[str] = []
    for chunk in chunks(text, True):
        head = _head(chunk)
        declared = _JAVA_TYPE.match(head)
        if not head or head.startswith("import "):
            imports.append(chunk)
        elif declared:
            types.append((declared.group(1), chunk))
        elif _JAVA_MEMBER.match(head):
            members.append(chunk)
        else:
            statements.append(chunk)
    names = [name for name, _chunk in types]
    if "Main" in names and not members and not statements:
        return text
    launch = [name for name, chunk in types if re.search(r"static\s+void\s+main\s*\(", chunk)]
    if not statements and launch:
        statements.append(f"{launch[0]}.main(args);")
    hoisted = [re.sub(r"^(\s*)public\s+", r"\1", chunk, count=1) for _name, chunk in types]
    body = _indent("\n".join(statements), 8)
    main = (
        "public class Main {\n"
        + _indent("\n".join(members))
        + "\n    public static void main(String[] args) throws Exception {\n"
        + body
        + "\n    }\n}\n"
    )
    return "\n".join(imports) + "\n\n" + "\n".join(hoisted) + "\n\n" + main


def _shape_csharp(text: str) -> str:
    if re.search(r"static\s+(?:async\s+)?(?:void|int|Task(?:<int>)?)\s+Main\s*\(", text):
        return text
    usings: list[str] = []
    types: list[str] = []
    statements: list[str] = []
    for chunk in chunks(text, True):
        head = _head(chunk)
        if not head or _CS_USING.match(head):
            usings.append(chunk)
        elif _CS_TYPE.match(head):
            types.append(chunk)
        else:
            statements.append(chunk)
    if not statements:
        statements.append("System.Console.Out.Flush();")
    return "\n".join([*usings, "", *statements, "", *types]) + "\n"


def _shape_scala(text: str) -> str:
    if re.search(r"\bobject\s+Main\b", text):
        return text
    entry = re.search(r"\bobject\s+(\w+)\s+extends\s+App\b", text) or re.search(
        r"\bobject\s+(\w+)\b[^\n]*\{(?:(?!\bobject\b).)*?\bdef\s+main\s*\(", text, re.DOTALL
    )
    if entry:
        return (
            text + "\n\nobject Main {\n  def main(args: Array[String]): Unit = "
            f"{entry.group(1)}.main(args)\n}}\n"
        )
    return (
        "object Main {\n  def main(args: Array[String]): Unit = {\n"
        + _indent(text)
        + "\n    ()\n  }\n}\n"
    )


def _shape_javascript(text: str) -> str:
    if "require(" in text and not re.search(r"^\s*import\b", text, re.MULTILINE):
        return (
            'import { createRequire } from "node:module";\n'
            "const require = createRequire(import.meta.url);\n" + text
        )
    return text


def shape(language: str, text: str) -> str:
    """Turn one guide block into a complete program for the worker runner."""

    if language in {"c", "cpp"}:
        return _shape_c(text, language == "cpp")
    if language == "go":
        return _shape_go(text)
    if language == "rust":
        return _shape_rust(text)
    if language == "swift":
        return _shape_swift(text)
    if language == "java":
        return _shape_java(text)
    if language == "csharp":
        return _shape_csharp(text)
    if language == "scala":
        if re.search(r"^\s*package\s", text, re.MULTILINE):
            return text
        return _shape_scala(text)
    if language == "javascript":
        return _shape_javascript(text)
    if language == "php" and not text.lstrip().startswith("<?php"):
        return "<?php\n" + text
    return text


_SCALA_STANDALONE = re.compile(
    r"^\s*package\s|\bobject\s+Main\b|\bobject\s+\w+\s+extends\s+App\b|\bdef\s+main\s*\(",
    re.MULTILINE,
)
SCALA_SPARK_IMPORTS = (
    "import java.nio.charset.StandardCharsets",
    "import java.nio.file.{Files, Path, Paths}",
    "import org.apache.spark.sql.{Column, DataFrame, Dataset, Row, SaveMode, SparkSession}",
    "import org.apache.spark.sql.expressions.Window",
    "import org.apache.spark.sql.functions._",
    "import org.apache.spark.sql.types._",
)
_SPARK_PYTHON_SETUP = (
    "from pyspark.sql import SparkSession\n"
    "spark = SparkSession.builder.master('local[2]').appName('ds60-guide')"
    + "".join(f".config({key!r}, {value!r})" for key, value in SPARK_SETTINGS)
    + ".getOrCreate()\n"
    "spark.sparkContext.setLogLevel('ERROR')\n"
    "owned_root = None\n"
    "owned_table = None\n"
)


def scala_standalone(text: str) -> bool:
    """True when a Scala block is a whole program with its own entry point."""

    return bool(_SCALA_STANDALONE.search(text))


def scala_program(chain: Sequence[str], prelude: str = "", spark: bool = False) -> str:
    """One Scala program that runs ``chain`` in order, each block nested in the last.

    Nesting every block in its own ``locally`` scope lets a later block rebind a
    name an earlier block defined, as a reader rerunning a cell would. A prelude
    (a solution or example file) keeps its definitions: its ``object Main`` is
    renamed ``Ds60Prelude`` and imported, so the block's own names shadow it.
    With ``spark``, the program first builds the local session the guides assume.
    Block text is not reindented, so multi-line string literals stay exact.
    """

    body = ""
    for text in reversed(chain):
        body = "locally {\n" + text + "\n" + (body + "\n" if body else "") + "()\n}"
    lines = list(SCALA_SPARK_IMPORTS) if spark else []
    renamed = 0
    if prelude:
        prelude, renamed = re.subn(
            r"^object\s+Main\b", "object Ds60Prelude", prelude, count=1, flags=re.MULTILINE
        )
        lines.append(prelude)
    lines.append("object Main {")
    if renamed:
        lines.append("  import Ds60Prelude._")
    lines.append("  def main(args: Array[String]): Unit = {")
    if spark:
        settings = "".join(f'.config("{key}", "{value}")' for key, value in SPARK_SETTINGS)
        lines += [
            '    val spark = SparkSession.builder().master("local[2]").appName("ds60-guide")'
            + settings
            + ".getOrCreate()",
            '    spark.sparkContext.setLogLevel("ERROR")',
            "    import spark.implicits._",
            "    var ownedRoot: Path = null",
            "    var ownedTable: String = null",
            "    try {",
            body,
            "    } finally spark.stop()",
        ]
    else:
        lines.append(body)
    lines += ["  }", "}", ""]
    return "\n".join(lines)


# Sessions ---------------------------------------------------------------------

_PYTHON_SESSION = """\
import contextlib as _ds60_contextlib
import io as _ds60_io
import signal as _ds60_signal
import sys as _ds60_sys
import traceback as _ds60_traceback

_ds60_blocks = @@BLOCKS@@


def _ds60_alarm(_signum, _frame):
    raise TimeoutError("the block ran longer than @@LIMIT@@ seconds")


def _ds60_describe(error):
    where = ""
    for frame in _ds60_traceback.extract_tb(error.__traceback__):
        if frame.filename.startswith("<guide block"):
            where = f"line {frame.lineno}: "
    message = "".join(_ds60_traceback.format_exception_only(type(error), error)).strip()
    return where + message


_ds60_signal.signal(_ds60_signal.SIGALRM, _ds60_alarm)
_ds60_prelude_error = ""
for _ds60_number, _ds60_source, _ds60_record in _ds60_blocks:
    _ds60_buffer = _ds60_io.StringIO()
    _ds60_status, _ds60_detail = "passed", ""
    _ds60_signal.alarm(@@LIMIT@@)
    try:
        with _ds60_contextlib.redirect_stdout(_ds60_buffer), _ds60_contextlib.redirect_stderr(
            _ds60_buffer
        ):
            exec(
                compile(_ds60_source, f"<guide block {_ds60_number}>", "exec", dont_inherit=True),
                globals(),
            )
    except SystemExit as _ds60_exit:
        if _ds60_exit.code not in (None, 0):
            _ds60_status, _ds60_detail = "failed", f"SystemExit({_ds60_exit.code!r})"
    except BaseException as _ds60_error:
        _ds60_status, _ds60_detail = "failed", _ds60_describe(_ds60_error)
    finally:
        _ds60_signal.alarm(0)
    if _ds60_record is None:
        _ds60_prelude_error = _ds60_detail and f"the prelude failed: {_ds60_detail}"
        continue
    if _ds60_status == "failed" and _ds60_prelude_error:
        _ds60_detail = f"{_ds60_prelude_error}; then {_ds60_detail}"
    _ds60_prelude_error = ""
    if _ds60_record:
        print(
            "@@DS60-RESULT",
            _ds60_number,
            _ds60_status,
            _ds60_detail[:900].encode("utf-8", "replace").hex(),
            file=_ds60_sys.__stdout__,
            flush=True,
        )
"""

_R_SESSION = """\
.ds60_text <- function(h) {
  if (nchar(h) == 0L) return("")
  starts <- seq(1L, nchar(h), 2L)
  rawToChar(as.raw(strtoi(substring(h, starts, starts + 1L), 16L)))
}
.ds60_hex <- function(s) {
  paste(as.character(charToRaw(enc2utf8(substr(s, 1L, 900L)))), collapse = "")
}
.ds60_blocks <- list(@@BLOCKS@@)
.ds60_prelude_error <- ""
for (.ds60_block in .ds60_blocks) {
  .ds60_current <- ""
  .ds60_outcome <- tryCatch({
    .ds60_exprs <- parse(text = .ds60_text(.ds60_block[[2L]]), keep.source = FALSE)
    setTimeLimit(elapsed = @@LIMIT@@, transient = FALSE)
    invisible(utils::capture.output(withCallingHandlers({
      for (.ds60_expr in .ds60_exprs) {
        .ds60_current <- paste(deparse(.ds60_expr, width.cutoff = 60L)[1L], collapse = "")
        .ds60_value <- withVisible(eval(.ds60_expr, envir = globalenv()))
        if (.ds60_value$visible) print(.ds60_value$value)
      }
    }, message = function(m) invokeRestart("muffleMessage"),
       warning = function(w) invokeRestart("muffleWarning"))))
    NULL
  }, error = function(e) paste0(conditionMessage(e), " [in: ", .ds60_current, "]"),
  finally = setTimeLimit(elapsed = Inf))
  .ds60_status <- if (is.null(.ds60_outcome)) "passed" else "failed"
  .ds60_detail <- if (is.null(.ds60_outcome)) "" else .ds60_outcome
  # A record of NA marks a prelude, whose failure is reported on its block.
  if (is.na(.ds60_block[[3L]])) {
    .ds60_prelude_error <- ""
    if (nzchar(.ds60_detail)) .ds60_prelude_error <- paste0("the prelude failed: ", .ds60_detail)
    next
  }
  if (.ds60_status == "failed" && nzchar(.ds60_prelude_error)) {
    .ds60_detail <- paste0(.ds60_prelude_error, "; then ", .ds60_detail)
  }
  .ds60_prelude_error <- ""
  if (isTRUE(.ds60_block[[3L]])) {
    cat("@@DS60-RESULT", .ds60_block[[1L]], .ds60_status, .ds60_hex(.ds60_detail), "\\n",
        file = stdout())
  }
}
"""

_JULIA_SESSION = """\
const _ds60_blocks = Tuple{Int,String,Bool}[@@BLOCKS@@]
function _ds60_run(source::String, number::Int)
    try
        redirect_stdout(devnull) do
            redirect_stderr(devnull) do
                include_string(Main, source, "guide block $(number)")
            end
        end
        return ("passed", "")
    catch err
        return ("failed", first(sprint(showerror, err), 900))
    end
end
for (_ds60_number, _ds60_hexed, _ds60_record) in _ds60_blocks
    _ds60_outcome = _ds60_run(String(hex2bytes(_ds60_hexed)), _ds60_number)
    if _ds60_record
        println(stdout, "@@DS60-RESULT ", _ds60_number, " ", _ds60_outcome[1], " ",
                bytes2hex(Vector{UInt8}(codeunits(_ds60_outcome[2]))))
        flush(stdout)
    end
end
"""


def _python_prelude(source: str) -> str:
    """Define a companion file's names without running its ``__main__`` entry point.

    The file runs as its own registered module, as an import would, so that its
    ``from __future__`` imports stay first and dataclasses can resolve their
    module. Its names then join the session like ``from module import *``.
    """

    return (
        "import sys as _ds60_psys, types as _ds60_ptypes\n"
        "_ds60_module = _ds60_ptypes.ModuleType('ds60_prelude')\n"
        "_ds60_psys.modules['ds60_prelude'] = _ds60_module\n"
        f"exec(compile({source!r}, '<guide prelude>', 'exec', dont_inherit=True), "
        "_ds60_module.__dict__)\n"
        "globals().update({_k: _v for _k, _v in vars(_ds60_module).items() "
        "if not _k.startswith('__')})\n"
    )


def build_session(
    language: str, replay: Sequence[Block], blocks: Sequence[Block], profile: str = ""
) -> str:
    """One cumulative script: replayed blocks run silently, recorded blocks report.

    Under the local Spark Python profile, the script first builds the ``spark``
    session the guides assume, as a prelude step whose failure is reported on the
    first block.
    """

    entries = [(block, False) for block in replay] + [(block, True) for block in blocks]
    if language == "python":
        # A record of None marks a prelude, whose failure is reported on its block.
        steps: list[tuple[int, str, bool | None]] = []
        if profile == SPARK_PYTHON and entries:
            steps.append((entries[0][0].index, _SPARK_PYTHON_SETUP, None))
        for block, record in entries:
            if block.prelude:
                steps.append((block.index, _python_prelude(block.prelude), None))
            steps.append((block.index, block.text, record))
        payload = repr(steps)
        template = _PYTHON_SESSION
    elif language == "r":
        # A record of NA marks a prelude, as None does for Python.
        r_steps: list[str] = []
        for block, record in entries:
            if block.prelude:
                r_steps.append(f'list({block.index}L, "{block.prelude.encode().hex()}", NA)')
            r_steps.append(
                f'list({block.index}L, "{block.text.encode().hex()}", '
                f"{'TRUE' if record else 'FALSE'})"
            )
        payload = ", ".join(r_steps)
        template = _R_SESSION
    elif language == "julia":
        payload = ", ".join(
            f'({block.index}, "{block.text.encode().hex()}", {"true" if record else "false"})'
            for block, record in entries
        )
        template = _JULIA_SESSION
    else:
        raise ValueError(f"No session runner for {language}")
    return template.replace("@@BLOCKS@@", payload).replace("@@LIMIT@@", str(BLOCK_SECONDS))


# Worker driver ----------------------------------------------------------------

DRIVER = """\
import glob, json, os, shutil, subprocess, sys, tempfile, threading
from pathlib import Path
from ds60sqlpy import worker_operations as w

w.TIMEOUTS = tuple(sorted(set(w.TIMEOUTS) | {300, 600}))
_child_environment = w.child_environment


def lab_environment(directory, base=None, *, profile_id=None):
    environment = _child_environment(directory, base, profile_id=profile_id)
    url = os.environ.get("DS60_DATABASE_URL")
    if url:
        # A database job stands in for the lab kernel, which sees the course URL
        # and the full installed package rather than the worker's module subset.
        environment["DS60_DATABASE_URL"] = url
        environment.pop("PYTHONPATH", None)
    build = os.environ.get("TMB_BUILD_DIR")
    if build:
        # A --track-image project image compiles its models here; its own R
        # sessions see the variable, which the worker allowlist would drop.
        environment["TMB_BUILD_DIR"] = build
    return environment


w.child_environment = lab_environment


def stanc(source, directory):
    found = [shutil.which("stanc"), *sorted(glob.glob("/opt/cmdstan*/bin/stanc"))]
    home = os.environ.get("CMDSTAN")
    if home:
        found.insert(0, os.path.join(home, "bin", "stanc"))
    tool = next((item for item in found if item and os.path.exists(item)), None)
    if tool is None:
        return {"status": "failed", "detail": "stanc is not installed in this image", "output": ""}
    directory.mkdir()
    (directory / "main.stan").write_text(source, encoding="utf-8")
    done = subprocess.run(
        [tool, "main.stan", "--o", "main.hpp"], cwd=directory, capture_output=True,
        text=True, timeout=120,
    )
    status = "succeeded" if done.returncode == 0 else "failed"
    return {"status": status, "detail": "", "output": (done.stdout + done.stderr)[-6000:]}


for line in sys.stdin:
    job = json.loads(line)
    result = {"id": job["id"]}
    try:
        with tempfile.TemporaryDirectory(prefix="guide-", dir="/tmp") as parent:
            os.chmod(parent, 0o711)
            directory = Path(parent) / "job"
            if job.get("stanc"):
                result.update(stanc(job["source"], directory))
            else:
                outcome = w.execute_operation(
                    job["profile"], job["source"], directory, job["timeout"],
                    threading.Event(), lambda status: None, isolate_user=True,
                )
                result.update(
                    status=outcome.status, detail=outcome.detail or "",
                    returncode=outcome.returncode,
                    output=outcome.raw_output or outcome.output,
                )
    except Exception as error:
        result.update(status="error", detail=f"{type(error).__name__}: {error}", output="")
    print("DS60-RESULT " + json.dumps(result), flush=True)
"""


def docker_command(image: str, name: str, database: Database | None = None) -> list[str]:
    """Build the worker command; a database run shares only that container's loopback."""

    return [
        "docker",
        "run",
        "--rm",
        "-i",
        "--name",
        name,
        "--network",
        f"container:{database.container}" if database else "none",
        *(["-e", f"{DATABASE_ENV}={database.url}"] if database else []),
        "--read-only",
        "--user",
        "0:0",
        "--tmpfs",
        "/tmp:size=1g,mode=1777,exec",
        "--cap-drop",
        "ALL",
        *[
            item
            for cap in ("CHOWN", "SETUID", "SETGID", "DAC_OVERRIDE", "KILL")
            for item in ("--cap-add", cap)
        ],
        "--security-opt",
        "no-new-privileges",
        "--pids-limit",
        "512",
        "--memory",
        "3g",
        "--cpus",
        "2",
        "--init",
        "-e",
        "DS60_GUIDE_DRIVER=" + DRIVER,
        "--entrypoint",
        "sh",
        image,
        "-c",
        'exec "$(command -v python3 || command -v python)" -c "$DS60_GUIDE_DRIVER"',
    ]


def run_container(
    image: str, jobs: Sequence[Job], deadline: float, database: Database | None = None
) -> dict[str, dict[str, Any]]:
    """Feed jobs to one disposable worker container and collect its results."""

    name = "ds60-guide-examples-" + uuid.uuid4().hex[:12]
    process = subprocess.Popen(
        docker_command(image, name, database),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert process.stdin and process.stdout and process.stderr
    errors: deque[str] = deque(maxlen=40)

    def feed() -> None:
        assert process.stdin
        try:
            for job in jobs:
                process.stdin.write(json.dumps(job.payload()) + "\n")
                process.stdin.flush()
            process.stdin.close()
        except (BrokenPipeError, OSError):
            pass

    def drain() -> None:
        assert process.stderr
        for line in process.stderr:
            errors.append(line.rstrip())

    def stop() -> None:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, check=False)

    threads = [
        threading.Thread(target=feed, daemon=True),
        threading.Thread(target=drain, daemon=True),
    ]
    for thread in threads:
        thread.start()
    timer = threading.Timer(max(1.0, deadline - time.monotonic()), stop)
    timer.start()
    results: dict[str, dict[str, Any]] = {}
    try:
        for line in process.stdout:
            if line.startswith("DS60-RESULT "):
                result = json.loads(line[len("DS60-RESULT ") :])
                results[str(result["id"])] = result
        process.wait()
    finally:
        timer.cancel()
        if process.poll() is None:
            stop()
            process.wait()
    for thread in threads:
        thread.join(timeout=5)
    reason = "deadline reached" if time.monotonic() >= deadline else "; ".join(errors)
    for job in jobs:
        results.setdefault(
            job.id,
            {
                "id": job.id,
                "status": "error",
                "detail": "container ended first: " + _clip(reason, 400),
                "output": "",
            },
        )
    return results


def _text(value: str | bytes | None) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return value or ""


def run_host(python: str, jobs: Sequence[Job], deadline: float) -> dict[str, dict[str, Any]]:
    """Run Python sessions with a host interpreter, each in a scratch directory."""

    results: dict[str, dict[str, Any]] = {}
    environment = {**os.environ, "MPLBACKEND": "Agg", "PYTHONDONTWRITEBYTECODE": "1"}
    for job in jobs:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            results[job.id] = {"id": job.id, "status": "error", "detail": "deadline reached"}
            continue
        with tempfile.TemporaryDirectory(prefix="ds60-guide-") as directory:
            script = Path(directory) / "session.py"
            script.write_text(job.payload()["source"], encoding="utf-8")
            try:
                done = subprocess.run(
                    [python, str(script)],
                    cwd=directory,
                    env=environment,
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=min(job.timeout, remaining),
                    check=False,
                )
            except subprocess.TimeoutExpired as error:
                results[job.id] = {
                    "id": job.id,
                    "status": "timeout",
                    "detail": f"ran longer than {error.timeout:.0f} seconds",
                    "output": _text(error.stdout) + _text(error.stderr),
                }
                continue
        results[job.id] = {
            "id": job.id,
            "status": "succeeded" if done.returncode == 0 else "failed",
            "detail": "",
            "returncode": done.returncode,
            "output": done.stdout + done.stderr,
        }
    return results


def describe(result: dict[str, Any]) -> str:
    output = str(result.get("output") or "")
    lines = [line for line in output.splitlines() if not line.startswith("@@DS60-RESULT")]
    tail = "\n".join(lines[-25:])
    head = str(result.get("status"))
    if result.get("detail"):
        head += ": " + str(result["detail"])
    return _clip(head + ("\n" + tail if tail else ""), 1500)


def settle_session(job: Job, result: dict[str, Any]) -> Job | None:
    """Record session markers; restart after a crash, replaying earlier blocks."""

    output = str(result.get("output") or "")
    seen = {
        int(match.group(1)): (
            match.group(2),
            bytes.fromhex(match.group(3)).decode("utf-8", "replace"),
        )
        for match in MARKER.finditer(output)
    }
    missing: list[Block] = []
    for block in job.blocks:
        if block.index in seen:
            status, detail = seen[block.index]
            block.settle(status == "passed", detail)
        else:
            missing.append(block)
    if not missing:
        return None
    first, rest = missing[0], missing[1:]
    first.settle(False, "the session stopped in this block: " + describe(result))
    if not rest:
        return None
    if not seen and job.retried:
        for block in rest:
            block.settle(False, "the session produced no results: " + describe(result))
        return None
    replay = [*job.replay, *(block for block in job.blocks if block.index < first.index)]
    return Job(job.profile, job.language, rest, replay=replay, retried=not seen, lane=job.lane)


def settle_program(job: Job, result: dict[str, Any]) -> None:
    ok = result.get("status") == "succeeded"
    for block in job.blocks:
        block.settle(ok, describe(result))


def scala_sources(blocks: Sequence[Block]) -> dict[int, str]:
    """Programs for a guide's Scala blocks, keyed by block index.

    A whole program (with its own entry point) runs as written. Under the local
    Spark profile, each other block runs after every earlier such block of its
    guide, as a reader working through the guide in one Spark shell would, with
    the ``spark`` session and ``ownedRoot`` the guides assume. Elsewhere a block
    runs on its own. A block's prelude, or the nearest earlier one, comes first.
    """

    sources: dict[int, str] = {}
    chain: list[str] = []
    prelude = ""
    for block in blocks:
        prelude = block.prelude or prelude
        if scala_standalone(block.text):
            sources[block.index] = shape(block.language, block.text)
            continue
        spark = block.profile == SPARK_SCALA
        if not spark and not prelude:
            sources[block.index] = shape(block.language, block.text)
            continue
        chain = [*chain, block.text] if spark else [block.text]
        sources[block.index] = scala_program(chain, prelude, spark=spark)
    return sources


def skip_missing_track_images(blocks: Sequence[Block], tracks: Collection[str]) -> list[Block]:
    """Skip executed blocks of a track that needs its own image when none was given."""

    for block in blocks:
        source = TRACK_IMAGE_SOURCES.get(block.track)
        if source and block.track not in tracks and block.kind in EXECUTED_KINDS:
            block.skip(
                f"needs the {block.track} project image built from {source}; "
                f"pass --track-image {block.track}=IMAGE to run it"
            )
    return [block for block in blocks if block.status == "pending"]


def build_jobs(blocks: Sequence[Block], tracks: Collection[str] = ()) -> list[Job]:
    """Group blocks into worker jobs; ``tracks`` with their own image get a lane."""

    jobs: list[Job] = []
    sessions: dict[tuple[str, str, str, int], list[Block]] = defaultdict(list)
    scala: dict[tuple[str, str], list[Block]] = defaultdict(list)

    def lane(block: Block) -> str:
        return f"{block.profile}@{block.track}" if block.track in tracks else ""

    for block in blocks:
        if block.kind == "session":
            alone = block.index if "isolated" in block.flags else -1
            sessions[(block.guide, block.language, block.profile, alone)].append(block)
        elif block.kind == "program" and block.language == "scala":
            scala[(block.guide, block.profile)].append(block)
        elif block.kind == "program":
            source = shape(block.language, block.text)
            job = Job(block.profile, block.language, [block], source=source, lane=lane(block))
            jobs.append(job)
        elif block.kind == "stan":
            jobs.append(
                Job("stan-cpu", "stan", [block], source=block.text, stanc=True, lane=lane(block))
            )
    for members in scala.values():
        sources = scala_sources(members)
        for block in members:
            jobs.append(
                Job(
                    block.profile,
                    "scala",
                    [block],
                    source=sources[block.index],
                    lane=lane(block),
                )
            )
    for (_guide, language, profile, _alone), members in sessions.items():
        jobs.append(Job(profile, language, members, lane=lane(members[0])))
    return jobs


def _work(
    image: str,
    bucket: list[Job],
    deadline: float,
    results: dict[str, dict[str, Any]],
    lock: threading.Lock,
    database: Database | None = None,
) -> None:
    found: dict[str, dict[str, Any]] = {}
    try:
        if image.startswith(HOST):
            found = run_host(image[len(HOST) :], bucket, deadline)
        elif database:
            for job in bucket:
                database.reset()
                found.update(run_container(image, [job], deadline, database))
        else:
            found = run_container(image, bucket, deadline)
    except Exception as error:  # noqa: BLE001 - a worker crash fails its jobs, not the run
        detail = f"worker crashed: {type(error).__name__}: {error}"
        for job in bucket:
            found.setdefault(job.id, {"id": job.id, "status": "error", "detail": detail})
    with lock:
        results.update(found)


def run_workers(
    jobs: list[Job],
    image_for: dict[str, str],
    parallel: int,
    deadline: float,
    database: Database | None = None,
) -> None:
    for image in sorted(set(image_for.values())):
        if image.startswith(HOST):
            if shutil.which(image[len(HOST) :]) is None:
                raise ValueError(f"Host interpreter {image[len(HOST) :]} is not executable")
            continue
        probe = subprocess.run(
            ["docker", "image", "inspect", image], capture_output=True, check=False
        )
        if probe.returncode:
            raise ValueError(f"Worker image {image} is not available; build or pull it first")
    pending = jobs
    for _round in range(MAX_ROUNDS):
        if not pending or time.monotonic() >= deadline:
            break
        followups: list[Job] = []
        by_lane: dict[tuple[str, bool], list[Job]] = defaultdict(list)
        for job in pending:
            online = bool(database) and job.database and not image_for[job.key].startswith(HOST)
            by_lane[(job.key, online)].append(job)
        for key, online in sorted(by_lane):
            group = sorted(by_lane[(key, online)], key=lambda job: -len(job.blocks))
            width = 1 if online else max(1, min(parallel, len(group)))
            buckets: list[list[Job]] = [[] for _ in range(width)]
            for position, job in enumerate(group):
                buckets[position % len(buckets)].append(job)
            started = time.monotonic()
            image = image_for[key]
            where = "host workers" if image.startswith(HOST) else "containers"
            label = key + (" with the course database" if online else "")
            print(
                f"{label}: {len(group)} jobs in {len(buckets)} {where}",
                file=sys.stderr,
                flush=True,
            )
            results: dict[str, dict[str, Any]] = {}
            lock = threading.Lock()
            threads = [
                threading.Thread(
                    target=_work,
                    args=(image, bucket, deadline, results, lock, database if online else None),
                )
                for bucket in buckets
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            for job in group:
                result = results.get(
                    job.id, {"id": job.id, "status": "error", "detail": "worker returned no result"}
                )
                if job.session:
                    followup = settle_session(job, result)
                    if followup:
                        followups.append(followup)
                else:
                    settle_program(job, result)
            print(
                f"{label}: done in {time.monotonic() - started:.0f}s", file=sys.stderr, flush=True
            )
        pending = followups


# Host checks ------------------------------------------------------------------


def check_static(block: Block, bash: str) -> None:
    text = block.text
    try:
        if block.language == "bash":
            done = subprocess.run(
                [bash, "-n"], input=text, capture_output=True, text=True, timeout=30, check=False
            )
            block.settle(done.returncode == 0, done.stderr)
        elif block.language == "json":
            try:
                json.loads(text)
            except json.JSONDecodeError:
                for line in text.splitlines():
                    if line.strip():
                        json.loads(line)
            block.settle(True)
        elif block.language == "yaml":
            if TEMPLATED.search(text):
                block.skip("templated YAML")
                return
            import yaml  # type: ignore[import-untyped]

            list(yaml.safe_load_all(text))
            block.settle(True)
        elif block.language == "xml":
            expat.ParserCreate().Parse(text, True)
            block.settle(True)
    except Exception as error:  # every parser reports its own error type
        block.settle(False, f"{type(error).__name__}: {error}")


class Postgres:
    """Run SQL blocks against per-guide clones of a disposable template database."""

    TEMPLATE = "ds60_guide_template"
    RUN = "ds60_guide_run"

    def __init__(self, prefix: str, maintenance: str, root: Path) -> None:
        self.prefix = shlex.split(prefix)
        self.maintenance = maintenance
        self.root = root

    def psql(
        self, database: str, *options: str, script: str | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [*self.prefix, "-d", database, *options],
            input=script,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
            check=False,
        )

    def admin(self, *statements: str) -> None:
        options = [item for statement in statements for item in ("-c", statement)]
        done = self.psql(self.maintenance, "-v", "ON_ERROR_STOP=1", *options)
        if done.returncode:
            raise ValueError("PostgreSQL administration failed: " + _clip(done.stderr, 400))

    def prepare(self) -> None:
        self.cleanup()
        self.admin(f"CREATE DATABASE {self.TEMPLATE}")
        setup = (self.root / SQL_SETUP).read_text(encoding="utf-8")
        done = self.psql(self.TEMPLATE, "-v", "ON_ERROR_STOP=1", script=setup)
        if done.returncode:
            raise ValueError("Loading the SQL course setup failed: " + _clip(done.stderr, 400))

    def cleanup(self) -> None:
        self.admin(
            f"DROP DATABASE IF EXISTS {self.RUN} WITH (FORCE)",
            f"DROP DATABASE IF EXISTS {self.TEMPLATE} WITH (FORCE)",
        )

    def run_guide(self, blocks: Sequence[Block]) -> None:
        self.admin(
            f"DROP DATABASE IF EXISTS {self.RUN} WITH (FORCE)",
            f"CREATE DATABASE {self.RUN} TEMPLATE {self.TEMPLATE}",
        )
        lines = [
            "\\set ON_ERROR_STOP 0",
            "\\set ON_ERROR_ROLLBACK on",
            "\\set VERBOSITY terse",
            "SET search_path TO training, public;",
            "SET statement_timeout = '30s';",
            "SET lock_timeout = '2s';",
        ]
        for block in blocks:
            lines.extend([f"\\warn @@DS60-BLOCK {block.index}", block.text, ";"])
        lines.append("\\warn @@DS60-BLOCK 0")
        done = self.psql(self.RUN, script="\n".join(lines) + "\n")
        reached: set[int] = set()
        errors: dict[int, list[str]] = defaultdict(list)
        current = 0
        for line in done.stderr.splitlines():
            marker = re.fullmatch(r"@@DS60-BLOCK (\d+)", line.strip())
            if marker:
                current = int(marker.group(1))
                reached.add(current)
            elif SQL_ERROR.search(line):
                errors[current].append(line.strip())
        for block in blocks:
            if block.index not in reached:
                block.settle(False, "not reached: " + _clip(done.stderr, 400))
            else:
                block.settle(not errors[block.index], "\n".join(errors[block.index][:6]))
            if block.status == "failed" and "expect-error" not in block.flags:
                self.excerpt(block)
        if errors[0] and 0 not in reached:
            raise ValueError("The SQL preamble failed: " + "; ".join(errors[0][:3]))

    def excerpt(self, block: Block) -> None:
        """Settle a failed block that is a verbatim excerpt of its own lesson file.

        CI runs every cataloged SQL lesson in full with ON_ERROR_STOP, so an excerpt
        that needs the lesson's earlier statements is executed there in context.
        """

        path = self.root / block.lesson_path
        shape = sql_shape(block.text)
        if not (block.lesson_path and shape and path.is_file()):
            return
        pattern = r"(?<![\w$])" + re.escape(shape) + r"(?![\w$])"
        if re.search(pattern, sql_shape(path.read_text(encoding="utf-8"))) is None:
            return
        failure = block.detail.splitlines()[0] if block.detail else "no error text"
        block.kind, block.status = "sql-excerpt", "passed"
        block.detail = _clip(
            f"verbatim excerpt of {block.lesson_path}, which `course.py sql all` runs "
            f"in full; alone it needs earlier lesson statements ({failure})"
        )


def sql_shape(text: str) -> str:
    """Normalize SQL for excerpt matching: no line comments, single spaces, no final ``;``."""

    return " ".join(re.sub(r"--[^\n]*", " ", text).split()).rstrip(";").rstrip()


class Database(Postgres):
    """The course database for Python sessions, in a network-less PostgreSQL container.

    Each session that reads DS60_DATABASE_URL gets a fresh ``advanced_sql_training``
    database cloned from a template loaded with the SQL course setup. The worker
    shares only the database container's loopback network.
    """

    TEMPLATE = "ds60_guide_python_template"
    RUN = "advanced_sql_training"

    def __init__(self, container: str, user: str, root: Path) -> None:
        inspect = subprocess.run(
            [
                "docker",
                "inspect",
                "--format",
                "{{.State.Running}} {{.HostConfig.NetworkMode}}",
                container,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if inspect.returncode or inspect.stdout.split() != ["true", "none"]:
            raise ValueError(
                f"--database-container {container} must be a running container "
                "started with --network none"
            )
        prefix = f"docker exec -i {shlex.quote(container)} psql -U {shlex.quote(user)} -X -q"
        super().__init__(prefix, "postgres", root)
        self.container = container
        self.url = f"postgresql://{quote(user, safe='')}@127.0.0.1:5432/{self.RUN}"

    def reset(self) -> None:
        self.admin(
            f"DROP DATABASE IF EXISTS {self.RUN} WITH (FORCE)",
            f"CREATE DATABASE {self.RUN} TEMPLATE {self.TEMPLATE}",
        )


# Report -----------------------------------------------------------------------


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def build_report(
    blocks: Sequence[Block], selection: frozenset[str], failure: str | None
) -> dict[str, Any]:
    statuses = Counter(block.status for block in blocks)
    complete = failure is None and not statuses["pending"]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": "scripts/check_guide_examples.py",
        "profiles": sorted(selection),
        "inventory": {
            "guides": len({block.guide for block in blocks}),
            "blocks": len(blocks),
            "by_kind": dict(sorted(Counter(block.kind for block in blocks).items())),
            "by_language": dict(sorted(Counter(block.language for block in blocks).items())),
            "by_profile": dict(
                sorted(Counter(block.profile for block in blocks if block.profile).items())
            ),
        },
        "summary": dict(sorted(statuses.items())),
        "complete": complete,
        "passed": complete and not statuses["failed"],
        "failure": failure,
        "results": [block.record() for block in blocks],
    }


def _version(root: Path) -> str:
    return str(
        tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--profiles",
        default="all",
        help="space or comma separated worker profiles, plus 'host' and 'postgres' (default: all)",
    )
    parser.add_argument(
        "--guides", action="append", default=[], help="fnmatch pattern for guide paths"
    )
    parser.add_argument("--image-template", default="ds60sqlpy-worker-{profile}:{version}")
    parser.add_argument(
        "--track-image",
        action="append",
        default=[],
        metavar="TRACK=IMAGE",
        help="run one track's blocks in this image instead, such as a local build with "
        "the track's own packages (repeatable)",
    )
    parser.add_argument("--version")
    parser.add_argument("--psql", help="command prefix that runs psql as an administrator")
    parser.add_argument("--database", default="postgres", help="maintenance database for --psql")
    parser.add_argument(
        "--database-container",
        help="running PostgreSQL container started with --network none; "
        "runs the Python sessions that read DS60_DATABASE_URL",
    )
    parser.add_argument(
        "--database-user", default="postgres", help="superuser in --database-container"
    )
    parser.add_argument("--bash", default=shutil.which("bash") or "bash")
    parser.add_argument(
        "--advanced-python",
        help="host Python with every extra installed; runs the python-advanced sessions",
    )
    parser.add_argument("--jobs", type=int, default=2, help="containers per worker profile")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--confirm-disposable", action="store_true")
    parser.add_argument("--list-only", action="store_true")
    parser.add_argument("--max-minutes", type=int, default=90)
    args = parser.parse_args(argv)
    if not 1 <= args.max_minutes <= 240:
        parser.error("--max-minutes must be between 1 and 240")
    if not 1 <= args.jobs <= 8:
        parser.error("--jobs must be between 1 and 8")
    track_images: dict[str, str] = {}
    for item in args.track_image:
        track, _, image = item.partition("=")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", track) or not image.strip():
            parser.error(f"--track-image expects TRACK=IMAGE, not {item!r}")
        track_images[track] = image.strip()
    root = args.root.resolve()
    if args.advanced_python:
        located = shutil.which(args.advanced_python)
        if located is None:
            parser.error(f"--advanced-python {args.advanced_python} is not executable")
        args.advanced_python = str(Path(located).absolute())
    selection = frozenset(item for item in re.split(r"[\s,]+", args.profiles) if item)
    unknown = selection - SELECTORS - frozenset(LANGUAGES)
    if unknown:
        parser.error("unknown profiles: " + ", ".join(sorted(unknown)))
    blocks = inventory(root, args.guides)
    classify(blocks, root)
    chosen = [block for block in blocks if block.status == "pending" and selected(block, selection)]
    if not args.advanced_python and not args.list_only:
        for block in chosen:
            if block.profile == ADVANCED_PROFILE:
                block.skip("needs the advanced extras; pass --advanced-python to run it")
        chosen = [block for block in chosen if block.status == "pending"]
    if not args.database_container and not args.list_only:
        for block in chosen:
            if block.kind == "session" and DATABASE_ENV in block.text:
                block.skip(f"reads {DATABASE_ENV}; pass --database-container to run it")
        chosen = [block for block in chosen if block.status == "pending"]
    if not args.list_only:
        chosen = skip_missing_track_images(chosen, track_images)
    for block in blocks:
        if block.status == "pending" and block not in chosen:
            block.status = "unselected"
    if args.list_only:
        kinds = Counter((block.kind, block.profile or "-") for block in blocks)
        for (kind, profile), count in sorted(kinds.items()):
            print(f"{kind:14} {profile:24} {count}")
        print(f"{len(blocks)} blocks in {len({b.guide for b in blocks})} guides; nothing executed")
        return 0
    if not args.confirm_disposable:
        parser.error("pass --confirm-disposable to execute guide examples")
    report_path = args.report if args.report.is_absolute() else root / args.report
    deadline = time.monotonic() + args.max_minutes * 60
    failure: str | None = None
    try:
        for block in chosen:
            if block.kind == "static":
                check_static(block, args.bash)
        sql = [block for block in chosen if block.kind == "sql"]
        if sql:
            if not args.psql:
                raise ValueError("SQL blocks were selected; pass --psql")
            postgres = Postgres(args.psql, args.database, root)
            postgres.prepare()
            try:
                by_guide: dict[str, list[Block]] = defaultdict(list)
                for block in sql:
                    by_guide[block.guide].append(block)
                for guide in sorted(by_guide):
                    if time.monotonic() >= deadline:
                        break
                    postgres.run_guide(by_guide[guide])
            finally:
                postgres.cleanup()
        jobs = build_jobs(chosen, track_images)
        if jobs:
            version = args.version or _version(root)
            image_for = {
                job.key: (
                    track_images[job.key.partition("@")[2]]
                    if job.lane
                    else HOST + args.advanced_python
                    if job.profile == ADVANCED_PROFILE
                    else args.image_template.format(profile=job.profile, version=version)
                )
                for job in jobs
            }
            database = None
            if args.database_container and any(job.database for job in jobs):
                database = Database(args.database_container, args.database_user, root)
                database.prepare()
            try:
                run_workers(jobs, image_for, args.jobs, deadline, database)
            finally:
                if database:
                    database.cleanup()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        failure = f"{type(error).__name__}: {error}"
    report = build_report(blocks, selection, failure)
    write_report(report_path, report)
    for block in blocks:
        if block.status == "failed":
            first = block.detail.splitlines()[0] if block.detail else ""
            print(
                f"FAILED {block.guide}:{block.line} [{block.language}] {first[:160]}",
                file=sys.stderr,
            )
    print(
        json.dumps(
            {
                "summary": report["summary"],
                "complete": report["complete"],
                "passed": report["passed"],
            }
        )
    )
    if failure:
        print(failure, file=sys.stderr)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
