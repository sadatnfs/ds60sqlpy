"""Standard-library checks for whether a code snippet can run on its own.

The classroom pad and the guide example harness share these rules. The module
imports nothing outside the standard library so host-side scripts can use it.
"""

from __future__ import annotations

import builtins
import re
import symtable

_FUTURE_IMPORT = re.compile(r"^from[ \t]+__future__[ \t]+import\b")
_MODULE_DUNDERS = frozenset(
    {"__name__", "__file__", "__doc__", "__builtins__", "__spec__", "__loader__", "__package__"}
)


def _hoist_future(source: str) -> str:
    lines = source.split("\n")
    future = [line for line in lines if _FUTURE_IMPORT.match(line)]
    if not future:
        return source
    return "\n".join([*future, *(line for line in lines if not _FUTURE_IMPORT.match(line))])


def python_free_names(source: str) -> frozenset[str] | None:
    """Return module-level names a snippet reads but never binds, or None if invalid."""

    hoisted = _hoist_future(source)
    try:
        compile(hoisted, "main.py", "exec", dont_inherit=True)
        table = symtable.symtable(hoisted, "main.py", "exec")
    except (SyntaxError, ValueError, OverflowError, MemoryError, RecursionError):
        return None
    bound: set[str] = set()
    referenced: set[str] = set()
    star = re.search(r"^\s*from\s+\S+\s+import\s+\*", hoisted, re.MULTILINE) is not None

    def visit(scope: symtable.SymbolTable, module: bool) -> None:
        for symbol in scope.get_symbols():
            name = symbol.get_name()
            if module:
                if symbol.is_assigned() or symbol.is_imported() or symbol.is_namespace():
                    bound.add(name)
                if symbol.is_referenced():
                    referenced.add(name)
            elif symbol.is_global():
                if symbol.is_declared_global() and symbol.is_assigned():
                    bound.add(name)
                if symbol.is_referenced():
                    referenced.add(name)
        for child in scope.get_children():
            visit(child, False)

    visit(table, True)
    if star:
        return frozenset()
    return frozenset(referenced - bound - set(dir(builtins)) - _MODULE_DUNDERS)


def standalone(language: str, text: str) -> bool:
    """Decide whether source in a normalized pad language can run on its own."""

    if language == "sql":
        return not any(line.lstrip().startswith("\\") for line in text.split("\n"))
    if language == "python":
        free = python_free_names(text)
        return free is not None and not free
    if language == "go":
        return "package main" in text and "func main(" in text
    if language in {"c", "cpp"}:
        return "int main(" in text
    if language == "java":
        return "static void main(" in text
    if language == "csharp":
        return "static void Main(" in text or "static async Task Main(" in text
    if language == "rust":
        return "fn main(" in text
    if language == "scala":
        return "def main(" in text or "@main" in text
    if language == "php":
        return text.lstrip().startswith("<?php")
    return False
