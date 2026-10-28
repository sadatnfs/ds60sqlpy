# Typed I/O, Text, and Categorical Domains

**Stable ID:** `python-pandas-07`. This lesson treats parsing and serialization
as explicit data contracts. Allow about three hours for the reading, worked
cases, implementations and independent comparisons.

## How to run this lesson

Start `./classroom`, select **Python** in `/classroom`, and open this unit.
Read its capability notice, paste the entire learner artifact into the coding
pad, save and Run. Docker supplies Python, pandas and Arrow. Windows learners
use the same commands in WSL 2. All CSV text and Parquet bytes are tiny original
fixtures created in memory; no dataset, account or external storage is required.

The learner script runs two worked examples without invoking the six unfinished
task functions. Implement and call each task separately as you work through the
contracts. Every Run has a fresh process, so save imports, fixture creation and
function calls together. The browser persists your submitted code, notes and
result; it does not keep an in-memory DataFrame alive between runs. Open the
separate explanation or complete executable reference when you choose to
compare your attempt. A zero exit from the demonstrations is not evidence that
the six independent contracts have been satisfied.

The optional prepared contributor command is
`uv run --no-sync python python/professional/lessons/py_pandas_07.py` from the
repository root. That host environment uses its own checkout-local state and
does not access the Docker learning volume. See the
[classroom guide](../../../docs/classroom-experience.md) and optional
[contributor setup](../../../CONTRIBUTING.md) for their respective boundaries.
Temporary serialized bytes here remain in the process, rather than becoming
an undocumented host-side output file.

## Level and prerequisites

- **Level:** Advanced.
- **Direct prerequisite:** `python-18`, [companion guide](../../ds-60day/companion-guides/day18_pandas_io_cleaning.md).
- **Direct prerequisite:** `python-pandas-01`, [companion guide](py_pandas_01.md).
- **Direct prerequisite:** `python-pandas-03`, [companion guide](py_pandas_03.md).
- **Artifacts:** [learner](../lessons/py_pandas_07.py) · [explanations](../solutions/py_pandas_07_solutions.md) · [executable reference](../solutions/py_pandas_07_solution.py).

This advanced practice lesson directly requires `python-18`,
`python-pandas-01` and `python-pandas-03`. Review string columns, nullable values,
explicit joins and row identity first. The examples target the prepared Core
environment's pandas 2.3 and Arrow libraries. They require no cloud client,
schema registry, special database extension or package installation during a Run.

## Learning objectives

Preserve leading-zero and literal-NA identifiers while reading CSV, then parse
integer-cent text through an exact lexical and range boundary. Distinguish an
unknown category from an originally missing observation before casting. Extract
structured ASCII codes while retaining invalid and missing states. Finally,
write and read real in-memory Parquet using explicit field types, nullability,
business identity and category-domain checks.

## Vocabulary and concepts

- **Logical type:** The meaning and permitted operations of a field. An identifier
  is a label even when every character is a digit. Removing its leading zeroes
  can change identity, while parsing a quantity's leading zeroes may preserve its
  numeric meaning. Decide the logical type before accepting parser inference.

- **Nullable dtype:** A representation that supports known values and a missing
  marker together. pandas `Int64`, with a capital I, represents signed integer
  values and `pd.NA`. It differs from NumPy `int64`, which has no equivalent
  nullable scalar representation in an ordinary integer array.

- **Lexical contract:** The accepted spelling of a value at an input boundary.
  This lesson permits signed ASCII decimal integer text, including leading zeroes
  and a plus sign for quantities. It rejects fractional text, exponent notation,
  surrounding whitespace and non-ASCII digit characters. Those are declared
  choices, not universal rules for every numerical parser.

- **Categorical domain:** The declared set of allowed labels and its metadata.
  Nominal categories have no less-than ranking even if their metadata lists them
  in a particular order. Internal integer codes refer to that domain; a code
  alone is not a portable business label across differently configured domains.

