"""Build standalone pads from reviewed case functions, without executing them."""

import ast
from pathlib import Path


def program_order(tree, functions):
    """Return (case function, program number) pairs in guide order.

    A casebook may declare a literal PROGRAM_ORDER tuple when its stable
    function names differ from the guide numbering. Otherwise the number is
    taken from the function name.
    """
    cases = sorted(name for name in functions if name.startswith("case_"))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "PROGRAM_ORDER"
        ):
            order = list(ast.literal_eval(node.value))
            if sorted(order) != cases:
                raise ValueError("PROGRAM_ORDER must list every case function exactly once.")
            return [(name, f"{position:02d}") for position, name in enumerate(order, 1)]
    return [(name, name[5:]) for name in cases]


def build(source, destination, prefix):
    text = source.read_text(encoding="utf-8")
    tree = ast.parse(text)
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    import_nodes = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    destination.mkdir(parents=True, exist_ok=True)
    for name, number in program_order(tree, functions):
        program_name = f"case_{number}"
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
        if program_name != name and program_name in required:
            raise ValueError(f"{program_name} would shadow a helper of {name}.")
        segments = []
        for n in tree.body:
            if isinstance(n, ast.FunctionDef) and n.name in required:
                segment = ast.get_source_segment(text, n)
                if n.name == name:
                    # The standalone program uses the guide number, not the casebook name.
                    if not segment.startswith(f"def {name}("):
                        raise ValueError(f"{name} must be an undecorated function.")
                    segment = f"def {program_name}(" + segment[len(f"def {name}(") :]
                segments.append(segment)
        parts += segments
        parts += [f"def main():\n    {program_name}()", 'if __name__ == "__main__":\n    main()']
        (destination / f"{prefix}_{number}.py").write_text(
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
