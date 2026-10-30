"""Required parser-only fence guard contracts for the prepared source toolchain.

No lesson is executed and no language compiler, model or network is invoked.
The same mutation fixtures are used by the focused pytest suite.
"""

from __future__ import annotations

from pathlib import Path

from scripts import format_inline_code as inline

TREE_EQUIVALENCES: list[tuple[str, str, str]] = [
    ("javascript", "f([1,2], {x:3});", "f([1,2,], {x:3,},);"),
    ("html", '<meta charset="utf-8">', '<meta charset="utf-8" />'),
    ("javascript", "const f=x=>x+1;", "const f=(x)=>x+1;"),
    ("typescript", "const f=x=>x+1;", "const f=(x)=>x+1;"),
    ("rust", "struct A { value:u32 }", "struct A { value:u32, }"),
    ("rust", 'fn f(x:i32){match x{_=>"value"}}', 'fn f(x:i32){match x{_=>"value",}}'),
    (
        "scala",
        "val result = source.select(1).collect()\n",
        "val result =\n  source.select(1).collect()\n",
    ),
    (
        "dockerfile",
        "RUN --mount=type=cache,target=/cache echo hi\n",
        "RUN --mount=type=cache,target=/cache \\\n  echo hi\n",
    ),
]

TREE_DIFFERENCES: list[tuple[str, str, str]] = [
    ("javascript", "const x=[1,,];", "const x=[1,];"),
    ("html", "<div></div>", "<div/>"),
    ("javascript", "const x=[,];", "const x=[];"),
    ("javascript", "f(a,b);", "f(a);"),
    ("typescript", "const f=(x:string)=>x;", "const f=(x:number)=>x;"),
    ("rust", "fn f(){let x=(a,);}", "fn f(){let x=(a);}"),
    ("scala", "val result = source.select(1)\n", "val result = source.select(2)\n"),
    (
        "dockerfile",
        "RUN --mount=type=cache,target=/one echo hi\n",
        "RUN --mount=type=cache,target=/two echo hi\n",
    ),
]

TREE_EQUIVALENCES.extend(
    [
        (
            "typescript",
            'type A = {kind:"one"} | {kind:"two"};',
            'type A = | {kind:"one"} | {kind:"two"};',
        ),
        ("typescript", "type A = string | (number & B);", "type A = | string | (number & B);"),
        ("scala", 'val query = "SELECT id FROM rows"\n', 'val query =\n  "SELECT id FROM rows"\n'),
    ]
)
TREE_DIFFERENCES.append(("typescript", "type A = string | number;", "type A = | string;"))

FAMILY = {
    "javascript": "web",
    "typescript": "web",
    "tsx": "web",
    "html": "web",
    "rust": "rust",
    "scala": "scala",
    "dockerfile": "docker",
}


def verify(root: Path, languages: set[str]) -> int:
    """Fail the formatting route when a reviewed semantic guard regresses."""
    checks = 0
    try:
        for expected_equal, cases in ((True, TREE_EQUIVALENCES), (False, TREE_DIFFERENCES)):
            for grammar, before, after in cases:
                if FAMILY[grammar] not in languages:
                    continue
                equal = (
                    inline.tree_signature(before.encode(), grammar)[0]
                    == inline.tree_signature(after.encode(), grammar)[0]
                )
                if equal != expected_equal:
                    raise ValueError(
                        "Inline guard contract failed: " + grammar + " semantic distinction"
                    )
                checks += 1
        if "python" in languages:
            before = b"x: int = 'first' # type: ignore[assignment]\ny: int = 'second'\n"
            moved = b"x: int = 'first'\ny: int = 'second' # type: ignore[assignment]\n"
            tool = inline.Formatter(root, lambda *args: moved)
            try:
                tool.format(before, "python", ".py")
            except inline.FormatFailure:
                checks += 1
            else:
                raise ValueError("Inline guard contract failed: moved Python type-ignore")
            inert = b"raise RuntimeError('this example must never execute')\n"
            tool = inline.Formatter(root, lambda source, *args: source)
            if tool.format(inert, "python", ".py") != inert:
                raise ValueError("Inline guard contract failed: inert Python source")
            checks += 1
        if "java" in languages:
            for source, expected in (
                (b"class Main {}\n", "unit"),
                (b"int value=1; assert value==1;\n", "statements"),
                (
                    b"boolean failed=false; try { fail(); } catch(Exception e) { failed=true; }\n",
                    "statements",
                ),
                (b"private int value=1;\n", "members"),
            ):
                wrapped, mode = inline.java_context(source)
                if mode != expected or inline.java_unwrap(wrapped, mode) != source:
                    raise ValueError("Inline guard contract failed: Java excerpt context")
                checks += 1
            try:
                inline.java_context(b"static void f() {} assert true;\n")
            except inline.UnsupportedSnippet:
                checks += 1
            else:
                raise ValueError("Inline guard contract failed: mixed Java contexts")
        if "rust" in languages:
            before = b"fn main(){custom!(a,b);}\n"
            candidate = b"fn main() { custom!(a, b,); }\n"
            tool = inline.Formatter(root, lambda *args: candidate)
            restored = tool.format(before, "rust", ".rs")
            if b"custom!(a,b)" not in restored or inline.rust_macro_regions(restored) != 1:
                raise ValueError("Inline guard contract failed: opaque Rust macro")
            checks += 1
        if "web" in languages:
            before = b'<label><input type="checkbox">Show a reminder</label>'
            after = b'<label><input type="checkbox" />Show a reminder</label>'
            if inline.tree_signature(before, "html")[0] != inline.tree_signature(after, "html")[0]:
                raise ValueError("Inline guard contract failed: HTML void tail")
            quoted = b"<p title='a  &amp; b'>literal  text</p>\n"
            candidate = b'<p title="a  &amp; b">literal  text</p>\n'
            if (
                inline.Formatter(root, lambda *args: candidate).format(quoted, "web", ".html")
                != quoted
            ):
                raise ValueError("Inline guard contract failed: HTML attribute/text values")
            checks += 2
        if "shell" in languages:
            source = "```sh\ndocker run <your-formatting-image> command\n```\n"
            tool = inline.Formatter(root, lambda value, *args: value)
            after, rows = inline.format_document(source, tool, {"shell"}, path="fixture.md")
            if (
                after != source
                or rows[0].get("reason") != "unsubstituted-shell-template-placeholder"
            ):
                raise ValueError("Inline guard contract failed: shell template")
            checks += 1
    except ImportError as error:
        raise ValueError(
            "Missing prepared syntax parser for inline guard contracts; use scripts/format-repo"
        ) from error
    return checks
