"""Small exact byte-BPE merges and incremental UTF-8 decoding."""

import codecs


def replace(tokens, pair, identity):
    result = []
    index = 0
    while index < len(tokens):
        if tuple(tokens[index : index + 2]) == pair:
            result.append(identity)
            index += 2
        else:
            result.append(tokens[index])
            index += 1
    return result


def example_one():
    pieces = {value: bytes([value]) for value in range(256)}
    pieces[258] = b"ab"
    pieces[259] = b"aba"
    tokens = list(b"aba ab")
    for pair, identity in [((97, 98), 258), ((258, 97), 259)]:
        tokens = replace(tokens, pair, identity)
    assert tokens == [259, 32, 258]
    assert b"".join(pieces[value] for value in tokens) == b"aba ab"
    print("Merge-ranked tokens:", tokens, "byte lengths:", [len(pieces[value]) for value in tokens])
    assert replace([97, 97, 97], (97, 97), 258) == [258, 97]


def example_two():
    data = "é🙂".encode()
    decoder = codecs.getincrementaldecoder("utf-8")(errors="strict")
    deltas = [decoder.decode(bytes([value]), final=False) for value in data]
    deltas.append(decoder.decode(b"", final=True))
    assert len(data) == 6 and len("é🙂") == 2
    assert deltas == ["", "é", "", "", "", "🙂", ""]
    assert "".join(deltas) == "é🙂"
    print("Byte deliveries:", list(data), "text deltas:", deltas)
    strict = codecs.getincrementaldecoder("utf-8")(errors="strict")
    try:
        strict.decode(b"\xff", final=True)
    except UnicodeDecodeError:
        print(
            "Invalid UTF-8 rejected; a serving display may explicitly choose replacement instead."
        )


def main():
    example_one()
    example_two()


if __name__ == "__main__":
    main()
