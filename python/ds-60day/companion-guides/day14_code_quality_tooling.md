# Day 14 — Code Quality: Black, Flake8, Mypy (Companion Guide)

## Learning objectives
- Auto‑format code with `black`
- Lint for style and correctness with `flake8`
- Type‑check with `mypy` and use pyproject config

## Workflow
```toml
# pyproject.toml
[tool.black]
line-length = 88

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203"]
```
Run:
```bash
black .
flake8 .
mypy .
```

## Why this matters
Consistent style reduces code review noise; linters catch bugs early; type checks prevent many runtime errors.

## Practice exercises
1) Apply black/flake8/mypy to your project; fix warnings
2) Add CI to run these tools on every PR

## Further reading
- Black: https://black.readthedocs.io
- Flake8: https://flake8.pycqa.org
- Mypy: https://mypy.readthedocs.io
