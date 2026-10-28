"""Publish the complete 72-chapter tutorial from disjoint maintained fragments."""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "courses/data-ml-engineering"
FRAGMENTS = {
    "foundations": (*range(1, 33), *range(41, 57)),
    "ml-lifecycle": range(33, 41),
    "serving": range(57, 73),
}
FIELDS = {
    "id",
    "title",
    "level",
    "minutes",
    "prerequisites",
    "runtime_profile",
    "language",
    "concepts",
    "outcome",
    "guide_source",
    "source_path",
    "related_paths",
}
PROFILES = {"python-core", "data-engineering", "spark-local-python", "llm-torch-cpu"}
MARKER = "<!-- worked-program -->"


def source_path(root: Path, value: Any) -> Path:
    if (
        not isinstance(value, str)
        or not value
        or Path(value).is_absolute()
        or ".." in Path(value).parts
    ):
        raise ValueError("Use a repository-relative content path")
    result = root / value
    if (
        result.is_symlink()
        or not result.is_file()
        or not result.resolve().is_relative_to(root.resolve())
    ):
        raise ValueError("Missing, linked or escaped content: " + value)
    return result


def load_chapters(root: Path = ROOT, *, complete: bool = True) -> list[dict[str, Any]]:
    base = root / "courses/data-ml-engineering"
    chapters: list[dict[str, Any]] = []
    seen: set[str] = set()
    for fragment, numbers in FRAGMENTS.items():
        path = base / "authoring" / fragment / "chapters.json"
        if not path.exists():
            if complete:
                raise ValueError("The complete book requires " + str(path.relative_to(root)))
            continue
        values = json.loads(path.read_text("utf-8"))
        if not isinstance(values, list):
            raise ValueError("A chapter fragment must be a list")
        allowed = {f"dme-{n:03}" for n in numbers}
        for chapter in values:
            if not isinstance(chapter, dict) or set(chapter) != FIELDS:
                raise ValueError("Invalid chapter record fields")
            key = chapter["id"]
            if not isinstance(key, str) or key not in allowed or key in seen:
                raise ValueError("Chapter identity is duplicated or outside fragment ownership")
            seen.add(key)
            prefix = f"courses/data-ml-engineering/authoring/{fragment}/"
            if any(
                not str(chapter[field]).startswith(prefix)
                for field in ("guide_source", "source_path")
            ):
                raise ValueError("Fragment source must remain in its owned directory")
            if chapter["runtime_profile"] not in PROFILES or chapter["language"] != "python":
                raise ValueError("A chapter requires an explicitly prepared Python profile")
            if (
                chapter["level"] not in {"beginner", "intermediate", "advanced"}
                or type(chapter["minutes"]) is not int
                or not 15 <= chapter["minutes"] <= 240
            ):
                raise ValueError("Invalid chapter level or time estimate")
            if not all(
                isinstance(chapter[name], list)
                for name in ("prerequisites", "concepts", "related_paths")
            ):
                raise ValueError("Invalid chapter list metadata")
            for name in ("title", "outcome"):
                if not isinstance(chapter[name], str) or not chapter[name].strip():
                    raise ValueError("Chapter title and outcome must be explicit text")
            prerequisites = chapter["prerequisites"]
            if any(
                not isinstance(value, str)
                or re.fullmatch(r"dme-\d{3}", value) is None
                or not 1 <= int(value[4:]) < int(key[4:])
                for value in prerequisites
            ) or len(prerequisites) != len(set(prerequisites)):
                raise ValueError("Book prerequisites must be unique earlier stable chapter IDs")
            if not chapter["concepts"] or any(
                not isinstance(value, str) or not value.strip() for value in chapter["concepts"]
            ):
                raise ValueError("Each chapter needs explicit named concepts")
            guide = source_path(root, chapter["guide_source"]).read_text("utf-8")
            program = source_path(root, chapter["source_path"]).read_text("utf-8")
            if not guide.startswith(f"# {key}: {chapter['title']}\n") or guide.count(MARKER) != 1:
                raise ValueError(key + " needs its exact chapter title and one program marker")
            if any(guide.count(f"## Worked case {i}:") != 1 for i in (1, 2)):
                raise ValueError(key + " requires two separately explained complete cases")
            if len(re.sub(r"```.*?```", "", guide, flags=re.S).split()) < 800:
                raise ValueError(key + " needs a substantive original teaching chapter")
            if "\u2014" in guide or "\u2014" in program:
                raise ValueError(key + " contains a prohibited punctuation character")
            tree = ast.parse(program)
            functions = {
                node.name
                for node in tree.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            if not {"example_one", "example_two", "main"} <= functions:
                raise ValueError(key + " needs two named executable cases and main")
            if len(program.encode()) > 100_000 or not program.endswith("\n"):
                raise ValueError(key + " needs bounded LF-terminated source")
            for link in chapter["related_paths"]:
                if not isinstance(link, dict) or set(link) != {"label", "path"}:
                    raise ValueError("Invalid related content link")
                source_path(root, link["path"])
            chapters.append(chapter)
    if complete and seen != {f"dme-{n:03}" for n in range(1, 73)}:
        raise ValueError("Publish only the complete dme-001 through dme-072 book")
    return sorted(chapters, key=lambda chapter: chapter["id"])


def relocate_links(text: str, source: Path, target: Path, root: Path) -> str:
    """Relocate real local Markdown links while leaving fenced program literals exact."""
    pattern = re.compile(r"(!?\[[^]\n]*\]\()([^\s)]+)(\))")

    def replace(match: re.Match[str]) -> str:
        value = match[2]
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return match[0]
        path = (source.parent / unquote(parsed.path)).resolve()
        if not path.is_relative_to(root.resolve()) or not path.exists():
            raise ValueError("Broken or escaped source Markdown link: " + value)
        relative = Path(os.path.relpath(path, target.parent)).as_posix()
        suffix = ("?" + parsed.query if parsed.query else "") + (
            "#" + parsed.fragment if parsed.fragment else ""
        )
        return match[1] + quote(relative, safe="/") + suffix + match[3]

    protected = re.compile(r"(?<!`)(?P<ticks>`+)(?!`).*?(?P=ticks)(?!`)|\\\(.*?\\\)|\\\[.*?\\\]")
    output = []
    fence = None
    display_math = False
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if fence is not None:
            output.append(line)
            if re.fullmatch(re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*", stripped):
                fence = None
            continue
        opening = re.match(r"(`{3,}|~{3,})", stripped)
        if opening:
            fence = opening[1]
            output.append(line)
            continue
        if stripped == r"\[":
            display_math = True
        if display_math:
            output.append(line)
            if stripped == r"\]":
                display_math = False
            continue
        offset = 0
        for token in protected.finditer(line):
            output.append(pattern.sub(replace, line[offset : token.start()]))
            output.append(token[0])
            offset = token.end()
        output.append(pattern.sub(replace, line[offset:]))
    return "".join(output)


def output_contracts(chapters: list[dict[str, Any]], root: Path = ROOT) -> dict[str, Any]:
    """Validate each owned output fragment against the shared receipt contract."""
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "src"))
    from scripts.declared_outputs import _normalized_unit

    identities = {chapter["id"] for chapter in chapters}
    records: dict[str, dict[str, Any]] = {}
    for fragment, numbers in FRAGMENTS.items():
        path = root / "courses/data-ml-engineering/authoring" / fragment / "output-contracts.json"
        if not path.exists():
            continue
        raw = json.loads(path.read_text("utf-8"))
        if (
            not isinstance(raw, dict)
            or set(raw) != {"schema_version", "units"}
            or type(raw["schema_version"]) is not int
            or raw["schema_version"] != 1
            or not isinstance(raw["units"], list)
        ):
            raise ValueError("Invalid book output-contract fragment")
        allowed = {f"dme-{number:03}" for number in numbers}
        for record in raw["units"]:
            if not isinstance(record, dict) or record.get("id") not in allowed:
                raise ValueError("Output contract is outside fragment ownership")
            key = record["id"]
            if key not in identities or key in records:
                raise ValueError("Output contract needs one completed admitted chapter")
            _normalized_unit(record)
            records[key] = record
    return {"schema_version": 1, "units": [records[key] for key in sorted(records)]}


