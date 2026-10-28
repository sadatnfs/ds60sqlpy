"""Bounded plot documents shared by workers, saved receipts and the classroom."""

from __future__ import annotations

import base64
import binascii
import json
import math
import struct
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

_OUTPUT_DIRECTORY: Path | None = None

MAX_ARTIFACT_BYTES = 384_000
MAX_PLOT_BYTES = 180_000
PLOT_TYPES = frozenset(
    {
        "scatter",
        "bar",
        "box",
        "histogram",
        "histogram2d",
        "histogram2dcontour",
        "heatmap",
        "contour",
        "violin",
        "pie",
        "image",
        "scatterternary",
    }
)


class UnsafeIntegerError(ValueError):
    """A numeric integer cannot be represented exactly by the browser contract."""


def _json_value(value: Any, depth: int = 0, *, exact_integers: bool = True) -> None:
    if depth > 32:
        raise ValueError("Chart nesting exceeds the limit.")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if exact_integers:
            _report_numbers(value)
        return
    if type(value) is float and math.isfinite(value):
        return
    if isinstance(value, str) and len(value) <= MAX_PLOT_BYTES:
        return
    if isinstance(value, list) and len(value) <= 20_000:
        for child in value:
            _json_value(child, depth + 1, exact_integers=exact_integers)
        return
    if isinstance(value, dict) and len(value) <= 2000:
        for key, child in value.items():
            if not isinstance(key, str) or len(key) > 200:
                raise ValueError("Invalid chart key.")
            _json_value(child, depth + 1, exact_integers=exact_integers)
        return
    raise ValueError("Charts need finite JSON values and bounded arrays.")


def _report_numbers(value: Any) -> None:
    """JSON browser consumers share IEEE754 integer precision."""
    if type(value) is int and abs(value) > 9_007_199_254_740_991:
        raise UnsafeIntegerError(
            "Represent large integer identifiers as strings to preserve exact values."
        )
    if isinstance(value, (list, dict)):
        for child in value.values() if isinstance(value, dict) else value:
            _report_numbers(child)


def _metadata(layout: dict[str, Any]) -> dict[str, Any]:
    meta = layout.get("meta", {})
    if not isinstance(meta, dict):
        return {}
    result: dict[str, Any] = {}
    description = meta.get("description")
    if description is not None:
        if not isinstance(description, str) or len(description) > 2000:
            raise ValueError("Chart description exceeds its limit.")
        result["description"] = description
    table = meta.get("table")
    if table is not None:
        if not isinstance(table, dict):
            raise ValueError("Chart table needs columns and rows.")
        columns, rows = table.get("columns"), table.get("rows")
        if (
            not isinstance(columns, list)
            or not 1 <= len(columns) <= 12
            or any(not isinstance(c, str) or not c or len(c) > 200 for c in columns)
            or not isinstance(rows, list)
            or len(rows) > 100
        ):
            raise ValueError("Chart table exceeds its bounds.")
        for row in rows:
            if not isinstance(row, list) or len(row) != len(columns):
                raise ValueError("Chart table row does not match columns.")
            for value in row:
                if value is not None and (
                    type(value) not in {str, bool, int, float}
                    or (isinstance(value, str) and len(value) > 2000)
                    or (type(value) is float and not math.isfinite(value))
                ):
                    raise ValueError("Chart table cells must be finite scalar values.")
        result["table"] = {"columns": columns, "rows": rows}
    return result


