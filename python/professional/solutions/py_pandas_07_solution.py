"""python-pandas-07: exact identity, typed parsing and Parquet references.

Parquet examples use tiny trusted bytes created by this program. Validating a
schema after decoding is not containment for arbitrary untrusted binary files.
"""

from __future__ import annotations

import csv
import re
from io import BytesIO, StringIO

import pandas as pd  # type: ignore[import-untyped]
import pyarrow as pa
import pyarrow.parquet as pq

_INTEGER = re.compile(r"[+-]?[0-9]+\Z")
_CODE = re.compile(r"\A(?P<prefix>[A-Z]{2})-(?P<number>[0-9]{4})\Z")
_COLUMNS = ["record_id", "group", "amount_cents"]
_SCHEMA = pa.schema(
    [
        pa.field("record_id", pa.string(), nullable=False),
        pa.field("group", pa.dictionary(pa.int32(), pa.string()), nullable=False),
        pa.field("amount_cents", pa.int64(), nullable=True),
    ]
)


def _strings(values: pd.Series) -> None:
    if not isinstance(values, pd.Series) or not isinstance(values.dtype, pd.StringDtype):
        raise ValueError("Expected an explicitly typed pandas string Series")


def _domain(allowed: tuple[str, ...]) -> None:
    if (
        not isinstance(allowed, tuple)
        or not allowed
        or any(not isinstance(value, str) or not value for value in allowed)
        or len(set(allowed)) != len(allowed)
    ):
        raise ValueError("Expected a nonempty unique tuple of category strings")


# Exercise 1: Preserve identity and validate CSV structure.
def read_identity_csv(text: str) -> pd.DataFrame:
    """Preserve literal NA and leading-zero IDs; parse amounts without a float stage."""
    if not isinstance(text, str):
        raise ValueError("Expected CSV text")
    try:
        records = list(csv.reader(StringIO(text), strict=True))
    except csv.Error as error:
        raise ValueError("Malformed CSV quoting") from error
    if not records or records[0] != _COLUMNS or any(len(row) != 3 for row in records[1:]):
        raise ValueError("Every CSV record must have the three declared fields")
    frame = pd.read_csv(
        StringIO(text),
        dtype="string",
        keep_default_na=False,
        skip_blank_lines=False,
        index_col=False,
    )
    if (
        list(frame.columns) != _COLUMNS
        or frame["record_id"].eq("").any()
        or frame["record_id"].duplicated().any()
        or frame["group"].eq("").any()
    ):
        raise ValueError("Expected unique known record IDs, known groups and the declared columns")
    frame["amount_cents"] = strict_int64(frame["amount_cents"])
    return frame


# Exercise 2: Parse exact signed integer text.
def strict_int64(values: pd.Series) -> pd.Series:
    """Parse signed ASCII integer text exactly; only empty strings/NA mean missing."""
    _strings(values)
    parsed: list[int | None] = []
    for value in values:
        if value is pd.NA or value == "":
            parsed.append(None)
        elif _INTEGER.fullmatch(value) is None:
            raise ValueError("Expected integer text without decimal, exponent or whitespace")
        else:
            number = int(value)
            if not -(2**63) <= number < 2**63:
                raise ValueError("Integer text is outside signed int64 range")
            parsed.append(number)
    return pd.Series(pd.array(parsed, dtype="Int64"), index=values.index.copy(), name=values.name)


# Exercise 3: Reject unknown labels before categorical conversion.
def known_categories(values: pd.Series, allowed: tuple[str, ...]) -> pd.Series:
    """Reject unknown observed labels before converting to a nominal categorical."""
    _strings(values)
    _domain(allowed)
    if (values.notna() & ~values.isin(allowed)).any():
        raise ValueError("Observed category is outside the declared domain")
    return values.astype(pd.CategoricalDtype(categories=list(allowed), ordered=False))


# Exercise 4: Retain valid, invalid and missing text states.
def extract_codes(values: pd.Series) -> pd.DataFrame:
    """Retain valid/invalid/missing states while extracting exact ASCII code parts."""
    _strings(values)
    valid = values.str.fullmatch(_CODE, na=False)
    parts = values.str.extract(_CODE)
    state = pd.Series("invalid", index=values.index, dtype="string")
    state = state.mask(values.isna(), "missing").mask(valid, "valid")
    parts["state"] = state
    return parts


def _checked_frame(frame: pd.DataFrame) -> None:
    if not isinstance(frame, pd.DataFrame) or list(frame.columns) != _COLUMNS:
        raise ValueError("Expected exactly record_id, group, amount_cents columns")
    _strings(frame["record_id"])
    if (
        frame["record_id"].isna().any()
        or frame["record_id"].eq("").any()
        or frame["record_id"].duplicated().any()
        or not isinstance(frame["group"].dtype, pd.CategoricalDtype)
        or frame["group"].dtype.ordered
        or frame["group"].isna().any()
        or str(frame["amount_cents"].dtype) != "Int64"
    ):
        raise ValueError("Expected unique string IDs, known nominal categories and Int64 amounts")
    _domain(tuple(frame["group"].cat.categories))


