# Textbook rendering

All subjects use the same reader in the Docker classroom and generated HTML
library. Prose is semantic HTML set in bundled Latin Modern text fonts. Explicit
TeX mathematics is compiled into KaTeX HTML with accessible MathML. Code retains
its own monospaced type, syntax colors and original selectable characters.

No CDN, remote font service or host TeX installation is needed. The Docker build
contains a separate Node stage that compiles formulas with the pinned vendored
KaTeX library. Node is not needed on the learner's host. The app stage verifies
that the compiled input inventory still matches the published lesson sources.

## Authoring and building

Use `\( ... \)` for inline mathematics and `\[ ... \]` on separate lines for
display mathematics. A fenced `math` block also represents a display expression.
Dollar signs remain literal in inline prose, including prices, shell variables
and regular expressions. Keep executable expressions in accurately tagged code
fences. Define each symbol, unit, dimension and assumption near its first use.

From the prepared contributor environment, with Node available:

```sh
python scripts/normalize_lesson_prose.py --write
python scripts/compile_lesson_tex.py
python scripts/build_lesson_readers.py
python scripts/compile_lesson_tex.py --check
python scripts/check_content_rendering.py
```

`make generate` performs these shared generation steps. Run any subject-specific
authoring generator first. The Docker build compiles the checked-in input
inventory, so source changes must regenerate that inventory before building.
A stale inventory causes an explicit build failure.

The compiler uses the real Markdown and notebook parser. It does not scan code
for mathematical-looking punctuation. `curriculum/tex-inputs.json` records exact
source/display pairs; `assets/vendor/textbook/compiled-tex.json` stores their
compiled output. Both are generated. A newly edited formula has a safe native
MathML fallback during development until the next compilation. Unsupported input
is displayed as escaped source and fails the content-rendering gate.

Display equations have a local sequence number and an expandable, highlighted
TeX source view. Browser printing retains textbook fonts, code and equations.
Long equations scroll horizontally within the lesson; they must not widen the
whole page. Generated readers link to one shared local stylesheet containing embedded,
checksum-verified font bytes. This avoids network requests and local-file font
restrictions. Keep the complete source/starter directory together when reading
offline.

## Validation boundaries

Successful compilation establishes renderability, not mathematical correctness.
Review matrix shapes, transpose scope, conditioning, units, indices and numerical
examples independently. `curriculum/formula-review.json` records reviewed
corrections. Candidate scans are triage tools, not a certification of every
formula. Preserve executable references and historical runtime evidence when
repairing prose.

Check representative inline expressions, aligned equations, matrices, fractions
and code on wide and narrow screens, in both appearance settings and print.
Confirm that copying code and expanded TeX source preserves their characters.
MathML supports assistive reading even though the visible layout uses KaTeX.

The compiler accepts a bounded TeX mathematics subset with trusted HTML and URL
commands disabled. It is not a shell-enabled document compiler. Font and library
licenses and checksums are retained beside the vendored assets. Source references:
[KaTeX server rendering](https://katex.org/docs/node),
[KaTeX options](https://katex.org/docs/options), and
[Latin Modern](https://ctan.org/pkg/lm).

## Scientific and data-language sources

New Julia, Stan and dbt SQL/Jinja sources use their accurate lexer and extension
labels. Typesetting a Stan model or highlighting Jinja does not compile it.
Applied Science and Bayesian Computing use tutorial mode with complete answers;
their generators embed the exact maintained programs before shared TeX and
reader generation. Formula review still needs dimensional, numerical and
assumption checks independent of successful KaTeX output.

Tables and JSON reports from actual runs are rendered as escaped structured data,
not converted into mathematical prose or executable HTML. Keep literal decimals,
identifiers, compiler messages and source characters intact. See
[the output contract](plotting.md) for limits and saved-result semantics.
