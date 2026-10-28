"""Evaluate component statuses rather than accepting HTTP200 as health."""

from __future__ import annotations

import json
import urllib.request


def check() -> dict[str, str]:
    with urllib.request.urlopen(
        "http://127.0.0.1:8080/api/v2/monitor/health", timeout=5
    ) as response:
        raw = response.read(16_385)
    if len(raw) > 16_384:
        raise ValueError("Health response exceeds budget")
    data = json.loads(raw)
    result = {
        name: data[name]["status"]
        for name in ("metadatabase", "scheduler", "dag_processor", "triggerer")
    }
    if any(value != "healthy" for value in result.values()):
        raise RuntimeError("Component status is not healthy: " + str(result))
    return result


if __name__ == "__main__":
    print(json.dumps(check()))
