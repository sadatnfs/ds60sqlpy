"""Reference implementation and exact boundary checks for python-algo-03."""

import math
import heapq
from collections import deque

def validate_graph(graph: dict[str, list[tuple[str, float]]]) -> None:
    if any(not isinstance(vertex,str) for vertex in graph):
        raise ValueError("Vertex labels must be strings")
    for edges in graph.values():
        for neighbor,weight in edges:
            if neighbor not in graph or isinstance(weight,bool) or not isinstance(weight,(int,float)) or not math.isfinite(weight) or weight<0:
                raise ValueError("Edges need existing vertices and finite nonnegative weights")

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

def expect_value_error(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")

def main():
    # Exercise 1: Validate the shortest-path assumptions
    validate_graph({"a":[("b",2.)],"b":[]});validate_graph({})
    expect_value_error(lambda:validate_graph({"a":[("z",1.)]}))
    expect_value_error(lambda:validate_graph({"a":[("a",-1.)]}))
    expect_value_error(lambda:validate_graph({"a":[("a",math.nan)]}))
    expect_value_error(lambda:validate_graph({"a":[("a",True)]}))
    # Exercise 2: Find minimum edge counts
    g={"a":[("b",10.),("c",1.)],"b":[],"c":[("b",1.)],"d":[]}
    assert bfs_hops(g,"a")=={"a":0,"b":1,"c":1}
    assert bfs_hops(g,"d")=={"d":0}
    expect_value_error(lambda:bfs_hops(g,"z"))
    # Exercise 3: Use cumulative cost and skip stale entries
    distance,parent=dijkstra(g,"a")
    assert distance["a"]==0 and distance["c"]==1 and distance["b"]==2 and math.isinf(distance["d"])
    assert parent["b"]=="c" and parent["d"] is None
    expect_value_error(lambda:dijkstra(g,"z"))
    expect_value_error(lambda:dijkstra({"a":[("b",1e308)],"b":[("c",1e308)],"c":[]},"a"))
    # Exercise 4: Verify a route rather than only its score
    assert reconstruct_path(parent,"a","b")==["a","c","b"]
    assert reconstruct_path(parent,"a","d") is None and reconstruct_path(parent,"a","a")==["a"]
    expect_value_error(lambda:reconstruct_path({"a":None,"x":"y","y":"x"},"a","x"))
    expect_value_error(lambda:reconstruct_path({"a":None,"b":"missing"},"a","b"))
    # Exercise 5: Order dependencies and expose cycles
    dag={"a":[("c",1.)],"b":[("c",1.)],"c":[],"d":[]}
    order=topological_order(dag)
    assert order==["a","b","c","d"]
    position={vertex:index for index,vertex in enumerate(order)}
    assert all(position[source]<position[target] for source,edges in dag.items() for target,_ in edges)
    expect_value_error(lambda:topological_order({"a":[("b",1.)],"b":[("a",1.)]}))
    assert topological_order({})==[]
    # Exercise 6: Transfer priority-queue reasoning to a stream
    assert largest_k(iter([4,1,9,3,8]),3)==[9.,8.,4.]
    assert largest_k([2,2,1],2)==[2.,2.] and largest_k([],3)==[] and largest_k([1,2],0)==[]
    expect_value_error(lambda:largest_k([math.nan],0))
    expect_value_error(lambda:largest_k([1],True))
    print("python-algo-03: all six normal and boundary contracts passed")

if __name__ == "__main__":
    main()
