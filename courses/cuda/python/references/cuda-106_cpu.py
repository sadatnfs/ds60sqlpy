"""Independent CPU reference with deterministic contract assertions."""

n, tile = 10, 4
blocks = [list(range(start, min(start + tile, n))) for start in range(0, n, tile)]
assert blocks == [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]
assert [i for block in blocks for i in block] == list(range(n))
print("CPU tile model:", blocks)