def book_readme(chapters: list[dict[str, Any]], summary: str) -> str:
    introduction = """# Data and ML Engineering

SUMMARY

The 72 tutorial chapters connect engineering foundations, data systems, ML
lifecycle decisions and LLM serving. Every chapter provides original theory,
two complete explained cases, failure diagnosis, answered interview discussion
and a maintained executable reference. There are no forced exams or hidden
answers. Start at dme-001 or follow a selected chapter's direct prerequisites.

## Open the book

Follow the [main Docker setup](../../README.md), then open the printed address
ending in `/classroom` and select **Data and ML Engineering**. A lightweight
`./classroom --starter` session can read the entire book and run Core chapters.
To select the complete set of ordinary runtimes used by this book from the
repository root:

```sh
BUILDKIT_PROGRESS=plain ./classroom \\
  --profile data-engineering --profile spark-local-python --profile llm-torch-cpu
```

Core is included automatically. Explicit profile flags replace the saved profile
selection, so include any additional language profiles you want to retain in that
selection. Later `./classroom` reuses the saved selection; `./classroom stop`
retains learner state, and `./classroom resume` starts without building or pulling.
See the [launcher guide](../../docs/one-command-classroom.md) for the full contract.

The host needs a Linux-container Docker engine and the documented Bash launcher;
Windows uses WSL 2. Compilers, Python packages and Spark's JVM belong inside the
prepared images. Use images matching the native engine architecture. No GPU,
cloud account, downloaded model weights or host language installation is needed
for the ordinary worked programs.

## Follow the learning route

| Chapters | Focus |
| --- | --- |
| [001-008](guides/dme-001.md) | Records, types, SQL grain, functions, tests and reproducibility |
| [009-016](guides/dme-009.md) | Ingestion, APIs, change events, history, time and quality |
| [017-024](guides/dme-017.md) | Query engines, Parquet, Spark, orchestration and checkpoints |
| [025-032](guides/dme-025.md) | Storage, snapshots, catalogs, Cassandra, Pinot and governance |
| [033-040](guides/dme-033.md) | Features, training, evaluation, MLflow and artifact acceptance |
| [041-048](guides/dme-041.md) | Serving, SLOs, monitoring, security, capacity and delivery |
| [049-056](guides/dme-049.md) | Connected capstones, restore, migration and recovery |
| [057-072](guides/dme-057.md) | LLM requests, weights, kernels, scheduling and streaming |

Read the changed-condition cases before editing the reference. Compare actual
output with the chapter's independent oracle, and inspect rejected conditions as
well as successful ones. Saved drafts, notes and results belong to their lesson
and runtime. A read marker or successful reference execution records activity;
it does not certify mastery or production readiness.

## Use the complete projects separately

Ordinary pads create bounded temporary state and do not start long-lived servers.
For persistent service work, copy the maintained project source into a new
learner-owned folder and follow that project's instructions:

- [Data-product service](projects/data-product/README.md): real HTTP snapshot
  ingestion, SQLite, Polars/DuckDB, immutable Parquet, failure recovery and rollback.
- [Inference service](projects/inference-service/README.md): actual CPU model
  execution, bounded requests, SSE, cancellation and durable operation receipts.
- [Focused ML service](../ml-engineering/projects/local-system/README.md): retained
  feature/model state, explicit activation, prediction and monitoring.
- [Apache and open-data workshops](../apache-data-platforms/README.md): separately
  prepared actual services for the mechanisms discussed in this book.

A Python mechanism model is identified as a model. It is never presented as an
executed Kafka, Flink, Cassandra, Pinot, cloud object store or table-format
service. Native program execution, application tests, actual HTTP service checks
and architecture/hardware qualification remain separate evidence.

## Chapter directory

| Chapter | Stage | Prepared runtime |
| --- | --- | --- |
"""
    directory = "\n".join(
        f"| [{chapter['id']}: {chapter['title']}](guides/{chapter['id']}.md) | "
        f"{chapter['level']} | `{chapter['runtime_profile']}` |"
        for chapter in chapters
    )
    return (
        introduction.replace("SUMMARY", summary)
        + directory
        + "\n\nMaintain the disjoint sources through the [authoring contract](authoring/README.md) "
        + "and [book validation guide](VALIDATION.md). "
        + "Existing [ML engineering](../ml-engineering/README.md), "
        + "[dbt](../dbt/README.md) and [Polars](../polars/README.md) "
        + "remain focused workshops with their stable lesson identities.\n"
    )


