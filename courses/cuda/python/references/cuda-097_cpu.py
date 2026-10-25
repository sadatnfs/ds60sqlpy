"""Independent CPU reference with deterministic contract assertions."""


def fused_reference(values, scale=2.0, bias=1.0):
    return [max(0.0, scale * x + bias) for x in values]


assert fused_reference([-2, 0, 3]) == [0, 1, 7]
assert fused_reference([]) == []
print("CPU custom-op oracle:", fused_reference([-2, 0, 3]))
