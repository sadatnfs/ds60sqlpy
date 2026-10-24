import { strict as assert } from 'node:assert';



export async function verify() {
  // Exercise 1: Inspect the actual host
  {
    assert.equal(Number(process.versions.node.split('.')[0]), 24);
    assert.equal(process.release.name, 'node');
  }

  // Exercise 2: Distinguish browser globals
  {
    assert.equal(typeof document, 'undefined');
    assert.equal(typeof window, 'undefined');
  }

  // Exercise 3: Use language arithmetic independently of host APIs
  {
    const total = 2 + 3;
    assert.equal(total, 5);
    assert.notEqual(total, '5');
  }

  // Exercise 4: Inspect module identity
  {
    assert.equal(new URL(import.meta.url).protocol, 'file:');
    assert.ok(import.meta.url.endsWith('.mjs'));
  }

  // Exercise 5: Observe strict module function calls
  {
    function receiver() { return this; }
    assert.equal(receiver(), undefined);
  }

  // Exercise 6: Await a real Promise result
  {
    const pending = Promise.resolve(7);
    assert.ok(pending instanceof Promise);
    const value = await pending;
    assert.equal(value, 7);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
