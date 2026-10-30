#!/usr/bin/env python3
"""Format maintained sources with the pinned, offline Docker toolchain.

The public entrypoint is scripts/format-repo. Generated and historically qualified
artifacts have explicit exclusions in format-policy.json; shared readers are
regenerated through their canonical builders after a complete formatting pass.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import shutil
import stat
import subprocess
import sys
import time
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_public_release import CREDENTIAL_DIRECTORY  # noqa: E402

LANGUAGES = (
    "python",
    "r",
    "julia",
    "stan",
    "dbt",
    "web",
    "java",
    "c",
    "cpp",
    "cuda",
    "php",
    "csharp",
    "go",
    "rust",
    "swift",
    "scala",
    "sql",
    "shell",
    "toml",
    "xml",
    "cmake",
    "docker",
)
SUFFIXES = {
    ".py": "python",
    ".r": "r",
    ".jl": "julia",
    ".stan": "stan",
    ".pyi": "python",
    ".ipynb": "python",
    ".js": "web",
    ".mjs": "web",
    ".cjs": "web",
    ".ts": "web",
    ".mts": "web",
    ".cts": "web",
    ".jsx": "web",
    ".tsx": "web",
    ".css": "web",
    ".scss": "web",
    ".html": "web",
    ".json": "web",
    ".jsonc": "web",
    ".yaml": "web",
    ".yml": "web",
    ".java": "java",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".cu": "cuda",
    ".cuh": "cuda",
    ".php": "php",
    ".hh": "cpp",
    ".cs": "csharp",
    ".go": "go",
    ".rs": "rust",
    ".swift": "swift",
    ".scala": "scala",
    ".sbt": "scala",
    ".sql": "sql",
    ".sh": "shell",
    ".command": "shell",
    ".toml": "toml",
    ".xml": "xml",
    ".csproj": "xml",
    ".config": "xml",
    ".cmake": "cmake",
}
# Also used for ZIPs without Git. Never descend into learner state or dependencies.
IGNORED_DIRS = {
    ".git",
    ".learning",
    ".workshop",
    ".classroom",
    ".venv",
    ".module-runtime",
    ".app-build",
    ".aws",
    ".oci",
    ".ssh",
    CREDENTIAL_DIRECTORY,
    ".serena",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    ".ipynb_checkpoints",
    ".build",
    ".swiftpm",
    "obj",
    "bin",
    "target",
    "work",
    "build",
    "dist",
    "artifacts",
    "mlruns",
    "classroom-runs",
}


def language_for(path: str) -> str | None:
    if path.startswith("courses/dbt/") and path.endswith(".sql"):
        return "dbt"
    name = Path(path).name
    if name == "Dockerfile" or name.startswith("Dockerfile."):
        return "docker"
    if name == "CMakeLists.txt":
        return "cmake"
    if path in {
        "classroom",
        "scripts/format-repo",
        "scripts/lint-repo",
        "scripts/publish-images",
        "courses/data-ml-engineering/projects/inference-service/workshop",
        "courses/advanced-spark-modeling/projects/spark-torch/workshop",
        "courses/advanced-spark-modeling/projects/spark-tmb/workshop",
        "courses/python-web/projects/web-lab/workshop",
    }:
        return "shell"
    return SUFFIXES.get(Path(path).suffix.lower())


def source_files(
    root: Path,
    *,
    include: Callable[[str], bool] | None = None,
    deadline: float | None = None,
) -> list[str]:
    """Use Git's ignore rules when available and a conservative ZIP fallback."""

    def check_deadline() -> None:
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError("Source inventory time limit reached; use a validated host snapshot")

    check_deadline()
    host_inventory = os.environ.get("DS60_FORMAT_FILE_LIST")
    if host_inventory:
        candidates = sorted(
            {os.fsdecode(p) for p in Path(host_inventory).read_bytes().split(b"\0") if p}
        )
    elif (root / ".git").exists():
        result = subprocess.run(
            [
                "git",
                "-c",
                f"safe.directory={root}",
                "-c",
                "core.fsmonitor=false",
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "-z",
            ],
            cwd=root,
            capture_output=True,
            check=True,
            timeout=30 if deadline is None else max(0.1, min(30, deadline - time.monotonic())),
        )
        candidates = sorted({os.fsdecode(p) for p in result.stdout.split(b"\0") if p})
    else:
        candidates = []
        for current, directories, filenames in os.walk(root, followlinks=False):
            check_deadline()
            directories[:] = sorted(
                d
                for d in directories
                if d not in IGNORED_DIRS and not (Path(current) / d).is_symlink()
            )
            candidates.extend((Path(current) / f).relative_to(root).as_posix() for f in filenames)
    wanted = {
        name
        for name in candidates
        if not Path(name).is_absolute()
        and ".." not in Path(name).parts
        and not any(part in IGNORED_DIRS for part in Path(name).parts)
        and (include is None or include(name))
    }
    ancestors = {parent.as_posix() for name in wanted for parent in Path(name).parents}
    safe: set[str] = set()
    visited: set[str] = set()

    def collect(directory: Path, prefix: str = "") -> None:
        check_deadline()
        if prefix in visited:
            return
        visited.add(prefix)
        # Close each directory stream before descending. Some Docker bind-mount
        # filesystems repeat entries when nested directory streams stay open.
        with os.scandir(directory) as iterator:
            entries = list(iterator)
        for entry in entries:
            check_deadline()
            name = prefix + entry.name
            if name not in wanted and name not in ancestors:
                continue
            if entry.is_symlink():
                continue
            if name in wanted and entry.is_file(follow_symlinks=False):
                safe.add(name)
            elif name in ancestors and entry.is_dir(follow_symlinks=False):
                collect(Path(entry.path), name + "/")

    collect(root)
    return sorted(safe)


