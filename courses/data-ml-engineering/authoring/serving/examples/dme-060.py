"""Hash-bound safe numerical checkpoints and deliberate corruption rejection."""

import hashlib
import io
import json

import numpy as np


def load(raw, expected_hash, shape):
    if len(raw) > 10000 or hashlib.sha256(raw).hexdigest() != expected_hash:
        raise ValueError("size or hash mismatch")
    with np.load(io.BytesIO(raw), allow_pickle=False) as arrays:
        if arrays.files != ["weight"]:
            raise ValueError("unexpected parameter names")
        matrix = arrays["weight"]
        if matrix.dtype != np.float32 or matrix.shape != shape or not np.isfinite(matrix).all():
            raise ValueError("shape, dtype or finiteness mismatch")
        return matrix.copy()


def example_one():
    source = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    buffer = io.BytesIO()
    np.savez_compressed(buffer, weight=source)
    raw = buffer.getvalue()
    digest = hashlib.sha256(raw).hexdigest()
    loaded = load(raw, digest, (2, 2))
    np.testing.assert_array_equal(loaded @ np.array([2.0, 1.0]), [4.0, 10.0])
    print(json.dumps({"checkpoint_bytes": len(raw), "sha256": digest, "shape": list(loaded.shape)}))
    return raw, digest


def example_two():
    raw, digest = example_one()
    damaged = raw[:-1] + bytes([raw[-1] ^ 1])
    for contents, shape in [(damaged, (2, 2)), (raw, (4, 1))]:
        try:
            load(contents, digest, shape)
        except ValueError as error:
            print("Rejected:", error)
        else:
            raise AssertionError("Invalid checkpoint reached readiness")
    print("The full project also validates archive members and array headers before allocation.")


def main():
    example_one()
    example_two()


if __name__ == "__main__":
    main()
