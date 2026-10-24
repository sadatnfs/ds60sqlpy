"""Generate only the swift subject from its durable teaching specifications."""

from importlib import import_module

from render import build

for module in ("foundations", "composition", "advanced"):
    import_module(module)

build()
