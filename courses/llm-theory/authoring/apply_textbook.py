"""Apply both coordinated LLM textbook prose layers after ordinary generation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
from pathlib import Path
from types import ModuleType

BASE = Path(__file__).resolve().parent


def load_layer(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, BASE / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load textbook prose layer " + name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def apply(
    only: set[str] | None = None, *, require_complete: bool = False
) -> dict[str, dict[str, object]]:
    selected = only if only is not None else {f"llm-{number:03}" for number in range(1, 49)}
    layers = [load_layer("textbook_foundations"), load_layer("textbook_advanced")]
    result: dict[str, dict[str, object]] = {}
    for identity in sorted(selected):
        if not re.fullmatch(r"llm-\d{3}", identity) or not 1 <= int(identity[-3:]) <= 48:
            raise ValueError("Unknown textbook chapter " + identity)
        layer = layers[0] if int(identity[-3:]) <= 24 else layers[1]
        if require_complete and not (layer.BASE / f"{identity}.md").is_file():
            raise ValueError("Missing textbook prose input " + identity)
        path = BASE.parent / "guides" / f"{identity}.md"
        before = path.read_text(encoding="utf-8")
        code = re.findall(r"```python\n(.*?)\n```", before, re.S)
        after = layer.enrich_guide(identity, before)
        if re.findall(r"```python\n(.*?)\n```", after, re.S) != code:
            raise ValueError("Textbook pass changed executable code in " + identity)
        if layer.enrich_guide(identity, after) != after:
            raise ValueError("Textbook prose application is not idempotent for " + identity)
        path.write_text(after, encoding="utf-8")
        result[identity] = {
            "before_sha256": hashlib.sha256(before.encode()).hexdigest(),
            "after_sha256": hashlib.sha256(after.encode()).hexdigest(),
            "python_blocks_unchanged": len(code),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", nargs="+")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    rows = apply(set(args.ids) if args.ids else None, require_complete=args.require_complete)
    print(f"Applied textbook prose to {len(rows)} guides with unchanged Python blocks.")


if __name__ == "__main__":
    main()