def render(root: Path = ROOT) -> dict[Path, str]:
    chapters = load_chapters(root)
    base = root / "courses/data-ml-engineering"
    generated: dict[Path, str] = {}
    plan: list[dict[str, Any]] = []
    admissions: list[dict[str, Any]] = []
    for chapter in chapters:
        key = chapter["id"]
        source = source_path(root, chapter["guide_source"])
        target = base / "guides" / (key + ".md")
        guide = relocate_links(source.read_text("utf-8"), source, target, root)
        program = source_path(root, chapter["source_path"]).read_text("utf-8")
        guide = guide.replace(MARKER, "```python\n" + program + "```")
        head, rest = guide.split("\n", 1)
        prerequisites = ", ".join("`" + name + "`" for name in chapter["prerequisites"]) or "None"
        guide = (
            head
            + (
                f"\n\n**Level:** {chapter['level'].title()} | "
                f"**Prepared runtime:** `{chapter['runtime_profile']}`\n\n"
                f"**Direct prerequisites:** {prerequisites}.\n\n"
                f"**Outcome:** {chapter['outcome']}\n\n"
                "Open the worked program in the classroom code pad. This tutorial exposes "
                "complete examples and answered discussions without an exam gate. "
                "The pad has fresh temporary state; separately documented projects use "
                "their own owned lifecycle.\n"
            )
            + rest
        )
        if chapter["related_paths"]:
            guide += "\n## Related focused workshops and projects\n\n"
            guide += (
                "\n".join(
                    "- ["
                    + link["label"]
                    + "]("
                    + Path(os.path.relpath(root / link["path"], target.parent)).as_posix()
                    + ")"
                    for link in chapter["related_paths"]
                )
                + "\n"
            )
        generated[target] = guide.rstrip() + "\n"
        plan.append(
            {
                "id": key,
                "title": chapter["title"],
                "level": chapter["level"],
                "minutes": chapter["minutes"],
                "prerequisites": chapter["prerequisites"],
                "runtime": chapter["runtime_profile"],
                "concepts": chapter["concepts"],
                "outcome": chapter["outcome"],
                "lab": (
                    "Run both complete cases, inspect their checks "
                    "and explain the changed assumption."
                ),
                "verification": (
                    "Compare the actual source-bound observations with the "
                    "chapter's independent oracles and stated limitations."
                ),
            }
        )
        admissions.append(
            {
                "id": key,
                "status": "authored",
                "language": "python",
                "runtime_profile": chapter["runtime_profile"],
                "guide_path": str(target.relative_to(root)),
                "source_path": chapter["source_path"],
                "solution_paths": [],
                "verification_id": None,
            }
        )
    track: dict[str, Any] = {
        "schema_version": 1,
        "id": "data-ml-engineering",
        "title": "Data and ML Engineering",
        "summary": (
            "A complete tutorial from engineering foundations through data systems, "
            "dependable ML workflows and the LLM serving lifecycle."
        ),
        "learning_mode": "tutorial",
        "lessons": plan,
    }
    generated[base / "track.json"] = json.dumps(track, indent=2, ensure_ascii=False) + "\n"
    generated[base / "figure-contracts.json"] = (
        json.dumps(output_contracts(chapters, root), indent=2) + "\n"
    )
    generated[base / "lessons.json"] = (
        json.dumps(
            {"schema_version": 1, "track_id": "data-ml-engineering", "lessons": admissions},
            indent=2,
        )
        + "\n"
    )
    generated[base / "README.md"] = book_readme(chapters, track["summary"])
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--source-check", action="store_true")
    args = parser.parse_args()
    if args.source_check:
        chapters = load_chapters(complete=False)
        print(f"Validated {len(chapters)} completed source chapters; no admission written.")
        return 0
    files = render()
    drift = []
    for path, text in files.items():
        if args.check:
            if not path.is_file() or path.read_text("utf-8") != text:
                drift.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, "utf-8")
    if drift:
        print("Book generation drift:\n" + "\n".join(drift))
        return 1
    print(
        f"Data and ML Engineering: {len(files)} published artifacts "
        f"{'checked' if args.check else 'written'}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
