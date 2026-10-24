import { strict as assert } from "node:assert";

type Result = { kind: "success"; value: number } | { kind: "failure"; message: string };
function assertNever(value: never): never {
  throw new Error("unhandled variant: " + JSON.stringify(value));
}
function formatResult(result: Result): string {
  switch (result.kind) {
    case "success":
      return `value:${result.value}`;
    case "failure":
      return `error:${result.message}`;
    default:
      return assertNever(result);
  }
}

export async function verify(): Promise<{ checks: number; status: string }> {
  // Exercise 1: Handle a result union
  {
    assert.equal(formatResult({ kind: "success", value: 7 }), "value:7");
    assert.equal(formatResult({ kind: "failure", message: "offline" }), "error:offline");
  }

  // Exercise 2: Preserve an empty string during narrowing
  {
    function describe(value: string | undefined): number | "missing" {
      return value === undefined ? "missing" : value.length;
    }
    assert.equal(describe(""), 0);
    assert.equal(describe(undefined), "missing");
  }

  // Exercise 3: Reject access to another variant payload
  {
    function negativeTypeCheck(result: Result): void {
      if (result.kind === "failure") {
        // @ts-expect-error failure has message, not value.
        void result.value;
      }
    }
    void negativeTypeCheck;
    assert.equal(formatResult({ kind: "failure", message: "bad" }), "error:bad");
  }

  // Exercise 4: Catch an unhandled new variant at compile time
  {
    type Extended = Result | { kind: "pending"; attempt: number };
    function negativeTypeCheck(result: Extended): string {
      switch (result.kind) {
        case "success":
          return String(result.value);
        case "failure":
          return result.message;
        default:
          // @ts-expect-error pending remains possible here.
          return assertNever(result);
      }
    }
    void negativeTypeCheck;
    assert.equal(formatResult({ kind: "success", value: 0 }), "value:0");
  }

  // Exercise 5: Use an honest unknown-value predicate
  {
    function hasFiniteValue(value: unknown): value is { value: number } {
      return (
        typeof value === "object" &&
        value !== null &&
        !Array.isArray(value) &&
        "value" in value &&
        typeof value.value === "number" &&
        Number.isFinite(value.value)
      );
    }
    assert.equal(hasFiniteValue({ value: 2 }), true);
    for (const value of [null, [], { value: "2" }, { value: NaN }])
      assert.equal(hasFiniteValue(value), false);
  }

  // Exercise 6: Expose the runtime limit of an asserted union
  {
    const malformed: unknown = { kind: "unexpected" };
    assert.throws(() => formatResult(malformed as Result), /unhandled variant/u);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
