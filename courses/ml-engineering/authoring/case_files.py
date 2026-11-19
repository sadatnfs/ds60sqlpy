"""Render the dbt project files and commands that a reference case writes and runs.

The dbt references build each project through one shared Python harness. This
module reads a case function statically, without importing dbt or running code,
and recovers the literal model SQL, YAML, CSV seeds and dbt commands that the
harness writes and invokes. Values computed only at run time are shown as
``<expression>`` placeholders and listed separately.
"""

from __future__ import annotations

import ast
import shlex
from dataclasses import dataclass, field
from typing import Any

import yaml

HARNESS = ("project", "invoke", "rows", "artifact", "relation")
_SQL_BREAKS = (
    "select ",
    "from ",
    "where ",
    "group by ",
    "order by ",
    "having ",
    "union all ",
    "left join ",
    "inner join ",
    "join ",
)


@dataclass(frozen=True)
class Opaque:
    text: str

    def __str__(self) -> str:
        return f"<{self.text}>"


@dataclass(frozen=True)
class PathRef:
    relative: str

    def __truediv__(self, other: str) -> PathRef:
        return PathRef(f"{self.relative}/{other}" if self.relative else other)

    def __str__(self) -> str:
        return self.relative or "."


class _Unknown(Exception):
    pass


@dataclass
class Trace:
    files: list[tuple[str, Any]] = field(default_factory=list)
    steps: list[tuple[str, Any]] = field(default_factory=list)


class _Reader:
    def __init__(self, source: str) -> None:
        self.source = source
        tree = ast.parse(source)
        self.functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        self.trace = Trace()
        self.results: dict[int, Any] = {}

    def segment(self, node: ast.AST) -> str:
        return ast.get_source_segment(self.source, node) or type(node).__name__

    def value(self, node: ast.AST, env: dict[str, Any]) -> Any:
        try:
            return self._value(node, env)
        except _Unknown:
            return Opaque(self.segment(node))

    def _value(self, node: ast.AST, env: dict[str, Any]) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in env and not isinstance(env[node.id], Opaque):
                return env[node.id]
            raise _Unknown
        if isinstance(node, ast.JoinedStr):
            parts = []
            for piece in node.values:
                if isinstance(piece, ast.Constant):
                    parts.append(str(piece.value))
                else:
                    assert isinstance(piece, ast.FormattedValue)
                    parts.append(str(self.value(piece.value, env)))
            return "".join(parts)
        if isinstance(node, ast.Dict):
            result: dict[Any, Any] = {}
            for key, item in zip(node.keys, node.values, strict=True):
                if key is None:
                    unpacked = self._value(item, env)
                    if not isinstance(unpacked, dict):
                        raise _Unknown
                    result.update(unpacked)
                else:
                    result[self._value(key, env)] = self.value(item, env)
            return result
        if isinstance(node, (ast.List, ast.Tuple)):
            items = [self.value(item, env) for item in node.elts]
            return items if isinstance(node, ast.List) else tuple(items)
        if isinstance(node, ast.IfExp):
            test = self._value(node.test, env)
            return self._value(node.body if test else node.orelse, env)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return not self._value(node.operand, env)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -self._value(node.operand, env)
        if isinstance(node, ast.BinOp):
            left, right = self._value(node.left, env), self._value(node.right, env)
            if isinstance(node.op, ast.Div) and isinstance(left, PathRef):
                return left / str(right)
            if isinstance(left, (Opaque, PathRef)) or isinstance(right, (Opaque, PathRef)):
                raise _Unknown
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            raise _Unknown
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "str"
            and len(node.args) == 1
        ):
            return str(self._value(node.args[0], env))
        raise _Unknown

    def run(self, name: str, arguments: list[Any], env_in: dict[str, Any] | None = None) -> Any:
        function = self.functions[name]
        env: dict[str, Any] = dict(env_in or {})
        parameters = [a.arg for a in function.args.args]
        defaults = function.args.defaults
        for index, parameter in enumerate(parameters):
            if index < len(arguments):
                env[parameter] = arguments[index]
            else:
                offset = index - (len(parameters) - len(defaults))
                if offset >= 0:
                    env[parameter] = self.value(defaults[offset], env)
        _, result = self.block(function.body, env)
        return result

    def block(self, statements: list[ast.stmt], env: dict[str, Any]) -> tuple[bool, Any]:
        for statement in statements:
            done, result = self.statement(statement, env)
            if done:
                return True, result
        return False, None

    def statement(self, node: ast.stmt, env: dict[str, Any]) -> tuple[bool, Any]:
        if isinstance(node, ast.With):
            for item in node.items:
                if isinstance(item.optional_vars, ast.Name):
                    env[item.optional_vars.id] = Opaque("temporary directory")
            return self.block(node.body, env)
        if isinstance(node, ast.If):
            try:
                test = self._value(node.test, env)
            except _Unknown:
                return False, None
            return self.block(node.body if test else node.orelse, env)
        if isinstance(node, ast.Assign):
            produced = self.expression(node.value, env)
            for target in node.targets:
                if isinstance(target, ast.Name):
                    env[target.id] = produced
            return False, None
        if isinstance(node, ast.Expr):
            self.expression(node.value, env)
            return False, None
        if isinstance(node, ast.Return):
            return True, None if node.value is None else self.expression(node.value, env)
        return False, None

    def expression(self, node: ast.AST, env: dict[str, Any]) -> Any:
        for call in _calls_in_order(node):
            self.call(call, env)
        if isinstance(node, ast.Call):
            produced = self._call_result(node, env)
            if produced is not None:
                return produced
        return self.value(node, env)

    def _call_result(self, node: ast.Call, env: dict[str, Any]) -> Any:
        if isinstance(node.func, ast.Name):
            if node.func.id == "project":
                return PathRef("")
            if node.func.id in self.functions and node.func.id not in HARNESS:
                return self.results.get(id(node))
        return None

    def call(self, node: ast.Call, env: dict[str, Any]) -> None:
        func = node.func
        if isinstance(func, ast.Name) and func.id == "project":
            self.create(node, env)
        elif isinstance(func, ast.Name) and func.id == "invoke":
            arguments = [self.value(a, env) for a in node.args[1:]]
            succeeds = True
            for keyword in node.keywords:
                if keyword.arg == "succeeds":
                    succeeds = self.value(keyword.value, env)
            self.trace.steps.append(("command", (arguments, succeeds)))
        elif isinstance(func, ast.Attribute) and func.attr == "write_text":
            target = self.value(func.value, env)
            if isinstance(target, PathRef) and node.args:
                content = self.value(node.args[0], env)
                if any(kind == "command" for kind, _ in self.trace.steps):
                    self.trace.steps.append(("file", (target.relative, content)))
                else:
                    self.trace.files.append((target.relative, content))
        elif isinstance(func, ast.Name) and func.id in self.functions and func.id not in HARNESS:
            arguments = [self.value(a, env) for a in node.args]
            if any(isinstance(a, PathRef) for a in arguments) and not _returns_project(
                self.functions[func.id]
            ):
                self.trace.steps.append(("helper", self.segment(node)))
                return
            self.results[id(node)] = self.run(func.id, arguments)
        elif isinstance(func, ast.Attribute) and self.segment(func).startswith("shutil."):
            self.trace.steps.append(("helper", self.segment(node)))

    def create(self, node: ast.Call, env: dict[str, Any]) -> None:
        names = ("directory", "models", "seeds", "schema", "snapshots", "macros")
        given = {names[i]: self.value(a, env) for i, a in enumerate(node.args) if i}
        given.update({k.arg: self.value(k.value, env) for k in node.keywords if k.arg})
        models = given.get("models") or {"answer": "select 42::integer as answer"}
        for name, sql in _items(models):
            self.trace.files.append((f"models/{name}.sql", sql))
        for name, csv in _items(given.get("seeds")):
            self.trace.files.append((f"seeds/{name}.csv", csv))
        if given.get("schema"):
            schema = given["schema"]
            document = {"version": 2, **schema} if isinstance(schema, dict) else schema
            self.trace.files.append(("models/schema.yml", document))
        if given.get("snapshots"):
            document = {"version": 2, "snapshots": given["snapshots"]}
            self.trace.files.append(("snapshots/snapshots.yml", document))
        for name, sql in _items(given.get("macros")):
            self.trace.files.append((f"macros/{name}.sql", sql))


