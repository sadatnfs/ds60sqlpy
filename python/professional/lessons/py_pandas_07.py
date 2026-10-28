"""python-pandas-07: Typed I/O, Text, and Categorical Domains.

Run both offline worked cases, then implement and independently verify the six
task contracts. Each browser Run is a fresh process. Answers are in solutions/.
"""

from __future__ import annotations

from io import StringIO

import pandas as pd


# Exercise 1: Preserve identity and validate CSV structure.
# Inputs: CSV text with exactly record_id,group,amount_cents fields in that order on every logical
# | record. No blank/ragged records; IDs are unique nonempty text, groups nonempty text, and empty
# | amounts mean unknown.
# Expected: Return those three columns with string IDs/groups and nullable Int64 amounts. Preserve
# | leading zeroes and literal NA identifiers, parse integer cents without a float stage, and reject
# | malformed structure or domain-invalid rows with ValueError.
# Verify: Assert exact IDs 00017/NA/00019 and exact integers 9007199254740993 and the int64 maximum.
# | Reject both short and four-field rows so an implicit CSV index cannot shift meanings.
def read_identity_csv(text: str) -> pd.DataFrame:
    """
    CSV text with exactly record_id,group,amount_cents fields in that order on every logical record.
    No blank/ragged records; IDs are unique nonempty text, groups nonempty text, and empty amounts
    mean unknown.

    Return those three columns with string IDs/groups and nullable Int64 amounts. Preserve leading
    zeroes and literal NA identifiers, parse integer cents without a float stage, and reject
    malformed structure or domain-invalid rows with ValueError.
    """
    raise NotImplementedError("Implement read_identity_csv")


# Exercise 2: Parse exact signed integer text.
# Inputs: A pandas string Series containing signed ASCII integer text, empty strings or pd.NA.
# | Leading zeroes and plus signs are allowed for quantities; whitespace, fractions, exponents and
# | non-ASCII digits are not.
# Expected: Return a same-index/same-name Int64 Series. Preserve zero and exact signed-int64
# | endpoints, map only declared empty/missing inputs to pd.NA, and reject invalid text or
# | out-of-range values with ValueError.
# Verify: Compare parsed values with exact Python integer oracles and assert both range boundaries
# | and one-past failures. Inspect missing positions independently from actual zero.
def strict_int64(values: pd.Series) -> pd.Series:
    """
    A pandas string Series containing signed ASCII integer text, empty strings or pd.NA. Leading
    zeroes and plus signs are allowed for quantities; whitespace, fractions, exponents and non-ASCII
    digits are not.

    Return a same-index/same-name Int64 Series. Preserve zero and exact signed-int64 endpoints, map
    only declared empty/missing inputs to pd.NA, and reject invalid text or out-of-range values with
    ValueError.
    """
    raise NotImplementedError("Implement strict_int64")


# Exercise 3: Reject unknown labels before categorical conversion.
# Inputs: A pandas string Series and a nonempty unique tuple of nonempty allowed category strings.
# | Original missing values are permitted.
# Expected: Return a same-index/name nominal categorical Series with the declared category order,
# | including unused categories. Preserve original missing values and reject unknown observed labels
# | before they can become manufactured missing values.
# Verify: Check red/blue/unused-green metadata and compare the original missing mask. Assert a
# | purple observed label raises instead of silently becoming NA.
def known_categories(values: pd.Series, allowed: tuple[str, ...]) -> pd.Series:
    """
    A pandas string Series and a nonempty unique tuple of nonempty allowed category strings.
    Original missing values are permitted.

    Return a same-index/name nominal categorical Series with the declared category order, including
    unused categories. Preserve original missing values and reject unknown observed labels before
    they can become manufactured missing values.
    """
    raise NotImplementedError("Implement known_categories")


