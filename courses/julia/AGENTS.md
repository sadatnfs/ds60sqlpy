# Julia course maintenance

Follow the root instructions and add-learning-path skill. This route owns Julia language and scientific-computing teaching artifacts. Shared runtime, dependency pins, UI, figure validation and Docker behavior belong to their central implementations.

- Maintain `authoring/unit-*.json`, `authoring/chapters/` and the four complete programs per unit in `authoring/programs/`. Preserve `julia-001` through `julia-032` and prerequisite order.
- Every unit has two explained complete worked programs and six distinct investigations. Keep the learner, reference and worked source versions consistent when a shared helper changes.
- Run the real pinned Julia formatter before this subject's pure-Python builder. Generate guides, sources, solutions and manifests together. Do not manually rewrite generated references or their hash inventory.
- Julia runs as a fresh `main.jl` process with two threads in a prepared read-only environment. Lessons never install packages, fetch datasets, attach GPUs or contact services. A source file is not a package manager.
- Preserve numerical assumptions, input grain, availability time, selection/holdout separation, tolerances and independent oracles. A synthetic score is not deployment evidence.
- Distinguish aliasing from object identity, tasks from threads, timing from correctness, first-call compilation from warm execution and source loading from package qualification.
- Keep bounded Plotly figures for units 020, 024 and 032, each with description and exact table. `DS60Plots` is classroom infrastructure, not a standard Julia package.
- Maintain `fixtures/sensor-calibration.csv` and its complete embedded capstone source together. The independent checker rejects mismatched fixture bytes and leakage cases.
- Run authoring round-trip checks, dedicated Python tests and actual Julia reference/worked/independent checks. Missing host Julia is an explicit skip, not runtime acceptance. Root integration separately checks browser delivery and saved results.
- Use primary documentation, explicit TeX mathematics, accurate code fences and professional prose without em dashes. Current online docs can differ from prepared package versions; verify APIs in the pinned runtime.
