import { strict as assert } from "node:assert";

export async function verify(): Promise<{ checks: number; status: string }> {
  // Exercise 1: Map a record into field flags
  {
    type Row = { id: string; count: number };
    type Flags<T> = { [K in keyof T]: boolean };
    const flags: Flags<Row> = { id: true, count: false };
    assert.deepEqual(flags, { id: true, count: false });
    function negativeTypeCheck(): void {
      // @ts-expect-error Every Row key must have a flag.
      const incomplete: Flags<Row> = { id: true };
      void incomplete;
    }
    void negativeTypeCheck;
  }

  // Exercise 2: Prove Omit does not remove runtime secrets
  {
    type RecordWithSecret = { id: string; secret: string };
    const full: RecordWithSecret = { id: "A", secret: "fixture-only" };
    const view: Omit<RecordWithSecret, "secret"> = full;
    assert.equal(Object.hasOwn(view, "secret"), true);
    const publicRecord: Pick<RecordWithSecret, "id"> = { id: full.id };
    assert.equal(Object.hasOwn(publicRecord, "secret"), false);
    assert.equal(JSON.stringify(publicRecord), '{"id":"A"}');
  }

  // Exercise 3: Compare distributed and whole-union array types
  {
    type Distributed<T> = T extends unknown ? T[] : never;
    type Whole<T> = [T] extends [unknown] ? T[] : never;
    const mixed: Whole<string | number> = ["A", 2];
    assert.deepEqual(mixed, ["A", 2]);
    function negativeTypeCheck(): void {
      // @ts-expect-error Distributed<string|number> is string[] | number[].
      const invalid: Distributed<string | number> = ["A", 2];
      void invalid;
    }
    void negativeTypeCheck;
  }

  // Exercise 4: Infer an array element type
  {
    type ElementOf<T> = T extends readonly (infer Item)[] ? Item : never;
    const value: ElementOf<readonly number[]> = 7;
    assert.equal(value, 7);
    function negativeTypeCheck(): void {
      // @ts-expect-error The extracted element type is number.
      const invalid: ElementOf<readonly number[]> = "seven";
      void invalid;
    }
    void negativeTypeCheck;
  }

  // Exercise 5: Derive an asynchronous result type without executing it
  {
    async function load(): Promise<{ count: number }> {
      return { count: 3 };
    }
    type Loaded = Awaited<ReturnType<typeof load>>;
    const expected: Loaded = { count: 3 };
    assert.deepEqual(await load(), expected);
  }

  // Exercise 6: Check a configuration with satisfies
  {
    const labels = { success: "Ready", failure: "Retry" } satisfies Record<
      "success" | "failure",
      string
    >;
    assert.equal(labels.success, "Ready");
    function negativeTypeCheck(): void {
      // @ts-expect-error typo is not a permitted literal key and failure is absent.
      const invalid = { success: "Ready", typo: "Retry" } satisfies Record<
        "success" | "failure",
        string
      >;
      void invalid;
    }
    void negativeTypeCheck;
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
