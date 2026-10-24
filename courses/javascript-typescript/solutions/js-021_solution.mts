import { strict as assert } from 'node:assert';



export async function verify(): Promise<{ checks: number; status: string }> {
  // Exercise 1: Use structural compatibility
  {
    function label(value: { id: string }): string { return value.id; }
    const wider = { id: 'A', count: 2 };
    assert.equal(label(wider), 'A');
    assert.equal(wider.count, 2);
    function negativeTypeCheck(): void {
      // @ts-expect-error A fresh literal is checked for excess properties.
      label({ id: 'A', count: 2 });
    }
    void negativeTypeCheck;
  }

  // Exercise 2: Observe mutation through an alias
  {
    const mutable = { count: 1 };
    const view: Readonly<{ count: number }> = mutable;
    mutable.count = 4;
    assert.equal(view.count, 4);
    function negativeTypeCheck(): void {
      // @ts-expect-error Writes through the readonly view are forbidden.
      view.count = 9;
    }
    void negativeTypeCheck;
  }

  // Exercise 3: Handle absent and zero-valued optional counts
  {
    type Options = { count?: number };
    function count(options: Options): number { return options.count ?? 10; }
    assert.equal(count({}), 10);
    assert.equal(count({ count: 0 }), 0);
  }

  // Exercise 4: Distinguish runtime presence from undefined
  {
    const absent: { count?: number } = {};
    const present: { count?: number } = { count: undefined };
    assert.equal(Object.hasOwn(absent, 'count'), false);
    assert.equal(Object.hasOwn(present, 'count'), true);
    assert.equal(JSON.stringify(absent), '{}');
    assert.equal(JSON.stringify(present), '{}');
  }

  // Exercise 5: Show shallow readonly and shallow freeze boundaries
  {
    const record = Object.freeze({ nested: { count: 1 } });
    record.nested.count = 3;
    assert.equal(record.nested.count, 3);
    assert.equal(Object.isFrozen(record), true);
    assert.equal(Object.isFrozen(record.nested), false);
  }

  // Exercise 6: Transform a readonly array without mutation
  {
    const values: readonly number[] = [1, 2];
    const doubled = values.map(value => value * 2);
    assert.deepEqual(doubled, [2, 4]);
    assert.deepEqual(values, [1, 2]);
    function negativeTypeCheck(): void {
      // @ts-expect-error A readonly array has no mutable push operation.
      values.push(3);
    }
    void negativeTypeCheck;
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