def _items(value: Any) -> list[tuple[Any, Any]]:
    if isinstance(value, dict):
        return list(value.items())
    return []


def _returns_project(function: ast.FunctionDef) -> bool:
    return any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "project"
        for n in ast.walk(function)
    )


def _calls_in_order(node: ast.AST) -> list[ast.Call]:
    found: list[ast.Call] = []

    def visit(current: ast.AST) -> None:
        if isinstance(current, (ast.Lambda, ast.FunctionDef)):
            return
        for child in ast.iter_child_nodes(current):
            visit(child)
        if isinstance(current, ast.Call):
            found.append(current)

    visit(node)
    return found


def read_case(source: str, function: str) -> Trace:
    reader = _Reader(source)
    reader.run(function, [])
    return reader.trace


class _IndentedDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        super().increase_indent(flow, False)

    def choose_scalar_style(self) -> str:
        # Match the repository's YAML formatter, which prefers double quotes.
        style = super().choose_scalar_style()
        return '"' if style == "'" else style


def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(_plain(k)): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if isinstance(value, (Opaque, PathRef)):
        return str(value)
    return value


def yaml_text(document: Any) -> str:
    return yaml.dump(
        _plain(document),
        Dumper=_IndentedDumper,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
        width=88,
    )


def sql_for_reading(sql: str) -> str:
    """Break a long one-line statement at top-level clauses without changing tokens.

    Statements that fit the dbt SQL formatter's 100-column limit stay on one line.
    Maintained references store longer models in that formatter's layout already.
    """
    if "\n" in sql or len(sql) <= 100:
        return sql
    characters = list(sql)
    depth, quote, jinja = 0, False, None
    index = 0
    lowered = sql.lower()
    while index < len(sql):
        pair = sql[index : index + 2]
        if jinja:
            if pair == jinja:
                if jinja == "%}" and index + 2 < len(sql) and sql[index + 2] == " ":
                    characters[index + 2] = "\n"
                jinja = None
                index += 2
                continue
            index += 1
            continue
        if quote:
            quote = sql[index] != "'"
            index += 1
            continue
        if pair in ("{{", "{%"):
            if pair == "{%" and index and sql[index - 1] == " ":
                characters[index - 1] = "\n"
            jinja = "}}" if pair == "{{" else "%}"
            if pair == "{{" and lowered.startswith("{{ config(", index):
                end = sql.find("}}", index)
                if end != -1 and end + 2 < len(sql) and sql[end + 2] == " ":
                    characters[end + 2] = "\n"
            index += 2
            continue
        char = sql[index]
        if char == "'":
            quote = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif (
            depth == 0
            and index
            and sql[index - 1] == " "
            and any(lowered.startswith(word, index) for word in _SQL_BREAKS)
        ):
            characters[index - 1] = "\n"
        index += 1
    text = "".join(characters)
    assert text.replace("\n", " ") == sql
    return text


