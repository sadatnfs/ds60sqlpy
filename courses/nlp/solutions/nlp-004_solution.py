"""Character-based word BPE demonstration, not a pretrained LLM tokenizer."""
from collections import Counter
import re

END = "</w>"


def merge_pair(tokens, pair):
    result = []
    i = 0
    while i < len(tokens):
        if i + 1 < len(tokens) and (tokens[i], tokens[i + 1]) == pair:
            result.append(tokens[i] + tokens[i + 1])
            i += 2
        else:
            result.append(tokens[i])
            i += 1
    return tuple(result)


def pair_counts(state, words):
    counts = Counter()
    for word, tokens in state.items():
        for pair in zip(tokens, tokens[1:]):
            counts[pair] += words[word]
    return counts


def train_bpe(words, steps):
    if type(steps) is not int or not 0 <= steps <= 20 or not words:
        raise ValueError("Use a nonempty tiny corpus and 0..20 merges.")
    for word, frequency in words.items():
        if not isinstance(word, str) or not re.fullmatch(r"[a-z]+", word):
            raise ValueError("This teaching corpus accepts lowercase ASCII words only.")
        if type(frequency) is not int or frequency < 1:
            raise ValueError("Frequencies must be positive integer counts.")
    state = {word: tuple(word) + (END,) for word in words}
    merges = []
    for _ in range(steps):
        counts = pair_counts(state, words)
        if not counts:
            break
        pair = min(counts, key=lambda candidate: (-counts[candidate], candidate))
        merges.append(pair)
        state = {word: merge_pair(tokens, pair) for word, tokens in state.items()}
    model = {"merges": tuple(merges), "alphabet": frozenset("".join(words))}
    return model, state


def encode(word, model):
    if not isinstance(word, str) or not re.fullmatch(r"[a-z]+", word):
        raise ValueError("Expected a lowercase ASCII word.")
    unknown = set(word) - model["alphabet"]
    if unknown:
        raise ValueError("Unknown symbols: " + ",".join(sorted(unknown)))
    tokens = tuple(word) + (END,)
    for pair in model["merges"]:
        tokens = merge_pair(tokens, pair)
    return tokens


def decode(tokens):
    joined = "".join(tokens)
    if not joined.endswith(END) or END in joined[:-len(END)]:
        raise ValueError("Expected exactly one terminal word marker.")
    return joined[:-len(END)]


def verify():
    # Exercise 1: different segmentation policies expose different units.
    text = "can't pay."
    assert text.split() == ["can't", "pay."]
    assert re.findall(r"\w+|[^\w\s]", text) == ["can", "'", "t", "pay", "."]
    assert re.findall(r"\w+(?:'\w+)*|[^\w\s]", text) == ["can't", "pay", "."]
    matches = list(re.finditer(r"\w+(?:'\w+)*|[^\w\s]", text))
    assert matches[1].span() == (6, 9)
    assert all(text[m.start():m.end()] == m.group(0) for m in matches)

    # Exercise 2: counts use corpus frequency, not only word types.
    words = {"low": 3, "lower": 1}
    counts = pair_counts({word: tuple(word)+(END,) for word in words}, words)
    assert counts[("l", "o")] == counts[("o", "w")] == 4
    assert counts[("w", END)] == 3

    # Exercise 3: no overlapping reuse of a symbol.
    assert merge_pair(("a", "a", "a", END), ("a", "a")) == ("aa", "a", END)
    assert decode(("aa", "a", END)) == "aaa"

    # Exercise 4: explicit ties produce reproducible training.
    model, state = train_bpe(words, 2)
    assert model["merges"] == (("l", "o"), ("lo", "w"))
    assert state == {"low": ("low", END), "lower": ("low", "e", "r", END)}
    reversed_model, reversed_state = train_bpe(dict(reversed(list(words.items()))), 2)
    assert model == reversed_model and state == reversed_state

    # Exercise 5: inference applies frozen rules and rejects unknown characters.
    before = model["merges"]
    assert encode("lower", model) == ("low", "e", "r", END)
    assert encode("row", model) == ("r", "o", "w", END)
    for word in ("low", "lower", "row"):
        assert decode(encode(word, model)) == word
    try:
        encode("slow", model)
    except ValueError as error:
        assert "Unknown symbols" in str(error)
    else:
        raise AssertionError("An unseen character was silently accepted.")
    assert model["merges"] == before

    # Exercise 6 is an explained compatibility contract, not an automatic model-quality score.
    return {"status": "passed", "automated_exercises": 5, "written_exercises": 1}


if __name__ == "__main__":
    print(verify())
