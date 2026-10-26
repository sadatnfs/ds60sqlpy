"""Bounded plot documents shared by workers, saved receipts and the classroom."""

from __future__ import annotations

import base64
import binascii
import json
import math
import struct
from pathlib import Path
from typing import Any

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


def _json_value(value: Any, depth: int = 0) -> None:
    if depth > 32:
        raise ValueError("Chart nesting exceeds the limit.")
    if value is None or type(value) in {bool, int}:
        return
    if type(value) is float and math.isfinite(value):
        return
    if isinstance(value, str) and len(value) <= MAX_PLOT_BYTES:
        return
    if isinstance(value, list) and len(value) <= 20_000:
        for child in value:
            _json_value(child, depth + 1)
        return
    if isinstance(value, dict) and len(value) <= 2000:
        for key, child in value.items():
            if not isinstance(key, str) or len(key) > 200:
                raise ValueError("Invalid chart key.")
            _json_value(child, depth + 1)
        return
    raise ValueError("Charts need finite JSON values and bounded arrays.")


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


def validate_artifacts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > 2:
        raise ValueError("Keep at most two figures in a classroom run.")
    if len(json.dumps(value, allow_nan=False).encode()) > MAX_ARTIFACT_BYTES:
        raise ValueError("Combined classroom figures exceed the saved-output limit.")
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
            _json_value(figure)
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
        else:
            raise ValueError("Unknown classroom figure format.")
    return result


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
