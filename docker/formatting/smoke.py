"""Exercise every installed formatter without network or learner files."""

import subprocess
import tempfile
from pathlib import Path

CONFIG = Path(__file__).resolve().parent


def output(command: list[str], source: str) -> str:
    result = subprocess.run(command, input=source, text=True, capture_output=True, check=True)
    return result.stdout


def stable(name: str, command: list[str], source: str, preserved: tuple[str, ...] = ()) -> None:
    formatted = output(command, source)
    if output(command, formatted) != formatted:
        raise RuntimeError(f"{name} formatting is not idempotent")
    for text in preserved:
        if text not in formatted:
            raise RuntimeError(f"{name} changed protected text: {text!r}")
    print(f"PASS {name}", flush=True)


def main() -> None:
    stable("Python", ["ruff", "format", "-"], "values=[1,2,3]\nprint(values)\n")
    prettier = ["prettier", "--config", str(CONFIG / "prettier.json")]
    for parser, source in (
        ("babel", "const values=[1,2,3]; console.log(values);\n"),
        ("typescript", "const value:number=42;console.log(value);\n"),
        ("css", ".card{color:red;padding:1rem}\n"),
        ("html", "<main><p>Hello</p></main>\n"),
        ("json", '{"a":1,"b":[2,3]}\n'),
        ("yaml", "services:\n app: {image: python:3.12}\n"),
        ("java", 'class Hello{public static void main(String[]a){System.out.println("hi");}}\n'),
        ("toml", "value={ left=1,right=2 }\n"),
        (
            "xml",
            "<Project><PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup></Project>\n",
        ),
    ):
        stable(parser, [*prettier, "--parser", parser], source)
    math = "\\(x^2 + y^2\\)"
    stable(
        "Markdown preserves mathematics and code fences",
        [*prettier, "--parser", "markdown"],
        f"# A lesson\n\n{math}\n\n```python\nx=1+2\n```\n",
        (math, "x=1+2"),
    )
    clang = ["clang-format", "--style=file:" + str(CONFIG / "clang-format.yaml")]
    stable("C", [*clang, "--assume-filename=main.c"], "int main(void){return 0;}\n")
    stable("C++", [*clang, "--assume-filename=main.cpp"], "int main(){auto x=1;return x-1;}\n")
    stable(
        "C#",
        [*clang, "--assume-filename=Program.cs"],
        'using System;\nclass Program{static void Main(){Console.WriteLine("hello");}}\n',
        ('"hello"',),
    )
    stable("Go", ["gofmt"], 'package main\nimport "fmt"\nfunc main(){fmt.Println("hi")}\n')
    stable(
        "Rust",
        ["rustfmt", "--config-path", str(CONFIG / "rustfmt.toml")],
        'fn main(){let value=42;println!("{}",value);}\n',
    )
    stable(
        "Swift",
        ["swift-format", "format", "--configuration", str(CONFIG / "swift-format.json")],
        "let values=[1,2,3]\nprint(values)\n",
    )
    stable(
        "Scala",
        [
            "scalafmt",
            "--config",
            str(CONFIG / "scalafmt.conf"),
            "--stdin",
            "--stdout",
            "--assume-filename",
            "Main.scala",
        ],
        'object Main{def main(args:Array[String]):Unit={println("hi")}}\n',
    )
    stable(
        "PostgreSQL and psql directives",
        [
            "pg_format",
            "--no-rcfile",
            "--redundant-parenthesis",
            "--spaces",
            "2",
            "--keyword-case",
            "0",
            "--function-case",
            "0",
            "--type-case",
            "0",
        ],
        "\\set ON_ERROR_STOP on\n\\if :ready\nselect 1 as n \\gset\n\\endif\n"
        "select '  literal spacing  ', ((1 + 2));\n",
        (
            "\\set ON_ERROR_STOP on",
            "\\if :ready",
            "\\gset",
            "\\endif",
            "'  literal spacing  '",
            "((1 + 2))",
        ),
    )
    stable("Shell", ["shfmt", "-i", "2", "-ci"], 'if true;then printf "%s\\n" "hello";fi\n')
    stable("Dockerfile", ["dockerfmt", "--indent", "2"], "FROM python:3.12\nRUN   echo hello\n")
    stable(
        "CMake",
        ["cmake-format", "--config-files", str(CONFIG / "cmake-format.yaml"), "-"],
        "cmake_minimum_required(VERSION 3.20)\nproject(example LANGUAGES CXX)\n",
    )
    with tempfile.TemporaryDirectory() as directory:
        notebook = Path(directory) / "example.ipynb"
        notebook.write_text(
            '{"cells":[{"cell_type":"code","execution_count":null,"metadata":{},"outputs":[],"source":["x=1+2\\n"]}],"metadata":{"language_info":{"name":"python"}},"nbformat":4,"nbformat_minor":5}',
            encoding="utf-8",
        )
        subprocess.run(
            ["ruff", "format", "--no-cache", str(notebook)], check=True, capture_output=True
        )
        subprocess.run(
            ["ruff", "format", "--no-cache", "--check", str(notebook)],
            check=True,
            capture_output=True,
        )
        print("PASS Python notebook", flush=True)


if __name__ == "__main__":
    main()