def load_policy(root: Path) -> dict[str, list[dict[str, str]]]:
    policy: Any = json.loads((root / "scripts/format-policy.json").read_text(encoding="utf-8"))
    if not isinstance(policy, dict) or set(policy) != {"exclude", "preserve"}:
        raise ValueError("format-policy.json must contain exclude and preserve lists")
    for section, key in (("exclude", "pattern"), ("preserve", "path")):
        if not isinstance(policy[section], list):
            raise ValueError(f"Invalid {section} policy")
        for rule in policy[section]:
            if not isinstance(rule, dict) or set(rule) != {key, "reason"}:
                raise ValueError(f"Every {section} rule needs {key} and reason")
            if not all(isinstance(v, str) and v.strip() for v in rule.values()):
                raise ValueError("Policy values must be nonempty strings")
    return policy


def exclusion(path: str, policy: dict[str, list[dict[str, str]]]) -> str | None:
    for rule in policy["preserve"]:
        if path == rule["path"]:
            return rule["reason"]
    for rule in policy["exclude"]:
        if fnmatch.fnmatchcase(path, rule["pattern"]):
            return rule["reason"]
    if Path(path).name in {"package-lock.json", "Cargo.lock", "uv.lock"} or path.endswith(".lock"):
        return "Dependency lockfile: regenerate with its package manager."
    return None


