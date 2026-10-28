"""Startup-loaded real Transformer inference; transport delays are not compute time."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from serving_checkpoint import load_checkpoint, verify_cache
from serving_contract import RequestSpec
from serving_model import choose_token
from serving_tokenizer import EOS, TextStream


class GenerationCancelled(RuntimeError):
    pass


class InferenceEngine:
    def __init__(
        self, model_directory: Path, device: str = "cpu", pacing_seconds: float = 0
    ) -> None:
        if device not in {"cpu", "cuda:0"}:
            raise ValueError(
                "Choose cpu or explicitly prepared cuda:0; devices never fall back silently"
            )
        if not 0 <= pacing_seconds <= 0.2:
            raise ValueError("Demonstration pacing must be zero through 0.2 seconds")
        started = time.perf_counter()
        self.model, self.tokenizer, self.manifest = load_checkpoint(model_directory)
        self.torch = self.model.torch
        self.torch.set_num_threads(2)
        if device == "cuda:0":
            if not self.torch.cuda.is_available():
                raise RuntimeError(
                    "CUDA was explicitly requested but this image/device cannot execute it; "
                    "use cpu or prepare a separate supported NVIDIA environment"
                )
            probe = self.torch.arange(16, device=device, dtype=self.torch.float32)
            actual = (probe * 2).cpu()
            self.torch.cuda.synchronize()
            if not self.torch.equal(actual, self.torch.arange(16, dtype=self.torch.float32) * 2):
                raise RuntimeError("CUDA allocation/kernel/readback probe failed")
        self.model.to(device).eval()
        self.device = device
        self.pacing_seconds = pacing_seconds
        self.load_seconds = time.perf_counter() - started
        warm = time.perf_counter()
        self.cache_checks = verify_cache(self.model, self.tokenizer)
        self.warm_seconds = time.perf_counter() - warm
        self.calls = 0
        self.context = self.model.config.context
        self.model_hash = self.manifest["manifest_sha256"]
        self.tokenizer_hash = self.manifest["files"]["tokenizer.json"]

    def synchronize(self) -> None:
        if self.device.startswith("cuda"):
            self.torch.cuda.synchronize()

    def describe(self) -> dict[str, Any]:
        return {
            "device": self.device,
            "model_sha256": self.model_hash,
            "tokenizer_sha256": self.tokenizer_hash,
            "context": self.context,
            "parameters": self.model.parameter_count,
            "vocabulary": self.tokenizer.vocab_size,
            "load_seconds": self.load_seconds,
            "warm_seconds": self.warm_seconds,
            "cache_checks": self.cache_checks,
            "generation_calls": self.calls,
            "pacing_seconds": self.pacing_seconds,
            "claim": (
                "Real locally trained synthetic Transformer; this is not evidence "
                "of pretrained-model capability or production capacity."
            ),
        }

    def generate(
        self,
        spec: RequestSpec,
        tokens: list[int],
        cancelled: threading.Event,
        emit: Callable[[dict[str, Any]], None],
    ) -> dict[str, Any]:
        self.calls += 1
        started = time.perf_counter()
        generator = self.torch.Generator(device=self.device).manual_seed(spec.seed)
        decoder = TextStream(spec.stops)
        text = ""
        compute_seconds = 0.0
        prefill_seconds = 0.0
        first_token_seconds = 0.0
        pacing_seconds = 0.0
        output_count = 0
        reason = "max_new_tokens"
        logits: Any = None
        cache: Any = None
        previous = 0
        try:
            for index in range(spec.max_new_tokens):
                if cancelled.is_set():
                    raise GenerationCancelled("cancelled")
                self.synchronize()
                compute_start = time.perf_counter()
                if index == 0:
                    source = self.torch.tensor([tokens], dtype=self.torch.long, device=self.device)
                    logits, cache = self.model.prefill(source)
                else:
                    source = self.torch.tensor(
                        [[previous]], dtype=self.torch.long, device=self.device
                    )
                    logits, cache = self.model.decode(source, cache)
                identity = choose_token(
                    logits[0, -1],
                    temperature=spec.temperature,
                    top_k=spec.top_k,
                    generator=generator,
                )
                self.synchronize()
                duration = time.perf_counter() - compute_start
                compute_seconds += duration
                if index == 0:
                    prefill_seconds = duration
                    first_token_seconds = time.perf_counter() - started
                if cancelled.is_set():
                    raise GenerationCancelled("cancelled")
                raw = self.tokenizer.token_bytes(identity)
                delta = decoder.feed(raw)
                text += delta
                output_count += 1
                emit(
                    {
                        "index": index,
                        "token_id": identity,
                        "bytes_hex": raw.hex(),
                        "text": delta,
                        "compute_seconds": duration,
                    }
                )
                previous = identity
                if identity == EOS:
                    reason = "eos"
                    break
                if decoder.stopped:
                    reason = "stop_string"
                    break
                if self.pacing_seconds:
                    pacing_start = time.perf_counter()
                    interrupted = cancelled.wait(self.pacing_seconds)
                    pacing_seconds += time.perf_counter() - pacing_start
                    if interrupted:
                        raise GenerationCancelled("cancelled")
            text += decoder.feed(b"", final=True)
            status = "completed"
        except GenerationCancelled as exc:
            status = "cancelled"
            reason = str(exc)
        finally:
            del cache, logits
        return {
            "status": status,
            "reason": reason,
            "text": text,
            "metrics": {
                "prompt_tokens": len(tokens),
                "output_tokens": output_count,
                "compute_seconds": compute_seconds,
                "prefill_and_first_sampling_seconds": prefill_seconds,
                "first_model_token_seconds": first_token_seconds,
                "generation_wall_seconds": time.perf_counter() - started,
                "demonstration_pacing_seconds": pacing_seconds,
                "replacement_characters": decoder.replacement_characters,
            },
        }
