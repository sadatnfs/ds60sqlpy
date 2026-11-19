# Deployment tutorial authoring

`units.json` owns stable IDs, prerequisites and outcomes. `chapters/01.md` through
`18.md` own the original explanations and two worked cases per unit. Run
`python3 authoring/build.py` from this subject to refresh its tutorial guides,
complete reading notebooks and admission metadata. `--check` reports drift.
Root shared reader/catalog generation remains a separate step.

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
