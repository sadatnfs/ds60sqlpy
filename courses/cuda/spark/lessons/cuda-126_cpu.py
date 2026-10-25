"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

events = [("task1", "write", "key-7"), ("task1-retry", "write", "key-7")]
raw = len(events)
idempotent = len({key for _, _, key in events})
assert raw == 2 and idempotent == 1
print("CPU retry model:", raw, "attempts;", idempotent, "logical keys")
