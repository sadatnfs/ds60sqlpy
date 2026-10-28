"""A real small causal Transformer with explicit full and cached inference."""

from __future__ import annotations

import importlib
import math
from dataclasses import asdict, dataclass
from typing import Any

Cache = list[tuple[Any, Any]]


@dataclass(frozen=True)
class ModelConfig:
    vocab_size: int
    context: int = 96
    width: int = 32
    heads: int = 4
    layers: int = 2
    expansion: int = 64

    def __post_init__(self) -> None:
        if (
            any(type(value) is not int for value in asdict(self).values())
            or not 258 <= self.vocab_size <= 322
            or not 16 <= self.context <= 256
            or not 16 <= self.width <= 128
            or not 1 <= self.heads <= 8
            or self.width % self.heads
            or not 1 <= self.layers <= 4
            or not self.width <= self.expansion <= 4 * self.width
        ):
            raise ValueError("Model dimensions exceed the bounded workshop contract")

    @classmethod
    def from_record(cls, value: Any) -> ModelConfig:
        if not isinstance(value, dict) or set(value) != set(cls.__dataclass_fields__):
            raise ValueError("Unknown model configuration fields")
        return cls(**value)


class TinyTransformer:
    """Compose registered Torch modules; caches are inference-only tensors."""

    def __init__(self, config: ModelConfig) -> None:
        self.config = config
        self.torch = importlib.import_module("torch")
        self.functional = importlib.import_module("torch.nn.functional")
        nn = self.torch.nn
        self.parts = nn.ModuleDict(
            {
                "token": nn.Embedding(config.vocab_size, config.width),
                "position": nn.Embedding(config.context, config.width),
                "blocks": nn.ModuleList(
                    [
                        nn.ModuleDict(
                            {
                                "norm_attention": nn.LayerNorm(config.width),
                                "qkv": nn.Linear(config.width, 3 * config.width, bias=False),
                                "attention_out": nn.Linear(config.width, config.width, bias=False),
                                "norm_ffn": nn.LayerNorm(config.width),
                                "up": nn.Linear(config.width, config.expansion),
                                "down": nn.Linear(config.expansion, config.width),
                            }
                        )
                        for _ in range(config.layers)
                    ]
                ),
                "norm_final": nn.LayerNorm(config.width),
                "head": nn.Linear(config.width, config.vocab_size, bias=False),
            }
        )
        for module in self.parts.modules():
            if isinstance(module, (nn.Linear, nn.Embedding)):
                nn.init.normal_(module.weight, mean=0.0, std=0.02)
                if getattr(module, "bias", None) is not None:
                    nn.init.zeros_(module.bias)

    def eval(self) -> TinyTransformer:
        self.parts.eval()
        return self

    def to(self, device: str) -> TinyTransformer:
        self.parts.to(device=device, dtype=self.torch.float32)
        return self

    def state(self) -> dict[str, Any]:
        return dict(self.parts.state_dict())

    def _forward(self, tokens: Any, cache: Cache | None) -> tuple[Any, Cache]:
        if (
            tokens.dtype != self.torch.long
            or tokens.ndim != 2
            or tokens.shape[0] < 1
            or tokens.shape[1] < 1
        ):
            raise ValueError("Tokens must be a nonempty batch-by-time int64 tensor")
        if bool(self.torch.any(tokens < 0)) or bool(
            self.torch.any(tokens >= self.config.vocab_size)
        ):
            raise ValueError("Token ID exceeds the vocabulary")
        batch, length = tokens.shape
        prior = 0
        if cache is not None:
            if len(cache) != self.config.layers or length != 1 or self.parts.training:
                raise ValueError("Cached inference takes one new token per sequence")
            if any(
                not self.torch.is_tensor(item) or item.ndim != 4 for pair in cache for item in pair
            ):
                raise ValueError("Cache entries must be rank-four tensors")
            prior = int(cache[0][0].shape[2])
            expected = (batch, self.config.heads, prior, self.config.width // self.config.heads)
            for key, value in cache:
                if (
                    tuple(key.shape) != expected
                    or tuple(value.shape) != expected
                    or key.device != tokens.device
                    or value.device != tokens.device
                ):
                    raise ValueError("Cache shape/device does not match this request")
                if key.dtype != self.torch.float32 or value.dtype != self.torch.float32:
                    raise ValueError("Cache dtype differs from the prepared model")
        if prior + length > self.config.context:
            raise ValueError("Request exceeds the position/context budget")
        positions = self.torch.arange(prior, prior + length, device=tokens.device)
        hidden = self.parts["token"](tokens) + self.parts["position"](positions)
        result: Cache = []
        for index, block in enumerate(self.parts["blocks"]):
            normalized = block["norm_attention"](hidden)
            packed = (
                block["qkv"](normalized)
                .reshape(
                    batch, length, 3, self.config.heads, self.config.width // self.config.heads
                )
                .permute(2, 0, 3, 1, 4)
            )
            query, key, value = packed.unbind(0)
            if cache is not None:
                key = self.torch.cat((cache[index][0], key), dim=2)
                value = self.torch.cat((cache[index][1], value), dim=2)
            # A one-token cached query may attend to its entire existing prefix.
            attended = self.functional.scaled_dot_product_attention(
                query, key, value, dropout_p=0.0, is_causal=cache is None
            )
            joined = attended.transpose(1, 2).contiguous().reshape(batch, length, self.config.width)
            hidden = hidden + block["attention_out"](joined)
            hidden = hidden + block["down"](
                self.functional.gelu(block["up"](block["norm_ffn"](hidden)))
            )
            result.append((key, value))
        return self.parts["head"](self.parts["norm_final"](hidden)), result

    def logits(self, tokens: Any) -> Any:
        return self._forward(tokens, None)[0]

    def prefill(self, tokens: Any) -> tuple[Any, Cache]:
        if self.parts.training:
            raise ValueError("Set eval mode before serving")
        with self.torch.inference_mode():
            return self._forward(tokens, None)

    def decode(self, tokens: Any, cache: Cache) -> tuple[Any, Cache]:
        if not cache:
            raise ValueError("Decode requires the corresponding request's prefill cache")
        with self.torch.inference_mode():
            return self._forward(tokens, cache)

    @property
    def parameter_count(self) -> int:
        return sum(int(parameter.numel()) for parameter in self.parts.parameters())


def choose_token(logits: Any, *, temperature: float, top_k: int, generator: Any) -> int:
    torch = importlib.import_module("torch")
    if logits.ndim != 1 or not bool(torch.isfinite(logits).all()):
        raise ValueError("Sampling requires one finite vocabulary-logit vector")
    if (
        type(temperature) not in {int, float}
        or not math.isfinite(temperature)
        or not 0 <= temperature <= 2
        or 0 < temperature < 0.05
    ):
        raise ValueError("Choose greedy zero or a temperature from 0.05 through two")
    if type(top_k) is not int or not 1 <= top_k <= int(logits.numel()) - 1:
        raise ValueError("Top-k must fit the non-BOS vocabulary")
    scores = logits.clone()
    scores[256] = -torch.inf
    if temperature == 0:
        return int(torch.argmax(scores).item())
    values, indices = torch.topk(scores, top_k)
    probabilities = torch.softmax((values - values.max()) / temperature, dim=0)
    position = int(torch.multinomial(probabilities, 1, generator=generator).item())
    return int(indices[position].item())
