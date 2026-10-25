"""cuda-010: CPU reference only, not CUDA execution."""

events = []
try:
    events.append("acquire-A")
    try:
        events.append("acquire-B-failed")
        raise RuntimeError("synthetic allocation failure")
    finally:
        events.append("release-A")
except RuntimeError:
    pass
assert events == ["acquire-A", "acquire-B-failed", "release-A"]
print(events)
