import { strict as assert } from "node:assert";
import { setTimeout as delay } from "node:timers/promises";

type Result<T> =
  | { ok: true; value: T }
  | { ok: false; error: "not_found" | "cancelled" | "operational" };
async function lookup(id: string): Promise<Result<number>> {
  return id === "A" ? { ok: true, value: 7 } : { ok: false, error: "not_found" };
}
async function waitForValue(signal: AbortSignal): Promise<Result<number>> {
  try {
    const value = await delay(1000, 7, { signal });
    return { ok: true, value };
  } catch (error: unknown) {
    if (error instanceof Error && error.name === "AbortError")
      return { ok: false, error: "cancelled" };
    throw error;
  }
}

export async function verify(): Promise<{ checks: number; status: string }> {
  // Exercise 1: Await and narrow a result
  {
    const present = await lookup("A");
    if (!present.ok) throw new Error(present.error);
    assert.equal(present.value, 7);
    assert.deepEqual(await lookup("missing"), { ok: false, error: "not_found" });
  }

  // Exercise 2: Show a failure result does not invoke catch
  {
    let caught = 0;
    const result = await lookup("missing").catch(() => {
      caught += 1;
      return { ok: false as const, error: "operational" as const };
    });
    assert.equal(caught, 0);
    assert.deepEqual(result, { ok: false, error: "not_found" });
  }

  // Exercise 3: Translate recognized cancellation
  {
    const controller = new AbortController();
    const pending = waitForValue(controller.signal);
    controller.abort(new Error("stop"));
    assert.deepEqual(await pending, { ok: false, error: "cancelled" });
  }

  // Exercise 4: Inspect an unknown rejection reason
  {
    function message(error: unknown): string {
      return error instanceof Error ? error.message : "unclassified failure";
    }
    try {
      await Promise.reject("not an Error");
    } catch (error: unknown) {
      assert.equal(message(error), "unclassified failure");
    }
  }

  // Exercise 5: Preserve every batch outcome
  {
    const outcomes = await Promise.allSettled([
      Promise.resolve(2),
      Promise.reject(new Error("offline")),
    ]);
    const summaries = outcomes.map((outcome) => {
      if (outcome.status === "fulfilled") return `value:${outcome.value}`;
      const reason: unknown = outcome.reason;
      return `error:${reason instanceof Error ? reason.message : "unknown"}`;
    });
    assert.deepEqual(summaries, ["value:2", "error:offline"]);
  }

  // Exercise 6: Reject unresolved and unnarrowed access
  {
    function negativeTypeCheck(result: Result<number>): void {
      // @ts-expect-error The failure alternative has no value.
      void result.value;
      // @ts-expect-error lookup returns a Promise, not an immediate payload.
      void lookup("A").value;
    }
    void negativeTypeCheck;
    assert.deepEqual(await lookup("A"), { ok: true, value: 7 });
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
