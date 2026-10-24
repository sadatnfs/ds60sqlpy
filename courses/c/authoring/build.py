"""Regenerate the subject from explicitly ordered durable sources."""

from importlib import import_module

from render import render

if __name__ == "__main__":
    # These modules register lessons in route order; alphabetical imports would renumber IDs.
    for section in ("foundations", "composition", "systems"):
        import_module(section)
    render()
