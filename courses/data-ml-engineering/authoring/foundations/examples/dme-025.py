"""A generation-based object-store mechanism model, not an S3 client."""

import hashlib
from threading import Lock


class Conflict(ValueError):
    pass


class Store:
    def __init__(self):
        self.objects = {}
        self.history = {}
        self.generation = 0
        self.lock = Lock()

    def put(self, key, body, expected_generation):
        if not isinstance(key, str) or not key or not isinstance(body, bytes) or len(body) > 4096:
            raise ValueError("Use a named object with bounded bytes")
        with self.lock:
            current = self.objects.get(key)
            observed = None if current is None else current[0]
            if observed != expected_generation:
                raise Conflict("Conditional write observed a different generation")
            self.generation += 1
            version = (self.generation, body, hashlib.sha256(body).hexdigest())
            self.objects[key] = version
            self.history[(key, version[0])] = version
            return version[0]

    def get(self, key, generation=None):
        with self.lock:
            return self.objects[key] if generation is None else self.history[(key, generation)]


def example_one():
    store = Store()
    first = store.put("products/v1", b'{"packages":6}', None)
    pointer = store.put("accepted", b"products/v1", None)
    data_key = store.get("accepted")[1].decode()
    accepted = store.get(data_key)
    assert accepted[0] == first and accepted[1] == b'{"packages":6}'
    second = store.put("products/v2", b'{"packages":9}', None)
    assert store.get("accepted")[1] == b"products/v1"
    store.put("accepted", b"products/v2", pointer)
    assert store.get("products/v1", first)[1] == b'{"packages":6}'
    return {
        "first_data_generation": first,
        "second_data_generation": second,
        "accepted_key": store.get("accepted")[1].decode(),
        "prior_version_retained": True,
    }


def example_two():
    store = Store()
    generation = store.put("accepted", b"v1", None)
    first_reader, second_reader = store.get("accepted"), store.get("accepted")
    assert first_reader[0] == second_reader[0] == generation
    store.put("accepted", b"v2", first_reader[0])
    try:
        store.put("accepted", b"v3", second_reader[0])
    except Conflict:
        pass
    else:
        raise AssertionError("A stale writer overwrote the accepted version")
    latest = store.get("accepted")
    store.put("accepted", b"v1", latest[0])
    returned = store.get("accepted")
    assert returned[2] == first_reader[2] and returned[0] != first_reader[0]
    try:
        store.put("accepted", b"v3", first_reader[0])
    except Conflict:
        pass
    else:
        raise AssertionError("A stale generation survived a return to identical bytes")
    return {
        "stale_writer_rejected": True,
        "same_bytes_same_digest": True,
        "same_bytes_different_generation": [first_reader[0], returned[0]],
        "scope": "local generation-CAS model; no cloud API was called",
    }


def main():
    print("Separate preparation from conditional publication:", example_one())
    print("Conflicts and the ABA boundary:", example_two())


if __name__ == "__main__":
    main()
