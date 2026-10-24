"""Generate the Rust learning path from original durable specifications."""

from importlib import import_module

from render import build

for module in ("foundations", "composition", "advanced"):
    import_module(module)
build()
