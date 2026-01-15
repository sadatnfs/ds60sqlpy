# Day 5 — Functions, Docstrings, and Type Hints (Companion Guide)

## Learning objectives
- Define functions with positional-only, keyword-only, defaults, `*args`, `**kwargs`
- Write clear docstrings (purpose, parameters, returns, raises)
- Add type hints to improve readability and tooling (mypy/IDE)
- Design functions for testability, reusability, and good error messages

## Why this matters
Functions are the basic unit of abstraction. Clear interfaces reduce bugs, speed up collaboration, and make code review easier. Type hints enable static checks and better IDE support without changing runtime behavior.

## Mental models
- A function is a contract: inputs (types, constraints) → outputs (types, guarantees)
- Keep functions small and single-purpose; compose small functions into pipelines
- Prefer pure functions (no hidden global state) for easier testing and reasoning

## Defining functions and signatures
```python
# Positional and keyword params with defaults

def normalize(values: list[float], *, eps: float = 1e-9) -> list[float]:
    total = sum(values) or eps
    return [v / total for v in values]

# *args (variadic positional) and **kwargs (variadic keyword)

def summarize(title: str, *items: str, uppercase: bool = False, **meta: object) -> dict:
    data = [i.upper() if uppercase else i for i in items]
    return {"title": title, "count": len(data), "items": data, "meta": meta}
```
Use keyword-only params (the `*,` marker) for clarity on “configuration” arguments.

## Docstrings that help humans
```python
def topk(values: list[float], k: int) -> list[float]:
    """
    Return the top-k values in descending order.

    Args:
        values: sequence of numeric values (may be empty)
        k: number of values to return (k >= 0)

    Returns:
        A new list of up to k values sorted descending.

    Raises:
        ValueError: if k < 0
    """
    if k < 0:
        raise ValueError("k must be non-negative")
    return sorted(values, reverse=True)[:k]
```
Use Google or NumPy style consistently; include constraints and error conditions.

## Type hints in practice
- Scalar types: `int, float, str, bool`
- Containers: `list[int]`, `dict[str, float]`, `tuple[int, str]`
- Optional: `str | None` (Python 3.10+) or `Optional[str]`
- Callables: `Callable[[int, int], int]`
- Type aliases: `UserId = int`

Type hints do not enforce at runtime—use mypy for static checks.

## Validating inputs and raising errors
Keep validation upfront with helpful messages:
```python
def percentile(p: float) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"percentile p must be in [0, 1], got {p!r}")
    return p
```

## Designing for testability
- Pure functions with inputs/outputs
- Avoid I/O inside core logic (return data instead, do I/O at the edges)
- Deterministic behavior; inject randomness via parameters with seeds

## Common pitfalls
- Overusing `*args/**kwargs` for generality; explicit is better than implicit
- Missing docstrings in public functions
- Ignoring edge cases (empty list, None, negative indices)

## Practice exercises
1) Write `moving_average(xs: Sequence[float], window: int) -> list[float]` with input validation and docstring.
2) Write `slugify(text: str, *, maxlen: int | None = None) -> str` that lowercases, replaces spaces with hyphens, removes unsafe chars, and truncates to `maxlen` if given.
3) Add type hints and docstrings to two functions you’ve already written; run `mypy` and fix any warnings.

## Stretch goals
- Add `@overload` definitions for a function that returns different types based on input signature.
- Use `TypedDict` or `dataclasses.dataclass` to define structured return types.

## Check your understanding
- What’s the value of keyword-only parameters? Give an example where it improves clarity.
- How do type hints improve code quality without runtime checks?
- Write a docstring for a function that may raise `ValueError` and explain when it occurs.

## Further reading
- PEP 8 (style): https://peps.python.org/pep-0008/
- PEP 484 (type hints): https://peps.python.org/pep-0484/
- Mypy docs: https://mypy.readthedocs.io/en/stable/
- Google Python Style Guide: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
