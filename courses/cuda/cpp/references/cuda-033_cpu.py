"""cuda-033: CPU reference only, not CUDA execution."""

useful, transferred = 400, 1600
assert useful / transferred == 0.25
assert 12_000_000 / 0.0002 == 60_000_000_000
print({"useful_fraction": useful / transferred, "useful_GB_per_second": 60})
