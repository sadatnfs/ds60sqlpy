"""cuda-033: CPU reference only, not CUDA execution."""

useful, transferred = 400, 1600
assert useful / transferred == 0.25
print({"useful_fraction": useful / transferred})
assert 12_000_000 / 0.0002 == 60_000_000_000
