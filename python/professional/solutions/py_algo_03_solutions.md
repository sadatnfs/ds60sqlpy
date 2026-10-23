# python-algo-03: Explained reference solutions

These answers implement the contracts in [Graph Traversal, Priority Queues, and Shortest-Path Evidence](../companion-guides/py_algo_03.md). Compare after an attempt. The [executable reference](py_algo_03_solution.py) contains the complete implementations and assertions. Each answer explains the mechanism, not just the final value.

## Exercises and reasoning

### Exercise 1: Validate the shortest-path assumptions

Require string vertex labels, edges to existing vertices and finite nonnegative numeric weights. Reject Boolean weights, missing neighbor vertices, negative weights and nonfinite weights with ValueError. Empty graphs are valid structures.

**Expected:** a->b with weight 2 passes when both vertices exist. Weight-1, NaN, True or an edge to absent z fails.

```python
def validate_graph(graph: dict[str, list[tuple[str, float]]]) -> None:
    if any(not isinstance(vertex,str) for vertex in graph):
        raise ValueError("Vertex labels must be strings")
    for edges in graph.values():
        for neighbor,weight in edges:
            if neighbor not in graph or isinstance(weight,bool) or not isinstance(weight,(int,float)) or not math.isfinite(weight) or weight<0:
                raise ValueError("Edges need existing vertices and finite nonnegative weights")
```

Validation establishes the assumptions used by the Dijkstra proof before any route is reported. Including every neighbor as an explicit vertex distinguishes an unreachable or terminal node from a misspelled label. A zero-weight edge is permitted and can be meaningful; a negative edge is rejected because it changes the algorithmic problem. The graph can contain cycles under these nonnegative weights, even though the later topological-order function will reject cycles for its own purpose.

```python
validate_graph({"a":[("b",2.)],"b":[]});validate_graph({})
expect_value_error(lambda:validate_graph({"a":[("z",1.)]}))
expect_value_error(lambda:validate_graph({"a":[("a",-1.)]}))
expect_value_error(lambda:validate_graph({"a":[("a",math.nan)]}))
expect_value_error(lambda:validate_graph({"a":[("a",True)]}))
```

### Exercise 2: Find minimum edge counts

Return minimum hop counts from start to reachable vertices using a deque frontier. Ignore edge magnitudes for this hop-count question, but validate graph and require start to exist. Do not include unreachable vertices in the result.

**Expected:** For a->b(weight 10), a->c(weight 1), c->b(weight 1), hops are a 0, b1, c1. An isolated d is absent; an unknown start raises ValueError.

```python
def bfs_hops(graph: dict[str, list[tuple[str, float]]], start: str) -> dict[str, int]:
    validate_graph(graph)
    if start not in graph:
        raise ValueError("Start vertex is absent")
    distance={start:0};frontier=deque([start])
    while frontier:
        vertex=frontier.popleft()
        for neighbor,_ in graph[vertex]:
            if neighbor not in distance:
                distance[neighbor]=distance[vertex]+1
                frontier.append(neighbor)
    return distance
```

A FIFO queue processes all vertices at hop distance d before vertices at distance d+1. Marking a vertex when it is enqueued prevents duplicate frontier entries and ensures its first discovered hop count is minimal. Edge weights remain irrelevant by contract, so this result should not be relabeled as minimum travel cost. The isolated-node test verifies that reachability is represented honestly.

```python
g={"a":[("b",10.),("c",1.)],"b":[],"c":[("b",1.)],"d":[]}
assert bfs_hops(g,"a")=={"a":0,"b":1,"c":1}
assert bfs_hops(g,"d")=={"d":0}
expect_value_error(lambda:bfs_hops(g,"z"))
```

### Exercise 3: Use cumulative cost and skip stale entries

Return distances and parent links for every graph vertex using a min-heap and nonnegative weights. Unreachable vertices retain infinity and None. Push improved candidates and skip stale popped entries. Reject an absent start or cumulative-cost overflow.

**Expected:** In the a, b, c, d fixture, distances are a 0, c1, b2, d infinity and parent[b]=c. The earlier direct b cost 10 must not overwrite the improved cost 2.

```python
def dijkstra(graph: dict[str, list[tuple[str, float]]], start: str) -> tuple[dict[str, float], dict[str, str | None]]:
    validate_graph(graph)
    if start not in graph:
        raise ValueError("Start vertex is absent")
    distance={vertex:math.inf for vertex in graph};parent={vertex:None for vertex in graph}
    distance[start]=0.;frontier=[(0.,start)]
    while frontier:
        cost,vertex=heapq.heappop(frontier)
        if cost!=distance[vertex]:
            continue
        for neighbor,weight in graph[vertex]:
            candidate=cost+weight
            if not math.isfinite(candidate):
                raise ValueError("Cumulative path cost exceeds finite floating range")
            if candidate<distance[neighbor]:
                distance[neighbor]=candidate;parent[neighbor]=vertex
                heapq.heappush(frontier,(candidate,neighbor))
    return distance,parent
```

The heap initially contains a direct route to b costing ten, then receives a cheaper route costing two through c. The old entry remains but is ignored because it no longer matches the distance table. Parent links change only on strict improvement, retaining a deterministic route for this fixture. Nonnegative weights justify processing minimum known costs; removing the validation would invalidate that argument even if some negative-edge examples happened to work.

```python
distance,parent=dijkstra(g,"a")
assert distance["a"]==0 and distance["c"]==1 and distance["b"]==2 and math.isinf(distance["d"])
assert parent["b"]=="c" and parent["d"] is None
expect_value_error(lambda:dijkstra(g,"z"))
expect_value_error(lambda:dijkstra({"a":[("b",1e308)],"b":[("c",1e308)],"c":[]},"a"))
```

