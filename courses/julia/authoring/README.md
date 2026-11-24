# Maintained Julia teaching sources

The 32 `unit-*.json` records contain title, stage, prerequisites, outcome, key terms, references and six investigations. `key_terms` holds three to five distinct `[term, definition]` pairs; each definition is one sentence of at least six words. The builder validates them and renders a `## Key terms` section after the classroom execution notes. `chapters/` contains original explanations with two worked-program insertion points. `programs/` contains four complete executable sources per unit: learner, reference, worked A and worked B. These are maintained sources, not fragments. Keep common helpers synchronized when changing a unit.

Each unit also carries solution reasoning. `approach` is a paragraph of at least 35 words on the reference strategy. Every investigation adds `why` (at least 12 words: why the expected observation holds for this code), `wrong` (at least 12 words: one plausible wrong approach and why it fails, distinct within the unit) and `verify` (at least 6 words: the check or assertion that confirms it). The optional `checks_note` (at least 30 words) explains what the reference `exercise_checks` assertions cover. The builder renders these into `solutions/julia-NNN_solutions.md` as an Approach section, four labeled notes per investigation and a closing `## Reference checks` block that quotes `exercise_checks`, and it fails if any explained solution is under 700 words. State only values that follow from the code or that a reference assertion pins, because `build.py` does not run Julia.

Format these Julia files using the repository's pinned JuliaFormatter integration. It parses and compares syntax without executing learner code. Then generate this subject:

```sh
python courses/julia/authoring/build.py
python courses/julia/authoring/build.py --check
python -m pytest tests/test_julia_curriculum.py
```

The builder runs no Julia or learner program. It copies already-formatted sources and embeds complete worked programs into guides. Generated `track.json`, `lessons.json`, `figure-contracts.json` and `fixtures/reference-contracts.json` preserve exact generator bytes; do not independently reformat them. Root integration refreshes shared catalogs, TeX and readers after subject checks pass.

For actual runtime checks inside an explicitly prepared Julia worker or contributor environment:

```sh
python courses/julia/authoring/check_runtime.py \
  --project /opt/julia-env \
  --helper src/ds60sqlpy/worker_figures.jl \
  --all-worked --learners
```

The source checkout, Python interpreter, locked Julia environment and helper must be available at those paths. The command does not build an image, install a package or access a learner volume. It runs every program in a fresh temporary directory with two threads, emits source-bound JSON records and fails on missing required figures. Reference and worked programs are staged as `main.jl`. `--independent-only` runs the separate scientific contract suite. `--julia PATH` selects an already-installed interpreter.

`formatter_contract.jl` independently verifies that parser line metadata may change while operators, literals, macro arguments and quoted expressions remain protected. The runtime checker runs this alongside the scientific checks.

`independent_checks.jl` imports reference helpers into isolated modules and checks independent numerical values, input rejection, aliases, calendar semantics, availability time, optimization, task completion, native interfaces and holdout isolation. It does not call reference `main` routines as its only oracle. Python tests verify source contracts and the capstone's rational arithmetic independently; their optional host-runtime test explicitly skips if Julia or its prepared environment is absent.

The ordinary course contains three canonical Plotly examples: 020, 024 and 032. Each emits one artifact with description and exact table. Worked and learner programs have their own expected figure counts. A valid capture still needs the central browser/artifact acceptance gates.
