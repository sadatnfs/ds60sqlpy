# Day 4 — Loops, Comprehensions, and Generators (Companion Guide)

## Learning objectives
- Master `for`/`while` loops and idiomatic iteration patterns
- Replace imperative loops with list/dict/set comprehensions when appropriate
- Understand generators, lazy evaluation, and back‑pressure friendly pipelines

## Why this matters
Iteration appears everywhere in data work: reading files, cleaning records, transforming rows. Comprehensions and generators make your code faster to write, often faster to run, and easier to reason about memory use.

## Mental models
- Comprehension = “map + (optional) filter” in one readable expression
- Generator = a function that *yields* values on demand; think of it as a lazy stream
- Iterables vs iterators: an iterable can produce a fresh iterator; an iterator *is* a consuming stream

## Patterns and examples
### Basic `for` and `enumerate`
```python
for i, item in enumerate(items, start=1):
    print(i, item)
```
`enumerate` beats manual index tracking.

### List/dict/set comprehensions
```python
# Filter + transform
squares = [x*x for x in range(10) if x % 2 == 0]
# Dict from pairs
square_map = {x: x*x for x in range(5)}
# Unique letters
unique = {c for c in 'datascience'}
```
Prefer comprehensions for single‑line, clear transformations.

### Generator functions and expressions
```python
def count_up_to(n):
    for i in range(1, n+1):
        yield i

# generator expression
lines = (line.strip() for line in open('file.txt'))
```
Use generators to avoid loading everything into memory.

### Chaining generators to build pipelines
```python
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line.rstrip('\n')

def only_ints(lines):
    for s in lines:
        if s.isdigit():
            yield int(s)

def evens(nums):
    for n in nums:
        if n % 2 == 0:
            yield n

for n in evens(only_ints(read_lines('data.txt'))):
    process(n)
```
Pipelines scale to large files and are naturally testable piece‑by‑piece.

## Common pitfalls
- List comprehension with heavy side effects: use a loop when clarity matters
- Accidentally materializing big lists when a generator would suffice
- Closing files: prefer `with` or wrap file iteration in a generator that uses a context manager

## Practice exercises
1) Convert a two‑step loop (`filter` then `map`) into a single list comprehension.
2) Write a generator that yields sliding windows of size `k` over a list.
3) Build a streaming CSV cleaner: read a CSV row‑by‑row, strip whitespace, and yield dicts.

## Stretch goals
- Reimplement `itertools.groupby` to group consecutive equal items
- Benchmark a comprehension vs a `map`/`filter` vs a loop for 1e6 integers

## Check your understanding
- When do comprehensions hurt readability? Give an example.
- Why can generators lower memory usage and enable back‑pressure?

## Further reading
- itertools: https://docs.python.org/3/library/itertools.html
- Generator how‑to: https://docs.python.org/3/howto/functional.html#generators
