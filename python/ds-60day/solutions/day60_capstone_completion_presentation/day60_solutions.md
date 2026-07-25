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
