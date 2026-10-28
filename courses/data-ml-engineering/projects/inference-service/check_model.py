"""Real Torch checks for prepared synthetic assets; no network or model downloads."""

from __future__ import annotations

import argparse
import io
import json
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from serving_checkpoint import load_checkpoint, sha256, verify_cache
from serving_model import choose_token
from serving_tokenizer import BOS, canonical_json


def reject(directory: Path, message: str) -> None:
    try:
        load_checkpoint(directory)
    except (ValueError, RuntimeError):
        return
    raise AssertionError(message)


def qualify(directory: Path) -> dict[str, Any]:
    model, tokenizer, metadata = load_checkpoint(directory)
    torch = model.torch
    torch.set_num_threads(2)
    checks = verify_cache(model, tokenizer)
    with torch.inference_mode():
        for text in ("a", "é🙂", "A model learns from data."):
            ids = tokenizer.encode(text, add_bos=True)
            assert tokenizer.decode(ids) == text
            tensor = torch.tensor([ids], dtype=torch.long)
            whole, _ = model.prefill(tensor)
            prefill, cache = model.prefill(tensor[:, :1])
            fragments = [prefill]
            for position in range(1, len(ids)):
                part, cache = model.decode(tensor[:, position : position + 1], cache)
                fragments.append(part)
            torch.testing.assert_close(torch.cat(fragments, dim=1), whole, rtol=2e-5, atol=2e-5)
        try:
            model.decode(
                torch.tensor([[1]]), [(torch.zeros(2), torch.zeros(2))] * model.config.layers
            )
        except ValueError:
            pass
        else:
            raise AssertionError("Malformed cache rank reached attention")
        try:
            model.prefill(torch.zeros((1, model.config.context + 1), dtype=torch.long))
        except ValueError:
            pass
        else:
            raise AssertionError("Context overflow reached position lookup")
    logits = torch.arange(tokenizer.vocab_size, dtype=torch.float32)
    logits[BOS] = 100000
    assert choose_token(logits, temperature=0, top_k=20, generator=None) == tokenizer.vocab_size - 1
    first = torch.Generator().manual_seed(9)
    second = torch.Generator().manual_seed(9)
    a = [choose_token(logits, temperature=1, top_k=20, generator=first) for _ in range(20)]
    b = [choose_token(logits, temperature=1, top_k=20, generator=second) for _ in range(20)]
    assert a == b and BOS not in a
    original = {path.name: path.read_bytes() for path in directory.iterdir() if path.is_file()}
    with tempfile.TemporaryDirectory(prefix="ds60-model-check-") as temporary:
        copy = Path(temporary)
        for name, raw in original.items():
            (copy / name).write_bytes(raw)
        damaged = bytearray(original["weights.npz"])
        damaged[-1] ^= 1
        (copy / "weights.npz").write_bytes(damaged)
        reject(copy, "Changed checkpoint bypassed its hash")
        arrays = {name: value.detach().numpy() for name, value in model.state().items()}
        key = next(iter(arrays))
        arrays[key] = np.zeros((1,), dtype=np.float32)
        buffer = io.BytesIO()
        np.savez_compressed(buffer, **arrays)
        altered = buffer.getvalue()
        manifest = json.loads(original["manifest.json"])
        manifest["files"]["weights.npz"] = sha256(altered)
        (copy / "weights.npz").write_bytes(altered)
        (copy / "manifest.json").write_bytes(canonical_json(manifest))
        reject(copy, "Hash-consistent wrong-shape checkpoint was accepted")
    assert {
        path.name: path.read_bytes() for path in directory.iterdir() if path.is_file()
    } == original
    return {
        "model_sha256": metadata["manifest_sha256"],
        "parameters": model.parameter_count,
        "device": "cpu",
        "checks": checks,
        "additional": [
            "Unicode roundtrip",
            "several cached prefixes",
            "cache rank rejection",
            "context rejection",
            "BOS excluded",
            "private seeded sampler",
            "corruption rejection",
            "hash-consistent shape rejection",
            "original asset bytes unchanged",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(qualify(args.model), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
