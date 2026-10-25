"""Independent CPU reference with deterministic contract assertions."""

rows = 1_000_000
assert rows // 100 == 10000 and rows // 10 == 100000
runs = [{"backend": "CPU", "cache": "cold"}, {"backend": "GPU", "cache": "warm"}]
assert runs[0]["cache"] != runs[1]["cache"]
print("CPU benchmark worksheet: unmatched cache comparison rejected")
