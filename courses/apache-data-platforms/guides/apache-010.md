# apache-010: Schemas, nested data and dictionaries

Tutorial mode. Stage: beginner. Direct prerequisites: `apache-009`.

## Key terms

- **Struct type:** A nested Arrow type with named child fields, each with its own type and validity, so a missing child value differs from a missing parent record.
- **List offsets:** The offsets buffer of a list array. The size of the list at position i is offset i + 1 minus offset i, which delimits its child values.
- **Dictionary encoding:** Storing repeated values as integer indices into a dictionary of distinct values, which saves space and comparison work for low-cardinality categories.
- **Schema metadata:** Key-value annotations on a schema or field, such as a unit or source-system label. They document intent but do not enforce any validation.

## The mechanism

A business record often contains a list of items, an optional address and a
category. Flattening everything to strings discards the structure that query
engines need. Arrow expresses these relationships in its schema: a field has a
name, type and nullability; a struct has named child fields; a list has a child
value type; and a dictionary array maps integer indices into a dictionary of
values. These are storage and interpretation contracts, not merely display hints.

List offsets delimit the child values belonging to each parent slot. For a
non-null list at position \(i\), its logical size is
\(\ell_i=o_{i+1}-o_i\). A null list has no observed list value, so its offsets
alone must not be used to manufacture an empty list. Child validity is separate
from parent validity. The distinction matters whenever a nested aggregation asks
whether information is absent, a collection is empty, or one member is missing.

A schema can also carry metadata such as a unit or source-system label. Metadata
is useful documentation, but a label saying 'validated' is not a validation step.
The receiving program must still enforce the constraints its calculation needs.
This example deliberately makes all fields and values small enough to inspect.

## Worked case A: missing list, empty list and missing element

The first case creates three records. The first has quantities `[2, None]`, the
second has an empty quantities list, and the third has a missing quantities list.
Converting to Python preserves these as three different values. The first record
has one observed item quantity and one unobserved quantity; the second reports
zero items; the third supplies no list at all. Those are different statements
about the data collection process.

The program uses a typed list child and checks the list offsets, parent null
count and child null count independently. The valid list lengths are 2 and 0,
while the missing list's length remains missing. If downstream code replaces
that missing length with zero, it has asserted that no items existed. That might
be a justified business rule, but the assertion belongs in a named transformation
with evidence, not in an accidental serialization conversion.

The worked record also contains a struct-valued shipping address. A missing
address differs from a present address whose optional postal code is missing.
A customer-service task may route these cases differently: one needs an address,
the other needs clarification of one component. Nested types preserve enough
information to make that decision later.

## Worked case B: dictionary encoding preserves values, not universal codes

The second case encodes repeated region labels into a dictionary. Repetition can
be represented with small integer indices plus one copy of each distinct label.
The approximate payload comparison is \(nb+\sum_j |s_j|\) versus
\(\sum_i |s_i|\), before offsets, validity and allocator overhead, where
\(b\) is the index width. This comparison explains a possible saving; it is
not a benchmark or a promise for every cardinality.

Two arrays built independently may assign different index numbers to the same
region. The program creates reversed encounter order and shows that index 0 means
different values in the two dictionaries. Comparing raw indices across those
arrays would give incorrect matches. Decoding recovers the labels, and an engine
that combines dictionary arrays must reconcile dictionary identity appropriately.
The equality test in the program checks decoded semantics rather than assuming
a globally stable encoding.

A dictionary is not automatically an ordered category. A ranking such as bronze,
silver and gold needs an explicit ordering contract; lexical or encounter order
may not match business meaning. Similarly, integer identifiers should not be
compressed by a lossy conversion merely because their printed forms look numeric.

## Mistakes and diagnosis

When a nested result seems to lose rows, inspect parent and child validity
separately before flattening. When a join on dictionary codes returns unexpected
matches, verify that both sides refer to the same dictionary. When a schema
changes, compare nested field types and nullability as well as top-level names.
An unchanged column name can still hide a changed child type.

## Interview discussion

**Why is an empty list different from a null list in an analytical system?**
An empty list is an observed collection of cardinality zero. A null list indicates
that the collection value is absent. Counting missing collections as zero changes
the population being measured. A strong implementation preserves the distinction,
then applies an explicit business rule when required. The two worked cases also
show why physical encodings can be efficient while still requiring careful
semantic interpretation at system boundaries.

## Worked examples

### Distinguish a null list from an empty list

```python
import pyarrow as pa
import pyarrow.compute as pc

quantities = pa.array([[2, None], [], None], type=pa.list_(pa.int64()))
print(quantities.offsets.to_pylist())
print(pc.list_value_length(quantities).to_pylist())
print(quantities.null_count, quantities.values.null_count)
```

```text
[0, 2, 2, 2]
[2, 0, None]
1 1
```

The offsets 0, 2, 2, 2 show that the empty list and the null list both occupy zero child slots, yet the lengths differ: zero for the empty basket and null for the unknown one. The two null counts separate a missing list from a missing element inside a list. Flattening this column before counting would erase both distinctions, so count at the list level first.

### Compare dictionary columns by decoded values

```python
import pyarrow as pa

left = pa.array(["east", "west"]).dictionary_encode()
right = pa.array(["west", "east"]).dictionary_encode()
print(left.indices.to_pylist(), right.indices.to_pylist())
print(left.dictionary_decode().to_pylist(), right.dictionary_decode().to_pylist())
```

```text
[0, 1] [0, 1]
['east', 'west'] ['west', 'east']
```

Both columns store indices 0 and 1, but they decode to opposite region orders because each batch built its own dictionary. Comparing or joining on raw indices across batches would report a false match. Unify dictionaries or decode before comparison, and treat any pipeline that persists dictionary codes as stable identifiers as a defect waiting for a new batch.

## Complete worked source

This is a complete editable worked program for the declared prepared runtime. It uses bounded local fixtures and does not install packages or start distributed services.

```python
import pyarrow as pa
import pyarrow.compute as pc

quantities = pa.array([[2, None], [], None], type=pa.list_(pa.int64()))
assert quantities.to_pylist() == [[2, None], [], None]
assert quantities.offsets.to_pylist() == [0, 2, 2, 2]
assert quantities.null_count == 1 and quantities.values.null_count == 1
assert pc.list_value_length(quantities).to_pylist() == [2, 0, None]
address_type = pa.struct([("city", pa.string()), ("postal", pa.string())])
addresses = pa.array([{"city": "Example City", "postal": None}, None], type=address_type)
assert addresses.to_pylist() == [{"city": "Example City", "postal": None}, None]
left = pa.array(["east", "west", "east", None]).dictionary_encode()
right = pa.array(["west", "east", "west", None]).dictionary_encode()
assert left.dictionary[0].as_py() == "east"
assert right.dictionary[0].as_py() == "west"
assert left.indices.to_pylist() == right.indices.to_pylist()
assert left.dictionary_decode().to_pylist() != right.dictionary_decode().to_pylist()
assert left.dictionary_decode().to_pylist() == ["east", "west", "east", None]
print("List lengths preserve missing collections:", pc.list_value_length(quantities).to_pylist())
print("Same physical indices, different dictionaries:", left.indices.to_pylist())
print("Decoded left:", left.dictionary_decode().to_pylist())
print("Decoded right:", right.dictionary_decode().to_pylist())
```

## Primary references

- [Arrow nested data model](https://arrow.apache.org/docs/python/data.html)
- [Arrow dictionary and list layout](https://arrow.apache.org/docs/format/Columnar.html)
