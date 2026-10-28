def rubric_score(criteria):
    applicable = [value for value in criteria.values() if value is not None]
    if not applicable:
        raise ValueError("No applicable rubric dimensions")
    if any(type(v) is not int or v not in (0, 1, 2) for v in applicable):
        raise ValueError("Invalid rubric label")
    return sum(applicable) / (2 * len(applicable))


def admit(criteria, access_ok):
    return rubric_score(criteria) >= 0.75 and access_ok is True


def adjudicate(records, item, label, reason):
    if type(label) is not int or label not in (0, 1, 2):
        raise ValueError("Invalid adjudication label")
    originals = [r for r in records if r["item"] == item]
    if len(originals) < 2 or not reason.strip():
        raise ValueError("Adjudication needs originals and reason")
    if len({r["rubric"] for r in originals}) != 1:
        raise ValueError("Mixed rubric versions")
    return records + [
        {
            "item": item,
            "annotator": "adjudicator",
            "label": label,
            "rubric": originals[0]["rubric"],
            "parents": [r["annotator"] for r in originals],
            "reason": reason,
        }
    ]


# === EXAMPLE A ===
def worked_a():
    criteria = {"correctness": 2, "evidence": 2, "style": 2, "format": None}
    assert rubric_score(criteria) == 1
    assert admit(criteria, True) and not admit(criteria, False)
    weaker = {"correctness": 1, "evidence": 1, "style": 2, "format": None}
    assert rubric_score(weaker) == 2 / 3
    print(
        "Applicable score:",
        rubric_score(criteria),
        "restricted answer admitted:",
        admit(criteria, False),
    )


# === EXAMPLE B ===
def worked_b():
    labels = [
        {"item": "q1", "annotator": "a", "label": 1, "rubric": "v1"},
        {"item": "q1", "annotator": "b", "label": 2, "rubric": "v1"},
    ]
    resolved = adjudicate(labels, "q1", 1, "Unit absent from numerical answer")
    assert len(labels) == 2 and len(resolved) == 3
    assert resolved[-1]["parents"] == ["a", "b"] and resolved[1]["label"] == 2
    print("Original labels retained:", [r["label"] for r in labels])


# === EXERCISES ===
def exercise_checks():
    assert rubric_score({"a": 0, "b": 2}) == 0.5
    assert rubric_score({"a": 2, "b": None}) == 1
    assert not admit({"a": 2}, None)
    for invalid in ({"a": None}, {"a": 3}, {"a": True}):
        try:
            rubric_score(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid rubric admitted")
    rows = [
        {"item": "q", "annotator": "a", "label": 1, "rubric": "v1"},
        {"item": "q", "annotator": "b", "label": 1, "rubric": "v2"},
    ]
    try:
        adjudicate(rows, "q", 1, "Versions differ")
    except ValueError:
        pass
    else:
        raise AssertionError("Mixed versions admitted")


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-003: all reference checks passed")


if __name__ == "__main__":
    main()
