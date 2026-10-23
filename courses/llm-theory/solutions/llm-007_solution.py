from __future__ import annotations

import hashlib
import json
from collections import Counter

END = (256,)


def byte_tokens(word):
    if not isinstance(word, str):
        raise TypeError("training words must be text")
    return [(value,) for value in word.encode("utf-8")] + [END]


def merge_pair(tokens, pair):
    output = []
    index = 0
    while index < len(tokens):
        if index + 1 < len(tokens) and (tokens[index], tokens[index + 1]) == pair:
            output.append(tokens[index] + tokens[index + 1])
            index += 2
        else:
            output.append(tokens[index])
            index += 1
    return output


def fit_bpe(words, limit):
    words = list(words)
    if not words or type(limit) is not int or limit < 0:
        raise ValueError("nonempty training collection and nonnegative integer limit required")
    corpus = [byte_tokens(word) for word in words]
    rules = []
    for _ in range(limit):
        counts = Counter(pair for word in corpus for pair in zip(word, word[1:], strict=False))
        if not counts:
            break
        maximum = max(counts.values())
        pair = min(pair for pair, count in counts.items() if count == maximum)
        rules.append(pair)
        corpus = [merge_pair(word, pair) for word in corpus]
    return rules


def encode_word(word, rules):
    tokens = byte_tokens(word)
    for pair in rules:
        tokens = merge_pair(tokens, pair)
    return tokens


def decode_tokens(tokens):
    values = [value for token in tokens for value in token]
    if not values or values[-1] != 256 or 256 in values[:-1]:
        raise ValueError("exactly one final end marker required")
    return bytes(values[:-1]).decode("utf-8")


def merge_hash(rules):
    return hashlib.sha256(json.dumps(rules, separators=(",", ":")).encode()).hexdigest()


def verify():
    # Exercise 1: deterministic tied first pair
    rules = fit_bpe(["ab", "ac"], 1)
    assert rules == [((97,), (98,))]
    assert rules == fit_bpe(["ac", "ab"], 1)
    # Exercise 2: one actual merge
    assert (
        encode_word("ab", rules) == [(97, 98), END]
        and decode_tokens(encode_word("ab", rules)) == "ab"
    )
    # Exercise 3: nonoverlapping replacement
    merged = merge_pair(byte_tokens("aaaa"), ((97,), (97,)))
    assert merged == [(97, 97), (97, 97), END] and decode_tokens(merged) == "aaaa"
    # Exercise 4: validation cannot fit a new merge
    before = merge_hash(rules)
    assert encode_word("ad", rules) == [(97,), (100,), END] and merge_hash(rules) == before
    # Exercise 5: bounded and absent fits
    assert fit_bpe(["ab"], 0) == []
    for words, limit in (([], 1), (["ab"], -1)):
        try:
            fit_bpe(words, limit)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid fit accepted")
    # Exercise 6: byte fallback preserves Unicode
    encoded = encode_word("é", rules)
    assert encoded == [(195,), (169,), END] and decode_tokens(encoded) == "é"
    return {"merges": len(rules), "merge_hash": merge_hash(rules)}


if __name__ == "__main__":
    print(verify())
