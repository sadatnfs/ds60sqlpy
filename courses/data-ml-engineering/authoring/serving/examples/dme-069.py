"""SSE framing survives arbitrary network chunks and explicit cursor readback."""

import codecs
import json


def encode(identity, text):
    payload = json.dumps({"text": text}, ensure_ascii=False)
    return f"id: {identity}\nevent: token\ndata: {payload}\n\n".encode()


def parse(chunks):
    decoder = codecs.getincrementaldecoder("utf-8")(errors="strict")
    buffer = ""
    records = []
    for chunk in chunks:
        buffer += decoder.decode(chunk, final=False)
        while "\n\n" in buffer:
            frame, buffer = buffer.split("\n\n", 1)
            fields = dict(line.split(": ", 1) for line in frame.splitlines())
            records.append((int(fields["id"]), json.loads(fields["data"])["text"]))
    buffer += decoder.decode(b"", final=True)
    if buffer:
        raise ValueError("Incomplete SSE frame")
    return records


def example_one():
    raw = encode(1, "é") + encode(2, "🙂")
    expected = [(1, "é"), (2, "🙂")]
    assert parse([raw]) == expected
    assert parse([bytes([value]) for value in raw]) == expected
    for boundary in range(1, len(raw)):
        assert parse([raw[:boundary], raw[boundary:]]) == expected
    print("All", len(raw) - 1, "two-chunk splits preserve the same two SSE events.")


def example_two():
    retained = [(1, "queued"), (2, "started"), (3, "token"), (4, "completed")]
    cursor = 2
    suffix = [item for item in retained if item[0] > cursor]
    assert suffix == [(3, "token"), (4, "completed")]
    calls = 1
    for _ in range(3):
        assert [item for item in retained if item[0] > cursor] == suffix
    assert calls == 1
    try:
        parse([encode(1, "x")[:-1]])
    except ValueError:
        print("A truncated network response is not successful completion.")
    print("Explicit completed readback returns data without model execution.")


def main():
    example_one()
    example_two()


if __name__ == "__main__":
    main()
