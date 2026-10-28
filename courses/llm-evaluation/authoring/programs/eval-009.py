def citation_metrics(claims, links, support):
    if not claims or len(set(claims)) != len(claims):
        raise ValueError("Distinct eligible claims required")
    if len(set(links)) != len(links) or any(
        c not in claims or (c, d) not in support for c, d in links
    ):
        raise ValueError("Unjudged or duplicate link")
    if any(type(support[pair]) is not bool for pair in links):
        raise ValueError("Support judgment must be known Boolean")
    valid = [(c, d) for c, d in links if support[c, d] is True]
    return {
        "link_precision": len(valid) / len(links) if links else None,
        "claim_coverage": len({c for c, d in valid}) / len(claims),
    }


def eligible_evidence(document, cutoff, allowed):
    return document["id"] in allowed and document["published"] <= cutoff


# === EXAMPLE A ===
def worked_a():
    claims = ["c1", "c2", "c3"]
    links = [("c1", "d1"), ("c2", "d2"), ("c2", "d1")]
    support = {("c1", "d1"): True, ("c2", "d2"): True, ("c2", "d1"): False}
    result = citation_metrics(claims, links, support)
    assert result == {"link_precision": 2 / 3, "claim_coverage": 2 / 3}
    assert citation_metrics(claims, links[:1], support) == {
        "link_precision": 1.0,
        "claim_coverage": 1 / 3,
    }
    print("Citation metrics:", result)


# === EXAMPLE B ===
def worked_b():
    document = {"id": "d1-v2", "published": 12}
    assert not eligible_evidence(document, 10, {"d1-v2"})
    assert eligible_evidence(document, 12, {"d1-v2"})
    assert not eligible_evidence(document, 12, set())
    support = True
    truth = False
    assert support and not truth
    print("Faithful repetition can still be false:", support, truth)


# === EXERCISES ===
def exercise_checks():
    assert citation_metrics(["c"], [], {}) == {"link_precision": None, "claim_coverage": 0.0}
    assert citation_metrics(["c"], [("c", "d")], {("c", "d"): False}) == {
        "link_precision": 0.0,
        "claim_coverage": 0.0,
    }
    for links, support in [([("c", "d")], {}), ([("c", "d"), ("c", "d")], {("c", "d"): True})]:
        try:
            citation_metrics(["c"], links, support)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid citation accepted")
    assert not eligible_evidence({"id": "restricted", "published": 1}, 20, {"public"})
    assert eligible_evidence({"id": "public", "published": 20}, 20, {"public"})


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-009: all reference checks passed")


if __name__ == "__main__":
    main()
