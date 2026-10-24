import { strict as assert } from "node:assert";

function identity<T>(value: T): T {
  return value;
}
function getProperty<T, K extends keyof T>(value: T, key: K): T[K] {
  return value[key];
}
function first<T>(values: readonly T[]): T | undefined {
  return values.length === 0 ? undefined : values[0];
}
function measuredLength<T extends { length: number }>(value: T): number {
  return value.length;
}
function mapValues<T, U>(values: readonly T[], convert: (value: T) => U): U[] {
  return values.map(convert);
}

export async function verify(): Promise<{ checks: number; status: string }> {
  // Exercise 1: Preserve identity type and object identity
  {
    const value: number = identity(7);
    const record = { id: "A" };
    assert.equal(value, 7);
    assert.equal(identity(record), record);
    function negativeTypeCheck(): void {
      // @ts-expect-error identity preserves number rather than inventing string.
      const text: string = identity(7);
      void text;
    }
    void negativeTypeCheck;
  }

  // Exercise 2: Connect a key to its exact result type
  {
    const row = { id: "A", count: 2 };
    const id: string = getProperty(row, "id");
    const count: number = getProperty(row, "count");
    assert.equal(id, "A");
    assert.equal(count, 2);
    function negativeTypeCheck(): void {
      // @ts-expect-error missing is not a key of this record.
      getProperty(row, "missing");
    }
    void negativeTypeCheck;
  }

  // Exercise 3: Expose absence in a generic first function
  {
    assert.equal(first([4, 5]), 4);
    assert.equal(first<number>([]), undefined);
    function negativeTypeCheck(): void {
      // @ts-expect-error The function promises possible absence.
      const definite: number = first<number>([]);
      void definite;
    }
    void negativeTypeCheck;
  }

  // Exercise 4: Use only the constrained length property
  {
    assert.equal(measuredLength("abc"), 3);
    assert.equal(measuredLength([1, 2]), 2);
    function negativeTypeCheck(): void {
      // @ts-expect-error number has no required length property.
      measuredLength(7);
    }
    void negativeTypeCheck;
  }

  // Exercise 5: Transform while preserving output element type
  {
    const values = [2, 4];
    const labels: string[] = mapValues(values, (value) => `item:${value}`);
    assert.deepEqual(labels, ["item:2", "item:4"]);
    assert.deepEqual(values, [2, 4]);
  }

  // Exercise 6: Avoid pretending a constraint is the exact caller type
  {
    function negativeTypeCheck<T extends { length: number }>(value: T): T {
      void value;
      // @ts-expect-error T may require additional fields or a more specific shape.
      return { length: 0 };
    }
    void negativeTypeCheck;
    assert.equal(measuredLength({ length: 5, id: "A" }), 5);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
