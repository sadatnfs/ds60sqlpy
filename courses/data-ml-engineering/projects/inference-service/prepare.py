"""Train and verify original tiny model assets inside an owned Docker project."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import time
from pathlib import Path

from serving_checkpoint import load_checkpoint, save_checkpoint, verify_cache
from serving_model import ModelConfig, TinyTransformer
from serving_tokenizer import BOS, EOS, fit_tokenizer


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, default=Path(__file__).with_name("corpus.txt"))
    parser.add_argument("--steps", type=int, default=256)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error("Existing model assets are never overwritten; choose a new owned directory")
    if not 32 <= args.steps <= 512:
        parser.error("Training steps must be between 32 and 512")
    raw = args.corpus.read_bytes()
    if not 100 <= len(raw) <= 100_000:
        parser.error("Use a bounded local corpus")
    text = raw.decode("utf-8", errors="strict")
    torch = importlib.import_module("torch")
    torch.set_num_threads(2)
    torch.manual_seed(314159)
    torch.use_deterministic_algorithms(True)
    tokenizer = fit_tokenizer(text, 48)
    config = ModelConfig(tokenizer.vocab_size)
    model = TinyTransformer(config)
    sequence = []
    for line in text.splitlines():
        if line.strip():
            sequence.extend([BOS, *tokenizer.encode(line.strip()), EOS])
    data = torch.tensor(sequence, dtype=torch.long)
    window = 48
    if len(data) < window + 2:
        parser.error("Corpus does not provide a complete training window")
    generator = torch.Generator().manual_seed(2718)
    optimizer = torch.optim.AdamW(model.parts.parameters(), lr=0.005, weight_decay=0.01)
    losses = []
    started = time.perf_counter()
    for step in range(args.steps):
        starts = torch.randint(0, len(data) - window - 1, (8,), generator=generator)
        inputs = torch.stack([data[index : index + window] for index in starts])
        targets = torch.stack([data[index + 1 : index + window + 1] for index in starts])
        optimizer.zero_grad(set_to_none=True)
        logits = model.logits(inputs)
        loss = torch.nn.functional.cross_entropy(
            logits.reshape(-1, config.vocab_size), targets.reshape(-1)
        )
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parts.parameters(), 1.0)
        optimizer.step()
        losses.append(float(loss.detach()))
        if step == 0 or (step + 1) % 64 == 0:
            print(json.dumps({"training_step": step + 1, "cross_entropy": losses[-1]}), flush=True)
    elapsed = time.perf_counter() - started
    if not losses[-1] < losses[0]:
        raise RuntimeError("The declared tiny training run did not reduce its objective")
    model.eval()
    checks = verify_cache(model, tokenizer)
    training = {
        "corpus_sha256": hashlib.sha256(raw).hexdigest(),
        "steps": args.steps,
        "initial_loss": losses[0],
        "final_loss": losses[-1],
        "wall_seconds": elapsed,
        "device": "cpu",
        "torch_version": torch.__version__,
        "seed": 314159,
        "checks": checks,
    }
    manifest = save_checkpoint(args.output, model, tokenizer, training)
    restored, saved_tokenizer, _ = load_checkpoint(args.output)
    assert saved_tokenizer == tokenizer
    restored_checks = verify_cache(restored, tokenizer)
    print(
        json.dumps(
            {
                "prepared": True,
                "parameters": manifest["parameter_count"],
                "vocabulary": tokenizer.vocab_size,
                "checks": restored_checks,
                "claim": manifest["claim"],
            }
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
