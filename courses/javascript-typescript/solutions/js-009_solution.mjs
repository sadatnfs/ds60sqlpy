import { strict as assert } from 'node:assert';

function validateOrder(value) {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) throw new TypeError('order object required');
  const keys = Object.keys(value).sort();
  if (keys.join(',') !== 'id,priceCents,quantity' || typeof value.id !== 'string' || value.id === '') throw new TypeError('exact order schema required');
  if (!Number.isSafeInteger(value.quantity) || value.quantity <= 0 || !Number.isSafeInteger(value.priceCents) || value.priceCents < 0) throw new RangeError('valid integer quantity and cents required');
  return { id: value.id, quantity: value.quantity, priceCents: value.priceCents };
}
function total(order) {
  const result = order.quantity * order.priceCents;
  if (!Number.isSafeInteger(result)) throw new RangeError('total exceeds safe integer range');
  return result;
}

export async function verify() {
  // Exercise 1: Accept a valid order
  {
    const raw = { id: 'A', quantity: 2, priceCents: 125 };
    const order = validateOrder(raw);
    assert.equal(total(order), 250);
    assert.notEqual(order, raw);
  }

  // Exercise 2: Reject syntactically valid but wrong-shaped JSON
  {
    for (const text of ['null', '[]', '{"id":"A","quantity":1,"priceCents":2,"extra":true}']) {
      assert.throws(() => validateOrder(JSON.parse(text)), TypeError);
    }
  }

  // Exercise 3: Reject invalid numeric domain values
  {
    for (const raw of [{ id: 'A', quantity: 0, priceCents: 2 }, { id: 'A', quantity: 1.5, priceCents: 2 }, { id: 'A', quantity: 1, priceCents: -1 }]) {
      assert.throws(() => validateOrder(raw), RangeError);
    }
  }

  // Exercise 4: Prevent unsafe integer multiplication
  {
    const order = validateOrder({ id: 'A', quantity: 2, priceCents: Number.MAX_SAFE_INTEGER });
    assert.throws(() => total(order), RangeError);
  }

  // Exercise 5: Preserve a translated cause
  {
    const original = new SyntaxError('invalid fixture JSON');
    const contextual = new Error('Cannot read order fixture', { cause: original });
    assert.equal(contextual.cause, original);
    assert.match(contextual.message, /order fixture/u);
  }

  // Exercise 6: Prove rejected input caused no mutation
  {
    const raw = { id: 'A', quantity: -1, priceCents: 5 };
    const before = structuredClone(raw);
    assert.throws(() => validateOrder(raw), RangeError);
    assert.deepEqual(raw, before);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
