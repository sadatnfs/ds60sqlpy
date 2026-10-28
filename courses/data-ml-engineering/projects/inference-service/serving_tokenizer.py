"""Original bounded byte-BPE tokenizer, with no downloaded vocabulary."""

from __future__ import annotations

import codecs
import json
from collections import Counter
from dataclasses import dataclass
from typing import Any

BOS = 256
EOS = 257
MAX_MERGES = 64
MAX_PIECE_BYTES = 64


def replace_pair(tokens: list[int], pair: tuple[int, int], replacement: int) -> list[int]:
    result: list[int] = []
    position = 0
    while position < len(tokens):
        if position + 1 < len(tokens) and (tokens[position], tokens[position + 1]) == pair:
            result.append(replacement)
            position += 2
        else:
            result.append(tokens[position])
            position += 1
    return result


@dataclass(frozen=True)
class Tokenizer:
    merges: tuple[tuple[int, int], ...] = ()

    def __post_init__(self) -> None:
        if len(self.merges) > MAX_MERGES:
            raise ValueError("Tokenizer merge count exceeds the prepared contract")
        pieces = [bytes([value]) for value in range(256)] + [b"", b""]
        seen: set[tuple[int, int]] = set()
        for pair in self.merges:
            if (
                len(pair) != 2
                or any(
                    type(value) is not int or value < 0 or value >= len(pieces) for value in pair
                )
                or BOS in pair
                or EOS in pair
                or pair in seen
            ):
                raise ValueError("Invalid or cyclic tokenizer merge")
            combined = pieces[pair[0]] + pieces[pair[1]]
            if not combined or len(combined) > MAX_PIECE_BYTES:
                raise ValueError("Tokenizer piece exceeds the byte limit")
            pieces.append(combined)
            seen.add(pair)

    @property
    def vocab_size(self) -> int:
        return 258 + len(self.merges)

    def pieces(self) -> tuple[bytes, ...]:
        result = [bytes([value]) for value in range(256)] + [b"", b""]
        for left, right in self.merges:
            result.append(result[left] + result[right])
        return tuple(result)

    def encode(self, text: str, *, add_bos: bool = False) -> list[int]:
        tokens = list(text.encode("utf-8", errors="strict"))
        for rank, pair in enumerate(self.merges, 258):
            tokens = replace_pair(tokens, pair, rank)
        return ([BOS] if add_bos else []) + tokens

    def token_bytes(self, identity: int) -> bytes:
        if type(identity) is not int or not 0 <= identity < self.vocab_size:
            raise ValueError("Unknown tokenizer ID")
        return self.pieces()[identity]

    def decode(self, identities: list[int], *, errors: str = "strict") -> str:
        return b"".join(self.token_bytes(identity) for identity in identities).decode(
            "utf-8", errors=errors
        )

    def record(self) -> dict[str, Any]:
        return {
            "format": "ds60-byte-bpe-v1",
            "normalization": "none",
            "bos_id": BOS,
            "eos_id": EOS,
            "merges": [list(pair) for pair in self.merges],
        }

    @classmethod
    def from_record(cls, value: Any) -> Tokenizer:
        if (
            not isinstance(value, dict)
            or set(value) != {"format", "normalization", "bos_id", "eos_id", "merges"}
            or value["format"] != "ds60-byte-bpe-v1"
            or value["normalization"] != "none"
            or type(value["bos_id"]) is not int
            or value["bos_id"] != BOS
            or type(value["eos_id"]) is not int
            or value["eos_id"] != EOS
            or not isinstance(value["merges"], list)
            or any(not isinstance(pair, list) or len(pair) != 2 for pair in value["merges"])
        ):
            raise ValueError("Tokenizer metadata does not match its format")
        return cls(tuple((pair[0], pair[1]) for pair in value["merges"]))


def fit_tokenizer(text: str, merge_count: int = 32) -> Tokenizer:
    if type(merge_count) is not int or not 0 <= merge_count <= MAX_MERGES:
        raise ValueError("Choose a bounded tokenizer merge count")
    tokens = list(text.encode("utf-8"))
    if not tokens or len(tokens) > 100_000:
        raise ValueError("Use a nonempty bounded local training corpus")
    merges: list[tuple[int, int]] = []
    pieces = [bytes([value]) for value in range(256)] + [b"", b""]
    for identity in range(258, 258 + merge_count):
        counts = Counter(zip(tokens, tokens[1:], strict=False))
        candidates = [
            pair
            for pair, count in counts.items()
            if count >= 2 and len(pieces[pair[0]] + pieces[pair[1]]) <= MAX_PIECE_BYTES
        ]
        if not candidates:
            break
        pair = min(candidates, key=lambda item: (-counts[item], item))
        merges.append(pair)
        pieces.append(pieces[pair[0]] + pieces[pair[1]])
        tokens = replace_pair(tokens, pair, identity)
    return Tokenizer(tuple(merges))


class TextStream:
    """Decode complete UTF-8 characters and hold possible stop-string prefixes."""

    def __init__(self, stops: tuple[str, ...] = ()) -> None:
        if (
            len(stops) > 4
            or len(set(stops)) != len(stops)
            or any(not isinstance(stop, str) or not 1 <= len(stop) <= 32 for stop in stops)
        ):
            raise ValueError("Use up to four distinct bounded stop strings")
        self.stops = stops
        self.decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        self.pending = ""
        self.stopped = False
        self.replacement_characters = 0

    def feed(self, data: bytes, *, final: bool = False) -> str:
        if self.stopped:
            return ""
        text = self.decoder.decode(data, final=final)
        self.replacement_characters += text.count("\ufffd")
        self.pending += text
        matches = [(self.pending.find(stop), rank) for rank, stop in enumerate(self.stops)]
        positions = [(position, rank) for position, rank in matches if position >= 0]
        if positions:
            position, _ = min(positions)
            output = self.pending[:position]
            self.pending = ""
            self.stopped = True
            return output
        hold = 0
        if not final:
            for stop in self.stops:
                for length in range(1, len(stop)):
                    if self.pending.endswith(stop[:length]):
                        hold = max(hold, length)
        output = self.pending[:-hold] if hold else self.pending
        self.pending = self.pending[-hold:] if hold else ""
        return output


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
        + "\n"
    ).encode()
