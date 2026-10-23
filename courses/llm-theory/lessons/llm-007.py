"""llm-007: predict from the companion guide, then modify an owned copy."""

from collections import Counter

corpus = [[(97,), (98,), (256,)], [(97,), (99,), (256,)]]
counts = Counter(pair for word in corpus for pair in zip(word, word[1:], strict=False))
maximum = max(counts.values())
pair = min(pair for pair, count in counts.items() if count == maximum)
assert pair == ((97,), (98,))


def merge_once(tokens, chosen):
    result, index = [], 0
    while index < len(tokens):
        if index + 1 < len(tokens) and (tokens[index], tokens[index + 1]) == chosen:
            result.append(tokens[index] + tokens[index + 1])
            index += 2
        else:
            result.append(tokens[index])
            index += 1
    return result


assert merge_once(corpus[0], pair) == [(97, 98), (256,)]
print(pair, merge_once(corpus[0], pair))

rules = [pair]
before = tuple(rules)
validation = [(97,), (100,), (256,)]
for chosen in rules:
    validation = merge_once(validation, chosen)
assert validation == [(97,), (100,), (256,)]
assert tuple(rules) == before
assert bytes(value for token in validation[:-1] for value in token).decode("utf-8") == "ad"
print(validation)

# Exercise 1: Trace the first candidate counts
# Use ab and ac as training words and calculate every neighboring pair count before a
# merge.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 2: Construct a one-step trainer
# Implement fit_bpe(words,limit) and learn exactly one merge from ab and ac.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 3: Diagnose overlapping replacement
# Apply the a+a pair to aaaa. Consume matched positions once from left to right.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 4: Freeze validation encoding
# Encode ad with the one-rule tokenizer and compare its serialized merge hash before and
# after.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 5: Handle a bounded or absent fit
# Use merge limit zero, an empty training collection and a negative limit.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 6: Transfer to UTF-8 text
# Encode and decode é with the frozen one-rule tokenizer. Explain why its two bytes are
# not two Unicode characters.
# Add your attempt and keep its observed values or exception beside your prediction.
