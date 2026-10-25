"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""


def fused_reference(values, scale=2.0, bias=1.0):
    return [max(0.0, scale * x + bias) for x in values]


assert fused_reference([-2, 0, 3]) == [0, 1, 7]
assert fused_reference([]) == []
print("CPU custom-op oracle:", fused_reference([-2, 0, 3]))
