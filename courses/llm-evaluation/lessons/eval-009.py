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


worked_a()

# Task 1: Cite only c1 correctly among three eligible claims.
# Task 2: Evaluate an answer with one eligible claim and no links.
# Task 3: Add a link with no adjudicated support label.
# Task 4: Repeat an identical claim-document link.
# Task 5: Evaluate a day 10 answer with a day 12 document.
# Task 6: Construct a claim that accurately quotes an erroneous source.

# Implement your six changes below.