# Exercise 4: Retain valid, invalid and missing text states.
# Inputs: A pandas string Series. The fictional code format is exactly two ASCII uppercase letters,
# | hyphen and four ASCII digits; nonmatching observations remain represented.
# Expected: Return prefix,number,state columns with the same index and row count. Keep the
# | four-digit suffix as text. Classify valid/invalid/missing separately; extracted fields are
# | missing for nonmatches.
# Verify: Assert AB-0007 preserves suffix 0007, bad text differs from a source missing value,
# | full-width digits are invalid, and valid substrings inside extra text cannot pass.
def extract_codes(values: pd.Series) -> pd.DataFrame:
    """
    A pandas string Series. The fictional code format is exactly two ASCII uppercase letters, hyphen
    and four ASCII digits; nonmatching observations remain represented.

    Return prefix,number,state columns with the same index and row count. Keep the four-digit suffix
    as text. Classify valid/invalid/missing separately; extracted fields are missing for nonmatches.
    """
    raise NotImplementedError("Implement extract_codes")


# Exercise 5: Serialize real Parquet under an explicit business schema.
# Inputs: Exactly record_id,group,amount_cents columns: unique nonmissing string IDs, nonmissing
# | nominal categorical groups and nullable Int64 amounts. Input is a small trusted fixture.
# Expected: Return actual in-memory Parquet bytes with the explicit non-null string/dictionary
# | fields and nullable signed-int64 amount schema. Exclude the row index, retain business columns,
# | and never mutate the input frame.
# Verify: Inspect the real Arrow field schema and compare a deep original frame after writing.
# | Preserve exact large integer and missing amount meanings through the subsequent independently
# | checked readback.
def parquet_bytes(frame: pd.DataFrame) -> bytes:
    """
    Exactly record_id,group,amount_cents columns: unique nonmissing string IDs, nonmissing nominal
    categorical groups and nullable Int64 amounts. Input is a small trusted fixture.

    Return actual in-memory Parquet bytes with the explicit non-null string/dictionary fields and
    nullable signed-int64 amount schema. Exclude the row index, retain business columns, and never
    mutate the input frame.
    """
    raise NotImplementedError("Implement parquet_bytes")


# Exercise 6: Enforce logical compatibility and consumer domain.
# Inputs: Small trusted Parquet bytes from the exercise and an explicit allowed category tuple. The
# | encoded-byte limit is not a sandbox for arbitrary hostile binary inputs.
# Expected: Reject incompatible field order/types/nullability or invalid business
# | identities/domains, then return the declared string/category/Int64 pandas table with a fresh row
# | index. Validate observed labels before casting and restore the consumer-declared category
# | domain.
# Verify: Use assert_frame_equal against the explicit original business table, including unknown
# | positions, exact integers and unused category metadata. Reject a readable Parquet file with an
# | incompatible integer-ID schema.
def read_parquet_payload(payload: bytes, allowed: tuple[str, ...]) -> pd.DataFrame:
    """
    Small trusted Parquet bytes from the exercise and an explicit allowed category tuple. The
    encoded-byte limit is not a sandbox for arbitrary hostile binary inputs.

    Reject incompatible field order/types/nullability or invalid business identities/domains, then
    return the declared string/category/Int64 pandas table with a fresh row index. Validate observed
    labels before casting and restore the consumer-declared category domain.
    """
    raise NotImplementedError("Implement read_parquet_payload")


def worked_examples() -> None:
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

    labels = pd.Series(["red", "purple", pd.NA], dtype="string")
    domain = pd.CategoricalDtype(categories=["red", "blue"], ordered=False)
    cast = labels.astype(domain)
    unknown = labels.notna() & ~labels.isin(domain.categories)
    assert cast.isna().tolist() == [False, True, True]
    assert unknown.tolist() == [False, True, False]
    print("Unknown observed labels:", labels[unknown].tolist())


if __name__ == "__main__":
    worked_examples()
    print("Examples passed. Implement and verify the six separate task functions.")
