"""Functions and collection lifetime make data transformations reviewable."""


def delayed_ids(records, threshold):
    if type(threshold) is not int or threshold < 0:
        raise ValueError("Use a nonnegative integer delay threshold")
    result = []
    for record in records:
        if record["delay_minutes"] > threshold:
            result.append(record["id"])
    return result


def example_one():
    original = [
        {"id": "A", "delay_minutes": 0},
        {"id": "B", "delay_minutes": 12},
        {"id": "C", "delay_minutes": 5},
    ]
    before = [dict(record) for record in original]
    strict = delayed_ids(original, 5)
    lenient = delayed_ids(original, 15)
    assert strict == ["B"] and lenient == [] and original == before
    assert delayed_ids(original, 5) == strict
    return {
        "threshold_5_ids": strict,
        "threshold_15_ids": lenient,
        "input_unchanged": original == before,
    }


def example_two():
    iterator = (value for value in [2, 3, 1])
    first_total = sum(iterator)
    mistaken_second_total = sum(iterator)
    assert first_total == 6 and mistaken_second_total == 0
    fresh_iterator = iter([2, 3, 1])
    materialized = list(fresh_iterator)
    assert sum(materialized) == sum(materialized) == 6

    # A fresh collection is an explicit policy, not a hidden shared default.
    def append_identity(identity, previous=None):
        updated = [] if previous is None else list(previous)
        updated.append(identity)
        return updated

    a, b = append_identity("A"), append_identity("B")
    assert a == ["A"] and b == ["B"]
    previous = ["A"]
    updated = append_identity("B", previous)
    assert previous == ["A"] and updated == ["A", "B"]
    return {
        "first_iterator_total": first_total,
        "exhausted_iterator_total": mistaken_second_total,
        "repeatable_list_total": sum(materialized),
        "separate_outputs": [a, b],
    }


def main():
    print("Explicit input/output function:", example_one())
    print("Collection lifetime changes the result:", example_two())


if __name__ == "__main__":
    main()
