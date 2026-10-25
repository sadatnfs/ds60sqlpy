"""Independent CPU reference with deterministic contract assertions."""

values = [1, None, 3]


def expression(x):
    return None if x is None else x * 2


expected = [2, None, 6]
assert [expression(x) for x in values] == expected
print("CPU expression parity oracle:", expected)
