"""Execute a Python pad and capture explicitly shown plots without browser access."""

from __future__ import annotations

import base64
import contextlib
import io
import json
import runpy
import sys
from pathlib import Path
from typing import Any

from ds60sqlpy.plot_artifacts import validate_artifacts


def main() -> None:
    saved: list[dict[str, Any]] = []

    def append(artifact: dict[str, Any]) -> None:
        if len(saved) >= 2:
            print("Figure limit reached: the first two figures are retained.", file=sys.stderr)
            return
        try:
            checked = validate_artifacts([*saved, artifact])
            Path("ds60-figures.json").write_text(json.dumps(checked, allow_nan=False), "utf-8")
        except (OSError, ValueError, TypeError, RecursionError) as exc:
            print("Figure omitted: " + str(exc), file=sys.stderr)
            return
        saved[:] = checked

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
    try:
        sys.argv = ["main.py"]
        runpy.run_path("main.py", run_name="__main__")
    finally:
        pyplot = sys.modules.get("matplotlib.pyplot")
        if pyplot is not None:
            with contextlib.suppress(Exception):
                pyplot.show()


if __name__ == "__main__":
    main()
