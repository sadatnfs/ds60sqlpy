# Day 7 — Strings, Regular Expressions, and Pathlib (Companion Guide)

## Learning objectives
- Clean and normalize text with Python string methods
- Parse patterns with regular expressions (regex)
- Work with files and directories via `pathlib` in a cross-platform way

## Why this matters
Text cleaning is a core step in almost every data workflow—logs, CSV headers, free-form notes. A practical regex vocabulary + safe file handling saves time and reduces bugs.

## Mental models
- Prefer string methods for simple tasks (strip/lower/replace); reach for regex when patterns vary or need validation
- Compile regexes you reuse; write readable patterns with named groups
- Treat `Path` objects as first-class citizens; avoid manual path string concatenation

## Text normalization toolbox
```python
s = '  Data Science  '
s_clean = s.strip().lower().replace(' ', '_')  # 'data_science'
```
Common transforms: `strip`, `lower`, `upper`, `title`, `replace`, `split`, `join`.

## Regex basics
```python
import re
EMAIL = re.compile(r"[\w.%-]+@[\w.-]+\.[A-Za-z]{2,}")
match = EMAIL.search('contact alice@example.com today')
match.group(0)  # 'alice@example.com'
```
Prefer raw strings `r"..."` for regex; escape sequences stay predictable.

### Named groups and validation
```python
DATE = re.compile(r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})")
if m := DATE.search('2025-01-03'):
    int(m['y']), int(m['m']), int(m['d'])
```
Use anchors `^` `$` for full-string validation: `re.fullmatch(pattern, s)`.

## Pathlib idioms
```python
from pathlib import Path
data_dir = Path('data')
data_dir.mkdir(exist_ok=True)
for p in data_dir.glob('*.csv'):
    print(p.name, p.stat().st_size)
```
Avoid `os.path.join`/string concatenation; `Path` overloads `/` for subpaths: `(data_dir / 'file.csv')`.

## Robust file reads
- Always open with context managers (`with Path(...).open() as f:`)
- For unknown encodings, try `encoding='utf-8'` then consider `errors='replace'`

## Common pitfalls
- Greedy vs lazy regex quantifiers (`.*` vs `.*?`)
- Backslashes in Windows paths; raw strings prevent `"\n"` surprises
- Assuming OS-specific separators; use `Path` for portability

## Practice exercises
1) Extract all emails from a multiline string and return a unique, lowercased set
2) Given files `Report (Jan).csv`, `Report (Feb).csv`, rename to `report-jan.csv`, `report-feb.csv`
3) Validate dates in multiple formats using alternation and named groups

## Stretch goals
- Build a small anonymizer: replace emails and phone numbers in a file with placeholders
- Write a `slugify` function that keeps only `[a-z0-9-]` and collapses multiple hyphens

## Check your understanding
- When is regex overkill? Give an example solved more simply with `split` or `replace`
- What are greedy vs lazy quantifiers? Show a before/after match

## Further reading
- re docs: https://docs.python.org/3/library/re.html
- pathlib docs: https://docs.python.org/3/library/pathlib.html
