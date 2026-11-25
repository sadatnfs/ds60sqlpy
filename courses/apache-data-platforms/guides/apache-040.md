# apache-040: Field IDs and schema evolution

Tutorial mode. Stage: intermediate. Direct prerequisites: `apache-039`, `apache-010`.

## Key terms

- **Field ID:** A stable numeric identifier Iceberg assigns to each column, so a rename or reorder keeps the same identity for existing data files.
- **Schema evolution:** Committing a new table schema, such as adding, renaming or dropping a column, without rewriting existing data files.
- **Optional field:** A column that may be null. Adding one is safe because older files that lack it read as missing.
- **Required field:** A column that may not be null. Adding one without a valid default is unsafe because older files contain no value for it.
- **Type promotion:** A widening type change, such as int to long, that Iceberg allows because every old value remains valid under the new type.

## A field name is not its identity

A table column can be renamed, reordered or removed while older data files remain.
If a reader identified columns only by position, moving a field could make one
column's bytes appear under another name. If it identified columns only by display
name, a rename could look like deleting one field and creating a different one.
Iceberg assigns stable numeric field IDs to separate identity from presentation.

Schema evolution still needs compatibility rules. Adding an optional field allows
older rows to have no stored value, which a compatible reader can represent as
missing. Adding a required field without a valid default is different: old files
do not contain that value. Type changes must respect supported promotion rules;
a string cannot be reinterpreted as an integer merely because some current values
happen to contain digits.

The program performs real PyIceberg schema commits while retaining the original
Parquet files. It records the initial amount field ID and the existing data-file
paths, renames the field, and verifies that the new name refers to the same ID.
This demonstrates metadata evolution, not a physical rewrite or an inference
based on identical row counts.

## Worked case A: rename an amount without rewriting data

The first case renames amount to revenue. Reading the current table returns the
original amounts under the new name, and the field ID remains unchanged. The
program also checks that the data-file path set is unchanged. These observations
together support the claim that this rename changed metadata rather than
rewriting the fixture's data files.

An application using the old display name can still fail after this change.
Stable identity protects table interpretation; it does not automatically rewrite
every downstream SQL query, feature declaration or dashboard. A rollout therefore
needs consumer compatibility, a migration plan and a policy for exposing aliases
or versioned views where supported.

Nested fields also have identities. Renaming a parent or rearranging struct
members cannot be reasoned about solely by top-level position. The small example
uses a flat schema so the exact observations are readable, but the identity
principle extends through the table schema. Always inspect the schema that the
selected engine actually loads rather than assuming support from a format name.

## Worked case B: optional addition and required-field rejection

The second case adds an optional integer quality field. Existing rows return
null for quality, preserving the distinction between not recorded and a measured
zero. A new append supplies quality for order 4; the program checks both the old
missing values and the new present value. The new Arrow input schema must include
the complete current table columns with compatible types.

It then attempts to add a required field without supplying a default. The prepared
PyIceberg API rejects this unsupported evolution. The program checks that the
failed field is absent afterward and the existing data remains readable. Catching
a real exception and checking retained state is more informative than merely
printing a warning about a possible schema error.

Deleting a field and later adding another field with the old name is not a safe
way to rename. The new field receives a different identity and should not inherit
old values by textual coincidence. Similarly, rearranging a CSV header outside
a typed table contract can lose the identity information that the format relies
on. Interoperability requires preserving the relevant metadata at each boundary.

## Diagnosis and interview discussion

Record schema IDs, field IDs, display names, nullability and physical types.
When an engine disagrees with another reader, inspect its connector version and
field-ID support. Avoid fixing a mismatch with a broad cast until the original
identity and unit meaning are understood. A successful cast can hide lost data
or a wrong semantic unit.

**Interview discussion: how can a rename be safe for stored files and disruptive
for applications?** The files remain interpretable through stable field IDs, but
application text still refers to display names and business contracts. These
cases demonstrate both the storage-level safety of a rename and the need for
explicit compatibility rules when adding values that old rows never contained.

## Worked examples

### Confirm a rename keeps the field identifier

```python fragment
before = table.schema().find_field("amount").field_id
with table.update_schema() as update:
    update.rename_column("amount", "revenue")
after = table.schema().find_field("revenue").field_id
print(before, after, before == after)
```

Both identifiers print the same small integer and the comparison is True, because Iceberg resolves columns by field ID and the rename only changes metadata. The Parquet files written before the rename still say amount in their own schema, and readers map them through the ID. A tool that matches by name instead of ID would read nulls for revenue in old files, so test renames with the reader you actually deploy.

### Add an optional column without rewriting old rows

```python fragment
from pyiceberg.types import LongType

with table.update_schema() as update:
    update.add_column("quality", LongType())
rows = table.scan().to_arrow().to_pylist()
print([row["quality"] for row in rows])
```

Existing rows report None for quality because the new field ID is absent from their files, and no data file is rewritten. Adding a required column to a table that already has rows is rejected, since old rows could not satisfy it. If a reader shows zeros instead of None for old rows, a default is being applied downstream and should be documented rather than assumed.

## Complete worked source

Run it as the [worked program rules](../STUDY-GUIDE.md#worked-programs) describe.

```python
import tempfile
from pathlib import Path

import pyarrow as pa
from pyiceberg.catalog import load_catalog
from pyiceberg.types import LongType

with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    catalog = load_catalog(
        "lesson",
        type="sql",
        uri="sqlite:///" + str(root / "catalog.db"),
        warehouse=(root / "warehouse").as_uri(),
    )
    catalog.create_namespace("demo")
    data = pa.table({"id": [1, 2, 3], "region": ["east", "west", "east"], "amount": [4, 9, 7]})
    table = catalog.create_table("demo.orders", schema=data.schema)
    table.append(data)

    field_id = table.schema().find_field("amount").field_id
    paths = {task.file.file_path for task in table.scan().plan_files()}
    with table.update_schema() as update:
        update.rename_column("amount", "revenue")
    assert table.schema().find_field("revenue").field_id == field_id
    assert {task.file.file_path for task in table.scan().plan_files()} == paths
    assert sum(table.scan().to_arrow()["revenue"].to_pylist()) == 20
    with table.update_schema() as update:
        update.add_column("quality", LongType())
    table.append(pa.table({"id": [4], "region": ["west"], "revenue": [2], "quality": [1]}))
    rows = sorted(table.scan().to_arrow().to_pylist(), key=lambda row: row["id"])
    assert [row["quality"] for row in rows] == [None, None, None, 1]
    try:
        with table.update_schema() as update:
            update.add_column("required_new", LongType(), required=True)
    except ValueError as error:
        print("Required addition rejected:", str(error))
    else:
        raise AssertionError("Invalid required evolution accepted")
    assert "required_new" not in table.schema().column_names
    assert table.scan().to_arrow().num_rows == 4
    print("Retained field ID:", field_id, "quality values:", [row["quality"] for row in rows])
```

## Primary references

- [PyIceberg table API](https://py.iceberg.apache.org/api/)
- [Iceberg table specification](https://iceberg.apache.org/spec/)
