# Day 2 — Python Basics: Variables and Core Types (Companion Guide)

This guide expands the Day 2 notebook with more narrative, examples, and exercises.

## Learning objectives
- Understand names (identifiers), assignment, and dynamic typing in Python
- Use Python’s scalar types: `int`, `float`, `bool`, and `str`
- Perform type conversions safely and recognize when implicit coercion does not occur
- Employ f-strings, string methods, and simple input/output

## Why this matters
Everything you build rests on a solid understanding of values and types. Data science often involves messy inputs; you must be comfortable checking and converting types safely and clearly documenting your intent with readable code.

## Mental models
- Names and objects: `x = 42` binds the name `x` to an integer object `42`. Rebinding doesn’t copy; it points `x` to a new object.
- Mutability vs immutability: Numbers and strings are immutable—operations return new objects. You’ll see mutability later with lists/dicts.
- Truthiness: Python determines truth value contextually—empty containers are `False`, non-empty are `True`; zero is `False`, non-zero is `True`.

## Core concepts with examples

### Variables and assignment
```python
x = 42          # int
pi = 3.14159    # float
name = 'Ada'    # str
is_ready = True # bool
```
Use descriptive names; avoid single letters except in short-lived scopes.

### Numeric types and operations
```python
# ints and floats
count = 7
ratio = 22 / 7            # float division
whole = 22 // 7           # integer division: 3
remainder = 22 % 7        # modulus: 1
power = 2 ** 10           # exponentiation: 1024
```
Be mindful of division semantics: `/` always returns float; use `//` for floor division.

### Type conversions (casting)
```python
int('5')          # 5
float('2.7')      # 2.7
str(123)          # '123'
bool(0), bool(1)  # False, True
```
Handle bad inputs explicitly:
```python
def to_int(s: str) -> int | None:
    try:
        return int(s)
    except ValueError:
        return None
```

### Strings and f-strings
```python
s = 'Data Science'
s.lower(), s.upper(), s.strip()
'f-strings: x={x}, pi≈{pi:.2f}'
```
Prefer f-strings to `format()` for readability.

### Truthiness and comparisons
```python
if []:
    print('truthy')
else:
    print('falsy')   # prints 'falsy'

3 < 5 < 10     # chained comparisons → True
'a' < 'b'      # lexicographic ordering
```

### Input/output patterns
For CLI scripts, prefer `argparse` (Day 15). For quick demos, you can use `input()` but validate carefully:
```python
raw = input('Enter a number: ')
val = to_int(raw)
if val is None:
    print('Please enter a valid integer')
```

## Common pitfalls
- Assuming implicit coercion: `int + str` raises `TypeError`. Convert explicitly.
- Floating point surprises: `0.1 + 0.2 != 0.3` due to binary representation. Use `math.isclose()` for approximate comparisons.
- Shadowing built-ins: Don’t name variables `list`, `str`, `sum`, etc.

## Practice exercises
1) Write a function `percent(n, total)` that returns a string like `'37.5%'` with one decimal place; protect against division by zero.
2) Given `'  Data Science  '`, write code to trim, lowercase, and replace spaces with hyphens.
3) Read two numbers as strings, convert safely, and print both their sum and product with labeled f-strings.

## Stretch goals
- Implement `safe_float(s: str, default: float = float('nan')) -> float` that logs the bad input (use print or logging for now).
- Implement a small REPL loop that accepts expressions and uses `eval` safely (restrict builtins; or better, parse with `ast.literal_eval`).

## Check your understanding
- What’s the difference between `/` and `//`? When would you use each?
- Why does `0.1 + 0.2` not equal `0.3` exactly? How do you compare floats safely?
- Explain truthiness for numbers, strings, and containers with examples.

## Further reading
- Python docs on built-in types: https://docs.python.org/3/library/stdtypes.html
- Floating point arithmetic: https://docs.python.org/3/tutorial/floatingpoint.html
- f-strings: https://docs.python.org/3/reference/lexical_analysis.html#f-strings
