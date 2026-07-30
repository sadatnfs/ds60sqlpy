# Day 60 — Solutions: Capstone Completion and Presentation

We deliver a presentation outline, packaging checklist, and reproducibility steps.

Contents
- Exercise 1: Slide/story outline
- Exercise 2: Packaging checklist and Makefile
- Exercise 3: Demo plan and smoke tests

---

Exercise 1 — Slide outline
```markdown
1) Context and stakes — the problem and why it matters
2) Data — sources, quality, challenges; quick EDA visual
3) Methods — models, features, validation; why chosen
4) Results — metrics vs baseline; error analysis
5) Deployment — how to use; latency, cost, monitoring
6) Risks and ethics — limitations, mitigation
7) Next steps — roadmap and open questions
```

Exercise 2 — Packaging
```makefile
# Makefile
PYTHON ?= python

setup:
	$(PYTHON) -m pip install -e ".[quality]"

train:
	$(PYTHON) -m src.train

eval:
	$(PYTHON) -m src.eval

serve:
	$(PYTHON) -m uvicorn app:app --host 0.0.0.0 --port 8000

smoke:
	$(PYTHON) -m pytest -q tests/smoke
```

Create the virtual environment with the operating-system-specific setup before
using the Makefile. On Windows, pass the interpreter explicitly if `make` is
available: `make PYTHON=.venv/Scripts/python.exe smoke`. VS Code tasks or a
PowerShell script are equally valid Windows automation.

Checklist
- Declare dependencies in `pyproject.toml`, keep a reviewed lock, and include a
  README with exact commands
- Save trained model and schema artifacts under artifacts/
- Provide sample inputs/outputs; add smoke tests

---

Exercise 3 — Demo and smoke tests
```python
# tests/smoke/test_api.py
import requests

def test_health():
    r = requests.get('http://localhost:8000/health')
    assert r.status_code == 200

def test_predict():
    r = requests.post('http://localhost:8000/predict', json={'x':1,'y':2})
    assert r.status_code == 200 and 'pred' in r.json()
```
Notes
- Practice the live demo; have screenshots/videos as backup
- Keep the narrative crisp; focus on impact and honesty

---

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1 — Original lesson practice

**Prompt:** Finalize the data and training/evaluation pipeline.

**How to reason about it:** Freeze the final candidate and rebuild data, training, and evaluation from clean state. Stop adding model families; unresolved issues belong in limitations or future work.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 2 — Original lesson practice

**Prompt:** Produce a results notebook and README with exact reproduction steps.

**How to reason about it:** Generate README metrics and plots from the same tested evaluation path, with exact commands, expected outputs, and OS variants. Hand-edited numbers are a drift risk.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 3 — Original lesson practice

**Prompt:** Save artifacts under an ignored `artifacts/` path and retain dependency metadata/lock.

**How to reason about it:** Keep reproducible artifacts under ignored paths, but retain code, schema, manifest, and dependency lock. A reviewer should be able to recreate large/generated files rather than receive hidden local state.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 4 — Original lesson practice

**Prompt:** Prepare presentation-ready visuals and the short story above.

**How to reason about it:** Every visual needs a question, labeled population/metric/unit, readable baseline, and limitation. The short story should fit the audience and avoid causal or production claims unsupported by the evidence.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 5 — Original lesson practice

**Prompt:** Write three takeaways and one open question.

**How to reason about it:** Three takeaways and one open question should connect directly to results and remaining uncertainty. A takeaway is not 'the model worked'; it states what the measured evidence supports.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 6 — Cold-start reproduction

**Prompt:** Clone/copy the project into a fresh temporary directory, follow only the README on Windows or POSIX, and log every ambiguity, manual step, network access, output, and elapsed stage.

**Reasoning before implementation:** Use a clean environment and no notebook state. Verify the documented offline path after the one connected bootstrap.

The acceptance run should create data/artifacts only in documented ignored
locations, run tests, train/evaluate, and reproduce reported metrics within
declared tolerance. Record interpreter, dependency lock, and data fingerprint.

Fix the instructions—not the clean environment—when a hidden import, working
directory, cache, or absolute path is discovered. Repeat until the run needs no
undocumented intervention.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 7 — Claim-to-evidence matrix

**Prompt:** Create a table mapping every headline claim to metric/visual, dataset and split, sample size, uncertainty, reproduction command, limitation, and owner.

**Reasoning before implementation:** Remove or soften claims with no direct evidence. Distinguish predictive association, operational estimate, and causal conclusion.

The matrix should expose inconsistencies such as a slide using validation
metrics while the README quotes test metrics, or a fairness claim without
group support. Link each claim to the exact generated artifact and code path.

If evidence is exploratory, label it. A polished chart cannot upgrade weak
methodology into a confirmed finding.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 8 — Failure-tolerant demo

**Prompt:** Prepare and rehearse a five-minute demo with a preflight check, time budget, local fixtures, screenshots/static fallback, and recovery from one intentionally broken dependency or service.

**Reasoning before implementation:** The core result must not depend on live internet. Demonstrate the reproducible workflow, not a fragile sequence of manual notebook cells.

Start from a known command and versioned fixture. Keep the live portion short,
and prepare generated outputs that are clearly labeled as prior evidence—not
pretended live execution. A failed optional API/UI should not erase the model
evaluation story.

Practice the failure transition and state what remains verified. Never expose
credentials or sensitive records while troubleshooting on screen.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 9 — Operational handoff

**Prompt:** Write an ownership and maintenance section covering artifact/data refresh, dependency updates, monitoring, incident contact, rollback, known limitations, and end-of-life criteria.

**Reasoning before implementation:** Name roles and cadences, not personal credentials. Connect each maintenance action to a test or acceptance gate.

Even a portfolio project benefits from explicit “not deployed” status and the
conditions that would be required before real use. If deployed, identify who
can approve promotion/rollback and how stale data/models are detected.

Avoid personal email, tokens, or organization-specific secrets in the portable
repository. Use placeholder roles and documented configuration boundaries.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 10 — Retrospective and next experiment

**Prompt:** Write a retrospective with what changed your belief, strongest and weakest evidence, one discarded path, remaining risk, and one bounded next experiment with a predeclared decision rule.

**Reasoning before implementation:** The next experiment should resolve the highest-value uncertainty, not simply try a more complex model.

A useful retrospective distinguishes process success from favorable metrics.
State what would falsify the current conclusion and what data or design would
reduce uncertainty most.

The next experiment should define population, intervention/change, comparison,
metric, minimum practical effect, budget, and stop rule before execution. This
turns the capstone ending into a disciplined handoff rather than an endless
model search.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.
