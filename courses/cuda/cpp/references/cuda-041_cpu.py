"""cuda-041: CPU reference only, not CUDA execution."""

events = [
    "allocate_A",
    "write_A",
    "ready",
    "wait_ready_B",
    "read_B",
    "done",
    "wait_done_A",
    "free_A",
]
assert events.index("read_B") < events.index("free_A")
reserved_mib, live_mib = 64, 0
assert reserved_mib >= live_mib
print({"lifetime_order": events, "reserved_MiB": reserved_mib, "live_MiB": live_mib})
