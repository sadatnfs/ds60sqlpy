"""Build and run beginner-safe, learner-local SQL lesson notebooks.

The checked-in SQL curriculum intentionally uses ``psql`` meta-commands.  A
generated notebook therefore renders the source for reading and delegates
execution to ``psql -f`` instead of rewriting the file as JupySQL cells.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Any, Literal
from urllib.parse import parse_qs, unquote, urlsplit

from ds60sqlpy.catalog import Catalog, Lesson

SqlArtifactKind = Literal["lesson", "solution"]

COURSE_DATABASE_NAME = "advanced_sql_training"
DATABASE_RESET_CONFIRMATION = f"RESET {COURSE_DATABASE_NAME}"
MAX_TRANSCRIPT_CHARACTERS = 200_000
PSQL_TIMEOUT_SECONDS = 900
LIBPQ_ROUTING_ENVIRONMENT = frozenset(
    {
        "DS60_DATABASE_URL",
        "PGHOST",
        "PGHOSTADDR",
        "PGPORT",
        "PGSERVICE",
        "PGSERVICEFILE",
        "PGOPTIONS",
    }
)
LESSON_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PSQL_INCLUDE_PATTERN = re.compile(r"^\s*\\(?P<command>ir|i)\s+(?P<argument>.+?)\s*$")
SQL_DOLLAR_QUOTE_PATTERN = re.compile(r"\$(?:[A-Za-z_][A-Za-z0-9_]*)?\$")


def _sql_identifier_continuation(character: str) -> bool:
    """Return whether PostgreSQL can treat a character as part of an identifier."""

    return bool(character) and (not character.isascii() or character.isalnum() or character in "_$")


class SqlNotebookError(RuntimeError):
    """Raised when a generated SQL notebook cannot proceed safely."""


@dataclass(frozen=True, slots=True)
class SqlNotebookWorkspace:
    """Paths selected for one generated notebook and editable SQL copy."""

    lesson_id: str
    artifact_kind: SqlArtifactKind
    solution_index: int
    source_path: Path
    sql_path: Path
    notebook_path: Path


@dataclass(frozen=True, slots=True)
class SqlNotebookReadiness:
    """Secret-free readiness summary suitable for display in a notebook."""

    psql_found: bool
    database_safe: bool
    workspace_present: bool
    messages: tuple[str, ...]

    @property
    def ready(self) -> bool:
        """Return whether the generated workspace can be executed."""

        return self.psql_found and self.database_safe and self.workspace_present


@dataclass(frozen=True, slots=True)
class SqlNotebookRun:
    """Captured result of one fixed, non-shell ``psql`` invocation."""

    label: str
    path: Path
    returncode: int
    stdout: str
    stderr: str

    @property
    def succeeded(self) -> bool:
        """Return whether ``psql`` completed successfully."""

        return self.returncode == 0

    def transcript(self) -> str:
        """Return a bounded learner-facing transcript without a connection URL."""

        status = "PASS" if self.succeeded else f"FAIL (exit {self.returncode})"
        sections = [f"[{status}] {self.label}"]
        if self.stdout.strip():
            sections.extend(("", self.stdout.rstrip()))
        if self.stderr.strip():
            sections.extend(("", "psql messages:", self.stderr.rstrip()))
        return "\n".join(sections)

    def require_success(self) -> None:
        """Raise a concise error after the transcript has been displayed."""

        if not self.succeeded:
            raise SqlNotebookError(
                f"{self.label} failed with psql exit code {self.returncode}. "
                "Read the transcript above, fix the first error, and run the cell again."
            )


def validate_course_database_target(value: str) -> str:
    """Validate a libpq target and return it without exposing or rewriting it.

    Only the literal course database name or a PostgreSQL URL whose path names
    that database is accepted.  Key-value DSNs and URL parameters that can
    override the database or service are deliberately rejected.
    """

    target = value.strip()
    if target == COURSE_DATABASE_NAME:
        return target
    if not target:
        raise SqlNotebookError(
            "DS60_DATABASE_URL is empty. Remove it to use native local PostgreSQL, "
            "or set it to the disposable course database."
        )

    try:
        parsed = urlsplit(target)
    except ValueError as exc:
        raise SqlNotebookError("DS60_DATABASE_URL is not a valid PostgreSQL URL.") from exc
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise SqlNotebookError(
            f"DS60_DATABASE_URL must be a PostgreSQL URL or the literal {COURSE_DATABASE_NAME!r}."
        )
    if not target.startswith(("postgres://", "postgresql://")):
        raise SqlNotebookError("DS60_DATABASE_URL must use PostgreSQL URL syntax with //.")
    if parsed.fragment:
        raise SqlNotebookError("DS60_DATABASE_URL must not contain a URL fragment.")

    database_name = unquote(parsed.path.removeprefix("/"))
    if "/" in database_name or database_name != COURSE_DATABASE_NAME:
        raise SqlNotebookError(
            "Refusing to run: DS60_DATABASE_URL does not select the disposable "
            f"{COURSE_DATABASE_NAME} database."
        )

    authority = parsed.netloc.rsplit("@", maxsplit=1)[-1]
    if "," in authority:
        raise SqlNotebookError("DS60_DATABASE_URL must not use a multi-host authority.")
    try:
        hostname = parsed.hostname
        _ = parsed.port
    except ValueError as exc:
        raise SqlNotebookError("DS60_DATABASE_URL has an invalid host or port.") from exc
    local_hosts = {None, "localhost", "127.0.0.1", "::1"}
    if hostname is not None:
        hostname = unquote(hostname).casefold()
    if hostname not in local_hosts:
        raise SqlNotebookError(
            "DS60_DATABASE_URL must use local PostgreSQL (a local socket, "
            "localhost, 127.0.0.1, or ::1)."
        )

    query_keys = {key.casefold() for key in parse_qs(parsed.query, keep_blank_values=True)}
    allowed_parameters = {"sslmode"}
    unsupported = sorted(query_keys - allowed_parameters)
    if unsupported:
        raise SqlNotebookError(
            "DS60_DATABASE_URL contains an unsupported connection parameter: "
            + ", ".join(unsupported)
        )
    return target


def course_psql_environment(
    target: str,
    *,
    application_name: str,
    connect_timeout: int,
) -> dict[str, str]:
    """Build a child environment that cannot reroute the validated target."""

    validated = validate_course_database_target(target)
    environment = os.environ.copy()
    for name in LIBPQ_ROUTING_ENVIRONMENT:
        environment.pop(name, None)
    environment["PGDATABASE"] = validated
    environment["PGAPPNAME"] = application_name
    environment["PGCONNECT_TIMEOUT"] = str(connect_timeout)
    return environment


def _course_database_target() -> str:
    return validate_course_database_target(
        os.environ.get("DS60_DATABASE_URL", COURSE_DATABASE_NAME)
    )


def _cataloged_sql_source(
    catalog: Catalog,
    lesson_id: str,
    artifact_kind: SqlArtifactKind,
    solution_index: int,
) -> tuple[Lesson, Path]:
    try:
        lesson = catalog.get(lesson_id)
    except KeyError as exc:
        raise SqlNotebookError(str(exc)) from exc
    if lesson.track != "sql":
        raise SqlNotebookError(f"Lesson is not in the SQL track: {lesson_id}")
    if not LESSON_ID_PATTERN.fullmatch(lesson.id):
        raise SqlNotebookError(f"SQL lesson has an unsafe catalog ID: {lesson.id!r}")
    if artifact_kind == "lesson":
        if solution_index != 1:
            raise SqlNotebookError("solution_index applies only to solution notebooks.")
        source = catalog.resolve(lesson.lesson_path)
    elif artifact_kind == "solution":
        sql_solutions = tuple(
            catalog.resolve(path)
            for path in lesson.solution_paths
            if Path(path).suffix.casefold() == ".sql"
        )
        if solution_index < 1 or solution_index > len(sql_solutions):
            raise SqlNotebookError(
                f"{lesson_id} has {len(sql_solutions)} executable SQL solution(s); "
                f"solution {solution_index} does not exist."
            )
        source = sql_solutions[solution_index - 1]
    else:
        raise SqlNotebookError(f"Unsupported SQL artifact kind: {artifact_kind!r}")
    if source.suffix.casefold() != ".sql" or not source.is_file():
        raise SqlNotebookError(f"Cataloged SQL source is missing: {source.name}")
    return lesson, source


def _workspace_for(
    catalog: Catalog,
    lesson_id: str,
    artifact_kind: SqlArtifactKind,
    solution_index: int,
) -> SqlNotebookWorkspace:
    _, source = _cataloged_sql_source(
        catalog,
        lesson_id,
        artifact_kind,
        solution_index,
    )
    stem = "lesson" if artifact_kind == "lesson" else f"solution-{solution_index}"
    directory = catalog.repo_root / ".learning" / "sql" / lesson_id / stem
    source_relative = source.relative_to(catalog.repo_root)
    sql_path = directory / "workspace" / source_relative
    notebook_path = directory / "guided.ipynb"
    repo_root = catalog.repo_root.resolve()
    for candidate in (
        catalog.repo_root / ".learning",
        catalog.repo_root / ".learning" / "sql",
        catalog.repo_root / ".learning" / "sql" / lesson_id,
        directory,
        directory / "workspace",
    ):
        if candidate.is_symlink():
            raise SqlNotebookError("Generated SQL workspace contains a symbolic-link directory.")
    resolved_directory = directory.resolve()
    if not resolved_directory.is_relative_to(repo_root):
        raise SqlNotebookError("Generated SQL workspace escaped the repository.")
    resolved_workspace = (directory / "workspace").resolve()
    if (
        notebook_path.parent.resolve() != resolved_directory
        or not sql_path.parent.resolve().is_relative_to(resolved_workspace)
    ):
        raise SqlNotebookError("Generated SQL workspace escaped .learning.")
    return SqlNotebookWorkspace(
        lesson_id=lesson_id,
        artifact_kind=artifact_kind,
        solution_index=solution_index,
        source_path=source,
        sql_path=sql_path,
        notebook_path=notebook_path,
    )


def _cell_id(lesson_id: str, artifact_name: str, label: str) -> str:
    digest = hashlib.sha256(f"{lesson_id}:{artifact_name}:{label}".encode()).hexdigest()
    return f"ds60-{digest[:12]}"


def _markdown_cell(
    lesson_id: str,
    artifact_name: str,
    label: str,
    source: str,
) -> dict[str, Any]:
    return {
        "cell_type": "markdown",
        "id": _cell_id(lesson_id, artifact_name, label),
        "metadata": {},
        "source": source,
    }


def _code_cell(
    lesson_id: str,
    artifact_name: str,
    label: str,
    source: str,
) -> dict[str, Any]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": _cell_id(lesson_id, artifact_name, label),
        "metadata": {"tags": ["live-postgres"]},
        "outputs": [],
        "source": source,
    }


def _sql_fence(source: str) -> str:
    longest = max((len(match.group()) for match in re.finditer(r"`+", source)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}sql\n{source.rstrip()}\n{fence}"


def _notebook_document(
    catalog: Catalog,
    lesson: Lesson,
    workspace: SqlNotebookWorkspace,
) -> dict[str, Any]:
    artifact_name = (
        "learner lesson"
        if workspace.artifact_kind == "lesson"
        else f"executable solution {workspace.solution_index}"
    )
    source = workspace.source_path.read_text(encoding="utf-8")
    source_relative = workspace.source_path.relative_to(catalog.repo_root).as_posix()
    guide_relative = lesson.guide_path
    guide_link = f"../../../../{guide_relative}"
    sql_link = workspace.sql_path.relative_to(workspace.notebook_path.parent).as_posix()
    sql_filename = workspace.sql_path.name
    artifact_token = workspace.artifact_kind
    solution_index = workspace.solution_index

    setup_code = dedent(
        f"""\
        from pathlib import Path
        import sys

        def find_course_root(start: Path) -> Path:
            for candidate in (start.resolve(), *start.resolve().parents):
                if (
                    (candidate / "curriculum" / "catalog.json").is_file()
                    and (candidate / "src" / "ds60sqlpy").is_dir()
                ):
                    return candidate
            raise RuntimeError(
                "Course root not found. Start Jupyter from the ds60sqlpy repository."
            )

        REPO_ROOT = find_course_root(Path.cwd())
        source_root = REPO_ROOT / "src"
        if str(source_root) not in sys.path:
            sys.path.insert(0, str(source_root))

        from ds60sqlpy.catalog import Catalog
        from ds60sqlpy.sql_notebook import (
            DATABASE_RESET_CONFIRMATION,
            prepare_sql_workspace,
            run_sql_workspace,
            sql_notebook_readiness,
            verify_course_database,
        )

        catalog = Catalog.load(REPO_ROOT)
        LESSON_ID = {lesson.id!r}
        ARTIFACT_KIND = {artifact_token!r}
        SOLUTION_INDEX = {solution_index}
        print(f"Ready to guide {{LESSON_ID}} from {{REPO_ROOT.name}}.")
        """
    )
    readiness_code = dedent(
        """\
        readiness = sql_notebook_readiness(
            catalog,
            LESSON_ID,
            ARTIFACT_KIND,
            SOLUTION_INDEX,
        )
        for message in readiness.messages:
            print(message)
        print("Ready to execute:", readiness.ready)
        """
    )
    prepare_code = dedent(
        """\
        # Change this one value only when you are ready to reset the course-owned
        # training schema in advanced_sql_training.
        CONFIRM_COURSE_RESET = False

        if not CONFIRM_COURSE_RESET:
            print(
                "Preparation has not run. Set CONFIRM_COURSE_RESET = True, "
                "then run this cell again."
            )
        else:
            preparation_runs = prepare_sql_workspace(
                catalog,
                LESSON_ID,
                ARTIFACT_KIND,
                SOLUTION_INDEX,
                confirmation=DATABASE_RESET_CONFIRMATION,
            )
            for preparation_run in preparation_runs:
                print(preparation_run.transcript(), end="\\n\\n")
                preparation_run.require_success()
        """
    )
    run_code = dedent(
        """\
        lesson_run = run_sql_workspace(
            catalog,
            LESSON_ID,
            ARTIFACT_KIND,
            SOLUTION_INDEX,
        )
        print(lesson_run.transcript())
        lesson_run.require_success()
        """
    )
    verify_code = dedent(
        """\
        verification_run = verify_course_database(catalog)
        print(verification_run.transcript())
        verification_run.require_success()
        """
    )

    cells = [
        _markdown_cell(
            lesson.id,
            artifact_name,
            "goal",
            dedent(
                f"""\
                # {lesson.id.upper()} — {lesson.title}

                ## Goal

                This is the guided **{artifact_name}** workspace. Read the lesson,
                edit the private working copy, prepare the disposable database, and
                run the complete script without leaving Jupyter.

                - [Open the rendered companion guide]({guide_link})
                - [Open the editable SQL working copy]({sql_link})
                - Catalog source: `{source_relative}`

                Your editable files live under `.learning/`, are ignored by Git, and
                do not change the official lesson or solution.
                """
            ),
        ),
        _markdown_cell(
            lesson.id,
            artifact_name,
            "setup",
            dedent(
                f"""\
                ## Setup

                1. Start this notebook through the course portal.
                2. Run the next two cells to locate the repository and check `psql`.
                3. If readiness is false, return to the portal's setup check.

                The runner accepts only `{COURSE_DATABASE_NAME}`. It reads an optional
                `DS60_DATABASE_URL` from the Jupyter process without displaying it.
                No connection string or password is saved in this notebook.

                Full scripts run through `psql -X -v ON_ERROR_STOP=1 -f`. This is
                important: `{source_relative}` may contain `psql` commands that are
                not valid JupySQL syntax.
                """
            ),
        ),
        _code_cell(lesson.id, artifact_name, "imports", setup_code),
        _code_cell(lesson.id, artifact_name, "readiness", readiness_code),
        _markdown_cell(
            lesson.id,
            artifact_name,
            "steps",
            dedent(
                f"""\
                ## Steps

                ### 1. Read and edit the SQL

                The snapshot below is the official source at notebook creation time.
                Edit [{sql_filename}]({sql_link}) in JupyterLab's text editor. Run
                small sections in a SQL client only when the lesson asks you to;
                the notebook runner always executes the whole editable copy.

                ### Official source snapshot

                {_sql_fence(source)}

                ### 2. Prepare the disposable database

                The next cell starts with confirmation set to `False`. Read its
                warning, change it to `True`, and run it. Preparation resets only the
                course-owned `training` schema, verifies seed data, and prepares any
                declared stateful predecessor for this lesson.
                """
            ),
        ),
        _code_cell(lesson.id, artifact_name, "prepare", prepare_code),
        _markdown_cell(
            lesson.id,
            artifact_name,
            "run-heading",
            dedent(
                f"""\
                ### 3. Run the editable `{sql_filename}` file

                `psql` receives a fixed workspace path selected from the course
                catalog. The runner rejects changed `psql` shell/include commands
                and arbitrary runner paths. Your editable SQL is still real database
                code: do not paste untrusted SQL, and use only the disposable,
                least-privileged course role.
                """
            ),
        ),
        _code_cell(lesson.id, artifact_name, "run", run_code),
        _markdown_cell(
            lesson.id,
            artifact_name,
            "checks",
            dedent(
                """\
                ## Checks

                A successful lesson exit is the first check. The next cell also runs
                the course seed-data invariants. If it fails, rerun preparation before
                continuing. Stateful project schemas can have their own checks in the
                lesson.
                """
            ),
        ),
        _code_cell(lesson.id, artifact_name, "verify", verify_code),
        _markdown_cell(
            lesson.id,
            artifact_name,
            "next",
            dedent(
                """\
                ## Next Steps

                1. Complete every prediction and exercise in the editable SQL file.
                2. Explain the first error before changing the query.
                3. Compare with the solution only after making a serious attempt.
                4. Return to the course portal, record completion, and open the
                   recommended next lesson.

                For short exploratory queries after learning this workflow, use the
                separate PostgreSQL-magics lesson. Full course scripts should continue
                through this `psql` runner so their meta-commands keep working.
                """
            ),
        ),
    ]

    return {
        "cells": cells,
        "metadata": {
            "course": {
                "artifact": f"generated-sql-{workspace.artifact_kind}",
                "day": lesson.day,
                "lesson_id": lesson.id,
                "source_path": source_relative,
                "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "tags": [
                    "generated",
                    "learner-local",
                    "live-postgres",
                    "psql",
                    "sql",
                ],
                "track": "sql",
            },
            "kernelspec": {
                "display_name": "Python (ds60sqlpy)",
                "language": "python",
                "name": "ds60sqlpy",
            },
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def generate_sql_notebook(
    catalog: Catalog,
    lesson_id: str,
    artifact_kind: SqlArtifactKind = "lesson",
    solution_index: int = 1,
) -> SqlNotebookWorkspace:
    """Create missing learner-local files without overwriting learner edits."""

    lesson, _ = _cataloged_sql_source(
        catalog,
        lesson_id,
        artifact_kind,
        solution_index,
    )
    workspace = _workspace_for(
        catalog,
        lesson_id,
        artifact_kind,
        solution_index,
    )
    workspace.notebook_path.parent.mkdir(parents=True, exist_ok=True)
    workspace.sql_path.parent.mkdir(parents=True, exist_ok=True)
    if workspace.sql_path.is_symlink() or workspace.notebook_path.is_symlink():
        raise SqlNotebookError("Generated SQL workspace contains a symbolic-link file.")

    if not workspace.sql_path.exists():
        workspace.sql_path.write_text(
            workspace.source_path.read_text(encoding="utf-8"),
            encoding="utf-8",
            newline="\n",
        )
    _copy_relative_include_dependencies(catalog, workspace)
    if not workspace.notebook_path.exists():
        document = _notebook_document(catalog, lesson, workspace)
        workspace.notebook_path.write_text(
            json.dumps(document, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    return workspace


def _psql_meta_segments(source: str) -> tuple[str, ...]:
    r"""Return psql meta-command segments outside SQL literals and comments.

    ``psql`` accepts a backslash command after SQL on the same physical line,
    not only at the beginning of a line.  This small lexer therefore tracks
    PostgreSQL strings, quoted identifiers, dollar quotes, and nested block
    comments before treating any remaining backslash as executable client
    syntax.  A meta-command consumes the rest of its physical line; comparing
    that exact tail with the checked-in source also catches ``\\`` separators
    and additional commands.
    """

    segments: list[str] = []
    index = 0
    block_comment_depth = 0
    dollar_quote: str | None = None
    single_quote = False
    single_quote_escapes = False
    double_quote = False

    while index < len(source):
        if dollar_quote is not None:
            if source.startswith(dollar_quote, index):
                index += len(dollar_quote)
                dollar_quote = None
            else:
                index += 1
            continue

        if block_comment_depth:
            if source.startswith("/*", index):
                block_comment_depth += 1
                index += 2
            elif source.startswith("*/", index):
                block_comment_depth -= 1
                index += 2
            else:
                index += 1
            continue

        character = source[index]
        if single_quote:
            if character == "'" and source[index : index + 2] == "''":
                index += 2
            elif character == "'":
                single_quote = False
                single_quote_escapes = False
                index += 1
            elif single_quote_escapes and character == "\\" and index + 1 < len(source):
                index += 2
            else:
                index += 1
            continue

        if double_quote:
            if character == '"' and source[index : index + 2] == '""':
                index += 2
            elif character == '"':
                double_quote = False
                index += 1
            else:
                index += 1
            continue

        if source.startswith("--", index):
            newline = source.find("\n", index + 2)
            index = len(source) if newline == -1 else newline + 1
            continue
        if source.startswith("/*", index):
            block_comment_depth = 1
            index += 2
            continue
        if character == "'":
            previous = source[index - 1] if index else ""
            before_previous = source[index - 2] if index > 1 else ""
            single_quote = True
            single_quote_escapes = previous in {"e", "E"} and (
                not _sql_identifier_continuation(before_previous)
            )
            index += 1
            continue
        if character == '"':
            double_quote = True
            index += 1
            continue
        if character == "$":
            match = SQL_DOLLAR_QUOTE_PATTERN.match(source, index)
            previous = source[index - 1] if index else ""
            separated = not _sql_identifier_continuation(previous)
            if match is not None and separated:
                dollar_quote = match.group(0)
                index = match.end()
                continue
        if character == "\\":
            newline = source.find("\n", index)
            line_end = len(source) if newline == -1 else newline
            segments.append(source[index:line_end].strip())
            index = len(source) if newline == -1 else newline + 1
            continue
        index += 1

    return tuple(segments)


def _meta_command_segments(path: Path) -> tuple[str, ...]:
    """Return every executable psql meta-command segment in a SQL file."""

    return _psql_meta_segments(path.read_text(encoding="utf-8"))


def _literal_include_argument(raw: str, path: Path) -> str:
    value = raw.strip()
    if value.startswith(("'", '"')):
        quote = value[0]
        closing = value.find(quote, 1)
        if closing == -1:
            raise SqlNotebookError(f"Unclosed psql include path in {path.name}.")
        argument = value[1:closing]
        remainder = value[closing + 1 :].strip()
        if remainder:
            raise SqlNotebookError(f"Unsupported psql include syntax in {path.name}.")
    else:
        fields = value.split(maxsplit=1)
        argument = fields[0]
        if len(fields) > 1:
            raise SqlNotebookError(f"Unsupported psql include syntax in {path.name}.")
    if not argument or ":" in argument or "`" in argument:
        raise SqlNotebookError(
            f"Dynamic psql include paths are not allowed in generated workspaces: {path.name}"
        )
    return argument


def _relative_include_sources(
    catalog: Catalog,
    source: Path,
    *,
    seen: set[Path] | None = None,
) -> tuple[Path, ...]:
    r"""Resolve the fixed recursive ``\ir`` graph beneath the repository."""

    visited = seen if seen is not None else set()
    resolved_source = source.resolve()
    if resolved_source in visited:
        return ()
    visited.add(resolved_source)

    dependencies: list[Path] = []
    for segment in _meta_command_segments(source):
        match = PSQL_INCLUDE_PATTERN.match(segment)
        if match is None:
            continue
        if match.group("command") != "ir":
            raise SqlNotebookError(
                f"Cataloged SQL must use repository-relative \\ir, not \\i: {source.name}"
            )
        argument = _literal_include_argument(match.group("argument"), source)
        dependency = (source.parent / argument).resolve()
        if (
            not dependency.is_relative_to(catalog.repo_root)
            or dependency.suffix.casefold() != ".sql"
            or not dependency.is_file()
        ):
            raise SqlNotebookError(
                f"Cataloged psql include is missing or leaves the repository: {argument}"
            )
        dependencies.append(dependency)
        dependencies.extend(_relative_include_sources(catalog, dependency, seen=visited))
    return tuple(dict.fromkeys(dependencies))


def _copy_relative_include_dependencies(
    catalog: Catalog,
    workspace: SqlNotebookWorkspace,
) -> None:
    mirror_root = workspace.notebook_path.parent / "workspace"
    for source in _relative_include_sources(catalog, workspace.source_path):
        relative = source.relative_to(catalog.repo_root)
        destination = mirror_root / relative
        if destination.parent.is_symlink() or not destination.parent.resolve().is_relative_to(
            mirror_root.resolve()
        ):
            raise SqlNotebookError("A mirrored psql include escaped the generated workspace.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.is_symlink():
            raise SqlNotebookError("A mirrored psql include is a symbolic link.")
        if not destination.exists():
            destination.write_text(
                source.read_text(encoding="utf-8"),
                encoding="utf-8",
                newline="\n",
            )


def _validate_workspace_meta_commands(
    catalog: Catalog,
    workspace: SqlNotebookWorkspace,
) -> None:
    if _meta_command_segments(workspace.sql_path) != _meta_command_segments(workspace.source_path):
        raise SqlNotebookError(
            "The editable SQL copy changed a psql meta-command. Restore the "
            "cataloged meta-command segments; edit SQL exercises only."
        )

    mirror_root = workspace.notebook_path.parent / "workspace"
    for source in _relative_include_sources(catalog, workspace.source_path):
        mirrored = mirror_root / source.relative_to(catalog.repo_root)
        if (
            not mirrored.is_file()
            or mirrored.is_symlink()
            or not mirrored.resolve().is_relative_to(mirror_root.resolve())
            or mirrored.read_bytes() != source.read_bytes()
        ):
            raise SqlNotebookError(
                "A fixed psql include dependency changed or is missing. Remove "
                "this generated lesson workspace and reopen it from the portal."
            )


def sql_notebook_readiness(
    catalog: Catalog,
    lesson_id: str,
    artifact_kind: SqlArtifactKind = "lesson",
    solution_index: int = 1,
) -> SqlNotebookReadiness:
    """Return a display-safe environment check for one generated workspace."""

    workspace = _workspace_for(
        catalog,
        lesson_id,
        artifact_kind,
        solution_index,
    )
    psql_found = shutil.which("psql") is not None
    messages = [
        (
            "[PASS] PostgreSQL command-line client found."
            if psql_found
            else "[FAIL] psql was not found on PATH for the Jupyter process."
        )
    ]
    try:
        _course_database_target()
        database_safe = True
        messages.append(f"[PASS] Connection target is restricted to {COURSE_DATABASE_NAME}.")
    except SqlNotebookError as exc:
        database_safe = False
        messages.append(f"[FAIL] {exc}")

    workspace_present = (
        workspace.sql_path.is_file()
        and not workspace.sql_path.is_symlink()
        and workspace.sql_path.resolve().is_relative_to(
            (catalog.repo_root / ".learning" / "sql").resolve()
        )
    )
    messages.append(
        "[PASS] Editable SQL working copy is present."
        if workspace_present
        else "[FAIL] Editable SQL working copy is missing or unsafe."
    )
    return SqlNotebookReadiness(
        psql_found=psql_found,
        database_safe=database_safe,
        workspace_present=workspace_present,
        messages=tuple(messages),
    )


def _bounded_output(value: str) -> str:
    if len(value) <= MAX_TRANSCRIPT_CHARACTERS:
        return value
    omitted = len(value) - MAX_TRANSCRIPT_CHARACTERS
    return (
        value[:MAX_TRANSCRIPT_CHARACTERS]
        + f"\n... DS60 truncated {omitted} additional transcript characters ...\n"
    )


def _run_psql(catalog: Catalog, path: Path, label: str) -> SqlNotebookRun:
    executable = shutil.which("psql")
    if executable is None:
        raise SqlNotebookError(
            "psql is not on PATH for the Jupyter process. Return to the portal "
            "readiness check or restart Jupyter after PostgreSQL setup."
        )
    target = _course_database_target()
    command = [
        executable,
        "-X",
        "--no-password",
        "-v",
        "ON_ERROR_STOP=1",
        "--pset",
        "pager=off",
        "-f",
        str(path),
    ]
    # libpq accepts a database name or connection URL through PGDATABASE. Keep
    # a password-bearing URL out of the child process argument list and remove
    # inherited routing variables that could override the validated local target.
    environment = course_psql_environment(
        target,
        application_name="ds60sqlpy-guided-notebook",
        connect_timeout=10,
    )
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            cwd=catalog.repo_root,
            encoding="utf-8",
            env=environment,
            errors="replace",
            timeout=PSQL_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return SqlNotebookRun(
            label=label,
            path=path,
            returncode=124,
            stdout="",
            stderr=(
                f"Stopped after {PSQL_TIMEOUT_SECONDS} seconds. Check for a lock "
                "or unavailable PostgreSQL service."
            ),
        )
    return SqlNotebookRun(
        label=label,
        path=path,
        returncode=result.returncode,
        stdout=_bounded_output(result.stdout),
        stderr=_bounded_output(result.stderr),
    )


def _fixed_course_sql(catalog: Catalog, relative_path: str, label: str) -> SqlNotebookRun:
    path = catalog.resolve(relative_path)
    allowed = {
        catalog.repo_root / "sql" / "postgres-60day" / "00_setup.sql",
        catalog.repo_root / "sql" / "postgres-60day" / "00_verify.sql",
    }
    if path not in {candidate.resolve() for candidate in allowed}:
        raise SqlNotebookError("Support SQL file is not on the fixed course allowlist.")
    return _run_psql(catalog, path, label)


def prepare_sql_workspace(
    catalog: Catalog,
    lesson_id: str,
    artifact_kind: SqlArtifactKind = "lesson",
    solution_index: int = 1,
    *,
    confirmation: str,
) -> tuple[SqlNotebookRun, ...]:
    """Reset course seed data and build any declared stateful predecessors."""

    lesson, _ = _cataloged_sql_source(
        catalog,
        lesson_id,
        artifact_kind,
        solution_index,
    )
    if confirmation != DATABASE_RESET_CONFIRMATION:
        raise SqlNotebookError(
            "Database preparation was not confirmed. Use the exact confirmation "
            f"{DATABASE_RESET_CONFIRMATION!r} only for the disposable course database."
        )

    runs: list[SqlNotebookRun] = []
    setup = _fixed_course_sql(
        catalog,
        "sql/postgres-60day/00_setup.sql",
        "Reset and seed the training schema",
    )
    runs.append(setup)
    if not setup.succeeded:
        return tuple(runs)
    verification = _fixed_course_sql(
        catalog,
        "sql/postgres-60day/00_verify.sql",
        "Verify deterministic seed data",
    )
    runs.append(verification)
    if not verification.succeeded or lesson.stateful_group is None:
        return tuple(runs)

    predecessors = (
        candidate
        for candidate in catalog.lessons("sql")
        if candidate.stateful_group == lesson.stateful_group and candidate.day < lesson.day
    )
    for predecessor in predecessors:
        predecessor_path = catalog.resolve(predecessor.lesson_path)
        run = _run_psql(
            catalog,
            predecessor_path,
            f"Prepare stateful prerequisite {predecessor.id}",
        )
        runs.append(run)
        if not run.succeeded:
            break
    return tuple(runs)


def run_sql_workspace(
    catalog: Catalog,
    lesson_id: str,
    artifact_kind: SqlArtifactKind = "lesson",
    solution_index: int = 1,
) -> SqlNotebookRun:
    """Run only the computed learner-local SQL copy for a cataloged artifact."""

    workspace = _workspace_for(
        catalog,
        lesson_id,
        artifact_kind,
        solution_index,
    )
    workspace_root = (catalog.repo_root / ".learning" / "sql").resolve()
    if (
        not workspace.sql_path.is_file()
        or workspace.sql_path.is_symlink()
        or not workspace.sql_path.resolve().is_relative_to(workspace_root)
    ):
        raise SqlNotebookError(
            "The generated SQL working copy is missing or unsafe. Reopen the "
            "cataloged artifact from the course portal."
        )
    _validate_workspace_meta_commands(catalog, workspace)
    return _run_psql(
        catalog,
        workspace.sql_path,
        f"Run {lesson_id} {artifact_kind}",
    )


def verify_course_database(catalog: Catalog) -> SqlNotebookRun:
    """Run the fixed seed-data verification script."""

    return _fixed_course_sql(
        catalog,
        "sql/postgres-60day/00_verify.sql",
        "Verify course database",
    )
