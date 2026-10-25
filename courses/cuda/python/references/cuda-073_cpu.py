"""Independent CPU reference with deterministic contract assertions."""


def affine_reference(values, scale):
    return [scale * x for x in values]


assert affine_reference([1, -2, 3], 2) == [2, -4, 6]
assert affine_reference([], 2) == []
print("CPU kernel oracle:", affine_reference([1, -2, 3], 2))
