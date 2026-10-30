# Durable Java authoring

`specs.py` contains the original teaching cases, `render.py` assembles the
published artifacts, and `build.py` is the normal entrypoint. Preserve the
existing java-001 through java-036 identities, prerequisites, six exercise
contracts, answer-free starters and separate checked references. Directly
authored multi-file fixtures remain under their existing ownership.

Use the [prepared contributor formatting toolchain](../../../docker/formatting/README.md),
including its locked Python parsing dependencies, Prettier 3.6.2 and
prettier-plugin-java 2.7.7. Run from the repository root inside that environment:

```sh
python courses/java/authoring/build.py
```

The command is unchanged. Before writing a guide or explanatory solution, the
renderer passes its completed Markdown through the shared in-memory
`canonical_markdown` adapter. The adapter checks ownership, parsing, protected
literal values and idempotence. It changes only admitted fence bodies and
reports explicitly preserved fragments or transcripts. Missing prepared tools
are errors, with no silent raw-output fallback or automatic download. The
generator does not compile or execute Java.

The renderer retains its existing UTF-8/backslashreplace serialization before
those guards. In particular, authored Python surrogate code units become the
same Java Unicode escapes that the previous file writer produced. This does
not replace literal contents with a visually similar string. Standalone Java
solutions and starter files keep their existing assembly and normal shared
source-formatting route.

There is no separate builder `--check` mode. Hash the generated artifacts, rerun
the command in the same prepared environment and compare hashes. Follow the
normal source formatting step, then the read-only Java fence check:

```sh
python scripts/format_inline_code.py --check --language java
```

Run the Java publication contracts in `tests/test_java_lessons.py`. Actual JDK
qualification uses the explicitly prepared Java 21 environment, with assertions
enabled; preserve H2 and other declared fixture boundaries. Existing checks for
source literals, child-JVM environment and separate diagnostic output remain
unchanged. A generation or formatter pass is not compiler, runtime or learner
mastery evidence.

Use [CONTRIBUTING](../../../CONTRIBUTING.md) and the
[validation guide](../../../docs/validation.md) for shared checks. Refresh shared
readers only after the owner-generated content passes its checks; never edit
generated HTML or weaken publication assertions to hide drift.
