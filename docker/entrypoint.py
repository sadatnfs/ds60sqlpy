#!/usr/bin/env python3
"""Prepare the ephemeral workspace root and drop to the learner identity."""

from ds60sqlpy.container_runtime import entrypoint

if __name__ == "__main__":
    raise SystemExit(entrypoint())
