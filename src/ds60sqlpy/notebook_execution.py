"""Execute ordinary Python or notebook-shaped cells in a bounded outer worker.

This module supplies cell semantics, not process containment. The caller owns
timeouts, output bounds, plotting, and process-tree cleanup.
"""

from __future__ import annotations

import io
import json
import os
import re
import runpy
import sys
import tempfile
import tokenize
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_CELL_MARKER = re.compile(r"^#\s*%%(?:[ \t].*)?$")
_IGNORED = {tokenize.ENCODING, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT, tokenize.NL}


@dataclass(frozen=True, slots=True)
class PythonCell:
    """One source cell, retaining its one-based submitted-file offset."""

    code: str
    start_line: int


def python_cells(source: str) -> tuple[tuple[PythonCell, ...], bool]:
    """Split top-level standalone markers, and detect real IPython syntax.

    Python's tokenizer protects comments and multiline strings. A cell magic's
    body is opaque text through the next top-level cell marker, so SQL/shell
    syntax cannot poison tokenization of later Python cells. Percent operators
    inside brackets or explicit continuations are ordinary Python.
    """

    lines = source.splitlines(keepends=True)
    markers: list[int] = []
    has_magic = False
    offset = 0
    while offset < len(lines):
        restart: int | None = None
        depth = 0
        statement_start = True
        previous: tokenize.TokenInfo | None = None
        tokens = tokenize.generate_tokens(io.StringIO("".join(lines[offset:])).readline)
        try:
            for token in tokens:
                row = offset + token.start[0] - 1
                if (
                    token.type == tokenize.COMMENT
                    and token.start[1] == 0
                    and depth == 0
                    and statement_start
                    and _CELL_MARKER.fullmatch(token.string)
                ):
                    markers.append(row)
                    restart = row + 1
                    break
                if token.type == tokenize.NEWLINE:
                    statement_start = True
                    previous = None
                    continue
                if token.type in _IGNORED:
                    continue
                if token.type == tokenize.ERRORTOKEN and token.string.isspace():
                    continue
                if token.type == tokenize.OP:
                    first = lines[row][: token.start[1]].strip() == ""
                    assignment = previous is not None and previous.string == "="
                    if (
                        token.string == "%"
                        and depth == 0
                        and ((first and statement_start) or assignment)
                    ):
                        has_magic = True
                        if first and lines[row][token.start[1] :].startswith("%%"):
                            # Cell magics own their full body. Do not parse it
                            # as Python, or remove/rewrite any of its contents.
                            next_marker = next(
                                (
                                    index
                                    for index in range(row + 1, len(lines))
                                    if _CELL_MARKER.fullmatch(lines[index].rstrip("\r\n"))
                                ),
                                None,
                            )
                            if next_marker is not None:
                                markers.append(next_marker)
                                restart = next_marker + 1
                            else:
                                restart = len(lines)
                            break
                    if token.string in {"(", "[", "{"}:
                        depth += 1
                    elif token.string in {")", "]", "}"}:
                        depth = max(0, depth - 1)
                # Python 3.11/3.12 classify bare exclamation marks differently.
                # Neither emits an operator token for one inside a string.
                if token.type in {tokenize.OP, tokenize.ERRORTOKEN} and token.string == "!":
                    first = lines[row][: token.start[1]].strip() == ""
                    assignment = previous is not None and previous.string == "="
                    if depth == 0 and ((first and statement_start) or assignment):
                        has_magic = True
                statement_start = False
                previous = token
        except (tokenize.TokenError, IndentationError):
            # Keep malformed code intact. runpy/IPython reports the original
            # syntax error; guessing boundaries after an open string is unsafe.
            pass
        if restart is None:
            break
        offset = restart

    cells: list[PythonCell] = []
    start = 0
    for marker in markers:
        body = "".join(lines[start:marker])
        if body.strip():
            cells.append(PythonCell(body, start + 1))
        start = marker + 1
    body = "".join(lines[start:])
    if body.strip() or not cells:
        cells.append(PythonCell(body, start + 1))
    return tuple(cells), bool(markers) or has_magic


def _write_error_line(runtime_directory: Path, line: int | None) -> None:
    if line is None or line < 1:
        return
    temporary: str | None = None
    try:
        runtime_directory.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=runtime_directory, prefix=".execution-", delete=False
        ) as handle:
            temporary = handle.name
            json.dump({"error_line": line}, handle)
            handle.flush()
        Path(temporary).replace(runtime_directory / "execution.json")
    except OSError:
        print("Could not save the original source-line hint.", file=sys.stderr)
    finally:
        if temporary is not None:
            with suppress(OSError):
                Path(temporary).unlink(missing_ok=True)


def _leading_blank_lines(source: str) -> int:
    count = 0
    for line in source.splitlines():
        if line.strip():
            break
        count += 1
    return count


def _error_line(error: BaseException, sources: dict[str, PythonCell]) -> int | None:
    if isinstance(error, SyntaxError) and error.filename in sources and error.lineno:
        cell = sources[error.filename]
        return cell.start_line + _leading_blank_lines(cell.code) + error.lineno - 1
    found = None
    traceback = error.__traceback__
    while traceback is not None:
        filename = traceback.tb_frame.f_code.co_filename
        if filename in sources:
            cell = sources[filename]
            found = cell.start_line + _leading_blank_lines(cell.code) + traceback.tb_lineno - 1
        traceback = traceback.tb_next
    return found


