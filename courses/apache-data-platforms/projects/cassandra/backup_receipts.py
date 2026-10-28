"""Atomic source-bound backup evidence without replacing an existing receipt."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


def save_receipt(directory: Path, identity: str, result: dict[str, Any]) -> None:
    if not re.fullmatch(r"restore_[a-f0-9]{16}", identity):
        raise ValueError("Invalid owned restore identity")
    if directory.is_symlink():
        raise ValueError("Evidence directory cannot be a symbolic link")
    directory.mkdir(mode=0o700, parents=False, exist_ok=True)
    target = directory / (identity + ".json")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=directory, prefix=".pending-", delete=False
        ) as output:
            temporary = Path(output.name)
            json.dump(result, output, indent=2)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.link(temporary, target)  # Atomic create; never replace historical evidence.
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