def _validate_artifacts(
    value: Any, *, legacy_plotly_integers: bool = False
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > 2:
        raise ValueError(
            "Keep at most two saved outputs (figures or structured reports) in a classroom run."
        )
    if len(json.dumps(value, allow_nan=False).encode()) > MAX_ARTIFACT_BYTES:
        raise ValueError("Combined classroom outputs exceed the saved-output limit.")
    result: list[dict[str, Any]] = []
    for artifact in value:
        if not isinstance(artifact, dict):
            raise ValueError("Invalid figure document.")
        kind = artifact.get("kind")
        if kind == "png":
            encoded = artifact.get("data")
            if not isinstance(encoded, str):
                raise ValueError("Invalid PNG data.")
            try:
                raw = base64.b64decode(encoded, validate=True)
            except (ValueError, binascii.Error) as exc:
                raise ValueError("Invalid PNG encoding.") from exc
            if (
                len(raw) > MAX_PLOT_BYTES
                or len(raw) < 24
                or raw[:8] != b"\x89PNG\r\n\x1a\n"
                or raw[12:16] != b"IHDR"
            ):
                raise ValueError("Invalid or oversized PNG.")
            width, height = struct.unpack(">II", raw[16:24])
            if not 1 <= width <= 4096 or not 1 <= height <= 4096 or width * height > 4_000_000:
                raise ValueError("PNG dimensions exceed the classroom limit.")
            title = artifact.get("description", "Generated figure")
            if not isinstance(title, str) or len(title) > 2000:
                raise ValueError("Invalid figure description.")
            result.append({"kind": "png", "data": encoded, "description": title})
        elif kind == "plotly":
            figure = artifact.get("figure")
            if not isinstance(figure, dict) or set(figure) - {"data", "layout", "frames"}:
                raise ValueError("Invalid Plotly document.")
            if len(json.dumps(figure, allow_nan=False).encode()) > MAX_PLOT_BYTES:
                raise ValueError("Plotly figure exceeds the classroom limit.")
            _json_value(figure, exact_integers=not legacy_plotly_integers)
            traces, layout, frames = (
                figure.get("data"),
                figure.get("layout", {}),
                figure.get("frames", []),
            )
            if (
                not isinstance(traces, list)
                or not 1 <= len(traces) <= 40
                or not isinstance(layout, dict)
                or not isinstance(frames, list)
                or len(frames) > 100
            ):
                raise ValueError("Invalid Plotly traces or layout.")
            if layout.get("images"):
                raise ValueError(
                    "External/background images are not part of offline chart capture."
                )
            layers = [(traces, layout)]
            for frame in frames:
                if not isinstance(frame, dict) or set(frame) - {
                    "data",
                    "layout",
                    "name",
                    "group",
                    "traces",
                    "baseframe",
                }:
                    raise ValueError("Invalid Plotly animation frame.")
                layers.append((frame.get("data", []), frame.get("layout", {})))
            for layer_traces, layer_layout in layers:
                if (
                    not isinstance(layer_traces, list)
                    or len(layer_traces) > 40
                    or not isinstance(layer_layout, dict)
                    or layer_layout.get("images")
                ):
                    raise ValueError("Invalid frame layout or external background images.")
                for trace in layer_traces:
                    if (
                        not isinstance(trace, dict)
                        or trace.get("type", "scatter") not in PLOT_TYPES
                    ):
                        raise ValueError(
                            "This chart type needs a separately prepared Plotly project."
                        )
                    if "source" in trace:
                        raise ValueError(
                            "Chart image sources are unavailable; use inline numeric data."
                        )
            metadata = _metadata(layout)
            result.append({"kind": "plotly", "figure": figure, **metadata})
        elif kind in {"table", "json"}:
            title = artifact.get("description", "Structured result")
            if not isinstance(title, str) or not title.strip() or len(title) > 2000:
                raise ValueError("Invalid report description.")
            if len(json.dumps(artifact, allow_nan=False).encode()) > MAX_PLOT_BYTES:
                raise ValueError("Structured report exceeds the classroom limit.")
            if kind == "table":
                table = _metadata({"meta": {"table": artifact.get("table")}}).get("table")
                if table is None:
                    raise ValueError("Structured table needs columns and rows.")
                _report_numbers(table)
                result.append({"kind": kind, "description": title, "table": table})
            else:
                if "data" not in artifact:
                    raise ValueError("Structured report needs data.")
                _json_value(artifact["data"])
                _report_numbers(artifact["data"])
                result.append({"kind": kind, "description": title, "data": artifact["data"]})
        else:
            raise ValueError("Unknown classroom figure format.")
    return result


def validate_artifacts(value: Any) -> list[dict[str, Any]]:
    """Validate new outputs with strict browser integer precision."""
    return _validate_artifacts(value)


def read_saved_artifacts(value: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Project saved figures for display without changing any stored value.

    Only the historical Plotly integer contract is relaxed during validation.
    Every original shape, resource and offline-content check still runs before
    an unsafe figure can be withheld. Structured table/JSON writes did not exist
    under the old contract and remain strict here.
    """
    checked = _validate_artifacts(value, legacy_plotly_integers=True)
    visible: list[dict[str, Any]] = []
    withheld: list[dict[str, Any]] = []
    total_raw_bytes = 0
    for position, artifact in enumerate(checked, 1):
        if artifact["kind"] != "plotly":
            visible.append(artifact)
            continue
        try:
            _report_numbers(artifact["figure"])
        except UnsafeIntegerError:
            # Serialize in Python before the browser receives JSON. Integer
            # literals remain numeric and exact inside this opaque text string.
            raw_json = json.dumps(artifact["figure"], ensure_ascii=True, allow_nan=False)
            size = len(raw_json.encode("utf-8"))
            total_raw_bytes += size
            if size > MAX_PLOT_BYTES or total_raw_bytes > MAX_ARTIFACT_BYTES:
                raise ValueError(
                    "Saved figure downloads exceed their original byte budgets."
                ) from None
            withheld.append(
                {
                    "position": position,
                    "reason": (
                        "This saved figure contains numeric integers outside the browser's "
                        "exact range and is not rendered. Its original saved data, source "
                        "and output were retained. Download the original figure JSON "
                        "to inspect the exact values."
                    ),
                    "raw_json": raw_json,
                }
            )
        else:
            visible.append(artifact)
    return visible, withheld


def read_artifacts(directory: Path) -> tuple[list[dict[str, Any]], str]:
    path = directory / "ds60-figures.json"
    collected: list[dict[str, Any]] = []
    warnings: list[str] = []
    try:
        if path.exists():
            if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_ARTIFACT_BYTES:
                raise ValueError("Figure file exceeds its limit or is not an ordinary file.")
            payload = json.loads(path.read_text("utf-8"))
            if not isinstance(payload, list):
                raise ValueError("Figure file needs an array.")
            for item in payload[:2]:
                try:
                    collected = validate_artifacts([*collected, item])
                except (ValueError, TypeError, RecursionError) as exc:
                    warnings.append("Figure omitted: " + str(exc)[:200])
            if len(payload) > 2:
                warnings.append("Only the first two figure entries were considered.")
        for png in sorted(directory.glob(".ds60-r-*.png"))[:2]:
            if len(collected) == 2:
                break
            if png.is_symlink() or not png.is_file() or png.stat().st_size > MAX_PLOT_BYTES:
                warnings.append("An invalid or oversized R PNG was omitted.")
                continue
            item = {
                "kind": "png",
                "data": base64.b64encode(png.read_bytes()).decode(),
                "description": "R figure " + str(len(collected) + 1),
            }
            try:
                collected = validate_artifacts([*collected, item])
            except (ValueError, TypeError, RecursionError) as exc:
                warnings.append("R figure omitted: " + str(exc)[:200])
        return collected, " ".join(warnings)[:1000]
    except (OSError, TypeError, ValueError, RecursionError) as exc:
        return collected, "Figure capture could not be saved: " + str(exc)[:300]


@contextmanager
def output_directory(directory: Path) -> Iterator[None]:
    """Anchor one execution's output while restoring any surrounding capture scope."""
    global _OUTPUT_DIRECTORY
    previous = _OUTPUT_DIRECTORY
    _OUTPUT_DIRECTORY = directory
    try:
        yield
    finally:
        _OUTPUT_DIRECTORY = previous


def publish_artifact(artifact: dict[str, Any]) -> None:
    """Append one bounded result in the current job without replacing earlier outputs.

    This API is intended for classroom Python programs. Files remain in the job's
    scratch directory; the worker validates and saves the complete result receipt.
    """
    directory = _OUTPUT_DIRECTORY or Path.cwd()
    path = directory / "ds60-figures.json"
    existing: Any = []
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_ARTIFACT_BYTES:
            raise ValueError("Existing output is not an ordinary bounded artifact file.")
        existing = json.loads(path.read_text("utf-8"))
    checked = validate_artifacts([*validate_artifacts(existing), artifact])
    encoded = json.dumps(checked, allow_nan=False)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=directory, prefix=".ds60-output-", delete=False
        ) as stream:
            temporary = stream.name
            stream.write(encoded)
            stream.flush()
        Path(temporary).replace(path)
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def publish_table(columns: list[str], rows: list[list[Any]], *, description: str) -> None:
    """Save up to 100 rows and 12 columns with an explicit description."""
    publish_artifact(
        {"kind": "table", "description": description, "table": {"columns": columns, "rows": rows}}
    )


def publish_report(data: Any, *, description: str) -> None:
    """Save a finite JSON report while retaining its source-bound run receipt."""
    publish_artifact({"kind": "json", "description": description, "data": data})
