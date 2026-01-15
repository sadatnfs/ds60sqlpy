# Day 10 — Testing with Pytest (Companion Guide)

## Learning objectives
- Write unit tests with pytest and run them locally
- Use assertions and `pytest.mark.parametrize`
- Structure a test suite and handle expected exceptions

## Why this matters
Tests are executable documentation. They prevent regressions and enable refactors with confidence.

## Mental models
- Unit tests: fast, isolated, deterministic
- Arrange → Act → Assert: set up inputs, run the function, assert on outputs/effects

## Pytest basics
```
project/
  src/
    mymod.py
  tests/
    test_mymod.py
```
```python
# tests/test_mymod.py
import pytest
from src.mymod import add

@pytest.mark.parametrize('a,b,exp', [(1,2,3),(0,0,0),(-1,1,0)])
def test_add(a,b,exp):
    assert add(a,b) == exp

def test_raises():
    with pytest.raises(ValueError):
        normalize([])
```
Run `pytest -q`.

## Fixtures and tmp paths (teaser)
Use fixtures to set up reusable state; built‑in `tmp_path` provides a temporary directory per test.

## Common pitfalls
- Non-determinism in tests (randomness, timestamps); inject seeds/fixed times
- Tests doing network/I/O unnecessarily; mock or isolate

## Practice exercises
1) Write tests for your CSV/JSON utilities; cover happy path and edge cases
2) Add a failing test for a known bug; implement the fix and watch it go green
3) Introduce `pytest.mark.slow` for long tests; run `-m "not slow"` in quick cycles

## Further reading
- pytest docs: https://docs.pytest.org
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html
