# Day 10 — Solutions: Testing with Pytest

We write tests for `safe_divide` and `validate_email` (from earlier days) and include a negative test using `pytest.raises`.

Contents
- Exercise 1: Install pytest; write tests for `safe_divide` and `validate_email`
- Exercise 2: Negative test expecting exceptions

---

Prereq functions (from Day 3; include here for context/tests)
```python
def safe_divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError('b must not be 0')
    return a / b

class InvalidEmailError(ValueError):
    pass

def validate_email(email: str) -> None:
    if '@' not in email:
        raise InvalidEmailError('Missing @ in email')
```

Install pytest (in your venv)
```
pip install pytest
```

Project layout
```
project/
  src/
    mymod.py              # optional location for your functions
  tests/
    test_core.py
```

tests/test_core.py
```python
import pytest

from mymod import safe_divide, validate_email, InvalidEmailError

@pytest.mark.parametrize('a,b,exp', [
    (10, 2, 5.0),
    (3, 2, 1.5),
    (-6, 3, -2.0),
])
def test_safe_divide_happy(a, b, exp):
    assert safe_divide(a, b) == exp

def test_safe_divide_raises():
    with pytest.raises(ZeroDivisionError):
        safe_divide(1, 0)

def test_validate_email_ok():
    validate_email('user@example.com')  # no exception

def test_validate_email_bad():
    with pytest.raises(InvalidEmailError):
        validate_email('not-an-email')
```

Run tests
```
pytest -q
```
Notes
- Use parametrize to cover multiple cases succinctly.
- Use `with pytest.raises(...)` to assert the exact exception type.
- Keep business logic and tests separate; import the functions under test.