- **Schema compatibility:** A policy about which fields and representations a
  consumer accepts. A readable Parquet file is not necessarily compatible with
  the receiving application. Names, order, logical types, nullability, category
  values and unique business identity can require separate checks.

## Syntax anatomy and exact parsing

`read_csv(..., dtype="string", keep_default_na=False)` first reads the declared
fields as text and preserves tokens such as `NA`. It also preserves empty
fields as empty strings. The lesson then applies field-specific rules: record
IDs and groups cannot be empty, while an empty amount explicitly means unknown.
A text amount `NA` is not an accepted missing-amount token under this contract.
The parser does not silently trim or normalize identifiers.

The input contract also requires exactly three fields in every logical CSV
record, with no blank records. Check that structure before pandas inference:
some ragged inputs can otherwise be interpreted as an implicit row index,
shifting values into the wrong named columns without the intended schema error.
Use the standard CSV parser to respect quoted commas and embedded newlines;
counting physical lines or splitting on commas is not an equivalent check.

Parse valid integer text with Python's exact `int` before constructing nullable
`Int64`. Check the signed range \([-2^{63},2^{63}-1]\) first. Avoid a float
intermediate: binary64 cannot represent every consecutive integer beyond
\(2^{53}\). Casting a rounded float to an integer does not recover lost digits.
Use integer cents for this fixture's stated unit; interpreting a value as dollars
instead would still be a semantic error even with a perfectly valid integer dtype.

## Worked example / walkthrough

### Worked example 1: Inference can erase identifiers and round quantities

```python
from io import StringIO
import pandas as pd

text = "record_id,group,amount_cents\n00017,NA,9007199254740993\n00018,red,\n"
inferred = pd.read_csv(StringIO(text))
typed = pd.read_csv(StringIO(text), dtype="string", keep_default_na=False)
assert inferred.record_id.tolist() == [17, 18]
assert pd.isna(inferred.group.iloc[0])
assert int(inferred.amount_cents.iloc[0]) != 9007199254740993
assert typed.record_id.tolist() == ["00017", "00018"]
assert typed.group.iloc[0] == "NA"
assert typed.amount_cents.iloc[0] == "9007199254740993"
print("Preserved IDs:", typed.record_id.tolist())
```

The first table contains several plausible transformations that violate the
producer contract. Numeric ID inference discards leading zeroes. Default missing
token handling interprets a literal category label as missing. A missing amount
causes floating representation, and the large known integer loses a digit.
All of these can happen before later cleaning functions inspect the DataFrame.
The second read preserves the original text so each conversion can be deliberate.

Unknown amounts must stay distinguishable from zero-cent amounts. The strict
parser maps only its declared empty or missing input to `pd.NA`, retains an
explicit zero, and refuses invalid text rather than converting it to an accepted
zero. Negative cents can represent a refund here; an application that forbids
negative amounts needs an additional business predicate.

### Worked example 2: A categorical cast can conceal a previously unknown label

```python
labels = pd.Series(["red", "purple", pd.NA], dtype="string")
domain = pd.CategoricalDtype(categories=["red", "blue"], ordered=False)
cast = labels.astype(domain)
unknown_before_cast = labels.notna() & ~labels.isin(domain.categories)
assert cast.isna().tolist() == [False, True, True]
assert unknown_before_cast.tolist() == [False, True, False]
print("Unknown observed labels:", labels[unknown_before_cast].tolist())
```

After the cast, the unknown purple label and the originally missing observation
look alike. The original values are needed to distinguish them. Validate known
labels against the declared domain first, then cast. Do not calculate an
unknown-label rate only from the cast result. That would mix a domain violation
with source missingness and could conceal an upstream vocabulary change.

Retain unused declared categories when the contract requires them. Observing no
green rows does not prove green is no longer a valid category. Conversely, a
category appearing in a file's metadata does not authorize it in the receiving
application. The reader receives the expected domain explicitly and checks the
decoded observed labels before restoring the selected categorical representation.

