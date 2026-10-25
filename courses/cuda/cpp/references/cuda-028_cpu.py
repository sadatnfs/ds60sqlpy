"""cuda-028: CPU reference only, not CUDA execution."""

events = ["payload_write", "release_flag", "acquire_flag", "payload_read"]
positions = {name: i for i, name in enumerate(events)}
assert (
    positions["payload_write"]
    < positions["release_flag"]
    < positions["acquire_flag"]
    < positions["payload_read"]
)
print({"conceptual_happens_before": events, "GPU_memory_model_test": False})
