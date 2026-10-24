import { strict as assert } from 'node:assert';

type Graph = ReadonlyMap<string, readonly string[]>;
function shortestPath(graph: Graph, start: string, target: string): string[] | undefined {
  if (!graph.has(start) || !graph.has(target)) throw new RangeError('start and target must exist');
  for (const neighbors of graph.values()) for (const neighbor of neighbors) {
    if (!graph.has(neighbor)) throw new RangeError('missing neighbor');
  }
  const queue = [start];
  const parent = new Map<string, string | null>([[start, null]]);
  for (let cursor = 0; cursor < queue.length; cursor += 1) {
    const vertex = queue[cursor];
    if (vertex === target) {
      const path: string[] = [];
      let current: string | null = vertex;
      while (current !== null) {
        path.push(current);
        const previous: string | null | undefined = parent.get(current);
        if (previous === undefined) throw new Error('broken parent invariant');
        current = previous;
      }
      return path.reverse();
    }
    for (const neighbor of graph.get(vertex) ?? []) {
      if (!parent.has(neighbor)) { parent.set(neighbor, vertex); queue.push(neighbor); }
    }
  }
  return undefined;
}
function minCoins(coins: readonly number[], amount: number): number | undefined {
  if (!Number.isInteger(amount) || amount < 0 || amount > 1000 || coins.some(coin => !Number.isSafeInteger(coin) || coin <= 0)) throw new RangeError('positive coins and amount from 0 to 1000 required');
  const best: number[] = Array.from({ length: amount + 1 }, () => Infinity);
  best[0] = 0;
  for (let value = 1; value <= amount; value += 1) {
    for (const coin of coins) if (coin <= value) best[value] = Math.min(best[value], best[value - coin] + 1);
  }
  return Number.isFinite(best[amount]) ? best[amount] : undefined;
}

export async function verify(): Promise<{ checks: number; status: string }> {
  // Exercise 1: Find a shortest unweighted path
  {
    const graph: Graph = new Map([['A', ['B', 'C']], ['B', ['D']], ['C', ['D']], ['D', []]]);
    assert.deepEqual(shortestPath(graph, 'A', 'D'), ['A', 'B', 'D']);
  }

  // Exercise 2: Beat greedy coin selection
  {
    assert.equal(minCoins([1, 3, 4], 6), 2);
    assert.equal(minCoins([1, 3, 4], 0), 0);
  }

  // Exercise 3: Terminate on a cyclic graph
  {
    const graph: Graph = new Map([['A', ['B']], ['B', ['A', 'C']], ['C', ['B']]]);
    assert.deepEqual(shortestPath(graph, 'A', 'C'), ['A', 'B', 'C']);
    assert.deepEqual(shortestPath(graph, 'A', 'A'), ['A']);
  }

  // Exercise 4: Separate disconnection from malformed input
  {
    assert.equal(shortestPath(new Map([['A', []], ['B', []]]), 'A', 'B'), undefined);
    assert.throws(() => shortestPath(new Map([['A', ['missing']]]), 'A', 'A'), RangeError);
  }

  // Exercise 5: Represent unreachable coin amounts
  {
    assert.equal(minCoins([2], 3), undefined);
    assert.equal(minCoins([2], 4), 2);
  }

  // Exercise 6: Reject invalid recurrence configurations
  {
    for (const coins of [[0], [-1], [1.5]]) assert.throws(() => minCoins(coins, 5), RangeError);
    assert.throws(() => minCoins([1], 1001), RangeError);
    assert.equal(minCoins([], 1), undefined);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
