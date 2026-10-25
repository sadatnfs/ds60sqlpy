"""Independent CPU reference with deterministic contract assertions."""

edges = [("upload", "transform"), ("transform", "download")]
order = ["upload", "transform", "download"]
positions = {name: i for i, name in enumerate(order)}
assert all(positions[a] < positions[b] for a, b in edges)
bad = ["download", "upload", "transform"]
assert not all(bad.index(a) < bad.index(b) for a, b in edges)
print("CPU dependency model: ordered pipeline accepted; premature download rejected")