## Text validation and Unicode

The structured-code exercise accepts exactly two ASCII uppercase letters, a
hyphen and four ASCII digits. Use a full-match policy and named capture groups,
not an unanchored search that accepts a valid substring inside malformed text.
The numeric-looking suffix remains a string so `0007` does not become `7`.
Return valid, invalid and missing states separately while retaining every input
row and its original index.

This ASCII code policy is specific to a fictional identifier format. It does
not imply that Unicode names or category values are invalid generally. Unicode
normalization and case folding can intentionally make distinct spellings equal;
they can also merge previously distinct identities. Retain original text and
declare any normalization policy before applying it to business keys. Do not
silently normalize full-width digit characters merely to make this regex pass.

## Real Parquet and a declared compatibility boundary

The reference writes an actual Arrow table to Parquet bytes using an explicit
schema: non-null string `record_id`, non-null nominal dictionary/string `group`,
and nullable signed-int64 `amount_cents`. It excludes the pandas row index because
the business key is an explicit column. A custom index would not survive this
chosen export contract; use an explicit column or a different contract if it
carries meaning.

On read, check logical field order, types and nullability before making the
expected pandas representations. Validate observed category labels against the
consumer's supplied domain before categorical conversion. Recheck record-key
uniqueness and missingness after decoding. The complete roundtrip compares all
columns, values, dtypes and category metadata, not merely row count or a sum.
An intentionally incompatible Parquet schema must be rejected even though the
Parquet library can decode it successfully.

This is a strict small-fixture compatibility policy. Other systems deliberately
support field additions, nullable widening or identity-based schema evolution.
Those behaviors need explicit rules and versioned evidence. They should not
emerge accidentally from a permissive cast in a loader.

Only tiny trusted bytes produced by the example are used here. An encoded-byte
size limit does not bound a general binary decoder's memory use. Schema checks
after decoding are not a sandbox for arbitrary hostile files. The classroom's
outer process/resource boundary and deliberate input preparation remain separate.

## Exercises

1. **Preserve identity and validate CSV structure.**

**Inputs:** CSV text with exactly record_id,group,amount_cents fields in that order on every logical record. No blank/ragged records; IDs are unique nonempty text, groups nonempty text, and empty amounts mean unknown.

**Expected:** Return those three columns with string IDs/groups and nullable Int64 amounts. Preserve leading zeroes and literal NA identifiers, parse integer cents without a float stage, and reject malformed structure or domain-invalid rows with ValueError.

**Verify:** Assert exact IDs 00017/NA/00019 and exact integers 9007199254740993 and the int64 maximum. Reject both short and four-field rows so an implicit CSV index cannot shift meanings.

2. **Parse exact signed integer text.**

**Inputs:** A pandas string Series containing signed ASCII integer text, empty strings or pd.NA. Leading zeroes and plus signs are allowed for quantities; whitespace, fractions, exponents and non-ASCII digits are not.

**Expected:** Return a same-index/same-name Int64 Series. Preserve zero and exact signed-int64 endpoints, map only declared empty/missing inputs to pd.NA, and reject invalid text or out-of-range values with ValueError.

**Verify:** Compare parsed values with exact Python integer oracles and assert both range boundaries and one-past failures. Inspect missing positions independently from actual zero.

3. **Reject unknown labels before categorical conversion.**

**Inputs:** A pandas string Series and a nonempty unique tuple of nonempty allowed category strings. Original missing values are permitted.

**Expected:** Return a same-index/name nominal categorical Series with the declared category order, including unused categories. Preserve original missing values and reject unknown observed labels before they can become manufactured missing values.

**Verify:** Check red/blue/unused-green metadata and compare the original missing mask. Assert a purple observed label raises instead of silently becoming NA.

4. **Retain valid, invalid and missing text states.**

**Inputs:** A pandas string Series. The fictional code format is exactly two ASCII uppercase letters, hyphen and four ASCII digits; nonmatching observations remain represented.

