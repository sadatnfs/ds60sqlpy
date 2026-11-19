"""Describe the inspectable checks in an exercise program for its Verify line.

The text is derived from the exercise's own assertions, closeness checks and
expected exceptions, so each Verify line names the quantities, values,
tolerances and failures that the reference actually tests.
"""

from __future__ import annotations

import ast
import re

CLOSE_CALLS = {
    "assert_allclose": "matches",
    "assert_close": "matches",
    "assert_array_equal": "equals",
    "assert_equal": "equals",
    "assert_array_almost_equal": "matches",
    "assert_near": "matches",
}
MAX_EXPRESSION = 90


def _code(node: ast.AST) -> str:
    return ast.unparse(node).replace("`", "'")


def _close_call(node: ast.AST) -> tuple[str, ast.Call] | None:
    if not isinstance(node, ast.Call):
        return None
    name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
    if name in CLOSE_CALLS and len(node.args) >= 2:
        return CLOSE_CALLS[name], node
    return None


def _tolerance(call: ast.Call) -> str:
    values = {
        keyword.arg: re.sub(r"(\d)e-0(\d)", r"\1e-\2", _code(keyword.value))
        for keyword in call.keywords
        if keyword.arg
    }
    atol = values.get("atol")
    rtol = values.get("rtol")
    if atol not in (None, "0", "0.0") and rtol in (None, "0", "0.0"):
        return f" within {atol}"
    if atol in (None, "0", "0.0") and rtol not in (None, "0", "0.0"):
        return f" within relative tolerance {rtol}"
    if atol not in (None, "0", "0.0") and rtol not in (None, "0", "0.0"):
        return f" within atol {atol} and rtol {rtol}"
    if atol in ("0", "0.0") and rtol in ("0", "0.0"):
        return " exactly"
    return ""


def _short(text: str) -> bool:
    return len(text) <= MAX_EXPRESSION


def _checks(statements: list[ast.stmt], prefix: str, out: list[str]) -> None:
    for node in statements:
        if isinstance(node, ast.Assert):
            test = node.test
            parts = (
                test.values
                if isinstance(test, ast.BoolOp) and isinstance(test.op, ast.And)
                else [test]
            )
            for part in parts:
                text = _code(part)
                out.append(prefix + (f"`{text}`" if _short(text) else "the combined assertion"))
        elif isinstance(node, ast.Expr) and (found := _close_call(node.value)):
            verb, call = found
            left, right = _code(call.args[0]), _code(call.args[1])
            if _short(left) and _short(right):
                out.append(prefix + f"`{left}` {verb} `{right}`{_tolerance(call)}")
            else:
                out.append(prefix + f"a tensor comparison passes{_tolerance(call)}")
        elif isinstance(node, ast.Try) and node.handlers:
            names = [_code(handler.type) for handler in node.handlers if handler.type is not None]
            attempted = next(
                (
                    statement
                    for statement in reversed(node.body)
                    if isinstance(statement, (ast.Expr, ast.Assign, ast.AugAssign))
                ),
                None,
            )
            raises_on_success = any(
                isinstance(item, ast.Raise) for item in ast.walk(ast.Module(node.orelse, []))
            )
            if names and attempted is not None and raises_on_success:
                call = _code(attempted.value if isinstance(attempted, ast.Expr) else attempted)
                label = " or ".join(f"`{name}`" for name in names)
                subject = f"`{call}`" if _short(call) else "the invalid call"
                out.append(prefix + f"{subject} raises {label}")
                for handler in node.handlers:
                    _checks(handler.body, prefix + "the raised error satisfies ", out)
            else:
                _checks(node.body, prefix, out)
                for handler in node.handlers:
                    _checks(handler.body, prefix, out)
        elif isinstance(node, ast.For):
            target, iterable = _code(node.target), _code(node.iter)
            label = (
                f"for every `{target}` in `{iterable}`, "
                if _short(target + iterable)
                else "for every looped case, "
            )
            _checks(node.body, prefix + label, out)
        elif isinstance(node, ast.If) and node.body and isinstance(node.body[0], ast.Raise):
            required = _negated(node.test)
            out.append(prefix + (f"`{required}`" if _short(required) else "the guarded condition"))
        elif isinstance(node, (ast.With, ast.If)):
            _checks(node.body, prefix, out)
            if isinstance(node, ast.If):
                _checks(node.orelse, prefix, out)


def _negated(test: ast.expr) -> str:
    """Return the condition that must hold for ``if test: raise`` not to fire."""
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return _code(test.operand)
    if isinstance(test, ast.Compare) and len(test.ops) == 1:
        flipped = {
            ast.NotIn: ast.In(),
            ast.In: ast.NotIn(),
            ast.NotEq: ast.Eq(),
            ast.Eq: ast.NotEq(),
            ast.IsNot: ast.Is(),
            ast.Is: ast.IsNot(),
        }.get(type(test.ops[0]))
        if flipped is not None:
            return _code(ast.Compare(left=test.left, ops=[flipped], comparators=test.comparators))
    return "not (" + _code(test) + ")"


def describe_checks(code: str, limit: int = 4) -> str | None:
    """Return a sentence naming the checks in ``code``, or None for non-Python text."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    found: list[str] = []
    _checks(tree.body, "", found)
    if not found:
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                _checks(node.body, f"inside `{node.name}`, ", found)
    if not found:
        return None
    shown = found[:limit]
    if len(found) > limit:
        remaining = len(found) - limit
        shown.append(f"{remaining} further check{'s' if remaining != 1 else ''}")
    if len(shown) == 1:
        return shown[0]
    separator = "; " if any("," in item for item in shown) else ", "
    return separator.join(shown[:-1]) + " and " + shown[-1]
