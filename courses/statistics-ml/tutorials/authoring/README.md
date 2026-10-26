# Numerical source ownership

The three `*_casebook.py` files are durable, reviewed numerical sources for the
additive tutorials. Each case is a complete computation with explicit fixtures,
assertions and interpretation in its corresponding Markdown guide. Guides are
directly authored. Do not generate generic prose from function names.

`build_examples.py` parses the casebooks without executing them and copies each
case plus its helper-function closure into a standalone Python program. These
programs are the exact sources admitted by `tutorials/index.json` and can be
copied into the ordinary single-file classroom pad. They do not import sibling
files or require an undeclared mounted fixture. Shared generators, the original
forty chapter examples and the source outline have separate owners.

After editing a numerical case, run this focused builder with the prepared
contributor interpreter, format both source and outputs using the repository's
approved formatter, then run the focused numerical/tutorial checks. Formatting
must preserve AST meaning and literal values. Ordinary cases must never import
PyMC or ArviZ; those imports stay inside the separately admitted scientific
case 09 and its standalone Bayesian-profile program.

The index records direct prerequisites, profile, dependencies, concepts,
observable outcome and expected output labels. Dependencies describe the
prepared runtime, never commands that a lesson may execute. Keep all existing
forty chapter IDs, the 1,005 topic anchors and source-outline bytes unchanged.

Tests should independently check a mathematical identity, an exact finite
sampling calculation, a meaningful failure contrast or a bounded statistical
property. They must not infer learner mastery or real-world validity from a
zero exit code. MCMC diagnostic evidence and actual runtime qualification remain
distinct from syntax or content checks.
