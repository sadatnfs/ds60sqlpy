"""python-pandas-01: pandas Label Alignment, Nullable Logic, and Safe Assignment.

Run the worked examples, then implement the six contracts below.
Official implementations remain in solutions/.
"""

import pandas as pd  # type: ignore[import-untyped]


def aligned_difference(left: pd.Series, right: pd.Series) -> pd.Series:
    """
    Subtract right from left after requiring unique indices and exactly the same label set.
    Preserve left index order. Reject missing or duplicate labels with ValueError; do not
    silently form a union and invent missing results.
    """
    raise NotImplementedError("Implement aligned_difference")


def assign_by_label(frame: pd.DataFrame, name: str, values: pd.Series) -> pd.DataFrame:
    """
    Return a copied frame with a column assigned from a uniquely indexed Series covering
    exactly the frame index. Preserve frame order and existing source data. Reject duplicate
    or mismatched indices rather than assigning by position.
    """
    raise NotImplementedError("Implement assign_by_label")


def nullable_positive(values: pd.Series) -> pd.Series:
    """
    Require an Int64 nullable Series and return a nullable Boolean mask for values greater
    than zero. Preserve its index and unknown entries. Reject another dtype with ValueError
    so the missing-value representation is explicit.
    """
    raise NotImplementedError("Implement nullable_positive")


def select_known_true(frame: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
    """
    Filter a uniquely indexed frame with a Boolean or nullable-Boolean Series covering the
    same unique labels. Align by label, retain only known True entries, preserve frame order
    and return a copy. Reject integer flags or mismatched labels.
    """
    raise NotImplementedError("Implement select_known_true")


def reindex_with_presence(values: pd.Series, labels: list[str]) -> pd.DataFrame:
    """
    For unique source labels and unique target labels, return a DataFrame indexed in target
    order with value and present columns. Reindex values without filling them; present
    indicates whether the label existed in the source even if its value was missing.
    """
    raise NotImplementedError("Implement reindex_with_presence")


def strict_concat(frames: list[pd.DataFrame]) -> pd.DataFrame:
    """
    Concatenate a nonempty list of frames with exactly matching column order and dtypes, and
    globally unique row indices. Reject schema differences or duplicate identities with
    ValueError. Permit an empty typed frame within the list.
    """
    raise NotImplementedError("Implement strict_concat")


def worked_examples() -> None:
    left = pd.Series([20, 10], index=["b", "a"])
    right = pd.Series([1, 2], index=["a", "b"])
    result = left - right
    assert result.to_dict() == {"a": 9, "b": 18}
    assert (left.to_numpy() - right.to_numpy()).tolist() == [19, 8]
    print("Label subtraction:", result.to_dict())

    values = pd.Series([1, pd.NA, -2], dtype="Int64", index=["a", "b", "c"])
    mask = values.gt(0)
    assert str(mask.dtype) == "boolean" and pd.isna(mask.loc["b"])
    selected = values.loc[mask.fillna(False)]
    assert selected.index.tolist() == ["a"]
    print("Known positive rows:", selected.to_dict())


if __name__ == "__main__":
    worked_examples()
    print("Worked examples passed. Complete the six task functions and their boundary checks.")

# Exercise 1: Subtract by validated identities
# Prompt: Subtract right from left after requiring unique indices and exactly the same label set.
# Preserve left index order. Reject missing or duplicate labels with ValueError; do not silently
# form a union and invent missing results.
# Expected: left b=20, a=10 and right a=1, b=2 return b=18, a=9 in that order. A right Series
# missing b or with duplicate a raises ValueError.

# Exercise 2: Assign without swapping entities
# Prompt: Return a copied frame with a column assigned from a uniquely indexed Series covering
# exactly the frame index. Preserve frame order and existing source data. Reject duplicate or
# mismatched indices rather than assigning by position.
# Expected: Frame index[b, a] and Series a=100, b=200 create column[200,100]. The original frame
# has no new column; an extra Series label c raises ValueError.

# Exercise 3: Keep unknown comparison results
# Prompt: Require an Int64 nullable Series and return a nullable Boolean mask for values greater
# than zero. Preserve its index and unknown entries. Reject another dtype with ValueError so the
# missing-value representation is explicit.
# Expected: Int64[2, NA,0,-1] gives [True, NA, False, False] with dtype boolean. A plain float
# Series is rejected; an empty Int64 Series returns empty boolean.

# Exercise 4: Apply an explicit unknown-filter policy
# Prompt: Filter a uniquely indexed frame with a Boolean or nullable-Boolean Series covering the
# same unique labels. Align by label, retain only known True entries, preserve frame order and
# return a copy. Reject integer flags or mismatched labels.
# Expected: Frame index[b, a, c] and mask a=True, b=NA, c=False retain only a. The output can be
# mutated without changing frame; Int64[1,0,1] is rejected.

# Exercise 5: Distinguish absent labels from unknown values
# Prompt: For unique source labels and unique target labels, return a DataFrame indexed in target
# order with value and present columns. Reindex values without filling them; present indicates
# whether the label existed in the source even if its value was missing.
# Expected: Source a=NA, b=5 and targets[b, a, c] yield present[True, True, False] with b value 5
# and missing a, c. Duplicate target labels raise ValueError.

# Exercise 6: Append typed batches without hiding identity conflicts
# Prompt: Concatenate a nonempty list of frames with exactly matching column order and dtypes, and
# globally unique row indices. Reject schema differences or duplicate identities with ValueError.
# Permit an empty typed frame within the list.
# Expected: Two Int64 frames indexed a and b concatenate to index[a, b] preserving Int64. Repeated
# a, reversed columns, changed dtype or an empty list is rejected.
