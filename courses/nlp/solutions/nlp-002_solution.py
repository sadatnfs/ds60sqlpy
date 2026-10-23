"""Unicode representation and loss checks for the authored local fixture."""
from collections import defaultdict
import unicodedata as ud


def compatibility_groups(raw_values):
    groups = defaultdict(list)
    for raw in raw_values:
        groups[ud.normalize("NFKC", raw)].append(raw)
    return dict(groups)


def checked_span(raw, start, end):
    if type(start) is not int or type(end) is not int or not 0 <= start <= end <= len(raw):
        raise ValueError("Offsets must be valid code-point positions in this exact text version.")
    return raw[start:end]


def verify():
    composed, decomposed = "café", "cafe\u0301"
    # Exercise 1: lengths are observations of different representations.
    assert composed != decomposed
    assert (len(composed), len(decomposed)) == (4, 5)
    assert (len(composed.encode("utf-8")), len(decomposed.encode("utf-8"))) == (5, 6)

    # Exercise 2: canonical equivalence and idempotence.
    assert ud.normalize("NFC", composed) == ud.normalize("NFC", decomposed)
    assert ud.normalize("NFD", composed) == ud.normalize("NFD", decomposed)
    assert len(ud.normalize("NFC", decomposed)) == 4
    assert len(ud.normalize("NFD", composed)) == 5
    for form in ("NFC", "NFD", "NFKC", "NFKD"):
        for raw in (composed, decomposed, "① ﬁ Ａ", "Straße", "👩‍💻"):
            once = ud.normalize(form, raw)
            assert ud.normalize(form, once) == once

    # Exercise 3: retain the preimages of a many-to-one transformation.
    raw_values = ["1", "①", composed, decomposed]
    assert compatibility_groups(raw_values) == {"1": ["1", "①"], "café": [composed, decomposed]}
    assert raw_values == ["1", "①", composed, decomposed]

    # Exercise 4: matching forms are not lossless display forms.
    assert "Straße".casefold() == "strasse" and len("Straße".casefold()) == 7
    assert ud.normalize("NFC", "a") != ud.normalize("NFC", "\u0430")

    # Exercise 5: corruption is explicit, and original bytes survive.
    raw_bytes = b"caf\xff"
    try:
        raw_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        assert (error.start, error.end) == (3, 4)
    else:
        raise AssertionError("Invalid UTF-8 was accepted.")
    assert raw_bytes.decode("utf-8", errors="replace") == "caf\ufffd"
    assert raw_bytes == b"caf\xff"

    # Exercise 6: offsets refer to a version, not an abstract visual word.
    assert checked_span(decomposed, 0, 5) == decomposed
    normalized = ud.normalize("NFC", decomposed)
    try:
        checked_span(normalized, 0, 5)
    except ValueError:
        pass
    else:
        raise AssertionError("An offset from the wrong text version was accepted.")
    assert "Straße"[4:5] == "ß"
    assert "Straße".casefold()[4:5] == "s" != "ß".casefold()
    return {"status": "passed", "automated_exercises": 6}


if __name__ == "__main__":
    print(verify())
