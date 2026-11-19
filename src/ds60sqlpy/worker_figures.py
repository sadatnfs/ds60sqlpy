"""Execute a Python pad and capture explicitly shown plots without browser access."""

from __future__ import annotations

import base64
import contextlib
import io
import json
import runpy
import sys
import warnings
from pathlib import Path
from typing import Any

from ds60sqlpy import plot_artifacts
from ds60sqlpy.plot_artifacts import publish_artifact

LEARNER_FILE = "main.py"


def report_learner_error(error: Exception) -> bool:
    """Report an uncaught learner error from its first ``main.py`` frame.

    This mirrors ``notebook_execution.learner_excepthook`` for the legacy pad.
    Line numbers, caret markers, chained exceptions and later library frames are
    kept, and a SyntaxError points at the learner's line. The report goes
    through ``sys.excepthook`` because libraries such as PyTensor install their
    own hook. Returns False for a failure without a learner frame, such as a
    runner error, which the caller re-raises with Python's complete traceback.
    """

    start = error.__traceback__
    while start is not None and start.tb_frame.f_code.co_filename != LEARNER_FILE:
        start = start.tb_next
    if start is None and not (isinstance(error, SyntaxError) and error.filename == LEARNER_FILE):
        return False
    # Python's own hook prints the exception's attached traceback, not the argument.
    sys.excepthook(type(error), error.with_traceback(start), start)
    return True


def _run() -> None:
    def append(artifact: dict[str, Any]) -> None:
        try:
            publish_artifact(artifact)
        except (OSError, ValueError, TypeError, RecursionError) as exc:
            print("Figure omitted: " + str(exc), file=sys.stderr)

    def patch_plotly(module: Any) -> None:
        def show_plotly(figure: Any, *args: Any, **kwargs: Any) -> None:
            append({"kind": "plotly", "figure": json.loads(module.to_json(figure))})

        module.show = show_plotly

    def patch_matplotlib(pyplot: Any) -> None:
        def show_matplotlib(*args: Any, **kwargs: Any) -> None:
            for number in pyplot.get_fignums():
                figure = pyplot.figure(number)
                buffer = io.BytesIO()
                figure.savefig(buffer, format="png", dpi=90, bbox_inches="tight")
                append(
                    {
                        "kind": "png",
                        "data": base64.b64encode(buffer.getvalue()).decode(),
                        "description": figure.axes[0].get_title()
                        if figure.axes
                        else "Generated figure",
                    }
                )
                pyplot.close(figure)

        pyplot.show = show_matplotlib

    from ds60sqlpy.plot_capture import install_display_hooks

    install_display_hooks(patch_plotly, patch_matplotlib)
    # PyMC imports ArviZ, which announces its coming refactor on every fresh run.
    warnings.filterwarnings(
        "ignore",
        message=r"\s*ArviZ is undergoing a major refactor",
        category=FutureWarning,
        module="arviz",
    )
    try:
        sys.argv = [LEARNER_FILE]
        runpy.run_path(LEARNER_FILE, run_name="__main__")
    finally:
        pyplot = sys.modules.get("matplotlib.pyplot")
        if pyplot is not None:
            with contextlib.suppress(Exception):
                pyplot.show()


def main() -> None:
    with plot_artifacts.output_directory(Path.cwd()):
        try:
            return _run()
        except Exception as error:
            if not report_learner_error(error):
                raise
            raise SystemExit(1) from None


if __name__ == "__main__":
    main()