**Expected:** Return prefix,number,state columns with the same index and row count. Keep the four-digit suffix as text. Classify valid/invalid/missing separately; extracted fields are missing for nonmatches.

**Verify:** Assert AB-0007 preserves suffix 0007, bad text differs from a source missing value, full-width digits are invalid, and valid substrings inside extra text cannot pass.

5. **Serialize real Parquet under an explicit business schema.**

**Inputs:** Exactly record_id,group,amount_cents columns: unique nonmissing string IDs, nonmissing nominal categorical groups and nullable Int64 amounts. Input is a small trusted fixture.

**Expected:** Return actual in-memory Parquet bytes with the explicit non-null string/dictionary fields and nullable signed-int64 amount schema. Exclude the row index, retain business columns, and never mutate the input frame.

**Verify:** Inspect the real Arrow field schema and compare a deep original frame after writing. Preserve exact large integer and missing amount meanings through the subsequent independently checked readback.

6. **Enforce logical compatibility and consumer domain.**

**Inputs:** Small trusted Parquet bytes from the exercise and an explicit allowed category tuple. The encoded-byte limit is not a sandbox for arbitrary hostile binary inputs.

**Expected:** Reject incompatible field order/types/nullability or invalid business identities/domains, then return the declared string/category/Int64 pandas table with a fresh row index. Validate observed labels before casting and restore the consumer-declared category domain.

**Verify:** Use assert_frame_equal against the explicit original business table, including unknown positions, exact integers and unused category metadata. Reject a readable Parquet file with an incompatible integer-ID schema.


## Common pitfalls

If an ID loses zeroes, inspect its dtype and raw CSV token before further
transformation. If a large integer changes, find the first floating conversion;
casting later cannot repair it. If an unknown category disappears, compare the
original text with the cast's missing mask. If regex extraction succeeds on a
bad string, inspect anchoring and whether a substring rather than the full value
was matched.

If Parquet readback has the right row count but different meaning, compare
field order/types, category labels, integer values, unknown positions and exact
business IDs. Keep parser errors distinct from domain violations. Save the
small original fixture and the failed assertion rather than changing expected
values to accommodate an accidental conversion.

## Self-check

Explain when a numeric-looking field should remain text. Show why unknown,
invalid and zero are different observations. Reproduce the category-cast loss
without using a remote dataset. State which metadata this Parquet contract
preserves and which it deliberately excludes. Then construct one independently
specified schema mismatch that must fail before the data are accepted.

## Next step

Continue to [chunked data and state](py_pandas_04.md) after completing its declared prerequisites. Choose the sequence through the catalog rather than assuming that day labels are deadlines.

Apply these boundaries before feature joins, published data products and
browser visualization. Integers beyond JavaScript's exact range also need a
deliberate transport representation; a correct Python integer does not prevent
later browser rounding. Read the selected
[pandas I/O documentation](https://pandas.pydata.org/pandas-docs/version/2.3/user_guide/io.html)
and [categorical guide](https://pandas.pydata.org/pandas-docs/version/2.3/user_guide/categorical.html)
for the APIs. The exact field schema, missing tokens and rejection rules in
this lesson are original application contracts.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-pandas-07: Typed I/O, Text, and Categorical Domains.
Read python/professional/companion-guides/py_pandas_07.md and python/professional/lessons/py_pandas_07.py. Direct prerequisites: python-18, python-pandas-01, python-pandas-03.
Explain the vocabulary and the exact input/output meaning, then ask me to predict a concrete boundary result before my attempt. Give one hint at a time, review my row/value/schema/exception evidence, and ask retrieval questions in my own words. Do not read solutions/ until I request a comparison or have made an honest attempt. Use only prepared offline fixtures and preserve my saved work.
Done when all six contracts and boundary cases have inspected evidence, and I can explain why a plausible inferred or silently repaired result violates the declared meaning.
```