def inventory(root: Path) -> tuple[dict[str, list[str]], dict[str, str], list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    excluded: dict[str, str] = {}
    unmanaged: list[str] = []
    policy = load_policy(root)
    for path in source_files(root):
        reason = exclusion(path, policy)
        language = language_for(path)
        if reason:
            excluded[path] = reason
        elif language:
            groups[language].append(path)
        else:
            unmanaged.append(path)
    return dict(groups), excluded, unmanaged


def run(command: list[str], root: Path) -> bool:
    result = subprocess.run(command, cwd=root, check=False)
    return result.returncode == 0


def batches(paths: list[str], count: int = 100) -> list[list[str]]:
    # Explicit relative operands cannot be interpreted as command flags or globs.
    return [["./" + p for p in paths[i : i + count]] for i in range(0, len(paths), count)]


def streamed(
    command: list[str],
    paths: list[str],
    root: Path,
    check: bool,
    *,
    terminal_newline: bool = False,
) -> bool:
    """Use stdout formatters without executing source or writing on parse errors."""
    success = True
    for name in paths:
        path = root / name
        original = path.read_bytes()
        result = subprocess.run(command, input=original, cwd=root, capture_output=True, check=False)
        if result.returncode:
            print(f"Formatter failed: {name}", file=sys.stderr)
            print(result.stderr.decode("utf-8", errors="replace"), file=sys.stderr)
            success = False
        else:
            formatted = result.stdout
            if terminal_newline:
                formatted = formatted.rstrip(b"\r\n") + b"\n"
            if formatted != original:
                if check:
                    print(f"Needs formatting: {name}")
                    success = False
                else:
                    path.write_bytes(formatted)
    return success


def run_formatter(command: list[str], paths: list[str], root: Path, check: bool) -> bool:
    """Retain source permissions when an in-place formatter replaces a file."""
    modes = {} if check else {name: stat.S_IMODE((root / name).stat().st_mode) for name in paths}
    try:
        return run(command, root)
    finally:
        for name, mode in modes.items():
            path = root / name
            if path.is_symlink():
                raise ValueError(f"Formatter replaced source with a symlink: {name}")
            if stat.S_IMODE(path.stat().st_mode) != mode:
                path.chmod(mode)


def format_group(language: str, paths: list[str], root: Path, check: bool) -> bool:
    config = root / "docker/formatting"
    if language == "dbt":
        return streamed(
            [sys.executable, str(root / "scripts/dbt_source_tools.py"), "format"],
            paths,
            root,
            check,
        )
    if language == "julia":
        return streamed(
            [
                "julia",
                "--startup-file=no",
                "--compiled-modules=existing",
                "--project=/opt/julia-env",
                str(root / "scripts/julia_source_tools.jl"),
                "format",
            ],
            paths,
            root,
            check,
        )
    if language == "stan":
        return streamed(
            [sys.executable, str(root / "scripts/stan_source_tools.py"), "format"],
            paths,
            root,
            check,
        )
    if language == "r":
        return streamed(
            ["Rscript", "--vanilla", str(root / "scripts/r_source_tools.R"), "format"],
            paths,
            root,
            check,
        )
    if language == "rust":
        return streamed(
            ["rustfmt", "--config-path", str(config / "rustfmt.toml"), "--emit", "stdout"],
            paths,
            root,
            check,
        )
    if language == "sql":
        from scripts.sql_formatting import format_sql_paths

        return format_sql_paths(paths, root, check)
    if language == "docker":
        return streamed(["dockerfmt"], paths, root, check, terminal_newline=True)
    if language == "go" and check:
        result = subprocess.run(
            ["gofmt", "-l", *["./" + p for p in paths]],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return result.returncode == 0 and not result.stdout
    if language == "python":
        command = ["ruff", "format", "--no-cache", "--config", str(root / "pyproject.toml")]
        if check:
            command += ["--check"]
    elif language in {"web", "java", "toml", "xml", "php"}:
        command = [
            "prettier",
            "--config",
            str(config / "prettier.json"),
            "--ignore-path",
            "/dev/null",
            "--check" if check else "--write",
        ]
        if language == "xml":
            command += ["--parser", "xml"]
    elif language in {"c", "cpp", "csharp", "cuda"}:
        command = ["clang-format", f"--style=file:{config / 'clang-format.yaml'}"]
        command += ["--dry-run", "--Werror"] if check else ["-i"]
    elif language == "go":
        command = ["gofmt", "-w"]
    elif language == "swift":
        command = [
            "swift-format",
            "lint" if check else "format",
            "--configuration",
            str(config / "swift-format.json"),
        ]
        command += ["--strict"] if check else ["--in-place"]
    elif language == "scala":
        command = ["scalafmt", "--config", str(config / "scalafmt.conf"), "--non-interactive"]
        if check:
            command += ["--test"]
    elif language == "shell":
        # shfmt -w can replace files with restrictive modes on shared mounts.
        return streamed(["shfmt", "-ln", "bash", "-i", "2", "-ci"], paths, root, check)
    elif language == "cmake":
        command = [
            "cmake-format",
            "--config-files",
            str(config / "cmake-format.yaml"),
            "--check" if check else "-i",
        ]
    else:
        raise ValueError(f"No formatter for {language}")
    results = []
    for batch in batches(paths):
        passed = run_formatter(command + batch, batch, root, check)
        if passed and not check and language in {"web", "java", "toml", "xml", "php"}:
            # Some complex TypeScript layouts need one additional Prettier pass.
            # Bound convergence and never report a write pass as stable without a check.
            verify = ["--check" if part == "--write" else part for part in command]
            if not run(verify + batch, root):
                passed = run_formatter(command + batch, batch, root, False)
                passed = run(verify + batch, root) and passed
        results.append(passed)
    return all(results)


def ensure_publication_paths(root: Path) -> None:
    """Refuse symlinks in the trees read/written by canonical publication tools."""
    names = (
        "START_HERE.html",
        "README.md",
        "CONTRIBUTING.md",
        "AGENTS.md",
        "accomplishments",
        "lesson-pages",
        "reference-pages",
        "courses",
        "curriculum",
        "docs",
        "python",
        "sql",
        "bridge",
        "src",
        "scripts",
    )
    visited: set[Path] = set()

    def check_directory(directory: Path) -> None:
        if directory in visited:
            return
        visited.add(directory)
        with os.scandir(directory) as iterator:
            entries = list(iterator)
        for entry in entries:
            if entry.name in IGNORED_DIRS:
                continue
            path = Path(entry.path)
            if entry.is_symlink():
                raise ValueError(
                    f"Publication path must not be a symlink: {path.relative_to(root)}"
                )
            if entry.is_dir(follow_symlinks=False):
                check_directory(path)

    for name in names:
        base = root / name
        if base.is_symlink():
            raise ValueError(f"Publication path must not be a symlink: {name}")
        if base.is_dir():
            check_directory(base)


def generated_views(root: Path, check: bool) -> bool:
    """Use existing generators, including a read-only catalog/report comparison."""
    sys.path.insert(0, str(root / "src"))
    sys.path.insert(0, str(root))
    from ds60sqlpy.catalog_builder import build_catalog
    from scripts import audit_lesson_depth, audit_practice

    success = True
    catalog = json.dumps(build_catalog(root), indent=2, ensure_ascii=False) + "\n"
    catalog_path = root / "curriculum/catalog.json"
    if not catalog_path.is_file() or catalog_path.read_text(encoding="utf-8") != catalog:
        if check:
            print("Generated output needs refresh: curriculum/catalog.json")
            return False
        catalog_path.write_text(catalog, encoding="utf-8", newline="\n")
    artifacts = []
    for module in (audit_practice, audit_lesson_depth):
        rows = module.audit()
        if not all(row.passes for row in rows):
            print(f"Content audit failed: {module.__name__}", file=sys.stderr)
            success = False
        artifacts.append((module.DEFAULT_REPORT_PATH, module.render_report(rows)))
    for path, expected in artifacts:
        if path.read_text(encoding="utf-8") != expected:
            if check:
                print(f"Generated output needs refresh: {path.relative_to(root)}")
                success = False
            else:
                path.write_text(expected, encoding="utf-8", newline="\n")
    index_command = [
        sys.executable,
        str(root / "accomplishments/index.py"),
        "check" if check else "build",
        "--repo",
        str(root),
    ]
    if not run(index_command, root):
        return False
    for script in ("build_course_guide.py", "compile_lesson_tex.py", "build_lesson_readers.py"):
        command = [sys.executable, str(root / "scripts" / script)]
        if check:
            command.append("--check")
        success = run(command, root) and success
    return success


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lint", action="store_true", help="run static checks without changing sources"
    )
    parser.add_argument(
        "--check", action="store_true", help="report drift without changing sources"
    )
    parser.add_argument("--list", action="store_true", help="list coverage and exclusion reasons")
    parser.add_argument(
        "--language", choices=LANGUAGES, action="append", help="limit source formatters"
    )
    parser.add_argument(
        "--exclude-language", choices=LANGUAGES, action="append", default=[], help=argparse.SUPPRESS
    )
    parser.add_argument("--only-language", choices=LANGUAGES, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.only_language:
        args.language = [args.only_language]
    if args.lint:
        from scripts import lint_repo

        lint_args = [
            item for language in (args.language or []) for item in ("--language", language)
        ]
        if args.list:
            lint_args.append("--list")
        for language in args.exclude_language:
            lint_args.extend(["--exclude-language", language])
        return lint_repo.main(lint_args)
    print("Discovering source files and formatting policy...", flush=True)
    groups, excluded, unmanaged = inventory(ROOT)
    chosen = [
        language
        for language in LANGUAGES
        if (not args.language or language in args.language)
        and language not in args.exclude_language
    ]
    print(
        "Maintained source coverage: " + ", ".join(f"{k}={len(groups.get(k, []))}" for k in chosen),
        flush=True,
    )
    print(
        f"Preserved generated/vendor/evidence files: {len(excluded)}; "
        f"other file types: {len(unmanaged)}",
        flush=True,
    )
    if args.list:
        for language in chosen:
            for name in groups.get(language, []):
                print(f"FORMAT [{language}] {name}")
        for name, reason in excluded.items():
            print(f"PRESERVE {name}: {reason}")
        for name in unmanaged:
            print(f"OTHER {name}: no syntax formatter (binary, data, lock or compatibility file)")
        from scripts import format_inline_code

        inline_report = format_inline_code.inspect_sources(
            ROOT, set(chosen), check=True, list_only=True
        )
        format_inline_code.print_report(inline_report, detail=True)
        return 0
    if not args.language:
        ensure_publication_paths(ROOT)
    required = {
        "python": "ruff",
        "r": "Rscript",
        "julia": "julia",
        "stan": "stanc",
        "dbt": "sqlfmt",
        "web": "prettier",
        "java": "prettier",
        "c": "clang-format",
        "cpp": "clang-format",
        "cuda": "clang-format",
        "php": "prettier",
        "csharp": "clang-format",
        "go": "gofmt",
        "rust": "rustfmt",
        "swift": "swift-format",
        "scala": "scalafmt",
        "sql": "pg_format",
        "shell": "shfmt",
        "toml": "prettier",
        "xml": "prettier",
        "cmake": "cmake-format",
        "docker": "dockerfmt",
    }
    missing = sorted(
        {required[k] for k in chosen if groups.get(k) and not shutil.which(required[k])}
    )
    if missing:
        parser.error("Missing tools: " + ", ".join(missing) + ". Use ./scripts/format-repo.")
    from scripts import format_inline_code, inline_format_contracts

    active = {language for language in chosen if groups.get(language)}
    checked = inline_format_contracts.verify(ROOT, active)
    if checked:
        print(f"Verified {checked} parser-only inline guard contracts.", flush=True)

    # Fences in durable authoring strings are updated before Python/JSON source
    # style, so the same pass leaves both containers and embedded code canonical.
    inline_report = format_inline_code.inspect_sources(ROOT, set(chosen), check=args.check)
    format_inline_code.print_report(inline_report)
    success = bool(inline_report["passed"])
    for language in chosen:
        paths = groups.get(language, [])
        if paths:
            print(
                f"{'Checking' if args.check else 'Formatting'} {language}: {len(paths)} files",
                flush=True,
            )
            success = format_group(language, paths, ROOT, args.check) and success
    if success and not args.language:
        command = [sys.executable, str(ROOT / "scripts/normalize_lesson_prose.py")]
        if not args.check:
            command.append("--write")
        success = run(command, ROOT)
        if success:
            sync = [sys.executable, str(ROOT / "scripts/sync_example_fences.py")]
            if args.check:
                sync.append("--check")
            success = run(sync, ROOT)
        if success:
            success = generated_views(ROOT, args.check)
    elif args.language:
        print("Language-only pass: run the full command to refresh/check generated readers.")
    print("Formatting checks passed." if success else "Formatting failed; see diagnostics above.")
    return 0 if success else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Formatting error: {exc}", file=sys.stderr)
        raise SystemExit(2) from None