# Exercise 5: Serialize real Parquet under an explicit business schema.
def parquet_bytes(frame: pd.DataFrame) -> bytes:
    """Serialize the explicit business columns and nullable schema, without row-index metadata."""
    _checked_frame(frame)
    table = pa.Table.from_pandas(frame, schema=_SCHEMA, preserve_index=False, safe=True)
    sink = BytesIO()
    pq.write_table(table, sink, compression="NONE", use_dictionary=["group"])  # type: ignore[no-untyped-call]
    return sink.getvalue()


# Exercise 6: Enforce logical compatibility and consumer domain.
def read_parquet_payload(payload: bytes, allowed: tuple[str, ...]) -> pd.DataFrame:
    """Validate logical schema/domain and restore declared pandas representations.

    Only use this exercise with tiny trusted bytes. The encoded-byte bound
    below does not bound a general Parquet decoder's memory requirements.
    """
    _domain(allowed)
    if not isinstance(payload, bytes) or not 1 <= len(payload) <= 1_000_000:
        raise ValueError("Expected a small trusted Parquet byte payload")
    table = pq.read_table(BytesIO(payload))  # type: ignore[no-untyped-call]
    if not table.schema.equals(_SCHEMA, check_metadata=False):
        raise ValueError("Parquet logical field order/types/nullability do not match the contract")
    frame = table.to_pandas()
    frame["record_id"] = frame["record_id"].astype("string")
    # Check values against the caller's declared domain before the cast. An
    # unknown category must never disappear into a newly manufactured NA.
    frame["group"] = known_categories(frame["group"].astype("string"), allowed)
    frame["amount_cents"] = frame["amount_cents"].astype("Int64")
    _checked_frame(frame)
    return frame


def verify_examples() -> None:
    source = (
        "record_id,group,amount_cents\n"
        "00017,red,9007199254740993\n"
        "NA,blue,\n"
        "00019,red,9223372036854775807\n"
    )
    frame = read_identity_csv(source)
    assert frame.record_id.tolist() == ["00017", "NA", "00019"]
    assert frame.amount_cents.iloc[0] == 9007199254740993
    assert pd.isna(frame.amount_cents.iloc[1])
    assert frame.amount_cents.iloc[2] == 2**63 - 1
    for bad in [
        "record_id,group,amount_cents\nid,red,2,3\n",
        "record_id,group,amount_cents\nid,red\n",
        "record_id,group,amount_cents\nid,red,2\n\n",
    ]:
        try:
            read_identity_csv(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("A ragged or blank CSV record changed column meaning")
    parsed = strict_int64(pd.Series([str(-(2**63)), "+0002", "", pd.NA], dtype="string"))
    assert parsed.iloc[0] == -(2**63) and parsed.iloc[1] == 2 and parsed.isna().sum() == 2
    for text in ["1.0", "1e3", " 2", "٢", str(2**63), str(-(2**63) - 1)]:
        try:
            strict_int64(pd.Series([text], dtype="string"))
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid or out-of-range integer text was accepted")
    allowed = ("red", "blue", "green")
    frame["group"] = known_categories(frame["group"], allowed)
    assert list(frame.group.cat.categories) == list(allowed)
    try:
        known_categories(pd.Series(["purple", pd.NA], dtype="string"), allowed)
    except ValueError:
        pass
    else:
        raise AssertionError("An unknown category was silently converted to missing")
    codes = extract_codes(pd.Series(["AB-0007", "bad", pd.NA, "AB-０００７"], dtype="string"))
    assert codes.state.tolist() == ["valid", "invalid", "missing", "invalid"]
    assert codes.number.iloc[0] == "0007" and codes.prefix.iloc[0] == "AB"
    assert codes.number.iloc[1:].isna().all()
    original = frame.copy(deep=True)
    payload = parquet_bytes(frame)
    restored = read_parquet_payload(payload, allowed)
    pd.testing.assert_frame_equal(restored, frame.reset_index(drop=True))
    pd.testing.assert_frame_equal(frame, original)
    wrong = BytesIO()
    pq.write_table(pa.table({"record_id": [17]}), wrong)  # type: ignore[no-untyped-call]
    try:
        read_parquet_payload(wrong.getvalue(), allowed)
    except ValueError:
        pass
    else:
        raise AssertionError("An incompatible logical schema was accepted")
    print("python-pandas-07: all six typed-I/O and domain contracts passed")


if __name__ == "__main__":
    verify_examples()
