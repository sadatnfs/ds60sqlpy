"""llm-applied-010: bounded local reference checks. No network or persistent data writes."""

from collections import deque


def rewrite(query, synonyms):
    return " ".join(synonyms.get(token, token) for token in query.lower().split())


def walk(start, graph, max_hops):
    if type(max_hops) is not int or max_hops < 0:
        raise ValueError("nonnegative integer hop budget required")
    if start not in graph:
        return []
    queue = deque([(start, 0)])
    seen = {start}
    result = []
    while queue:
        node, depth = queue.popleft()
        result.append(node)
        if depth == max_hops:
            continue
        for target in graph[node]:
            if target in graph and target not in seen:
                seen.add(target)
                queue.append((target, depth + 1))
    return result


def verify():
    # Exercise 1: Apply a controlled synonym rewrite
    original = "buy rate"
    rewritten = rewrite(original, {"buy": "purchase"})
    assert rewritten == "purchase rate" and original == "buy rate"

    # Exercise 2: Retain a rewrite trace
    trace = {"original": original, "rewritten": rewritten, "policy": "synonyms-v1"}
    assert set(trace) == {"original", "rewritten", "policy"}

    # Exercise 3: Follow two evidence hops
    graph = {"metric": ["exclusions"], "exclusions": ["test_accounts"], "test_accounts": []}
    assert walk("metric", graph, 2) == ["metric", "exclusions", "test_accounts"]

    # Exercise 4: Stop at the declared depth
    assert walk("metric", graph, 1) == ["metric", "exclusions"]
    for bad_budget in [1.5, True, float("nan"), -1]:
        try:
            walk("metric", graph, bad_budget)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid hop budget accepted")

    # Exercise 5: Break a retrieval cycle
    cyclic = {**graph, "test_accounts": ["metric"]}
    result = walk("metric", cyclic, 10)
    assert result == ["metric", "exclusions", "test_accounts"] and len(result) == len(set(result))

    # Exercise 6: Preserve authorization across hops
    admitted = {"metric": ["restricted"], "public": []}
    assert walk("metric", admitted, 3) == ["metric"]
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