### Exercise 4: Verify a route rather than only its score

Reconstruct a start-to-goal path from parent links. Return None for an unreachable goal, return [start] when start equals goal, and reject absent vertices, unknown parent labels or a cycle encountered during reconstruction.

**Expected:** Parents from dijkstra produce[a, c, b] for a to b and None for a to d. A parent cycle x->y->x raises ValueError rather than looping.

```python
def reconstruct_path(parent: dict[str, str | None], start: str, goal: str) -> list[str] | None:
    if start not in parent or goal not in parent:
        raise ValueError("Start and goal must appear in the parent map")
    path=[];seen=set();vertex=goal
    while vertex!=start:
        if vertex in seen or vertex not in parent:
            raise ValueError("Parent chain contains a cycle or unknown vertex")
        seen.add(vertex);path.append(vertex);vertex=parent[vertex]
        if vertex is None:
            return None
    path.append(start)
    return list(reversed(path))
```

A distance is a numerical claim; the path supplies concrete transitions that can be independently checked and summed. Walking backward follows the predecessor relation, and reversing restores travel order. None terminates an unreachable chain, while a visited set prevents malformed evidence from causing an infinite loop. A zero-edge start-to-itself path is valid and differs from no path, so the return values preserve that distinction.

```python
assert reconstruct_path(parent,"a","b")==["a","c","b"]
assert reconstruct_path(parent,"a","d") is None and reconstruct_path(parent,"a","a")==["a"]
expect_value_error(lambda:reconstruct_path({"a":None,"x":"y","y":"x"},"a","x"))
expect_value_error(lambda:reconstruct_path({"a":None,"b":"missing"},"a","b"))
```

### Exercise 5: Order dependencies and expose cycles

Return a topological order using indegrees and a heap of available string labels, choosing the lexicographically smallest available vertex. Include isolated vertices. Raise ValueError when a directed cycle prevents processing every vertex.

**Expected:** a->c, b->c plus isolated d yields [a, b, c, d]. Every edge source precedes its target. a->b, b->a raises ValueError; empty graph returns [].

```python
def topological_order(graph: dict[str, list[tuple[str, float]]]) -> list[str]:
    validate_graph(graph)
    indegree={vertex:0 for vertex in graph}
    for edges in graph.values():
        for neighbor,_ in edges:
            indegree[neighbor]+=1
    frontier=[vertex for vertex,degree in indegree.items() if degree==0];heapq.heapify(frontier)
    result=[]
    while frontier:
        vertex=heapq.heappop(frontier);result.append(vertex)
        for neighbor,_ in graph[vertex]:
            indegree[neighbor]-=1
            if indegree[neighbor]==0:
                heapq.heappush(frontier,neighbor)
    if len(result)!=len(graph):
        raise ValueError("A directed cycle prevents a topological order")
    return result
```

Indegree counts unprocessed prerequisites. Only zero-indegree vertices are eligible, so removing one and updating its outgoing neighbors preserves dependency correctness. The heap adds a deterministic choice among eligible labels; it does not declare that this is the only valid topological order. If a cycle remains, no vertex within that cycle can become eligible, and the final count exposes the failure.

```python
dag={"a":[("c",1.)],"b":[("c",1.)],"c":[],"d":[]}
order=topological_order(dag)
assert order==["a","b","c","d"]
position={vertex:index for index,vertex in enumerate(order)}
assert all(position[source]<position[target] for source,edges in dag.items() for target,_ in edges)
expect_value_error(lambda:topological_order({"a":[("b",1.)],"b":[("a",1.)]}))
assert topological_order({})==[]
```

### Exercise 6: Transfer priority-queue reasoning to a stream

Consume finite numeric values and retain the k largest values, including duplicates, using at most k heap entries. Return descending values. Require nonnegative non-Boolean integer k and reject nonfinite input; k0 still validates the input stream.

**Expected:** [4,1,9,3,8] with k3 gives [9,8,4]; [2,2,1] with k2 gives [2,2]. Empty input or k0 yields []; NaN raises ValueError.

```python
def largest_k(values, k: int) -> list[float]:
    if isinstance(k,bool) or not isinstance(k,int) or k<0:
        raise ValueError("Expected a nonnegative integer k")
    heap=[]
    for raw in values:
        value=float(raw)
        if not math.isfinite(value):
            raise ValueError("Expected finite stream values")
        if k==0:
            continue
        if len(heap)<k:
            heapq.heappush(heap,value)
        else:
            heapq.heappushpop(heap,value)
    return sorted(heap,reverse=True)
```

Once the heap has k entries, its smallest candidate is the only one a new value can displace. heappushpop keeps the larger candidates without growing retained state beyond k. Duplicates remain because this is a multiset ranking task, not unique-value selection. Sorting only the final heap costs work in k rather than the full stream length. Input validation remains active even when no outputs are requested, avoiding a hidden bypass for malformed data.

```python
assert largest_k(iter([4,1,9,3,8]),3)==[9.,8.,4.]
assert largest_k([2,2,1],2)==[2.,2.] and largest_k([],3)==[] and largest_k([1,2],0)==[]
expect_value_error(lambda:largest_k([math.nan],0))
expect_value_error(lambda:largest_k([1],True))
```

## Verification and interpretation

Run `python python/professional/solutions/py_algo_03_solution.py` from the repository root with the prepared interpreter. The code checks normal inputs and explicit edge cases before printing its success line. Assertions are the evidence; the printed sentence alone is not. The helper `expect_value_error` requires an actual `ValueError` and fails if a function silently accepts an invalid input. Inspect each function's mutation and ordering behavior as part of its contract.
