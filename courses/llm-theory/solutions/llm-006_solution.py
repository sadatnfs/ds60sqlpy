from __future__ import annotations

import hashlib
import unicodedata


def encode_record(text, policy="none"):
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if policy not in {"none", "NFC"}:
        raise ValueError("policy must be none or NFC")
    normalized = text if policy == "none" else unicodedata.normalize("NFC", text)
    payload = normalized.encode("utf-8")
    return {
        "text": normalized,
        "payload": payload,
        "code_points": len(normalized),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "policy": policy,
    }


def decode_utf8(payload):
    return bytes(payload).decode("utf-8")


def verify():
    # Exercise 1: declared encoding units
    texts = ["cat", "café", "🙂"]
    assert [(len(t), len(t.encode("utf-8"))) for t in texts] == [(3, 3), (4, 5), (1, 4)]
    # Exercise 2: exact strict round trips
    for text in texts:
        assert decode_utf8(encode_record(text)["payload"]) == text
    # Exercise 3: canonical identity is a chosen policy
    composed, decomposed = "é", "e" + chr(0x0301)
    assert encode_record(composed)["sha256"] != encode_record(decomposed)["sha256"]
    assert encode_record(composed, "NFC")["sha256"] == encode_record(decomposed, "NFC")["sha256"]
    # Exercise 4: replacement cannot preserve malformed bytes
    try:
        decode_utf8(b"\xff")
    except UnicodeDecodeError:
        pass
    else:
        raise AssertionError("invalid UTF-8 accepted")
    assert b"\xff".decode("utf-8", errors="replace").encode("utf-8") != b"\xff"
    # Exercise 5: empty value and unsupported policy
    assert encode_record("")["payload"] == b"" and decode_utf8(b"") == ""
    try:
        encode_record("text", "mystery")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown normalization accepted")
    # Exercise 6: canonical grouping before partition
    docs = ["café", "cafe" + chr(0x0301), "tea"]
    assert len({encode_record(t)["sha256"] for t in docs}) == 3
    assert len({encode_record(t, "NFC")["sha256"] for t in docs}) == 2
    return {"raw_identities": 3, "NFC_identities": 2}


if __name__ == "__main__":
    print(verify())
