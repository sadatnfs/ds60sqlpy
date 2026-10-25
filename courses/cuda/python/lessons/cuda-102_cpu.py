"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

layers, batch, seq, heads, dim, width = 2, 1, 16, 4, 8, 2
cache = 2 * layers * batch * seq * heads * dim * width
assert cache == 4096
assert 2 * layers * batch * (2 * seq) * heads * dim * width == 8192
print("CPU KV-cache ledger:", cache, "bytes")
