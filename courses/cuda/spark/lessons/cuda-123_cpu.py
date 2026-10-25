"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

rows = 1_000_000
assert rows // 100 == 10000 and rows // 10 == 100000
runs = [{"backend": "CPU", "cache": "cold"}, {"backend": "GPU", "cache": "warm"}]
assert runs[0]["cache"] != runs[1]["cache"]
print("CPU benchmark worksheet: unmatched cache comparison rejected")
