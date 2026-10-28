# Maintained evaluation course sources

`unit-001.json` through `unit-024.json` hold route metadata and six concrete investigations per unit. `chapters/` holds original teaching prose. Each chapter has exactly one `{{WORKED_A}}` and `{{WORKED_B}}` insertion point. `programs/` holds standalone numerical or PyTorch reference programs, split by stable section comments. The builder extracts complete worked programs, formats Python using the repository Ruff configuration, and generates guides, learner files, executable references, explanatory solutions and manifests. Optional `_plotly.py.in` source fragments add three separate chart variants.

Run from a prepared contributor environment:

```sh
python courses/llm-evaluation/authoring/build.py
python courses/llm-evaluation/authoring/build.py --check
python -m pytest tests/test_llm_evaluation.py
```

The `.py.in` fragments intentionally use the numerical helper scope supplied by the builder. They are not standalone pads; their generated complete programs are formatted, parsed and executed during qualification.

The builder executes no lesson program. It requires Ruff for deterministic code style. Format maintained authoring code, regenerate this subject, then let the integration owner run shared TeX/readers and catalog checks. Generated `track.json`, `lessons.json` and `fixtures/reference-contracts.json` are exact generator outputs; do not independently reformat their bytes and claim no drift.

Every source program embeds small local inputs. The connected evaluation ledger is authored synthetic data with group, split and label-availability fields. Unit016 computes its decision from the actual held-out ledger rows. Mechanism counterexamples elsewhere deliberately change named assumptions; they do not pretend to be fresh model observations. Keep fixture provenance and program copies synchronized when changing that ledger.

The reference contract inventory records source hashes and expected markers. Those hashes bind source bytes but do not establish correctness. Tests must include independent values, invariants, rejected invalid input and numerical gradients. The PyTorch lessons require an actual prepared runtime; a missing host dependency is an explicit skip until the separate worker checks run. Plotly references require captured figures; their charts are not substitutes for the numerical or decision evidence.