def _block(path: str, content: Any) -> str:
    if isinstance(content, (dict, list)):
        return f"```yaml\n{yaml_text(content)}```"
    text = str(content)
    if path.endswith(".sql"):
        language, text = "sql", sql_for_reading(text)
    elif path.endswith((".yml", ".yaml")):
        language = "yaml"
    else:
        language = "text"
    return f"```{language}\n{text.rstrip()}\n```"


def _placeholders(value: Any, found: list[str]) -> None:
    if isinstance(value, Opaque):
        if value.text not in found:
            found.append(value.text)
    elif isinstance(value, dict):
        for key, item in value.items():
            _placeholders(key, found)
            _placeholders(item, found)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _placeholders(item, found)
    elif isinstance(value, str):
        pass


def _command(arguments: list[Any], succeeds: Any) -> str:
    line = "dbt " + " ".join(shlex.quote(str(a)) for a in arguments)
    if succeeds is False:
        line += " # expected to fail"
    elif isinstance(succeeds, Opaque):
        line += f" # success depends on {succeeds.text}"
    return line


def render_case(source: str, function: str, *, include_skeleton: bool = False) -> str:
    trace = read_case(source, function)
    blocks = []
    if include_skeleton:
        blocks.append(
            "Every case starts from the same two configuration files. The harness writes "
            "`dbt_project.yml` and `profiles.yml` with `yaml.safe_dump`; the `path` value is "
            "the temporary project's own `warehouse.duckdb` file.\n\n"
            "`dbt_project.yml`\n\n```yaml\n"
            + yaml_text(
                {
                    "name": "classroom",
                    "version": "1.0",
                    "config-version": 2,
                    "profile": "classroom",
                    "model-paths": ["models"],
                    "seed-paths": ["seeds"],
                    "snapshot-paths": ["snapshots"],
                    "macro-paths": ["macros"],
                }
            )
            + "```\n\n`profiles.yml`\n\n```yaml\n"
            + yaml_text(
                {
                    "classroom": {
                        "target": "dev",
                        "outputs": {
                            "dev": {
                                "type": "duckdb",
                                "path": "<project>/warehouse.duckdb",
                                "schema": "main",
                                "threads": 1,
                                "settings": {"threads": 2, "memory_limit": "256MB"},
                            }
                        },
                    }
                }
            )
            + "```"
        )
    placeholders: list[str] = []
    if trace.files:
        blocks.append(
            "**Project files.** The case writes these files before its first dbt command. "
            "YAML is shown in conventional key order; dbt reads the same mappings."
        )
        for path, content in trace.files:
            _placeholders(content, placeholders)
            blocks.append(f"`{path}`\n\n{_block(path, content)}")
    commands: list[str] = []

    def flush() -> None:
        if commands:
            blocks.append("```bash\n" + "\n".join(commands) + "\n```")
            commands.clear()

    if trace.steps:
        blocks.append(
            "**Commands and changes, in order.** Each `dbt` line is one `invoke(...)` call; "
            "the harness adds `--project-dir` and `--profiles-dir` for the temporary project."
        )
    for kind, detail in trace.steps:
        if kind == "command":
            _placeholders(detail[0], placeholders)
            commands.append(_command(*detail))
            continue
        flush()
        if kind == "file":
            path, content = detail
            if isinstance(content, Opaque):
                blocks.append(f"The program then writes `{path}` from values computed at run time.")
            else:
                _placeholders(content, placeholders)
                blocks.append(f"The case then writes `{path}`:\n\n{_block(path, content)}")
        else:
            blocks.append(f"The program then runs `{detail}`.")
    flush()
    if placeholders:
        values = ", ".join(f"`{text}`" for text in placeholders)
        blocks.append(f"Values in angle brackets are computed when the program runs: {values}.")
    return "\n\n".join(blocks)
