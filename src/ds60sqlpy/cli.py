"""Command-line interface for learners, maintainers, and Codex."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ds60sqlpy.catalog import Catalog, Track, find_repo_root
from ds60sqlpy.checks import CheckResult, run_checks
from ds60sqlpy.doctor import Diagnostic, diagnose
from ds60sqlpy.progress import ProgressStore
from ds60sqlpy.sql_runner import SqlRunner, SqlRunnerError

STATUS_MARK = {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}


def _print_diagnostic(item: Diagnostic) -> None:
    print(f"[{STATUS_MARK[item.status]:4}] {item.name}: {item.detail}")


def _print_check(item: CheckResult) -> None:
    location = f" ({item.path})" if item.path else ""
    print(f"[{STATUS_MARK[item.severity]:4}] {item.code}: {item.message}{location}")


def _catalog_rows(catalog: Catalog, track: Track | None) -> list[dict[str, Any]]:
    return [asdict(lesson) for lesson in catalog.lessons(track)]


def _cmd_doctor(args: argparse.Namespace, catalog: Catalog) -> int:
    diagnostics = diagnose(catalog)
    for diagnostic in diagnostics:
        _print_diagnostic(diagnostic)
    counts = Counter(item.status for item in diagnostics)
    print(
        f"\nEnvironment summary: {counts['pass']} pass, "
        f"{counts['warn']} warning, {counts['fail']} fail"
    )
    if counts["fail"]:
        return 1
    return 1 if args.strict and counts["warn"] else 0


def _cmd_catalog(args: argparse.Namespace, catalog: Catalog) -> int:
    track: Track | None = args.track
    rows = _catalog_rows(catalog, track)
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    lessons = catalog.lessons(track)
    id_width = max((len(lesson.id) for lesson in lessons), default=9)
    for lesson in lessons:
        solutions = len(lesson.solution_paths)
        print(
            f"{lesson.id:{id_width}} {lesson.level:12} {lesson.estimated_minutes:>3}m "
            f"{lesson.title} "
            f"[deps={lesson.dependency_group}; network={lesson.network}; "
            f"solutions={solutions}]"
        )
    return 0


def _cmd_validate(args: argparse.Namespace, catalog: Catalog) -> int:
    results = run_checks(catalog)
    if args.json:
        print(json.dumps([asdict(result) for result in results], indent=2))
    else:
        for result in results:
            if args.all or result.severity != "pass" or result.code.endswith(".summary"):
                _print_check(result)
        counts = Counter(item.severity for item in results)
        print(
            f"\nValidation summary: {counts['pass']} pass, "
            f"{counts['warn']} warning, {counts['fail']} fail"
        )
    counts = Counter(item.severity for item in results)
    if counts["fail"]:
        return 1
    return 1 if args.strict and counts["warn"] else 0


def _cmd_progress(args: argparse.Namespace, catalog: Catalog) -> int:
    store = ProgressStore(catalog)
    try:
        if args.progress_action == "complete":
            record = store.mark_complete(args.lesson_id, args.notes)
            print(f"Marked {record.lesson_id} complete at {record.completed_at}")
            return 0
        if args.progress_action == "reset":
            if not args.yes:
                print("Refusing to delete local progress without --yes.", file=sys.stderr)
                return 2
            store.reset()
            print("Removed .learning/progress.json")
            return 0
        completions = store.completions()
    except (KeyError, OSError, ValueError) as exc:
        print(f"Could not update progress: {exc}", file=sys.stderr)
        return 2

    if completions:
        print("Completed lessons:")
        for completion in completions:
            suffix = f" — {completion.notes}" if completion.notes else ""
            print(f"  {completion.lesson_id} ({completion.completed_at}){suffix}")
    else:
        print("No local progress recorded yet.")
    for track in ("python", "sql", "bridge"):
        next_lesson = store.next_lesson(track)
        if next_lesson:
            print(f"Next {track}: {next_lesson.id} — {next_lesson.title}")
        else:
            print(f"{track.capitalize()} track complete.")
    return 0


def _cmd_sql(args: argparse.Namespace, catalog: Catalog) -> int:
    try:
        runner = SqlRunner(catalog, args.database, quiet=args.quiet)
    except SqlRunnerError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.sql_action == "setup":
        if not args.yes:
            print(
                "SQL setup drops and recreates the course-owned training schema. "
                "Re-run with --yes.",
                file=sys.stderr,
            )
            return 2
        run = runner.setup()
        if run.returncode:
            return run.returncode
        return runner.verify().returncode

    if args.sql_action == "verify":
        return runner.verify().returncode

    if args.sql_action == "run":
        run = runner.lesson(args.day)
        return run.returncode

    if args.sql_action == "run-id":
        try:
            run = runner.lesson_id(args.lesson_id)
        except (KeyError, SqlRunnerError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return run.returncode

    if args.sql_action == "all":
        if args.reset:
            setup_run = runner.setup()
            if setup_run.returncode:
                return setup_run.returncode
            verify_run = runner.verify()
            if verify_run.returncode:
                return verify_run.returncode
        runs = runner.all_lessons()
        passed = sum(run.returncode == 0 for run in runs)
        expected = len(catalog.lessons("sql"))
        print(f"SQL lessons passed: {passed}/{expected}")
        return 0 if len(runs) == expected and passed == expected else 1

    if args.sql_action == "solutions":
        if args.reset:
            setup_run = runner.setup()
            if setup_run.returncode:
                return setup_run.returncode
            verify_run = runner.verify()
            if verify_run.returncode:
                return verify_run.returncode
        runs = runner.all_solutions()
        passed = sum(run.returncode == 0 for run in runs)
        expected = sum(
            Path(path).suffix == ".sql"
            for lesson in catalog.lessons("sql")
            for path in lesson.solution_paths
        )
        print(f"Executable SQL solutions passed: {passed}/{expected}")
        return 0 if len(runs) == expected and passed == expected else 1

    raise AssertionError(f"Unhandled SQL action: {args.sql_action}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ds60",
        description=(
            "Manage and validate the DS60 Python, PostgreSQL, and engineering curriculum."
        ),
    )
    parser.add_argument(
        "--repo",
        type=Path,
        help="Repository root (normally discovered automatically).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subparsers.add_parser("doctor", help="Check local tools and packages.")
    doctor_parser.add_argument("--strict", action="store_true", help="Fail on warnings.")

    catalog_parser = subparsers.add_parser("catalog", help="List cataloged lessons.")
    catalog_parser.add_argument("--track", choices=("python", "sql", "bridge"))
    catalog_parser.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser(
        "validate", help="Run fast structural repository checks."
    )
    validate_parser.add_argument("--strict", action="store_true", help="Fail on warnings.")
    validate_parser.add_argument("--json", action="store_true")
    validate_parser.add_argument("--all", action="store_true", help="Print passing details too.")

    progress_parser = subparsers.add_parser("progress", help="Track local learning progress.")
    progress_subparsers = progress_parser.add_subparsers(dest="progress_action", required=True)
    progress_subparsers.add_parser("show", help="Show completions and next lessons.")
    complete_parser = progress_subparsers.add_parser("complete", help="Complete a lesson.")
    complete_parser.add_argument(
        "lesson_id",
        help="For example: python-04, sql-12, or bridge-03",
    )
    complete_parser.add_argument("--notes", default="")
    reset_parser = progress_subparsers.add_parser("reset", help="Delete local progress.")
    reset_parser.add_argument("--yes", action="store_true")

    sql_parser = subparsers.add_parser("sql", help="Run PostgreSQL course scripts with psql.")
    sql_parser.add_argument(
        "--database",
        help="PostgreSQL URL; defaults to DS60_DATABASE_URL or the Compose database.",
    )
    sql_parser.add_argument("--quiet", action="store_true")
    sql_subparsers = sql_parser.add_subparsers(dest="sql_action", required=True)
    setup_parser = sql_subparsers.add_parser("setup", help="Reset and seed training schema.")
    setup_parser.add_argument("--yes", action="store_true")
    sql_subparsers.add_parser("verify", help="Verify course seed-data invariants.")
    run_parser = sql_subparsers.add_parser("run", help="Run one SQL lesson.")
    run_parser.add_argument("day", type=int, choices=range(1, 61), metavar="DAY")
    run_id_parser = sql_subparsers.add_parser(
        "run-id",
        help="Run one SQL lesson by stable catalog ID.",
    )
    run_id_parser.add_argument(
        "lesson_id",
        help="For example: sql-found-01, sql-18, or sql-ops-01",
    )
    all_parser = sql_subparsers.add_parser("all", help="Run all SQL lessons sequentially.")
    all_parser.add_argument(
        "--reset", action="store_true", help="Run destructive course setup first."
    )
    solutions_parser = sql_subparsers.add_parser(
        "solutions",
        help="Run every cataloged executable SQL solution sequentially.",
    )
    solutions_parser.add_argument(
        "--reset",
        action="store_true",
        help="Run destructive course setup first.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""

    args = _parser().parse_args(argv)
    try:
        root = find_repo_root(args.repo)
        catalog = Catalog.load(root)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    handlers = {
        "doctor": _cmd_doctor,
        "catalog": _cmd_catalog,
        "validate": _cmd_validate,
        "progress": _cmd_progress,
        "sql": _cmd_sql,
    }
    return handlers[args.command](args, catalog)
