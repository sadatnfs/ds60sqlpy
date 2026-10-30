"""Read only this container's cgroup counters for bounded qualification evidence."""

import json
from pathlib import Path

root = Path("/sys/fs/cgroup")
print(
    json.dumps(
        {
            name: (root / name).read_text()
            for name in [
                "memory.current",
                "memory.peak",
                "memory.events",
                "pids.current",
                "pids.events",
            ]
            if (root / name).exists()
        }
    )
)
