# python-pandas-07: Explained typed-I/O and domain solutions

The [complete executable reference](py_pandas_07_solution.py) implements all
six functions using actual pandas and Arrow APIs. It preserves a literal NA ID,
leading zeroes, unknown amounts and integers too large for exact consecutive
binary64 representation. The [guide](../companion-guides/py_pandas_07.md) explains
which policies are deliberate application choices and which behaviors belong
to the selected libraries.

## Exercise 1: Read identity-bearing CSV as text first

**Inputs:** CSV text with exactly record_id,group,amount_cents fields in that order on every logical record. No blank/ragged records; IDs are unique nonempty text, groups nonempty text, and empty amounts mean unknown.

**Expected:** Return those three columns with string IDs/groups and nullable Int64 amounts. Preserve leading zeroes and literal NA identifiers, parse integer cents without a float stage, and reject malformed structure or domain-invalid rows with ValueError.

**Verify:** Assert exact IDs 00017/NA/00019 and exact integers 9007199254740993 and the int64 maximum. Reject both short and four-field rows so an implicit CSV index cannot shift meanings.

```python
frame = pd.read_csv(StringIO(text), dtype="string", keep_default_na=False)
frame["amount_cents"] = strict_int64(frame["amount_cents"])
```

The first read preserves original field spellings. It does not apply default
missing-token interpretation or numeric inference to identifiers. The loader
then checks the exact three-column order, unique nonempty record IDs and
nonempty groups before parsing only the amount field through Exercise 2.

Before that read, standard-library `csv.reader` validates quoting and exactly
three fields per logical record. This closes a subtle counterexample: a
four-field input can be interpreted as an implicit index, leaving three plausible
but shifted named columns. Blank and short records are rejected as well. CSV
quoting is respected, so a comma inside a quoted identifier is not a fourth field.

The reference IDs are `00017`, `NA` and `00019`; all three survive exactly.
The first amount remains 9007199254740993, the second stays unknown and the
third is the signed-int64 maximum. Reading amounts as text first prevents a
missing value from forcing a lossy float stage. A later cast cannot restore
already rounded digits. The loader deliberately does not trim ID whitespace
or impose an unrelated structured-code format; those would be separate policies.

## Exercise 2: Parse integer text without losing digits

**Inputs:** A pandas string Series containing signed ASCII integer text, empty strings or pd.NA. Leading zeroes and plus signs are allowed for quantities; whitespace, fractions, exponents and non-ASCII digits are not.

**Expected:** Return a same-index/same-name Int64 Series. Preserve zero and exact signed-int64 endpoints, map only declared empty/missing inputs to pd.NA, and reject invalid text or out-of-range values with ValueError.

**Verify:** Compare parsed values with exact Python integer oracles and assert both range boundaries and one-past failures. Inspect missing positions independently from actual zero.

An explicitly typed string Series is required. Empty strings and its existing
missing marker become unknown integers. Every other value must match the
declared ASCII signed-integer spelling before exact Python integer conversion.

```python
number = int(value)
if not -(2**63) <= number < 2**63:
    raise ValueError("Integer text is outside signed int64 range")
```

Only after the range check does the reference build a nullable `Int64` array.
The original row index and Series name are retained. Duplicate row labels do
not change the positional conversion of each supplied value; this function
does not treat that index as a unique business key.

The minimum signed value and `+0002` are valid and retain their exact numerical
meaning. Decimal text, exponent notation, surrounding whitespace, non-ASCII
digits and values one past either boundary fail. An invalid token never becomes
zero or an apparently missing measurement. Tests compare with Python integer
oracles and inspect unknown positions separately from an actual zero.

## Exercise 3: Reject unknown categories before casting

**Inputs:** A pandas string Series and a nonempty unique tuple of nonempty allowed category strings. Original missing values are permitted.

**Expected:** Return a same-index/name nominal categorical Series with the declared category order, including unused categories. Preserve original missing values and reject unknown observed labels before they can become manufactured missing values.

**Verify:** Check red/blue/unused-green metadata and compare the original missing mask. Assert a purple observed label raises instead of silently becoming NA.

```python
unknown = values.notna() & ~values.isin(allowed)
if unknown.any():
    raise ValueError("Observed category is outside the declared domain")
```

The allowed domain must be a nonempty unique tuple of nonempty strings. Source
missing values remain permitted by this function. A known observed label outside
the domain is an error, while a source missing value is not classified as an
unknown observed label. These meanings are checked before any categorical cast.

The resulting dtype is nominal, with the exact declared category sequence,
including unused green in the reference. Listing a category first does not
make it lower-ranked because `ordered=False`. Reordering the category metadata
can change internal integer codes; compare labels and domain metadata rather
than treating the codes as portable identities. The later Parquet writer adds
a stricter nonmissing-group boundary for its particular table contract.

