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


worked_a()

# Task 1: Score one level 2 criterion and one inapplicable criterion.
# Task 2: Give a response all level 2 quality labels but a failed access gate.
# Task 3: Supply Boolean True as an ordinal rubric level.
# Task 4: Adjudicate labels 1 and 2 to final label 1.
# Task 5: Combine labels from v1 and v2 without a crosswalk.
# Task 6: Write a citation-looking response whose cited passage is irrelevant.

# Implement your six changes below.
