# polars-012: Arrow interoperability and categorical meaning

## Level and prerequisites

Intermediate. Direct prerequisites: `polars-003`, `polars-004`

**Outcome:** Move a typed table across an Arrow boundary while preserving its logical contract.

## Question and mechanism

Arrow is a language-independent columnar representation with explicit types and validity information. It can reduce serialization overhead when systems share compatible buffers, but a blanket claim of zero-copy interoperability is too strong. Casting, rechunking, string representation changes and conversion to Python objects can allocate new memory. Test values and types first, then inspect memory behavior for the particular path when it matters.

The first case demonstrates a value-preserving conversion between Polars and an Arrow table, including a null. It proves a logical round trip on the fixture. It does not measure every allocation or guarantee that another library will preserve all metadata. A data engineer should distinguish representation compatibility from the semantics of the fields being transported.

Categories introduce a further contract. A closed business vocabulary can have an order that differs from alphabetical order. Enum declares that vocabulary explicitly. It is useful for states such as new, paid and shipped, where unknown values should be rejected or quarantined. Physical category codes are implementation details and should not replace stable labels in an external interface.

## Syntax and data contract

to_arrow returns an Arrow Table; pl.from_arrow constructs a Polars result. Arrow columns expose type and null information, and to_pylist is a convenient small-fixture inspection method that creates Python objects. pl.Enum takes the ordered allowed labels. Casting an unknown label under strict behavior raises a real conversion error.

## Run the lesson

Open this subject in `/classroom`, then show its code and notes. The prepared `data-engineering` worker runs `main.py` in a fresh temporary directory. The examples use installed packages and synthetic local fixtures; no account, cloud service, network request or package download is required. Save source and notes before switching lessons. Temporary databases, project files and tracking artifacts are recreated by each complete program and removed after the job. The classroom retains the submitted source and bounded output, not an indefinitely running external service. The guide distinguishes this local execution from the deployment decisions that need an owned production environment.



## Worked case 1: Preserve values and validity

The first case converts a three-row frame into Arrow and back, checks exact identifier values and confirms that the value column retains one null. The assertions deliberately concern logical content rather than an unmeasured memory-sharing claim.

**Expected evidence:** Values and schema round-trip; the Arrow value column has one null.

```python
import polars as pl
import pyarrow as pa


def example_one():
    frame = pl.DataFrame({"id": [1, 2, 3], "value": [2.0, None, 4.0]})
    arrow = frame.to_arrow()
    assert arrow.column("id").to_pylist() == [1, 2, 3]
    assert arrow.column("value").null_count == 1
    restored = pl.from_arrow(arrow)
    assert restored.equals(frame)
    assert isinstance(arrow, pa.Table)
    return {"arrow_schema": str(arrow.schema), "round_trip": True, "nulls": 1}


if __name__ == "__main__":
    print(example_one())
```


## Worked case 2: Encode a closed ordered vocabulary

The second case defines the allowed workflow states and sorts them according to that order. It then attempts to encode an unknown state, which should not silently become a valid category.

**Expected evidence:** Business order is new, paid, shipped; unknown is rejected.

```python
import polars as pl


def example_two():
    status = pl.Enum(["new", "paid", "shipped"])
    frame = pl.DataFrame({"status": ["shipped", "new", "paid"]}).with_columns(
        pl.col("status").cast(status)
    )
    assert frame.sort("status")["status"].cast(pl.String).to_list() == ["new", "paid", "shipped"]
    try:
        pl.Series(["unknown"]).cast(status)
    except pl.exceptions.InvalidOperationError:
        rejected = True
    else:
        rejected = False
    assert rejected
    return {"business_order": ["new", "paid", "shipped"], "unknown_rejected": rejected}


if __name__ == "__main__":
    print(example_two())
```


## Practice

Make each requested change in a saved copy. Compare both the expected result and the deliberately changed assumption. The separate reference explains the answers.


### 1. Inspect a null bitmap conceptually

Explain why a null is separate from a numeric payload value.

**Check:** The answer identifies validity metadata.

**Hint:** A missing value is not necessarily a special numeric sentinel.


### 2. Avoid a zero-copy claim

State what the round-trip test actually proves.

**Check:** It proves logical equality on the fixture.

**Hint:** No allocation measurement was made.


### 3. Add a valid category

Extend the allowed states with returned.

**Check:** The cast accepts the new label under the revised contract.

**Hint:** Vocabulary evolution changes the schema.


### 4. Reject an unknown category

Add cancelled without changing the Enum.

**Check:** Strict conversion rejects it.

**Hint:** Unknown is not a synonym for null.


### 5. Compare sort policies

Compare business-order and alphabetical sorting.

**Check:** Their orders can differ.

**Hint:** Sort String and Enum representations separately.


### 6. Design an interchange contract

List what a receiver needs beyond an Arrow object.

**Check:** It includes grain, units, null policy and schema version.

**Hint:** A transport format cannot define domain meaning.


## Diagnose errors and misleading results

Unexpected copies are a performance question, while changed values are a correctness question. Diagnose them with different evidence. If categorical comparisons fail, check vocabulary versions and unknown labels before comparing physical codes. Keep label semantics visible when crossing languages or serializing an artifact.

## Transfer to independent work

Move a typed table across an Arrow boundary while preserving its logical contract. Document which properties were checked and which memory claims were not measured. Use explicit category vocabularies when business order matters, and test unknown-value handling as part of schema evolution.

## Primary references

- [Polars documentation: Arrow interoperability and categorical meaning](https://docs.pola.rs/user-guide/expressions/categorical-data-and-enums/)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository learning-companion skill for `polars-012`. Inspect the learner's own source and observations, ask for an explanation of the relevant data or state contract, and give a focused hint. Separate an assertion on this fixture from a claim about an external dataset or deployed service.
