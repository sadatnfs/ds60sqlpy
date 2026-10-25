"""cuda-040: CPU reference only, not CUDA execution."""

chunks, upload, compute, download = 3, 2, 3, 2
serial = chunks * (upload + compute + download)
ideal = upload + compute + download + (chunks - 1) * max(upload, compute, download)
assert serial == 21 and ideal == 13
print({"synthetic_serial_ms": serial, "ideal_pipeline_ms": ideal, "measured_overlap": False})
