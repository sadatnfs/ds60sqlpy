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
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
LANGUAGES = (
    "python",
    "web",
    "java",
    "c",
    "cpp",
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
    ".md": "web",
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
    ".classroom",
    ".venv",
    ".module-runtime",
    ".app-build",
    ".aws",
    ".oci",
    ".ssh",
    ".codex",
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
    name = Path(path).name
    if name == "Dockerfile" or name.startswith("Dockerfile."):
        return "docker"
    if name == "CMakeLists.txt":
        return "cmake"
    if path in {"classroom", "scripts/format-repo", "scripts/lint-repo"}:
        return "shell"
    return SUFFIXES.get(Path(path).suffix.lower())


def source_files(root: Path) -> list[str]:
    """Use Git's ignore rules when available and a conservative ZIP fallback."""
    host_inventory = os.environ.get("DS60_FORMAT_FILE_LIST")
    if host_inventory:
        candidates = sorted({os.fsdecode(p) for p in Path(host_inventory).read_bytes().split(b"\0") if p})
    elif (root / ".git").exists():
        result = subprocess.run(
            [
                "git",
                "-c",
                f"safe.directory={root}",
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "-z",
            ],
            cwd=root,
            capture_output=True,
            check=True,
        )
        candidates = sorted({os.fsdecode(p) for p in result.stdout.split(b"\0") if p})
    else:
        candidates = []
        for current, directories, filenames in os.walk(root, followlinks=False):
            directories[:] = sorted(
                d
                for d in directories
                if d not in IGNORED_DIRS and not (Path(current) / d).is_symlink()
            )
            candidates.extend((Path(current) / f).relative_to(root).as_posix() for f in filenames)
    wanted = {
        name for name in candidates
        if not Path(name).is_absolute() and ".." not in Path(name).parts
        and not any(part in IGNORED_DIRS for part in Path(name).parts)
    }
    ancestors = {parent.as_posix() for name in wanted for parent in Path(name).parents}
    safe: set[str] = set()
    visited: set[str] = set()

    def collect(directory: Path, prefix: str = "") -> None:
        if prefix in visited:
            return
        visited.add(prefix)
        # Close each directory stream before descending. Some Docker bind-mount
        # filesystems repeat entries when nested directory streams stay open.
        with os.scandir(directory) as iterator:
            entries = list(iterator)
        for entry in entries:
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


def streamed(command: list[str], paths: list[str], root: Path, check: bool) -> bool:
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
        elif result.stdout != original:
            if check:
                print(f"Needs formatting: {name}")
                success = False
            else:
                path.write_bytes(result.stdout)
    return success


def format_group(language: str, paths: list[str], root: Path, check: bool) -> bool:
    config = root / "docker/formatting"
    if language == "rust":
        return streamed(
            ["rustfmt", "--config-path", str(config / "rustfmt.toml"), "--emit", "stdout"],
            paths,
            root,
            check,
        )
    if language == "sql":
        return streamed(
            [
                "pg_format",
                "--no-rcfile",
                "--redundant-parenthesis",
                "--spaces",
                "2",
                "--keyword-case",
                "0",
                "--function-case",
                "0",
                "--type-case",
                "0",
            ],
            paths,
            root,
            check,
        )
    if language == "docker":
        return streamed(["dockerfmt"], paths, root, check)
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
    elif language in {"web", "java", "toml", "xml"}:
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
    elif language in {"c", "cpp", "csharp"}:
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
        command = ["shfmt", "-ln", "bash", "-i", "2", "-ci", "-d" if check else "-w"]
    elif language == "cmake":
        command = [
            "cmake-format",
            "--config-files",
            str(config / "cmake-format.yaml"),
            "--check" if check else "-i",
        ]
    else:
        raise ValueError(f"No formatter for {language}")
    results = [run(command + batch, root) for batch in batches(paths)]
    return all(results)


def ensure_publication_paths(root: Path) -> None:
    """Refuse symlinks in the trees read/written by canonical publication tools."""
    names = (
        "START_HERE.html",
        "README.md",
        "CONTRIBUTING.md",
        "AGENTS.md",
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
                raise ValueError(f"Publication path must not be a symlink: {path.relative_to(root)}")
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
    for script in ("build_journey_preview.py", "build_course_guide.py", "build_lesson_readers.py"):
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
    args = parser.parse_args(argv)
    if args.lint:
        from scripts import lint_repo

        lint_args = [
            item for language in (args.language or []) for item in ("--language", language)
        ]
        if args.list:
            lint_args.append("--list")
        return lint_repo.main(lint_args)
    print("Discovering source files and formatting policy...", flush=True)
    groups, excluded, unmanaged = inventory(ROOT)
    chosen = [language for language in LANGUAGES if not args.language or language in args.language]
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
        return 0
    if not args.language:
        ensure_publication_paths(ROOT)
    required = {
        "python": "ruff",
        "web": "prettier",
        "java": "prettier",
        "c": "clang-format",
        "cpp": "clang-format",
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
    success = True
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
        success = run(command, ROOT) and generated_views(ROOT, args.check)
    elif args.language:
        print("Language-only pass: run the full command to refresh/check generated readers.")
    print("Formatting checks passed." if success else "Formatting failed; see diagnostics above.")
    return 0 if success else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Formatting error: {exc}", file=sys.stderr)
        raise SystemExit(2) from None