## Exercise 4: Extract code parts without hiding invalid inputs

**Inputs:** A pandas string Series. The fictional code format is exactly two ASCII uppercase letters, hyphen and four ASCII digits; nonmatching observations remain represented.

**Expected:** Return prefix,number,state columns with the same index and row count. Keep the four-digit suffix as text. Classify valid/invalid/missing separately; extracted fields are missing for nonmatches.

**Verify:** Assert AB-0007 preserves suffix 0007, bad text differs from a source missing value, full-width digits are invalid, and valid substrings inside extra text cannot pass.

```python
valid = values.str.fullmatch(pattern, na=False)
parts = values.str.extract(pattern)
state = state.mask(values.isna(), "missing").mask(valid, "valid")
```

The pattern is anchored and has named `prefix` and `number` groups. `[A-Z]`
and `[0-9]` implement this fictional ASCII code specification, while the suffix
remains text. `AB-0007` therefore yields prefix AB and suffix 0007, without a
numeric conversion that would erase zeroes.

Malformed `bad`, a missing source field and full-width-digit text are retained
as separate input rows. Their extraction fields are unknown, but state is
invalid, missing and invalid respectively. Without the explicit state column,
an all-missing extraction result could conceal why parsing failed. This code
format does not prohibit Unicode generally; it merely enforces the declared
alphabet for this particular field. Tests also require full-string matching so
a valid substring inside extra text cannot pass.

## Exercise 5: Write a real Parquet payload with explicit fields

**Inputs:** Exactly record_id,group,amount_cents columns: unique nonmissing string IDs, nonmissing nominal categorical groups and nullable Int64 amounts. Input is a small trusted fixture.

**Expected:** Return actual in-memory Parquet bytes with the explicit non-null string/dictionary fields and nullable signed-int64 amount schema. Exclude the row index, retain business columns, and never mutate the input frame.

**Verify:** Inspect the real Arrow field schema and compare a deep original frame after writing. Preserve exact large integer and missing amount meanings through the subsequent independently checked readback.

The writer validates the complete three-column table, including unique string
IDs, known nominal groups and nullable Int64 amounts. Its Arrow schema fixes
the logical field types and nullability before serialization.

```python
table = pa.Table.from_pandas(frame, schema=schema, preserve_index=False, safe=True)
pq.write_table(table, sink, compression="NONE", use_dictionary=["group"])
```

The business identity is the explicit record ID column. A pandas row index is
deliberately excluded from this export, so a custom index would need another
declared representation if it carried meaning. Nominal dictionary encoding is
a representation of group labels; consumers still need the labels and domain
contract. The fixture's bytes are actual Parquet, not a JSON imitation labelled
with a Parquet suffix.

The code keeps a deep input copy and compares it after writing. Serialization
must not repair the caller's keys, replace missing amounts with zero or mutate
its category metadata. Byte equality across different writer versions is not
the acceptance criterion. Logical schema and exact meaning are checked by the
reader and independent roundtrip comparison.

## Exercise 6: Accept only compatible readback meaning

**Inputs:** Small trusted Parquet bytes from the exercise and an explicit allowed category tuple. The encoded-byte limit is not a sandbox for arbitrary hostile binary inputs.

**Expected:** Reject incompatible field order/types/nullability or invalid business identities/domains, then return the declared string/category/Int64 pandas table with a fresh row index. Validate observed labels before casting and restore the consumer-declared category domain.

**Verify:** Use assert_frame_equal against the explicit original business table, including unknown positions, exact integers and unused category metadata. Reject a readable Parquet file with an incompatible integer-ID schema.

The reader operates on tiny trusted bytes made by the example. It checks the
decoded Arrow schema against the expected field order, types and nullability.
A valid Parquet file with an incompatible integer record-ID field is rejected.

```python
if not table.schema.equals(expected_schema, check_metadata=False):
    raise ValueError("Parquet logical schema does not match the contract")
```

Library metadata unrelated to this explicit field contract is not required to
be byte-identical. The reader reconstructs string and nullable integer pandas
representations only after type compatibility is established. It checks observed
group labels against the supplied consumer domain before reapplying categorical
metadata, including any declared unused categories. This does not infer domain
authority merely from a producer's file metadata.

Finally, the same table boundary checks unique nonmissing IDs, known groups and
the declared amount dtype. `assert_frame_equal` compares complete values, unknown
positions, dtypes and categories with the original table after the intentionally
excluded row index is reset. A row count or total amount alone would miss changed
IDs and rounded integers. Encoded-byte bounds and schema inspection do not make
an arbitrary binary parser safe for hostile files; input preparation and process
resource containment remain separate from this compatibility exercise.