def _exit_status(error: BaseException) -> int:
    if isinstance(error, SystemExit):
        if error.code is None:
            return 0
        return error.code if isinstance(error.code, int) else 1
    return 130 if isinstance(error, KeyboardInterrupt) else 1


def execute_python_file(path: Path, runtime_directory: Path) -> int:
    """Execute a file, preserving ordinary scripts and true notebook semantics.

    IPython is imported only for real cell markers or IPython syntax. Its
    configuration/history live inside this run's private directory; no user's
    profile or startup scripts are loaded. Failure metadata contains only an
    original submitted-source line for the outer controller to range-check.
    """

    path = Path(path).resolve()
    runtime_directory = Path(runtime_directory)
    with tokenize.open(path) as handle:
        source = handle.read()
    cells, interactive = python_cells(source)
    if not interactive:
        try:
            runpy.run_path(str(path), run_name="__main__")
        except BaseException as error:
            # The actual file already has global line numbers. Do not apply
            # IPython's leading-empty-line normalization to ordinary scripts.
            traceback = error.__traceback__
            line = (
                error.lineno
                if isinstance(error, SyntaxError) and error.filename == str(path)
                else None
            )
            while traceback is not None:
                if traceback.tb_frame.f_code.co_filename == str(path):
                    line = traceback.tb_lineno
                traceback = traceback.tb_next
            if _exit_status(error) != 0:
                _write_error_line(runtime_directory, line)
            raise
        return 0

    ipython_directory = runtime_directory / "ipython"
    ipython_directory.mkdir(parents=True, exist_ok=True)
    previous_directory = os.environ.get("IPYTHONDIR")
    os.environ["IPYTHONDIR"] = str(ipython_directory.resolve())
    shell: Any = None
    previous_argv = sys.argv[:]
    try:
        try:
            import IPython
            from IPython.core.interactiveshell import InteractiveShell
            from traitlets.config import Config
        except ImportError:
            print(
                "Notebook cells and IPython magics need IPython. Install the notebooks "
                "profile in the selected Python backend, then run again.",
                file=sys.stderr,
            )
            return 2
        config = Config()
        config.HistoryManager.enabled = False
        config.HistoryManager.hist_file = ":memory:"
        config.InteractiveShell.history_load_length = 0
        config.InteractiveShell.colors = "nocolor" if IPython.version_info[0] >= 9 else "NoColor"

        class HeadlessInteractiveShell(InteractiveShell):
            """Permit inline/Agg formatting without a desktop event loop."""

            def enable_gui(self, gui: str | None = None) -> None:
                if gui is not None and gui.casefold() not in {"inline", "agg"}:
                    raise ValueError(
                        "Interactive GUI event loops are unavailable in the coding pad. "
                        "Use inline/Agg plots here, or the lesson's notebook/editor workflow."
                    )

            def enable_matplotlib(self, gui: str | None = None) -> Any:
                self.enable_gui(gui)
                return super().enable_matplotlib(gui)  # type: ignore[no-untyped-call]

        InteractiveShell.clear_instance()
        namespace = {"__name__": "__main__", "__file__": str(path), "__package__": None}
        shell = HeadlessInteractiveShell.instance(
            user_ns=namespace, config=config, ipython_dir=str(ipython_directory.resolve())
        )

        def headless_gui_magic(argument: str) -> None:
            # IPython's default %gui catches every error and reports success.
            # Let run_cell record this unsupported action as an actual failure.
            shell.enable_gui(argument.strip() or None)

        shell.register_magic_function(headless_gui_magic, "line", "gui")
        sys.argv[:] = [str(path), *previous_argv[1:]]
        sources: dict[str, PythonCell] = {}
        original_cache = shell.compile.cache
        current_cell = cells[0]

        def cache(code: str, number: int = 0, raw_code: str | None = None) -> str:
            filename: str = original_cache(code, number, raw_code=raw_code)
            sources[filename] = current_cell
            return filename

        shell.compile.cache = cache
        for index, cell in enumerate(cells, 1):
            current_cell = cell
            shell.execution_count = index
            result = shell.run_cell(cell.code, store_history=False, shell_futures=True)
            cell_error = result.error_before_exec
            if cell_error is None:
                cell_error = result.error_in_exec
            if cell_error is not None:
                status = _exit_status(cell_error)
                if status != 0:
                    first_line = cell.start_line + _leading_blank_lines(cell.code)
                    magic = cell.code.lstrip().startswith("%%")
                    line = first_line if magic else (_error_line(cell_error, sources) or first_line)
                    _write_error_line(runtime_directory, line)
                    print(
                        f"Notebook cell {index} failed at source line {line} "
                        f"(cell starts at line {cell.start_line}).",
                        file=sys.stderr,
                    )
                return status
        return 0
    finally:
        sys.argv[:] = previous_argv
        if previous_directory is None:
            os.environ.pop("IPYTHONDIR", None)
        else:
            os.environ["IPYTHONDIR"] = previous_directory
        if shell is not None:
            shell.history_manager.end_session()
            type(shell).clear_instance()
