# Deployment tutorial authoring

`units.json` owns stable IDs, prerequisites, outcomes and three to five `key_terms`
pairs per unit, rendered as a Key terms section before the first worked case.
`chapters/01.md` through `18.md` own the original explanations and two worked cases
per unit. Run `python3 authoring/build.py` from this subject to refresh its
tutorial guides, complete reading notebooks and admission metadata. `--check`
reports drift.
Root shared reader/catalog generation remains a separate step.

Each unit also owns a `worked_examples` list. Every entry has exactly `title`, `language` (python, bash, yaml, ini, dockerfile, sql or text), `code`, `interpretation` and an optional `output`. The builder renders each entry as a `## Worked example: <title>` section placed before Diagnose and transfer. It rejects duplicate titles or code anywhere in the track, em and en dashes, triple backticks inside code or output, Python code that does not parse, and an interpretation that is not one paragraph of at least 40 words ending in a period. Only include `output` when it was produced by running the block exactly as written; spark-submit, kubectl, PySpark and manifest examples carry no output, and an interpretation must say when stand-in data replaced a live cluster. The builder also fails when a guide has fewer than two fenced code blocks or fewer than 1050 words.

A chapter line `<!-- include: projects/PATH #symbol from="..." to="..." python -->`
embeds project source; the symbol and `from`/`to`/`until` selectors are optional.
A Python include must begin and end on whole statements of the cited file. The
generator prints it as the repository fence formatting check does (dedented, in the
locked Ruff style, with the same syntax and literal guards), so generation needs
Ruff from the `quality` extra. A fragment that check cannot admit as a program, such
as a lone decorator, stays verbatim.

The owned `projects/cluster-lab/` is handwritten runtime tooling. Source checks,
Compose configuration, actual local execution and Kubernetes/cloud execution are
different evidence. Update its qualification ledger only from real observations.
Do not replace placeholders in command examples with private endpoints or tokens.
Keep all cleanup scoped and preserve saved state. Do not use em dashes.
