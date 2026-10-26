"""Build standalone pads from reviewed case functions, without executing them."""

import ast
from pathlib import Path


def build(source, destination, prefix):
    text = source.read_text(encoding="utf-8")
    tree = ast.parse(text)
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    import_nodes = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    destination.mkdir(parents=True, exist_ok=True)
    for name in sorted(functions):
        if not name.startswith("case_"):
            continue
        required = {name}
        changed = True
        while changed:
            previous = required.copy()
            for dependency in previous:
                required |= {
                    n.id
                    for n in ast.walk(functions[dependency])
                    if isinstance(n, ast.Name) and n.id in functions
                }
            changed = required != previous
        used_names = {
            n.id
            for function in required
            for n in ast.walk(functions[function])
            if isinstance(n, ast.Name)
        }
        imports = []
        for node in import_nodes:
            names = [
                alias
                for alias in node.names
                if (alias.asname or alias.name.split(".")[0]) in used_names
            ]
            if not names:
                continue
            selected = (
                ast.Import(names=names)
                if isinstance(node, ast.Import)
                else ast.ImportFrom(module=node.module, names=names, level=node.level)
            )
            imports.append(ast.unparse(selected))
        parts = [
            '"""Complete offline worked example. See the matching tutorial for assumptions."""',
            "\n".join(imports),
        ]
        parts += [
            ast.get_source_segment(text, n)
            for n in tree.body
            if isinstance(n, ast.FunctionDef) and n.name in required
        ]
        parts += [f"def main():\n    {name}()", 'if __name__ == "__main__":\n    main()']
        (destination / f"{prefix}_{name[5:]}.py").write_text(
            "\n\n\n".join(parts) + "\n", encoding="utf-8"
        )


def main():
    root = Path(__file__).resolve().parent
    build(
        root / "experiment_casebook.py", root.parent / "experimentation" / "examples", "experiment"
    )
    for name in ("learning", "science"):
        source = root / f"{name}_casebook.py"
        if source.exists():
            build(source, root.parent / name / "examples", name)


if __name__ == "__main__":
    main()
